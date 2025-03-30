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

# No progress file needed anymore


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
            print("Client not authorized. Attempting sign-in...")
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input("Enter the code: "))
            except Exception as e:
                print(f"Sign in failed: {e}")
                return
        print("Connected and authorized.")

        # Get channel entity and ID
        print(f"Getting entity for channel: {channel_username}")
        try:
            entity = await client.get_entity(channel_username)
            # Ensure it's a channel/chat ID, not user ID
            if hasattr(entity, "broadcast") or hasattr(entity, "megagroup"):
                chat_id = entity.id
                print(f"Resolved channel ID: {chat_id}")
            else:
                print(
                    f"Error: {channel_username} does not appear to be a channel or group."
                )
                return
        except ValueError:
            print(
                f"Error: Could not find the channel/group '{channel_username}'. Please check the username/link."
            )
            return
        except Exception as e:
            print(f"Error getting channel entity: {e}")
            return

        # Get the last message ID stored in the database for this chat
        print(f"Fetching latest stored message ID for chat {chat_id} from database...")
        min_id_to_fetch = supabase.get_latest_message_id(chat_id)

        if min_id_to_fetch is None:
            print("Error fetching latest message ID from database. Aborting.")
            return
        elif min_id_to_fetch == 0:
            print(
                "No messages found in database for this chat. Will fetch all history."
            )
        else:
            print(
                f"Database contains messages up to ID {min_id_to_fetch}. Fetching newer messages only."
            )

        # Get the actual latest message ID in the channel for progress bar total
        latest_channel_id = 0
        print("Fetching current latest message ID from channel...")
        try:
            last_message = await client.get_messages(entity, limit=1)
            if last_message:
                latest_channel_id = last_message[0].id
                print(f"Current latest message ID in channel: {latest_channel_id}.")
            else:
                print("Channel appears empty. No messages to fetch.")
                return
        except Exception as e:
            print(
                f"Error fetching latest message ID from channel: {e}. Progress bar might be inaccurate."
            )
            # Use min_id_to_fetch as a fallback total if we can't get the latest
            latest_channel_id = min_id_to_fetch

        # Estimate total new messages for the progress bar
        estimated_new_messages = max(0, latest_channel_id - min_id_to_fetch)
        if estimated_new_messages == 0 and min_id_to_fetch > 0:
            print("Database is already up-to-date.")
            return

        print(f"Estimated new messages to process: {estimated_new_messages}")

        processed_in_session = 0
        inserted_in_session = 0

        # Initialize tqdm progress bar
        pbar = tqdm(
            total=estimated_new_messages, unit="msg", desc="Fetching New Messages"
        )

        try:
            # Iterate through messages newer than the last one stored
            # Use reverse=True to process oldest first among the new messages
            async for msg in client.iter_messages(
                entity, min_id=min_id_to_fetch, reverse=True
            ):
                processed_in_session += 1  # Count every message iterated over
                try:
                    # Basic check
                    if not hasattr(msg, "text") or not msg.text:
                        pbar.update(
                            1
                        )  # Update progress even for skipped non-text messages
                        continue

                    parsed = parse_message(msg)
                    # Supabase service handles None check and duplicate check
                    status = supabase.store_message(parsed)
                    if status == "inserted":
                        inserted_in_session += 1
                    # Optional: Log status if needed
                    # print(f"Msg {msg.id}: {status}")

                    pbar.update(1)  # Update progress bar

                except FloodWaitError as e:
                    wait_time = e.seconds
                    print(
                        f"\nFlood wait triggered - sleeping for {wait_time} seconds..."
                    )
                    pbar.set_description(f"Flood wait ({wait_time}s)")
                    await asyncio.sleep(wait_time)
                    pbar.set_description("Fetching New Messages")  # Reset description
                except Exception as e_inner:
                    print(f"\nError processing message ID {msg.id}: {e_inner}")
                    # Continue processing other messages

        except Exception as e_outer:
            # Catch errors during the iteration setup or major issues
            print(f"\nAn unexpected error occurred during message iteration: {e_outer}")
        finally:
            print("-" * 50)
            pbar.close()  # Close the progress bar
            print("-" * 50)
            print(f"\nMessage fetching finished.")
            print(f"Messages iterated in this session: {processed_in_session}")
            print(f"New messages inserted in this session: {inserted_in_session}")


if __name__ == "__main__":
    # Ensure the script runs within an asyncio event loop
    try:
        asyncio.run(backfill_history())
    except KeyboardInterrupt:
        print("\nBackfill interrupted by user.")
