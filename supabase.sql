-- SQL to create messages table in Supabase
CREATE TABLE messages (
    message_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    reply_to_message_id BIGINT,
    token_address TEXT,
    token_name TEXT,
    usd NUMERIC,
    mc BIGINT,
    vol BIGINT,
    dex TEXT,
    dex_paid BOOLEAN,
    top10_holder INTEGER,
    x FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (message_id, chat_id)
) WITH (ON CONFLICT DO NOTHING);

-- Create index for common query patterns
CREATE INDEX idx_timestamp ON messages (timestamp);
CREATE INDEX idx_token_address ON messages (token_address);
