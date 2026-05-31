from typing import List, Dict, Any
from datetime import datetime, timedelta
import sys
import pytz

def filter_open_play_events(events: List[Dict[str, Any]], target_city: str, target_name: str) -> List[Dict[str, Any]]:
    """Filter events by city and event name within the next 5 days."""
    tinton_falls_events = []

    # Get current time and 5 days from now
    now = datetime.now(pytz.UTC)
    five_days_later = now + timedelta(days=5)

    for event in events:
        if event.get('name', '').strip() != target_name:
            continue
        pods = event.get('pods', {}).get('items', [])
        if not pods:
            continue

        address = pods[0].get('address', {})
        if address.get('city', '') != target_city:
            continue
        
        # Check if event is within the next 5 days
        try:
            start_time = event.get('startTime', '')
            event_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            # Only include if event is within 5 days from now
            if now <= event_time <= five_days_later:
                tinton_falls_events.append(event)
        except (ValueError, TypeError):
            # Skip events with invalid dates
            continue
    
    return tinton_falls_events

def sort_events_by_date(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort events by start date ascending."""
    def get_date(event):
        try:
            start_time = event.get('startTime', '')
            return datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return datetime.max  # Put invalid dates at the end
    return sorted(events, key=get_date)

def format_event(event: Dict[str, Any]) -> str:
    """Format a single event for display."""
    event_id = event.get('id', 'Unknown ID')
    name = event.get('name', 'Unknown Event')
    start_time = event.get('startTime', 'Unknown Date')

    pods = event.get('pods', {}).get('items', [])

    # Format date - convert from UTC to local timezone
    timezone_str = pods[0].get('timezone', 'UTC') if pods else 'UTC'
    try:
        dt_utc = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        tz = pytz.timezone(timezone_str)
        dt_local = dt_utc.astimezone(tz)
        date_str = dt_local.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError, pytz.exceptions.UnknownTimeZoneError):
        date_str = start_time

    # Extract location from pods
    location = "Location not available"
    if pods:
        address = pods[0].get('address', {})
        if address:
            location = f"{address.get('street', '')}, {address.get('city', '')} {address.get('zip', '')}"

    # Calculate spots available and check waitlist status
    total_capacity = event.get('totalTeams', 0)
    registered = event.get('signups', {}).get('_total', 0)
    spots_available = total_capacity - registered
    
    # Check if event has waitlist feature
    features = event.get('features', [])
    has_waitlist = 'WAITLIST' in features
    
    # Determine status
    status_str = ""
    if spots_available <= 0:
        status_str = " [FULL - WAITLIST AVAILABLE]" if has_waitlist else " [FULL]"
    elif spots_available <= 3:
        status_str = " [LOW SPOTS]"

    # Build output
    output = f"ID: {event_id}\nEvent: {name}{status_str}\nDate/Time: {date_str} ({timezone_str})\nLocation: {location}\nSpots Available: {spots_available}/{total_capacity}"
    return output + "\n" + "-" * 40

def display_events(events: List[Dict[str, Any]]) -> None:
    """Display the list of events to stdout."""
    if not events:
        print("No Open Play events found.")
        return

    print(f"Found {len(events)} Open Play event(s):\n")
    for event in events:
        print(format_event(event))

def display_error(message: str) -> None:
    """Display an error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)