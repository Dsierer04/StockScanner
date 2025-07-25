import praw
import csv
import datetime
import time
import threading

# ===========================
# CONFIGURATION
# ===========================
CSV_FILE = "reddit_mentions.csv"

# Reddit API Credentials (replace with your own)
REDDIT_CLIENT_ID = "rKf6A5e6aP4gB3JcbJoP1Q"
REDDIT_CLIENT_SECRET = "jQFcCe3DlD62ESnYgudK6IAsat_RPw"
REDDIT_USER_AGENT = "StockDashboard/1.0 by YOUR_USERNAME"

# Subreddits to scan
SUBREDDITS = ["wallstreetbets", "stocks", "options", "investing"]

# Keywords to search for
TICKERS = ["AAPL", "TSLA", "AMZN", "NVDA", "SPY", "QQQ", "META", "GME", "AMC", "BB", "OPEN", "AI", "ETH", "BTC", "APE", "HOOD"]

# Scan interval (seconds)
SCAN_INTERVAL = 60  # 1 minute

# ===========================
# REDDIT INITIALIZATION
# ===========================
reddit = praw.Reddit(
    client_id=rKf6A5e6aP4gB3JcbJoP1Q,
    client_secret=jQFcCe3DlD62ESnYgudK6IAsat_RPw,
    user_agent=REDDIT_USER_AGENT
)

# ===========================
# CREATE CSV HEADER IF NOT EXISTS
# ===========================
def init_csv():
    try:
        with open(CSV_FILE, "x", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Source", "Ticker", "Text"])
    except FileExistsError:
        pass  # File already exists


# ===========================
# SAVE RESULTS TO CSV
# ===========================
def save_to_csv(results):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\')
        for source, ticker, text in results:
            safe_text = text.replace("\n", " ").replace("\r", " ")
            writer.writerow([datetime.datetime.now(), source, ticker, safe_text])


# ===========================
# SCAN REDDIT FOR TICKERS
# ===========================
def scan_reddit():
    print("✅ Scraping Reddit...")
    found = []
    for sub in SUBREDDITS:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.new(limit=30):  # Adjust as needed
            text = (post.title + " " + (post.selftext or "")).upper()
            for ticker in TICKERS:
                if f"${ticker}" in text or f" {ticker} " in text:
                    print(f"✅ Found Reddit post: {ticker} | {post.title[:80]}...")
                    found.append(("Reddit", ticker, post.title))
    return found


# ===========================
# MAIN SCANNER LOOP
# ===========================
def scanner():
    print("\n🚨 IF YOU SEE THIS, REDDIT-ONLY SCRIPT IS RUNNING 🚨\n")
    print("======================================================================")
    print("✅ RUNNING REDDIT STOCK DASHBOARD")
    print("======================================================================\n")
    print("🔥 SCANNER THREAD STARTED (REDDIT ONLY) 🔥\n")
    print("==================================================")
    print("🔥 SCANNING REDDIT FOR NEW MENTIONS...")
    print("==================================================\n")

    while True:
        reddit_data = scan_reddit()
        if reddit_data:
            save_to_csv(reddit_data)
        time.sleep(SCAN_INTERVAL)


# ===========================
# STARTUP
# ===========================
if __name__ == "__main__":
    init_csv()
    print(f"✅ RUNNING SCRIPT FROM: {__file__}\n")
    thread = threading.Thread(target=scanner)
    thread.start()




