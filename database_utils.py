import sqlite3
from datetime import datetime


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


def save_twitter_data(token, tweet, sentiment):
    conn = sqlite3.connect("memecoins.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO twitter_data VALUES (?, ?, ?, ?)",
        (token, tweet, sentiment, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


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
