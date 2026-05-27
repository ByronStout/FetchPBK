import requests
from typing import List, Dict, Any
import os
import base64
import json
import time

BASE_URL = "https://pickleballkingdom.podplay.app/apis/v2/events"
QUERY_PARAMS = "excludeUnlisted=true&ipp=500"
FIREBASE_API_KEY = "AIzaSyAsK04VLy0Jd42PhjJz2n1w1hVJNTYKHmw"

class APIError(Exception):
    pass

def fetch_events(token: str) -> List[Dict[str, Any]]:
    """
    Fetch all events from the API using the provided Bearer token.
    Handles pagination automatically to retrieve events.
    Stops when fewer items are returned or a reasonable limit is reached.
    """
    headers = {"Authorization": f"Bearer {token}"}
    all_events = []
    page = 1
    items_per_page = 500
    max_pages = 10  # Fetch up to 10 pages (5000 events) - should be more than enough for 5-day window
    
    try:
        while page <= max_pages:
            # Build URL with pagination
            url = f"{BASE_URL}?{QUERY_PARAMS}&page={page}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            data = response.json()
            # API returns a dict with 'items' key containing the events array
            items = data.get('items', []) if isinstance(data, dict) else data
            
            if not items:
                # No more items returned, we've reached the end
                break
            
            all_events.extend(items)
            
            # If we got fewer items than requested, we've reached the last page
            if len(items) < items_per_page:
                break
            
            page += 1
        
        return all_events
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise APIError("Invalid or expired token (401 Unauthorized)")
        else:
            raise APIError(f"API request failed: {e}")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Network error: {e}")

def get_bearer_token() -> str:
    """Get the Bearer token from environment variable."""
    token = os.getenv("PODPLAY_TOKEN", "")
    return token

def is_token_expired(token: str) -> bool:
    """Decode JWT payload and check expiry without verifying signature."""
    if not token:
        return True
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return time.time() >= payload.get("exp", 0)
    except Exception:
        return True

def fetch_new_token(email: str, password: str) -> str:
    """Authenticate with Firebase and return a fresh Bearer token."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
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
        return token
    except requests.exceptions.HTTPError:
        message = response.json().get("error", {}).get("message", "unknown error")
        raise APIError(f"Authentication failed: {message}")
    except requests.exceptions.RequestException as e:
        raise APIError(f"Network error during authentication: {e}")

def save_token_to_env(token: str) -> None:
    """Write the updated token back to .env."""
    from dotenv import find_dotenv, set_key
    env_path = find_dotenv()
    if env_path:
        set_key(env_path, "PODPLAY_TOKEN", token)