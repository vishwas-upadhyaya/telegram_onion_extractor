# Onion Link Extractor

A simple Python script that connects to specified Telegram channels, scans recent messages for `.onion` URLs, and saves any newly discovered links to a JSON file.

## Features

- Connects to one or more Telegram channels via Telethon.
- Scans messages and captions for URLs matching the `.onion` pattern.
- Keeps track of the last processed message per channel to avoid duplicates.
- Appends newly discovered links (with metadata) to a line-delimited JSON file.
- Configurable via environment variables stored in a `.env` file.

## Prerequisites

- Python 3.7+
- A Telegram API ID and API Hash (register your app at https://my.telegram.org).
- A Telegram account phone number (with optional 2FA password).

## Installation

1.  **Clone or download this repository.**
2.  **Create and activate a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate    # on Linux/macOS
    # venv\Scripts\activate       # on Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install telethon python-dotenv
    ```

## Configuration

1.  In the project directory, **create a `.env` file** with the following contents:
    ```env
    API_ID=1234567
    API_HASH=your_api_hash_here
    PHONE_NUMBER=+15551234567
    PASSWORD=your_2fa_password_if_any
    ```
2.  **Modify constants at the top of `onion_extractor.py`** if needed:
    -   `TARGET_CHANNELS`: list of Telegram channel usernames to scan.
    -   `OUTPUT_FILE`: path to the output file (default: `onion_links.json`).
    -   `LAST_MESSAGE_FILE`: path to store last-seen message IDs (default: `last_message_ids.json`).

## Usage

Run the script directly:
```bash
python tele_ex.py
```
## How it Works

The script will perform the following actions:

1.  **Connect to Telegram:** Authenticates using the credentials from your `.env` file. You may need to enter an authorization code sent to your Telegram account on the first run.
2.  **Iterate Through Target Channels:** Loops through each channel username specified in the `TARGET_CHANNELS` list (defined within the script).
3.  **Fetch Recent Messages:** For each channel, it fetches up to the latest 100 messages. This limit is configurable within the `extract_from_channel` method in the script.
4.  **Extract Onion URLs:** Scans the text content and media captions of these messages for URLs ending with `.onion`.
5.  **Append New Links:** Any newly discovered `.onion` URLs (not already present in the `onion_links.json` file) are appended as a new line to the `onion_links.json` file. Each link is stored as a JSON object.
6.  **Save Last Processed Message IDs:** The script records the ID of the newest message processed for each channel in the `last_message_ids.json` file.
7.  **Process Only New Messages on Subsequent Runs:** When re-running the script, it will only process messages that are newer than the last recorded message ID for each channel, preventing duplicate processing and link extraction.

## Output Format

Each discovered link is written as a JSON object on its own line in the output file (default: `onion_links.json`).
Here's an example of the JSON structure for a single link:

```json


![image](https://github.com/user-attachments/assets/d0dd2e16-85ac-449e-8453-93d6498cea84)

{
  "source": "telegram",
  "url": "http://exampleabcdefg.onion/path",
  "discovered_at": "2023-05-15T12:34:56Z",
  "context": "Found in @toronionlinks",
  "status": "pending"
}
