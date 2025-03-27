import requests
from config import DEXSCREENER_API_BASE


# Market trend tracking
def fetch_trends():
    try:
        dexscreener_url = f"{DEXSCREENER_API_BASE}/token-boosts/latest/v1"
        dexscreener_response = requests.get(dexscreener_url)
        dexscreener_data = (
            dexscreener_response.json()
            if dexscreener_response.status_code == 200
            else []
        )

        # Format the data
        dexscreener_trends = [
            {
                "chainId": token["chainId"],
                "tokenAddress": token["tokenAddress"],
                "url": token["url"],
                "icon": token["icon"],
            }
            for token in dexscreener_data
        ]

        return dexscreener_trends
    except requests.RequestException as e:
        print(f"Error fetching trends: {e}")
        return []
