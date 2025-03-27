import requests
import os
from config import (
    DEXSCREENER_API_BASE,
    LUNARCRUSH_API_BASE,
    DEXTOOLS_API_BASE,
    DEXTOOL_API_KEY,
)


# Market trend tracking
def fetch_trends():
    trends = []
    try:
        dexscreener_url = f"{DEXSCREENER_API_BASE}/token-boosts/latest/v1"
        dexscreener_response = requests.get(dexscreener_url)
        dexscreener_data = (
            dexscreener_response.json()
            if dexscreener_response.status_code == 200
            else []
        )

        # Format the Dexscreener data
        dexscreener_trends = [
            {
                "source": "Dexscreener",
                "chainId": token["chainId"],
                "tokenAddress": token["tokenAddress"],
                "url": token["url"],
                "icon": token["icon"],
            }
            for token in dexscreener_data
        ]
        trends.extend(dexscreener_trends)
    except requests.RequestException as e:
        print(f"Error fetching Dexscreener trends: {e}")

    try:
        lunarcrush_url = f"{LUNARCRUSH_API_BASE}/coins/list/v2?sort=social_volume_24h"
        lunarcrush_response = requests.get(lunarcrush_url)
        lunarcrush_data = (
            lunarcrush_response.json().get("data", [])
            if lunarcrush_response.status_code == 200
            else []
        )

        # Format the LunarCrush data
        lunarcrush_trends = [
            {
                "source": "LunarCrush",
                "symbol": coin["symbol"],
                "name": coin["name"],
                "social_volume_24h": coin["social_volume_24h"],
            }
            for coin in lunarcrush_data
        ]
        trends.extend(lunarcrush_trends)
    except requests.RequestException as e:
        print(f"Error fetching LunarCrush trends: {e}")

    try:
        dextools_url = f"{DEXTOOLS_API_BASE}/v2/ranking/solana/gainers"  # Using solana chain as requested
        headers = {"X-API-KEY": DEXTOOL_API_KEY}
        dextools_response = requests.get(dextools_url, headers=headers)
        dextools_data = (
            dextools_response.json() if dextools_response.status_code == 200 else []
        )

        # Format the Dextools data
        dextools_trends = [
            {
                "source": "Dextools",
                "exchangeName": token["exchangeName"],
                "pair": f"{token['mainToken']['symbol']}/{token['sideToken']['symbol']}",
                "variation24h": token["variation24h"],
            }
            for token in dextools_data
        ]
        trends.extend(dextools_trends)
    except requests.RequestException as e:
        print(f"Error fetching Dextools trends: {e}")

    return trends
