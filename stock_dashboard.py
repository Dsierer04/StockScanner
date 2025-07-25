print("\n🚨 IF YOU SEE THIS, REDDIT-ONLY SCRIPT IS RUNNING 🚨\n")
import os
print(f"\n✅ RUNNING SCRIPT FROM: {os.path.abspath(__file__)}\n")

import time
import threading
import datetime
import csv
from collections import deque, Counter
from flask import Flask, render_template_string, jsonify
import praw

print("\n" + "=" * 70)
print("✅ RUNNING REDDIT STOCK DASHBOARD")
print("=" * 70 + "\n")

# ===== SETTINGS =====
TICKERS = [
    "GME","AMC","BBBY","BB","NOK","TSLA","SPCE","PLTR","CLF","KOSS","F","AAPL","SPY","COIN","RIOT","MARA",
    "DWAC","BBIG","CVNA","TLRY","SNDL","APE","SOFI","NKLA","NIO","XELA","VFS","CLOV","WISH","HOOD","AI",
    "QQQ","UVXY","TQQQ","LCID","RBLX","ETH","BTC"
]
KEYWORDS = ["moon", "halt", "runner", "squeeze", "earnings", "guidance", "news", "breakout", "low float"]
CHECK_INTERVAL = 20  # Lowered from 60 to keep logs active and avoid Render idle shutdown
TRENDING_INTERVAL = 600
CSV_FILE = "mentions.csv"

# ===== Reddit API Credentials =====
reddit = praw.Reddit(
    client_id="rKf6A5e6aP4gB3JcbJoP1Q",
    client_secret="jQFcCe3DlD62ESnYgudK6IAsat_RPw",
    user_agent="StockPumpScanner"
)

mentions = deque(maxlen=500)
recent_mentions = deque()

# ===== CSV Setup =====
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Source", "Ticker", "Text"])

# ===== Reddit Scraper =====
def scrape_reddit():
    print("✅ Scraping Reddit...")
    results = []
    try:
        subreddits = ["wallstreetbets", "pennystocks", "daytrading", "stocks"]
        for sub in subreddits:
            for submission in reddit.subreddit(sub).new(limit=20):
                text = submission.title + " " + (submission.selftext or "")
                for ticker in TICKERS:
                    if ticker.lower() in text.lower() or f"${ticker.lower()}" in text.lower():
                        if any(k in text.lower() for k in KEYWORDS) or ticker in text.upper():
                            print(f"✅ Found Reddit post: {ticker} | {text[:80]}...")
                            results.append(("Reddit", ticker, text.strip()))
    except Exception as e:
        print(f"[ERROR] Reddit scraping failed: {e}")
    return results

# ===== Save to CSV =====
def save_to_csv(results):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for source, ticker, text in results:
            writer.writerow([datetime.datetime.now(), source, ticker, text])

# ===== Background Scanner =====
def scanner():
    print("\n🔥 SCANNER THREAD STARTED (REDDIT ONLY) 🔥\n")
    while True:
        print("\n" + "=" * 50)
        print("🔥 SCANNING REDDIT FOR NEW MENTIONS...")
        print("=" * 50 + "\n")
        reddit_data = scrape_reddit()
        if reddit_data:
            save_to_csv(reddit_data)
            for source, ticker, text in reddit_data:
                mentions.append({"time": datetime.datetime.now().strftime("%H:%M:%S"),
                                 "source": source, "ticker": ticker, "text": text})
                recent_mentions.append((datetime.datetime.now(), ticker))
            print(f"✅ Added {len(reddit_data)} mentions to feed.")
        else:
            print("❌ No new Reddit mentions found this cycle.")
        time.sleep(CHECK_INTERVAL)

# ===== Flask Dashboard =====
app = Flask(__name__)
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Reddit Stock Scanner</title>
<style>
body { background-color: #0f0f0f; color: #fff; font-family: Arial; margin: 0; }
h1 { color: #00ff91; text-align: center; }
.container { display: flex; justify-content: space-around; padding: 20px; }
.section { width: 45%; background: #1e1e1e; padding: 15px; border-radius: 8px; }
h2 { color: #00bfff; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { border-bottom: 1px solid #333; padding: 8px; text-align: left; }
.ticker { color: #00ff91; font-weight: bold; }
</style>
<script>
async function refreshData() {
    const res = await fetch('/data');
    const data = await res.json();
    document.getElementById('feed').innerHTML = data.feed_html;
    document.getElementById('trending').innerHTML = data.trending_html;
}
setInterval(refreshData, 10000);
</script>
</head>
<body>
<h1>🔥 Reddit Stock Scanner Dashboard</h1>
<div class="container">
<div class="section"><h2>Live Mentions</h2><div id="feed"></div></div>
<div class="section"><h2>Trending</h2><div id="trending"></div></div>
</div>
<script>refreshData();</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/data')
def get_data():
    feed_html = "<table class='table'><tr><th>Time</th><th>Source</th><th>Ticker</th><th>Text</th></tr>"
    for m in reversed(list(mentions)[-20:]):
        feed_html += f"<tr><td>{m['time']}</td><td>{m['source']}</td><td class='ticker'>{m['ticker']}</td><td>{m['text']}</td></tr>"
    feed_html += "</table>"

    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(seconds=TRENDING_INTERVAL)
    recent = [m[1] for m in recent_mentions if m[0] >= cutoff]
    trending_html = "<ul>"
    if recent:
        for ticker, count in Counter(recent).most_common(5):
            trending_html += f"<li><span class='ticker'>${ticker}</span> - {count} mentions</li>"
    else:
        trending_html += "<li>No trending data yet.</li>"
    trending_html += "</ul>"

    return jsonify({"feed_html": feed_html, "trending_html": trending_html})

# ===== Health Check for Render =====
@app.route('/health')
def health():
    return "OK", 200

# ===== Always Start Scanner Thread =====
threading.Thread(target=scanner, daemon=True).start()



