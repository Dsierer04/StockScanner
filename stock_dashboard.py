import praw
import csv
import datetime
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Reddit credentials from environment variables
import os
import praw

reddit = praw.Reddit(
    client_id=os.getenv("rKf6A5e6aP4gB3JcbJoP1Q"),
    client_secret=os.getenv("jQFcCe3DlD62ESnYgudK6IAsat_RPw"),
    user_agent=os.getenv("StockPumpScanner")
)

# Validate credentials
if not client_id or not client_secret or not user_agent:
    raise Exception("Missing Reddit API credentials! Check .env file or Render environment variables.")

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# CSV file to store data
CSV_FILE = "reddit_stock_data.csv"

# Ensure CSV file exists and has headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["timestamp", "source", "ticker", "post_text"])

# Function to save data to CSV safely
def save_to_csv(data):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)

# Function to scan Reddit for stock mentions
def scan_reddit():
    print("\n==================================================")
    print("🔥 SCANNING REDDIT FOR NEW MENTIONS...")
    print("==================================================\n")

    subreddit = reddit.subreddit("wallstreetbets+stocks+investing")
    posts = subreddit.new(limit=20)

    reddit_data = []
    for post in posts:
        text = post.title + " " + (post.selftext or "")
        safe_text = text.replace("\n", " ").replace("\r", " ")  # Clean text
        tickers = find_tickers(safe_text)

        for ticker in tickers:
            reddit_data.append([datetime.datetime.now(), "Reddit", ticker, safe_text])
            print(f"✅ Found Reddit post: {ticker} | {post.title[:100]}...")

    if reddit_data:
        save_to_csv(reddit_data)

# Simple function to extract tickers
def find_tickers(text):
    # Looks for $TSLA, $AAPL, etc.
    words = text.split()
    tickers = [w[1:].upper() for w in words if w.startswith("$") and len(w) > 1 and w[1:].isalpha()]
    return tickers

# Background thread to keep scanning
def scanner():
    while True:
        try:
            scan_reddit()
            time.sleep(60)  # Scan every 1 minute
        except Exception as e:
            print(f"❌ Error in scanner: {e}")
            time.sleep(10)

# Start scanner in a thread
if __name__ == "__main__":
    print("\n🚨 IF YOU SEE THIS, REDDIT STOCK DASHBOARD IS RUNNING 🚨")
    print("✅ Starting Reddit Scanner...\n")

    thread = threading.Thread(target=scanner)
    thread.start()






