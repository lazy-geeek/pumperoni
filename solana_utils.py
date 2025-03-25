import requests
from config import SOLANA_RPC, GMGN_API


def get_network_congestion():
    """Get Solana network congestion based on recent block time"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getRecentPerformanceSamples",
            "params": [4],  # Get last 4 samples
        }
        response = requests.post(SOLANA_RPC, json=payload)
        if response.status_code == 200:
            data = response.json()
            samples = data["result"]
            avg_tps = sum(sample["numTransactions"] for sample in samples) / (
                sum(sample["samplePeriodSecs"] for sample in samples) or 1
            )
            # Normal TPS is ~2000-4000, scale to 0-100 congestion
            congestion = min(100, max(0, (avg_tps - 2000) / 20))
            return congestion
        return 50  # Default medium congestion
    except Exception as e:
        print(f"Error getting network congestion: {e}")
        return 50  # Default value on error


def get_token_price(token):
    """Fetch current token price from GMGN API"""
    try:
        url = GMGN_API.format(token=token)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Assuming the API returns recent price data
            return float(data["data"][-1]["price"])
        return 1.0  # Default price on failure
    except Exception as e:
        print(f"Error getting token price: {e}")
        return 1.0  # Default price


def should_sell_due_to_market_conditions(token):
    """Basic market condition check for emergency sell"""
    try:
        # Get historical data
        url = GMGN_API.format(token=token)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            prices = [
                float(entry["price"]) for entry in data["data"][-5:]
            ]  # Last 5 points
            if len(prices) >= 5:
                # Sell if price dropped more than 30% in last 5 periods
                price_change = (prices[-1] - prices[0]) / prices[0] * 100
                return price_change < -30
        return False
    except Exception as e:
        print(f"Error checking market conditions: {e}")
        return False
