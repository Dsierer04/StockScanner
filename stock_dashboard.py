import praw
import csv
import datetime
import os
import threading
import time

# ✅ Initialize Reddit API with Environment Variables
reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
)

# ✅ Check if credentials exist
if not reddit.read_only:
    print("✅ Reddit API Authenticated Successfully!")
else:
    print("❌ Reddit API Failed to Authenticate. Check environment variables.")

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

# ✅ Example Data (replace with actual scanner logic)
sample_data = [
    ("Reddit", "AAPL", "Apple stock is looking bullish today!"),
    ("Reddit", "TSLA", "Tesla might pump soon!")
]

save_to_csv(sample_data)
print("✅ Data saved to CSV successfully!")







