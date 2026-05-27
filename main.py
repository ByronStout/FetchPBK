#!/usr/bin/env python3
"""
Pickleball Open Play CLI Tool

Fetches and displays Open Play pickleball sessions from Pickleball Kingdom API.
"""

import os
import sys
import getpass
from dotenv import load_dotenv

from api_client import get_bearer_token, fetch_events, fetch_new_token, save_token_to_env, is_token_expired, APIError
from display import filter_open_play_events, sort_events_by_date, display_events, display_error

def _reauthenticate() -> str:
    """Get fresh credentials (from .env or interactive prompt) and return a new token."""
    email = os.getenv("PODPLAY_EMAIL", "")
    password = os.getenv("PODPLAY_PASSWORD", "")
    if not email:
        email = input("PBK Email: ")
    if not password:
        password = getpass.getpass("PBK Password: ")
    token = fetch_new_token(email, password)
    save_token_to_env(token)
    return token

def main():
    load_dotenv()

    filter_city = os.getenv("FILTER_CITY", "Tinton Falls")
    filter_event_name = os.getenv("FILTER_EVENT_NAME", "High Intermediate Open Play (3.5 - 3.99)")

    try:
        token = get_bearer_token()

        if is_token_expired(token):
            print("Token expired or missing, re-authenticating...")
            token = _reauthenticate()

        try:
            events = fetch_events(token)
        except APIError as e:
            if "401" in str(e):
                print("Token rejected, re-authenticating...")
                token = _reauthenticate()
                events = fetch_events(token)
            else:
                raise

        open_play_events = filter_open_play_events(events, filter_city, filter_event_name)
        sorted_events = sort_events_by_date(open_play_events)
        display_events(sorted_events)

    except APIError as e:
        display_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        display_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()