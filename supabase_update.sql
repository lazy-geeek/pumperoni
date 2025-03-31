-- Update existing NULL or specific default values to the desired defaults
-- Ensures idempotency if run multiple times
UPDATE messages SET
    usd = COALESCE(usd, 0),
    mc = COALESCE(mc, 0),
    vol = COALESCE(vol, 0),
    top10_holder = COALESCE(top10_holder, 0),    
    reply_to_message_id = COALESCE(reply_to_message_id, 0)
WHERE
    usd IS NULL OR
    mc IS NULL OR
    vol IS NULL OR
    top10_holder IS NULL OR    
    reply_to_message_id IS NULL;

-- Add DEFAULT constraints and NOT NULL where they don't already exist
-- Note: Supabase UI might be easier for adding constraints if this fails due to existing data/types.

-- USD
ALTER TABLE messages ALTER COLUMN usd SET DEFAULT 0;
ALTER TABLE messages ALTER COLUMN usd SET NOT NULL;

-- MC
ALTER TABLE messages ALTER COLUMN mc SET DEFAULT 0;
ALTER TABLE messages ALTER COLUMN mc SET NOT NULL;

-- VOL
ALTER TABLE messages ALTER COLUMN vol SET DEFAULT 0;
ALTER TABLE messages ALTER COLUMN vol SET NOT NULL;

-- top10_holder
ALTER TABLE messages ALTER COLUMN top10_holder SET DEFAULT 0;
ALTER TABLE messages ALTER COLUMN top10_holder SET NOT NULL;

-- x (Default -1)
ALTER TABLE messages ALTER COLUMN x SET DEFAULT -1;
ALTER TABLE messages ALTER COLUMN x SET NOT NULL;

-- reply_to_message_id
ALTER TABLE messages ALTER COLUMN reply_to_message_id SET DEFAULT 0;
-- Assuming reply_to_message_id can sometimes legitimately be NULL if it's not a reply
-- If it MUST always have a value (even 0), uncomment the next line:
-- ALTER TABLE messages ALTER COLUMN reply_to_message_id SET NOT NULL;

-- Optional: Verify changes (run manually in SQL editor)
-- SELECT column_name, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'messages'
-- AND column_name IN ('usd', 'mc', 'vol', 'top10_holder', 'x', 'reply_to_message_id');

-- Check for remaining NULLs (should be 0 for NOT NULL columns)
-- SELECT COUNT(*) FROM messages WHERE usd IS NULL OR mc IS NULL OR vol IS NULL OR top10_holder IS NULL OR x IS NULL;
