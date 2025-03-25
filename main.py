import time
from datetime import datetime

from database_utils import setup_db, save_twitter_data, save_trends
from twitter_utils import (
    search_tweets,
    parse_tweet_for_tokens,
    analyze_twitter_sentiment,
)
from market_trends import fetch_trends
from trading_logic import buy_token, sell_token
from token_forecast import forecast_token


# Main execution
def main():
    setup_db()
    while True:
        tweets = search_tweets("#SolanaMemeCoins")
        for tweet, _ in tweets:
            tokens = parse_tweet_for_tokens(tweet)
            for token in tokens:
                sentiment = analyze_twitter_sentiment([tweet])
                save_twitter_data(token, tweet, sentiment)
                forecast_token(token)
                buy_token(token, 0.3 * 10**9)  # Consider moving SOL amount to config

        trends = fetch_trends()
        save_trends(trends)
        time.sleep(60)


if __name__ == "__main__":
    main()
