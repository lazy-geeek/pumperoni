import tweepy
from datetime import datetime
from .config import (
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

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
