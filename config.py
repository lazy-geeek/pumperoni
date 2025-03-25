import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
GMGN_API = "https://api.gmgn.ai/token/{token}/historical"
PUMPFUN_API = "https://pumpfun.com/trends"
RUGCHECK_API = "https://api.rugcheck.xyz/check/{token}"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"  # Solana RPC endpoint
