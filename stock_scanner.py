import requests
from bs4 import BeautifulSoup
import praw
import datetime
import time
import csv
from collections import deque, Counter

# ===== SETTINGS =====
TICKERS = [
    "GME","AMC","BBBY","BB","NOK","TSLA","SPCE","PLTR","CLF","KOSS","F","AAPL","SPY","COIN","RIOT","MARA",
    "DWAC","BBIG","CVNA","TLRY","SNDL","APE","SOFI","NKLA","NIO","XELA","VFS","CLOV","WISH","HOOD","AI",
    "QQQ","UVXY","TQQQ","LCID","RBLX","ETH","BTC"
]
KEYWORDS = ["moon", "halt", "runner", "squeeze", "earnings", "guidance", "news", "breakout", "low float"]
CSV_FILE = "mentions.csv"
CHECK_INTERVAL = 60  # Every minute
TRENDING_INTERVAL = 600  # Every 10 min

# ===== Reddit API =====
reddit = praw.Reddit(
    client_id="rKf6A5e6aP4gB3JcbJoP1Q",
    client_secret="jQFcCe3DlD62ESnYgudK6IAsat_RPw",
    user_agent="StockPumpScanner"
)

# ===== CSV Setup =====
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Time", "Source", "Ticker", "Text"])

# ===== Store last 10 min mentions =====
recent_mentions = deque()

# ===== Scrape Twitter =====
def scrape_twitter():
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    for ticker in TICKERS[:10]:
        try:
            url = f"https://twitter.com/search?q=%24{ticker}&src=typed_query&f=live"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                tweets = soup.find_all("div", {"data-testid": "tweetText"})
                for tweet in tweets[:3]:
                    text = tweet.get_text().strip()
                    if any(k in text.lower() for k in KEYWORDS) or ticker in text.upper():
                        results.append(("Twitter", ticker, text))
            else:
                print(f"[ERROR] Twitter blocked for {ticker}")
        except Exception as e:
            print(f"[ERROR] Twitter scrape failed for {ticker}: {e}")
    return results

# ===== Scrape Reddit =====
def scrape_reddit():
    results = []
    subreddits = ["wallstreetbets", "pennystocks", "daytrading", "stocks"]
    for sub in subreddits:
        for submission in reddit.subreddit(sub).new(limit=20):
            text = submission.title + " " + (submission.selftext or "")
            for ticker in TICKERS:
                if ticker.lower() in text.lower() or f"${ticker.lower()}" in text.lower():
                    if any(k in text.lower() for k in KEYWORDS) or ticker in text.upper():
                        results.append(("Reddit", ticker, text.strip()))
    return results

# ===== Save Mentions =====
def save_to_csv(results):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for source, ticker, text in results:
            writer.writerow([datetime.datetime.now(), source, ticker, text])

# ===== Display Raw Mentions =====
def display_new_mentions(results):
    for source, ticker, text in results:
        print(f"[{source}] ${ticker}: \"{text}\"")

# ===== Display Trending =====
def display_trending():
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(seconds=TRENDING_INTERVAL)
    recent = [m for m in recent_mentions if m[0] >= cutoff]
    if not recent:
        print("\n[INFO] No trending tickers in the last 10 min.\n")
        return
    tickers = [m[1] for m in recent]
    counter = Counter(tickers).most_common(5)
    print("\n🔥 Trending Tickers (Last 10 min):")
    for rank, (ticker, count) in enumerate(counter, start=1):
        print(f"{rank}. ${ticker} ({count} mentions)")
    print("-" * 50)

# ===== MAIN LOOP =====
print("🔥 Running Stock Pump Scanner (Terminal Mode)...")
last_trending_check = time.time()

while True:
    twitter_data = scrape_twitter()
    reddit_data = scrape_reddit()
    combined = twitter_data + reddit_data

    if combined:
        save_to_csv(combined)
        display_new_mentions(combined)
        for _, ticker, _ in combined:
            recent_mentions.append((datetime.datetime.now(), ticker))
    else:
        print("[INFO] No new mentions this cycle.")

    # Trending every 10 min
    if time.time() - last_trending_check >= TRENDING_INTERVAL:
        display_trending()
        last_trending_check = time.time()

    time.sleep(CHECK_INTERVAL)
