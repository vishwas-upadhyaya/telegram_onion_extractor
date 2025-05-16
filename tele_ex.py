import asyncio
import datetime
import json
import os
import re
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Message, Channel, User

load_dotenv()

# Load credentials from .env
try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    PHONE_NUMBER = os.getenv("PHONE_NUMBER")
    PASSWORD = os.getenv("PASSWORD", "")
except:
    print("could not load env vars properly")
    sys.exit(1)

TARGET_CHANNELS = ["toronionlinks"]
OUTPUT_FILE = "onion_links.json"
LAST_MESSAGE_FILE = "last_message_ids.json"

ONION_URL_PATTERN = re.compile(r'(https?://|tor://|)([a-zA-Z0-9\-]+?\.)+?onion\b(/\S*)?', re.IGNORECASE)

class OnionLinkExtractor:
    def __init__(self):
        self.client = TelegramClient('onion_extractor_session', API_ID, API_HASH)
        self.extracted_links = []
        self.last_message_ids = self.load_last_ids()

    def load_last_ids(self):
        if os.path.exists(LAST_MESSAGE_FILE):
            try:
                with open(LAST_MESSAGE_FILE, 'r') as f:
                    return json.load(f)
            except:
                print("error loading last message file")
        return {}

    def save_last_ids(self):
        try:
            with open(LAST_MESSAGE_FILE, 'w') as f:
                json.dump(self.last_message_ids, f)
        except:
            print("could not save last message ids")

    async def connect(self):
        print("trying to connect...")
        await self.client.start(phone=PHONE_NUMBER, password=PASSWORD)
        print("connected")

    def extract_links(self, text):
        if not text:
            return []
        found = ONION_URL_PATTERN.findall(text)
        result = []
        for proto, domain, path in found:
            if proto == "":
                proto = "http://"
            result.append(proto + domain + "onion" + (path if path else ""))
        return result

    def get_channel_name(self, entity):
        if hasattr(entity, 'username') and entity.username:
            return "@" + entity.username
        if hasattr(entity, 'title'):
            return entity.title
        return str(getattr(entity, 'id', 'unknown'))

    async def process_message(self, message, channel_name):
        links = self.extract_links(message.text if message.text else "")
        if not links and hasattr(message, 'caption'):
            links = self.extract_links(message.caption)

        for l in links:
            print("found:", l)
            self.extracted_links.append({
                "source": "telegram",
                "url": l,
                "discovered_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "context": f"Found in {channel_name}",
                "status": "pending"
            })

    async def get_entity(self, name):
        try:
            return await self.client.get_entity(name)
        except:
            print("can't get channel:", name)
            return None

    async def extract_from_channel(self, channel, limit=100):
        entity = await self.get_entity(channel)
        if not entity:
            return

        channel_name = self.get_channel_name(entity)
        print("checking channel:", channel_name)

        last_id = self.last_message_ids.get(channel, 0)
        newest_id = 0

        async for msg in self.client.iter_messages(entity, limit=limit):
            if msg.id > newest_id:
                newest_id = msg.id
            if last_id and msg.id <= last_id:
                continue
            await self.process_message(msg, channel_name)

        if newest_id > 0:
            self.last_message_ids[channel] = newest_id

    def save_links(self):
        existing = set()
        if os.path.exists(OUTPUT_FILE):
            try:
                with open(OUTPUT_FILE, 'r') as f:
                    for line in f:
                        try:
                            j = json.loads(line)
                            existing.add(j.get("url", ""))
                        except:
                            pass
            except:
                print("error reading existing links")

        try:
            with open(OUTPUT_FILE, 'a') as f:
                for item in self.extracted_links:
                    if item["url"] in existing:
                        continue
                    f.write(json.dumps(item) + "\n")
                    existing.add(item["url"])
        except:
            print("could not save links")

    async def run(self):
        await self.connect()
        for ch in TARGET_CHANNELS:
            await self.extract_from_channel(ch)
        self.save_links()
        self.save_last_ids()
        print("done")

async def main():
    x = OnionLinkExtractor()
    await x.run()

if __name__ == "__main__":
    asyncio.run(main())
