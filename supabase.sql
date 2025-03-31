-- SQL to create messages table in Supabase
CREATE TABLE messages (
    message_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    reply_to_message_id BIGINT NOT NULL DEFAULT 0,
    token_address TEXT,
    token_name TEXT,
    usd NUMERIC NOT NULL DEFAULT 0,
    mc BIGINT NOT NULL DEFAULT 0,
    vol BIGINT NOT NULL DEFAULT 0,
    dex TEXT,
    dex_paid BOOLEAN,
    top10_holder INTEGER NOT NULL DEFAULT 0,
    x FLOAT NOT NULL DEFAULT -1, -- Default -1 for x
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (message_id, chat_id)
);

-- Create index for common query patterns
CREATE INDEX idx_timestamp ON messages (timestamp);
CREATE INDEX idx_token_address ON messages (token_address);
