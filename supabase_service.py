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
        try:
            # Check for existing message first
            existing = self.get_message(
                message_data["message_id"], message_data["chat_id"]
            )

            if existing:
                print("⏩ Skipping duplicate message")
                return "skipped"

            response = self.client.table("messages").insert(message_data).execute()
            # Check if insert was successful (PostgREST returns data on success)
            if response.data:
                print("✅ Successfully stored new message")
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
