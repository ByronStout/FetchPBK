# Pickleball Open Play CLI Tool

A simple Python CLI tool to fetch and display Open Play pickleball sessions from Pickleball Kingdom's API.

## Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd d:\claude\weekend1-pk
   ```

2. **Set up a Python virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your `.env` file**

   | Variable | Description | Default |
   |---|---|---|
   | `PODPLAY_TOKEN` | Bearer token from Pickleball Kingdom | *(required)* |
   | `FILTER_CITY` | Facility city to filter by | `Tinton Falls` |
   | `FILTER_EVENT_NAME` | Event type to filter by | `High Intermediate Open Play (3.5 - 3.99)` |

   Example `.env`:
   ```
   PODPLAY_TOKEN=abc123def456...
   FILTER_CITY=Tinton Falls
   FILTER_EVENT_NAME=High Intermediate Open Play (3.5 - 3.99)
   ```

5. **Run the tool**
   ```bash
   python main.py
   ```

## What it does

- Fetches events from the Pickleball Kingdom API
- Filters to show only Open Play events
- Sorts events by date (ascending)
- Displays event name, date/time, and available spots (if provided)
- Warns if token is missing or invalid

## Requirements

- Python 3.7+
- Internet connection for API access
- Valid Bearer token for authentication

## Troubleshooting

- **"PODPLAY_TOKEN environment variable is not set"**: Make sure your `.env` file has the correct token
- **"Invalid or expired token (401 Unauthorized)"**: Check your token is valid and hasn't expired
- **No events found**: Verify `FILTER_CITY` and `FILTER_EVENT_NAME` in your `.env` match exactly what appears in the Pickleball Kingdom app
- **Network errors**: Ensure you have internet access

## Future Modifications

This tool is designed to be easily extensible. Potential enhancements:
- Add date range filtering
- Export results to CSV/JSON
- Add notifications for new events
- Support multiple clubs/locations


## Notes about my future changes

Add ability to log in without having to capture the Environment JWT
- Podplay uses Firebase
- https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyAsK04VLy0Jd42PhjJz2n1w1hVJNTYKHmw
