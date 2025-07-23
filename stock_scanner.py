import requests
from bs4 import BeautifulSoup
import praw
import pandas as pd
import sqlite3
import datetime
import time
from flask import Flask, render_template_string
from threading import Thread

# ===== SETTINGS =====
MENTION_SPIKE_MULTIPLIER = 3
TIME_WINDOW_MINUTES = 10

# ===== Reddit API (Update with your valid credentials) =====
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="StockPumpScanner"
)

# ===== Tickers =====
TICKERS = [
    "GME","AMC","BBBY","BB","NOK","TSLA","SPCE","PLTR","CLF","KOSS","F","AAPL","SPY","COIN","RIOT","MARA",
    "DWAC","BBIG","CVNA","TLRY","SNDL","APE","SOFI","NKLA","NIO","XELA","VFS","CLOV","WISH","HOOD","AI",
    "QQQ","UVXY","TQQQ","LCID","RBLX","ETH","BTC"
]

# ===== Sentiment Words =====
BULLISH_WORDS = ["moon", "rocket", "gain", "squeeze", "pump", "bullish", "buy", "up"]
BEARISH_WORDS = ["dump", "sell", "bearish", "down", "loss", "short"]

# ===== Sentiment Analyzer =====
def get_sentiment(text):
    text = text.lower()
    score = 0
    for word in BULLISH_WORDS:
        if word in text:
            score += 1
    for word in BEARISH_WORDS:
        if word in text:
            score -= 1
    return score

# ===== Database =====
conn = sqlite3.connect("mentions.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS mentions (timestamp TEXT, source TEXT, ticker TEXT, sentiment REAL)")
conn.commit()

# ===== Twitter Scraper (Direct Search) =====
def scrape_twitter():
    tweets = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for ticker in TICKERS[:10]:  # limit for speed
        try:
            url = f"https://twitter.com/search?q=%24{ticker}&src=typed_query&f=live"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                tweet_divs = soup.find_all("div", {"data-testid": "tweetText"})
                print(f"[DEBUG] {ticker}: {len(tweet_divs)} tweets found")
                for div in tweet_divs[:3]:  # take top 3 tweets
                    text = div.get_text().lower()
                    sentiment = get_sentiment(text)
                    tweets.append((datetime.datetime.now(), 'twitter', ticker.upper(), sentiment))
            else:
                print(f"[ERROR] Twitter returned {response.status_code} for {ticker}")
        except Exception as e:
            print(f"[ERROR] Failed to scrape Twitter for {ticker}: {e}")
    print(f"[INFO] Total tweets scraped: {len(tweets)}")
    return tweets

# ===== Reddit Scraper =====
def scrape_reddit():
    posts = []
    subreddits = ["wallstreetbets", "pennystocks", "daytrading", "stocks"]
    for sub in subreddits:
        for submission in reddit.subreddit(sub).new(limit=10):
            text = submission.title.lower()
            for ticker in TICKERS:
                if f"${ticker.lower()}" in text or ticker.lower() in text:
                    sentiment = get_sentiment(text)
                    posts.append((datetime.datetime.now(), 'reddit', ticker.upper(), sentiment))
    print(f"[INFO] Reddit posts scraped: {len(posts)}")
    return posts

# ===== Save Mentions =====
def save_mentions(data):
    if data:
        cur.executemany("INSERT INTO mentions VALUES (?, ?, ?, ?)", data)
        conn.commit()

# ===== Dashboard Template with Charts =====
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Stock Pump Scanner Dashboard</title>
<meta http-equiv="refresh" content="60">
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
    body {font-family: 'Roboto', sans-serif; background-color: #f4f6f8; margin: 0;}
    header {background-color: #2b2d42; color: white; text-align: center; padding: 20px 0; font-size: 28px; font-weight: 700;}
    .container {width: 90%; margin: 30px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 20px;}
    table {width: 100%; border-collapse: collapse; margin-top: 20px;}
    table thead {background-color: #edf2f4;}
    table th, table td {text-align: center; padding: 14px; font-size: 16px;}
    table th {color: #2b2d42; text-transform: uppercase; font-weight: 700;}
    table tr:nth-child(even) {background-color: #f8f9fa;}
    .status-good {color: green; font-weight: bold;}
    .status-bad {color: red; font-weight: bold;}
    .chart-container {width: 100%; margin-top: 30px;}
</style>
</head>
<body>
<header>Stock Pump Scanner Dashboard</header>
<div class="container">
    <h2>Live Market Watch</h2>
    <div class="chart-container">
        <canvas id="mentionsChart" height="80"></canvas>
    </div>
    <div class="chart-container">
        <canvas id="sentimentChart" height="80"></canvas>
    </div>
    <table>
        <thead>
            <tr>
                <th>Ticker</th>
                <th>Mentions (Last 10 min)</th>
                <th>Sentiment</th>
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                <td>{{row[0]}}</td>
                <td>{{row[1]}}</td>
                <td>
                    {% if row[2] > 0 %}
                        <span class="status-good">{{row[2]|round(2)}}</span>
                    {% else %}
                        <span class="status-bad">{{row[2]|round(2)}}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<script>
    const labels = [{% for row in data %}"{{row[0]}}",{% endfor %}];
    const mentions = [{% for row in data %}{{row[1]}},{% endfor %}];
    const sentiment = [{% for row in data %}{{row[2]|round(2)}},{% endfor %}];

    const ctx1 = document.getElementById('mentionsChart').getContext('2d');
    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mentions',
                data: mentions,
                backgroundColor: 'rgba(43, 45, 66, 0.7)'
            }]
        },
        options: {responsive: true, plugins: {legend: {display: false}}}
    });

    const ctx2 = document.getElementById('sentimentChart').getContext('2d');
    new Chart(ctx2, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sentiment Score',
                data: sentiment,
                borderColor: 'rgba(16, 204, 82, 1)',
                fill: false
            }]
        },
        options: {responsive: true}
    });
</script>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/')
def dashboard():
    df = pd.read_sql("SELECT * FROM mentions", conn)
    if df.empty:
        return render_template_string(TEMPLATE, data=[])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=TIME_WINDOW_MINUTES)
    recent = df[df['timestamp'] >= cutoff]
    grouped = recent.groupby('ticker').agg({'ticker':'count','sentiment':'mean'})
    grouped = grouped.rename(columns={'ticker':'mentions','sentiment':'avg_sentiment'}).reset_index()
    data = grouped.values.tolist()
    return render_template_string(TEMPLATE, data=data)

if __name__ == "__main__":
    print("🚀 Running Stock Pump Scanner + Dashboard on http://127.0.0.1:5000")

    def scanner():
        while True:
            print("[INFO] Scraping Twitter + Reddit...")
            twitter_data = scrape_twitter()
            reddit_data = scrape_reddit()
            save_mentions(twitter_data + reddit_data)
            time.sleep(60)

    Thread(target=scanner).start()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
