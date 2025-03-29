from telethon import TelegramClient, events
import re
import os

# Replace these with your own values
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE_NUMBER")
channel_username = os.getenv("TELEGRAM_CHANNEL_USERNAME")

# Create the client
client = TelegramClient("session_name", api_id, api_hash)

from message_parser import parse_message


# Event handler for new messages in the channel
@client.on(events.NewMessage(chats=channel_username))
async def handle_new_message(event):
    message_text = event.message.text
    print("New message received:")
    print(message_text)
    print("\nExtracted values:")

    # Parse the message
    extracted_data = parse_message(event.message)

    # Print the extracted data
    for key, value in extracted_data.items():
        print(f"{key}: {value}")
    print("-" * 50)


# Main function to start the client
async def main():
    # Start the client
    await client.start(phone)
    print(f"Monitoring channel: {channel_username}")

    # Keep the script running to listen for new messages
    await client.run_until_disconnected()


# Run the script
with client:
    client.loop.run_until_complete(main())
