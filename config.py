import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
DEXSCREENER_API_BASE = "https://api.dexscreener.com/latest/dex"
LUNARCRUSH_API_BASE = "https://lunarcrush.com/api4/public"
DEXTOOLS_API_BASE = "https://public-api.dextools.io/trial"  # Trial base URL, might need to change for production
DEXTOOL_API_KEY = os.getenv("DEXTOOL_API_KEY")
RUGCHECK_API = "https://api.rugcheck.xyz/check/{token}"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"  # Solana RPC endpoint
