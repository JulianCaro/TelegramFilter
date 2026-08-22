import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

CHANNELS = [x.strip() for x in os.environ['CHANNELS'].split(',') if x.strip()]
KEYWORDS = [x.strip() for x in os.environ['KEYWORDS'].split(',') if x.strip()]

REGEX_PATTERN = None

# "me" = Saved Messages
NOTIFY_TARGET = -1003733952726

# ----------------------------------------------------------

client = TelegramClient(
    StringSession(os.environ['SESSION']),
    int(os.environ['API_ID']),
    os.environ['API_HASH'],
)

_compiled = re.compile(REGEX_PATTERN, re.IGNORECASE) if REGEX_PATTERN else None


def matches(text: str) -> bool:
    low = text.lower()
    if any(k.lower() in low for k in KEYWORDS):
        return True
    if _compiled and _compiled.search(text):
        return True
    return False


@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    text = event.raw_text or ""
    if not matches(text):
        return
    chat = await event.get_chat()
    name = getattr(chat, "title", None) or getattr(chat, "username", "unknown")

    # Forward the original post to  Saved Messages
    await client.forward_messages(NOTIFY_TARGET, event.message)

    preview = text[:200].replace("\n", " ")
    await client.send_message(
        NOTIFY_TARGET,
        f"🔔 Match in {name}\n{preview}",
    )
    print(f"[match] {name}: {preview}")


def main():
    print("Starting... (matches will be forwarded to your Saved Messages)")
    client.start()
    print("Running. Press Ctrl+C to stop.")
    client.run_until_disconnected()


if __name__ == "__main__":
    main()