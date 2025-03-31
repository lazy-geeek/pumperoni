from supabase import create_client
import os
from typing import Dict, Optional, Literal


class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials not configured in .env")
        self.client = create_client(url, key)

    def store_message(
        self, message_data: Dict
    ) -> Literal["inserted", "skipped", "error"]:
        """Store parsed message data in Supabase, skipping duplicates. Returns status."""
        if message_data is None:
            # print("🚫 Skipping invalid/filtered message (None received)") # Silenced
            return "skipped"

        # Ensure default values for numeric fields before processing
        numeric_defaults = {
            "usd": 0.0,  # Use float for consistency
            "mc": 0,
            "vol": 0,
            "top10_holder": 0,
            "x": -1.0,  # Use float for consistency, default -1
            "reply_to_message_id": 0,  # Default 0 if not a reply
        }
        for field, default in numeric_defaults.items():
            # Set default only if the key is missing or the value is None
            if field not in message_data or message_data[field] is None:
                message_data[field] = default
            # Ensure correct type (e.g., handle potential string '0' if parser was inconsistent)
            # This is a bit defensive, ideally the parser handles types correctly
            elif field in ["usd", "x"] and not isinstance(
                message_data[field], (int, float)
            ):
                try:
                    message_data[field] = float(message_data[field])
                except (ValueError, TypeError):
                    message_data[field] = (
                        default  # Fallback to default if conversion fails
                    )
            elif field in [
                "mc",
                "vol",
                "top10_holder",
                "reply_to_message_id",
            ] and not isinstance(message_data[field], int):
                try:
                    message_data[field] = int(
                        float(message_data[field])
                    )  # Allow float->int conversion
                except (ValueError, TypeError):
                    message_data[field] = default  # Fallback

        try:
            # Check for existing message first
            existing = self.get_message(
                message_data["message_id"], message_data["chat_id"]
            )

            if existing:
                # print("⏩ Skipping duplicate message") # Silenced
                return "skipped"

            response = self.client.table("messages").insert(message_data).execute()
            # Check if insert was successful (PostgREST returns data on success)
            if response.data:
                # print("✅ Successfully stored new message") # Silenced

                # --- Start: Update original signal's x if this is a higher update ---
                is_update = message_data.get("reply_to_message_id", 0) != 0
                new_x = message_data.get("x", -1.0)

                if is_update and new_x != -1.0:
                    original_message_id = message_data["reply_to_message_id"]
                    chat_id = message_data["chat_id"]

                    try:
                        original_signal = self.get_message(original_message_id, chat_id)
                        if original_signal:
                            current_x = original_signal.get("x", -1.0)
                            # Ensure comparison is between floats
                            if float(new_x) > float(current_x):
                                update_response = (
                                    self.client.table("messages")
                                    .update({"x": float(new_x)})
                                    .eq("message_id", original_message_id)
                                    .eq("chat_id", chat_id)
                                    .execute()
                                )
                                if not update_response.data:
                                    print(
                                        f"⚠️ Failed to update x for original signal {original_message_id} in chat {chat_id}"
                                    )
                                # else:
                                #    print(f"✅ Updated x for original signal {original_message_id} to {new_x}") # Silenced
                        # else:
                        # print(f"ℹ️ Original signal {original_message_id} not found for update.") # Silenced

                    except Exception as update_err:
                        print(f"❌ Error updating original signal's x: {update_err}")
                # --- End: Update original signal's x ---

                return "inserted"
            else:
                # This case might indicate an issue not caught by exceptions
                print(
                    f"⚠️ Message storage might have failed silently for {message_data.get('message_id')}"
                )
                return "error"
        except Exception as e:
            # Handle potential duplicate key errors specifically if needed, though ON CONFLICT should prevent most
            # But other errors might occur
            print(f"❌ Error storing message: {e}")
            return "error"

    def get_message(self, message_id: int, chat_id: int) -> Optional[Dict]:
        """Retrieve a message by its composite key"""
        try:
            response = (
                self.client.table("messages")
                .select("*")
                .eq("message_id", message_id)
                .eq("chat_id", chat_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error retrieving message: {e}")
            return None

    def get_latest_message_id(self, chat_id: int) -> Optional[int]:
        """Retrieve the maximum message_id for a given chat_id"""
        try:
            # Use rpc to call a custom SQL function or directly query max(message_id)
            # Simpler approach: Query order by message_id desc, limit 1
            response = (
                self.client.table("messages")
                .select("message_id")
                .eq("chat_id", chat_id)
                .order("message_id", desc=True)
                .limit(1)
                .execute()
            )
            if response.data:
                return response.data[0]["message_id"]
            else:
                return 0  # Return 0 if no messages found for this chat_id
        except Exception as e:
            print(f"Error retrieving latest message ID: {e}")
            return None  # Indicate error
