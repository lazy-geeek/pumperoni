import tweepy
from datetime import datetime
from config import (
    TWITTER_BEARER_TOKEN,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

# Use Tweepy Client for v2 API
client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
)


def search_tweets(query):
    try:
        # Use v2 search endpoint
        response = client.search_recent_tweets(
            query=query, max_results=100, tweet_fields=["created_at", "text"]
        )
        if response.data:
            return [
                (tweet.text, tweet.created_at.isoformat()) for tweet in response.data
            ]
        return []
    except tweepy.TweepyException as e:
        print(f"Error searching tweets: {e}")
        return []


def parse_tweet_for_tokens(tweet):
    words = tweet.split()
    tokens = [word[1:] for word in words if word.startswith("$") and len(word) > 1]
    return tokens


def analyze_twitter_sentiment(tweets):
    return len(tweets)  # Crude sentiment measure
