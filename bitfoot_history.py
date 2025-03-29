from telethon import TelegramClient
import os
from message_parser import parse_message

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE_NUMBER")
channel_username = os.getenv("TELEGRAM_CHANNEL_USERNAME")


async def fetch_history():
    client = TelegramClient("history_session", api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input("Enter the code: "))

    channel = await client.get_entity(channel_username)
    messages = await client.get_messages(channel, limit=5)

    print("Last 5 messages from the channel:")
    for message in messages:
        print(f"\nMessage: {message.text}")
        parsed_data = parse_message(message.text)
        print("Parsed data:")
        for key, value in parsed_data.items():
            print(f"  {key}: {value}")
        print("-" * 50)

    await client.disconnect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(fetch_history())
