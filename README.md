# Pickleball Open Play CLI Tool

A simple Python CLI tool to fetch and display Open Play pickleball sessions from Pickleball Kingdom's API.

## Setup Instructions

1. **Clone or navigate to the project directory**
   ```powershell
   cd d:\claude\FetchPBK
   ```

2. **Set up a Python virtual environment** (recommended)
   ```powershell
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   # source .venv/bin/activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure your `.env` file**

   | Variable | Description | Default |
   |---|---|---|
   | `PODPLAY_EMAIL` | Your Pickleball Kingdom account email | *(required for auto-auth)* |
   | `PODPLAY_PASSWORD` | Your Pickleball Kingdom account password | *(required for auto-auth)* |
   | `PODPLAY_TOKEN` | Cached Bearer token (managed automatically) | *(auto-updated)* |
   | `FILTER_CITY` | Facility city to filter by | `Tinton Falls` |
   | `FILTER_EVENT_NAME` | Event type to filter by | `High Intermediate Open Play (3.5 - 3.99)` |

   Example `.env`:
   ```
   PODPLAY_EMAIL=you@example.com
   PODPLAY_PASSWORD=yourpassword
   PODPLAY_TOKEN=
   FILTER_CITY=Tinton Falls
   FILTER_EVENT_NAME=High Intermediate Open Play (3.5 - 3.99)
   ```

5. **Run the tool**
   ```powershell
   python main.py
   ```

## What it does

- Fetches events from the Pickleball Kingdom API
- Filters to show only Open Play events matching your configured city and event name
- Sorts events by date (ascending)
- Displays event name, date/time, location, and available spots

## Authentication

Bearer tokens issued by Pickleball Kingdom expire after 1 hour. The tool handles this automatically:

1. On each run it checks whether the saved `PODPLAY_TOKEN` is expired by inspecting the JWT locally (no network call)
2. If expired or missing, it re-authenticates using `PODPLAY_EMAIL` and `PODPLAY_PASSWORD` via Firebase
3. The new token is written back to `.env` automatically
4. If credentials are not set in `.env`, the tool will prompt for them interactively

If `PODPLAY_EMAIL` and `PODPLAY_PASSWORD` are set in `.env`, the tool runs fully unattended with no manual token management needed.

## Requirements

- Python 3.7+
- Internet connection for API access

## Troubleshooting

- **"Authentication failed: INVALID_LOGIN_CREDENTIALS"**: Check `PODPLAY_EMAIL` and `PODPLAY_PASSWORD` in your `.env`
- **"Token rejected, re-authenticating..."**: The saved token was rejected server-side; the tool will retry automatically using your credentials
- **No events found**: Verify `FILTER_CITY` and `FILTER_EVENT_NAME` in your `.env` match exactly what appears in the Pickleball Kingdom app
- **Network errors**: Ensure you have internet access

## Future Modifications

- Detect newly added sessions and auto-book them on a schedule
- Add date range filtering
- Support multiple clubs/locations
