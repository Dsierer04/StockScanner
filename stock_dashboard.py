import praw
import csv
import datetime
import os
import threading
import time

# ✅ Initialize Reddit API with Environment Variables
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="StockDashboard/1.0"
)

# ✅ CSV File Setup
CSV_FILE = "reddit_stock_mentions.csv"

# ✅ Function to Save Data to CSV
def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        if not file_exists:
            writer.writerow(["timestamp", "source", "ticker", "post_text"])
        for source, ticker, text in data:
            safe_text = text.replace("\n", " ").replace("\r", " ")
            writer.writerow([datetime.datetime.now(), source, ticker, safe_text])

# ✅ Reddit Scanner Function
def scan_reddit():
    print("\n🔥 SCANNER THREAD STARTED (REDDIT ONLY) 🔥\n")
    while True:
        print("✅ Scraping Reddit...")
        reddit_data = []
        for submission in reddit.subreddit("wallstreetbets+stocks").new(limit=20):
            tickers = [word for word in submission.title.split() if word.isupper() and len(word) <= 5]
            for ticker in tickers:
                reddit_data.append(("Reddit", ticker, submission.title))
                print(f"✅ Found Reddit post: {ticker} | {submission.title}")
        if reddit_data:
            save_to_csv(reddit_data)
        print("✅ Sleeping for 60 seconds before next scan...\n")
        time.sleep(60)

# ✅ Start Reddit Scanner in a Thread
def start_scanner():
    t = threading.Thread(target=scan_reddit, daemon=True)
    t.start()

if __name__ == "__main__":
    print("\n🚨 IF YOU SEE THIS, REDDIT-ONLY SCRIPT IS RUNNING 🚨\n")
    print("=======================================================================")
    print("✅ RUNNING REDDIT STOCK DASHBOARD")
    print("=======================================================================\n")
    start_scanner()

    # Keep main thread alive
    while True:
        time.sleep(1000)





