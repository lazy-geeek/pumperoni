-- SQL script to update the existing 'messages' table structure

-- Add the reply_to_message_id column if it doesn't exist
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS reply_to_message_id BIGINT;

-- Note: The primary key (message_id, chat_id) should already exist from the initial creation.
-- If it doesn't, you might need to add it manually:
-- ALTER TABLE messages ADD CONSTRAINT messages_pkey PRIMARY KEY (message_id, chat_id);
-- Running the above command might fail if the constraint already exists.

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_timestamp ON messages (timestamp);
CREATE INDEX IF NOT EXISTS idx_token_address ON messages (token_address);

-- Ensure other columns exist (optional, for completeness - uncomment if needed)
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(); -- Adjust default as needed
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS token_address TEXT;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS token_name TEXT;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS usd NUMERIC;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS mc BIGINT;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS vol BIGINT;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS dex TEXT;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS dex_paid BOOLEAN;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS top10_holder INTEGER;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS x FLOAT;
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
-- ALTER TABLE messages ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

SELECT 'Table messages updated successfully (if changes were needed).';
