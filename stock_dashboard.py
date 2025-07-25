import praw
import csv
import datetime
import os
import threading
import time

# ✅ Hardcoded Reddit API Credentials
reddit = praw.Reddit(
    client_id="rKf6A5e6aP4gB3JcbJoP1Q",
    client_secret="jQfCe3DLD62ESnYgudK6IAsat_RPw",
    user_agent="StockPumpScanner"
)

# ✅ CSV File Setup
CSV_FILE = "reddit_stock_mentions.csv"

# ✅ Save data to CSV
def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        if not file_exists:
            writer.writerow(["timestamp", "source", "ticker", "post_text"])
        for source, ticker, text in data:
            safe_text = text.replace("\n", " ").replace("\r", " ")
            writer.writerow([datetime.datetime.now(), source, ticker, safe_text])

# ✅ Fetch Reddit posts
def fetch_reddit_posts():
    subreddit = reddit.subreddit("wallstreetbets+stocks+investing")
    posts = []
    for post in subreddit.hot(limit=10):
        text = f"{post.title} {post.selftext}"
        tickers = [word for word in text.split() if word.isupper() and len(word) <= 5]
        for ticker in tickers:
            posts.append(("Reddit", ticker, text))
    return posts

# ✅ Scanner Thread
def scanner():
    print("🔥 SCANNER STARTED 🔥")
    while True:
        print("✅ Scraping Reddit...")
        reddit_data = fetch_reddit_posts()
        if reddit_data:
            save_to_csv(reddit_data)
            print(f"✅ Saved {len(reddit_data)} mentions")
        time.sleep(60)  # Run every 1 min

# ✅ Start Thread
if __name__ == "__main__":
    print("\n🚀 IF YOU SEE THIS, REDDIT-ONLY SCRIPT IS RUNNING 🚀\n")
    print("✅ RUNNING REDDIT STOCK DASHBOARD")
    t = threading.Thread(target=scanner)
    t.start()








