import requests
import tweepy
import sqlite3
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
GMGN_API = "https://api.gmgn.ai/token/{token}/historical"
PUMPFUN_API = "https://pumpfun.com/trends"
RUGCHECK_API = "https://api.rugcheck.xyz/check/{token}"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"  # Solana RPC endpoint


# Database setup
def setup_db():
    conn = sqlite3.connect("memecoins.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS tokens
                 (token text, platform text, trend_score real, timestamp text)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS twitter_data
                 (token text, tweet text, sentiment real, timestamp text)"""
    )
    conn.commit()
    conn.close()


# Twitter setup
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(auth)


def search_tweets(query):
    tweets = twitter_api.search_tweets(q=query, count=100)
    return [(tweet.text, datetime.now().isoformat()) for tweet in tweets]


def parse_tweet_for_tokens(tweet):
    words = tweet.split()
    tokens = [word[1:] for word in words if word.startswith("$") and len(word) > 1]
    return tokens


def analyze_twitter_sentiment(tweets):
    return len(tweets)  # Crude sentiment measure


def save_twitter_data(token, tweet, sentiment):
    conn = sqlite3.connect("memecoins.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO twitter_data VALUES (?, ?, ?, ?)",
        (token, tweet, sentiment, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


# Market trend tracking
def fetch_trends():
    try:
        gmgn_response = requests.get(GMGN_API.format(token="trends"))
        pumpfun_response = requests.get(PUMPFUN_API)
        gmgn_trends = gmgn_response.json() if gmgn_response.status_code == 200 else []
        pumpfun_trends = (
            pumpfun_response.json() if pumpfun_response.status_code == 200 else []
        )
        return gmgn_trends + pumpfun_trends
    except requests.RequestException as e:
        print(f"Error fetching trends: {e}")
        return []


def save_trends(trends):
    conn = sqlite3.connect("memecoins.db")
    c = conn.cursor()
    now = datetime.now().isoformat()
    for trend in trends:
        c.execute(
            "INSERT INTO tokens VALUES (?, ?, ?, ?)",
            (trend.get("token"), trend.get("platform"), trend.get("trend_score"), now),
        )
    conn.commit()
    conn.close()


# RugCheck verification
def check_token_safety(token):
    url = RUGCHECK_API.format(token=token)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("status") == "Good"
    return False


# Implemented placeholder functions
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


# Adaptive purchasing/selling
MIN_PURCHASE = 0.1 * 10**9  # 0.1 SOL in lamports
MAX_PURCHASE = 0.5 * 10**9  # 0.5 SOL in lamports
SLIPPAGE_TOLERANCE = 25  # in percentage
TARGET_RETURN = 20  # 20x return


def calculate_priority_fee(current_network_congestion):
    if current_network_congestion > 75:
        return 0.01 * 10**9
    return 0.001 * 10**9


def buy_token(token, amount_sol):
    if not check_token_safety(token):
        print(f"Token {token} failed safety check.")
        return
    priority_fee = calculate_priority_fee(get_network_congestion())
    slippage = amount_sol * (SLIPPAGE_TOLERANCE / 100)
    buy_amount = amount_sol + priority_fee
    if MIN_PURCHASE <= buy_amount <= MAX_PURCHASE:
        print(f"Attempting to buy {buy_amount/10**9} SOL worth of token {token}")
    else:
        print(f"Purchase amount {buy_amount/10**9} SOL out of specified range.")


def sell_token(token, initial_investment):
    current_price = get_token_price(token)
    target_price = initial_investment * TARGET_RETURN
    if current_price >= target_price:
        print(f"Selling token {token} at {current_price} for 20x return")
    elif should_sell_due_to_market_conditions(token):
        print(f"Emergency sell of token {token} at {current_price}")


# Token forecasting
def fetch_gmgn_data(token):
    url = GMGN_API.format(token=token)
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def preprocess_data(gmgn_data, twitter_data):
    features = []
    labels = []
    for entry in gmgn_data["data"]:
        features.append([entry["volume"], entry["holders"], entry["marketCap"]])
        labels.append(entry["price"])
    sentiment_score = analyze_twitter_sentiment(twitter_data)
    features = [feature + [sentiment_score] for feature in features]
    return np.array(features), np.array(labels)


def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print("Mean Squared Error:", mean_squared_error(y_test, predictions))
    print("R2 Score:", r2_score(y_test, predictions))
    return model


def forecast_token(token):
    gmgn_data = fetch_gmgn_data(token)
    twitter_data = search_tweets(f"${token}")
    if not gmgn_data:
        print("Failed to fetch data for token:", token)
        return
    X, y = preprocess_data(gmgn_data, twitter_data)
    model = train_model(X, y)
    next_day_features = np.array([X[-1]])
    prediction = model.predict(next_day_features)
    print(f"Predicted price for token {token} next day: {prediction[0]}")
    plt.figure(figsize=(10, 5))
    plt.plot(y, label="Actual")
    plt.plot(np.append(y[:-1], prediction), label="Predicted")
    plt.title(f"Token {token} Price Forecast")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.show()


# Main execution
def main():
    setup_db()
    while True:
        tweets = search_tweets("#SolanaMemeCoins")
        for tweet, timestamp in tweets:
            tokens = parse_tweet_for_tokens(tweet)
            for token in tokens:
                sentiment = analyze_twitter_sentiment([tweet])
                save_twitter_data(token, tweet, sentiment)
                forecast_token(token)
                buy_token(token, 0.3 * 10**9)

        trends = fetch_trends()
        save_trends(trends)
        time.sleep(60)


if __name__ == "__main__":
    main()
