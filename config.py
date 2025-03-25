import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
GMGN_API = "https://api.gmgn.ai/token/{token}/historical"
PUMPFUN_API = "https://pumpfun.com/trends"
RUGCHECK_API = "https://api.rugcheck.xyz/check/{token}"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"  # Solana RPC endpoint
