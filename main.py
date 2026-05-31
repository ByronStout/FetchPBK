#!/usr/bin/env python3
"""
Pickleball Open Play CLI Tool

Fetches and displays Open Play pickleball sessions from Pickleball Kingdom API.
"""

import os
import sys
import getpass
from dotenv import load_dotenv

from api_client import PodPlayClient, APIError
from display import sort_events_by_date, display_events, display_error


def _get_credentials() -> tuple[str, str]:
    email = os.getenv("PODPLAY_EMAIL", "") or input("PBK Email: ")
    password = os.getenv("PODPLAY_PASSWORD", "") or getpass.getpass("PBK Password: ")
    return email, password


def main():
    load_dotenv()

    filter_city = os.getenv("FILTER_CITY", "Tinton Falls")
    filter_event_name = os.getenv("FILTER_EVENT_NAME", "High Intermediate Open Play (3.5 - 3.99)")

    try:
        client = PodPlayClient.from_env()

        if not client.is_authenticated():
            print("Token expired or missing, re-authenticating...")
            client.authenticate(*_get_credentials())

        try:
            events = client.get_events(city=filter_city, event_name=filter_event_name)
        except APIError as e:
            if "401" in str(e):
                print("Token rejected, re-authenticating...")
                client.authenticate(*_get_credentials())
                events = client.get_events(city=filter_city, event_name=filter_event_name)
            else:
                raise

        sorted_events = sort_events_by_date(events)
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
