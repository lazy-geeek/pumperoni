import asyncio
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError
import os
from message_parser import parse_message
from supabase_service import SupabaseService
import time
from tqdm.asyncio import tqdm  # Use tqdm's async version

# Reuse existing Telegram config
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE_NUMBER")
channel_username = os.getenv("TELEGRAM_CHANNEL_USERNAME")

# No progress file needed


async def backfill_history():
    # Ensure environment variables are loaded
    if not all([api_id, api_hash, phone, channel_username]):
        print("Error: Telegram environment variables not set.")
        print(
            "Please ensure TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE_NUMBER, and TELEGRAM_CHANNEL_USERNAME are in your .env file."
        )
        return

    client = TelegramClient("history_session", api_id, api_hash)
    supabase = SupabaseService()

    async with client:
        # Connect and authenticate
        print("Connecting to Telegram...")
        await client.connect()
        if not await client.is_user_authorized():
            print(
                "Client not authorized. Please run bitfoot_signals.py first to authorize."
            )
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input("Enter the code: "))
            except Exception as e:
                print(f"Sign in failed: {e}")
                return
        print("Connected and authorized.")

        # Get the ID of the last message for the progress bar total (optional but nice)
        total_target = 0
        print("Fetching last message ID for progress bar total...")
        try:
            last_message = await client.get_messages(channel_username, limit=1)
            if last_message:
                total_target = last_message[0].id
                print(
                    f"Last message ID is {total_target}. Using this for progress bar total."
                )
            else:
                print(
                    "Could not fetch last message ID. Progress bar total might be inaccurate."
                )
        except Exception as e:
            print(
                f"Error fetching last message ID: {e}. Progress bar total might be inaccurate."
            )

        processed_in_session = 0
        print(f"Starting history processing for channel: {channel_username}")

        # Initialize tqdm progress bar
        pbar = tqdm(total=total_target, unit="msg", desc="Processing History")

        try:
            # Iterate through all messages using the async iterator
            # Set reverse=True to process oldest first, which feels more natural for backfill
            async for msg in client.iter_messages(channel_username, reverse=True):
                try:
                    # Basic check
                    if not hasattr(msg, "text") or not msg.text:
                        pbar.update(
                            1
                        )  # Still update progress for skipped non-text messages
                        continue

                    parsed = parse_message(msg)
                    # Supabase service handles None check and duplicate check
                    status = supabase.store_message(parsed)
                    if status == "inserted":
                        processed_in_session += 1
                    # Optional: Log status if needed, but keep it minimal
                    # print(f"Msg {msg.id}: {status}")

                    pbar.update(1)  # Update progress bar for every message iterated

                except FloodWaitError as e:
                    wait_time = e.seconds
                    print(
                        f"\nFlood wait triggered - sleeping for {wait_time} seconds..."
                    )
                    pbar.set_description(f"Flood wait ({wait_time}s)")
                    await asyncio.sleep(wait_time)
                    pbar.set_description("Processing History")  # Reset description
                except Exception as e_inner:
                    print(f"\nError processing message ID {msg.id}: {e_inner}")
                    # Decide if you want to continue or break on inner errors
                    # continue

        except Exception as e_outer:
            # Catch errors during the iteration setup or major issues
            print(f"\nAn unexpected error occurred during message iteration: {e_outer}")
        finally:
            print("-" * 50)
            pbar.close()  # Close the progress bar
            print("-" * 50)
            print(f"\nHistory processing finished.")
            print(f"New messages inserted in this session: {processed_in_session}")
            # Note: Can't easily report total processed across sessions without progress file


if __name__ == "__main__":
    # Ensure the script runs within an asyncio event loop
    try:
        asyncio.run(backfill_history())
    except KeyboardInterrupt:
        print("\nBackfill interrupted by user.")
