import requests
from typing import Dict, Any, List, Optional
import os
import base64
import json
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "https://pickleballkingdom.podplay.app/apis/v2/events"
QUERY_PARAMS = "excludeUnlisted=true&ipp=500"
FIREBASE_APP_ID = "AIzaSyAsK04VLy0Jd42PhjJz2n1w1hVJNTYKHmw"


class APIError(Exception):
    pass


class PodPlayClient:
    def __init__(self, token: str = ""):
        self._token = token

    @classmethod
    def from_env(cls) -> "PodPlayClient":
        """Create a client using the token stored in PODPLAY_TOKEN."""
        return cls(token=os.getenv("PODPLAY_TOKEN", ""))

    def is_authenticated(self) -> bool:
        """Return True if the current token is present and not expired."""
        if not self._token:
            return False
        try:
            payload_b64 = self._token.split(".")[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            return time.time() < payload.get("exp", 0)
        except Exception:
            return False

    def authenticate(self, email: str, password: str) -> None:
        """Fetch a fresh token from Firebase and persist it to .env."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_APP_ID}"
        try:
            response = requests.post(url, json={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            }, timeout=10)
            response.raise_for_status()
            token = response.json().get("idToken")
            if not token:
                raise APIError("Firebase returned no idToken")
            self._token = token
            self._save_token()
        except requests.exceptions.HTTPError:
            message = response.json().get("error", {}).get("message", "unknown error")
            raise APIError(f"Authentication failed: {message}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error during authentication: {e}")

    def get_events(
        self,
        *,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 5,
        city: Optional[str] = None,
        event_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch events from the API with optional filtering.

        Args:
            start_date: Start of the date window (default: now).
            end_date: End of the date window (default: start_date + days).
            days: Days ahead to fetch when end_date is not specified (default: 5).
            city: If provided, only return events at facilities in this city.
            event_name: If provided, only return events with this exact name.
        """
        headers = {"Authorization": f"Bearer {self._token}"}
        all_events = []
        page = 1
        items_per_page = 500
        max_pages = 10

        window_start = start_date if start_date is not None else datetime.now(timezone.utc)
        window_end = end_date if end_date is not None else window_start + timedelta(days=days)
        date_params = (
            f"&startDate={window_start.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            f"&endDate={window_end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )

        try:
            while page <= max_pages:
                url = f"{BASE_URL}?{QUERY_PARAMS}{date_params}&page={page}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                items = data.get('items', []) if isinstance(data, dict) else data

                if not items:
                    break

                all_events.extend(items)

                if len(items) < items_per_page:
                    break

                # Early exit: if last event on this page is past the window,
                # later pages will only be further out.
                try:
                    last_dt = datetime.fromisoformat(items[-1].get('startTime', '').replace('Z', '+00:00'))
                    if last_dt > window_end:
                        break
                except (ValueError, TypeError):
                    pass

                page += 1

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise APIError("Invalid or expired token (401 Unauthorized)")
            raise APIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {e}")

        if event_name is not None:
            all_events = [e for e in all_events if e.get('name', '').strip() == event_name]

        if city is not None:
            def _city(event: Dict[str, Any]) -> str:
                pods = event.get('pods', {}).get('items', [])
                return pods[0].get('address', {}).get('city', '') if pods else ''
            all_events = [e for e in all_events if _city(e) == city]

        return all_events

    def _save_token(self) -> None:
        """Persist the current token to .env."""
        from dotenv import find_dotenv, set_key
        env_path = find_dotenv()
        if env_path:
            set_key(env_path, "PODPLAY_TOKEN", self._token)
