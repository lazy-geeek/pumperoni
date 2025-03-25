import requests
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from config import GMGN_API
from twitter_utils import search_tweets, analyze_twitter_sentiment


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
