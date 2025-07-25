print("\n🚨 IF YOU SEE THIS, PLAYWRIGHT SCRIPT IS RUNNING 🚨\n")
import os
print(f"\n✅ RUNNING SCRIPT FROM: {os.path.abspath(__file__)}\n")

import time
import threading
import datetime
import csv
from collections import deque, Counter
from flask import Flask, render_template_string, jsonify
from playwright.sync_api import sync_playwright
import praw

print("\n" + "="*70)
print("✅ RUNNING PLAYWRIGHT STOCK DASHBOARD")
print("="*70 + "\n")

# ===== SETTINGS =====
TICKERS = [
    "GME","AMC","BBBY","BB","NOK","TSLA","SPCE","PLTR","CLF","KOSS","F","AAPL","SPY","COIN","RIOT","MARA",
    "DWAC","BBIG","CVNA","TLRY","SNDL","APE","SOFI","NKLA","NIO","XELA","VFS","CLOV","WISH","HOOD","AI",
    "QQQ","UVXY","TQQQ","LCID","RBLX","ETH","BTC"
]
KEYWORDS = ["moon", "halt", "runner", "squeeze", "earnings", "guidance", "news", "breakout", "low float"]
CHECK_INTERVAL = 60  # seconds between scans
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

# ===== Twitter Scraper =====
def scrape_twitter():
    print("✅ Starting Playwright for Twitter scraping...")
    results = []
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            for ticker in TICKERS[:5]:  # limit to 5 for speed
                try:
                    print(f"🔍 Scraping Twitter for ${ticker}...")
                    url = f"https://twitter.com/search?q=%24{ticker}&src=typed_query&f=live"
                    page.goto(url, timeout=45000)
                    page.wait_for_selector("article", timeout=15000)
                    tweets = page.query_selector_all("article div[lang]")
                    for tweet in tweets[:3]:
                        text = tweet.inner_text()
                        if any(k in text.lower() for k in KEYWORDS) or ticker in text.upper():
                            print(f"✅ Found tweet for ${ticker}: {text[:50]}...")
                            results.append(("Twitter", ticker, text.strip()))
                except Exception as e:
                    print(f"[ERROR] Twitter scrape failed for ${ticker}: {e}")
            browser.close()
    except Exception as e:
        print(f"[FATAL] Playwright failed: {e}")
    print("✅ Finished Twitter scraping.")
    return results

# ===== Reddit Scraper =====
def scrape_reddit():
    print("✅ Scraping Reddit...")
    results = []
    try:
        subreddits = ["wallstreetbets", "pennystocks", "daytrading", "stocks"]
        for sub in subreddits:
            for submission in reddit.subreddit(sub).new(limit=10):
                text = submission.title + " " + (submission.selftext or "")
                for ticker in TICKERS:
                    if ticker.lower() in text.lower() or f"${ticker.lower()}" in text.lower():
                        if any(k in text.lower() for k in KEYWORDS) or ticker in text.upper():
                            print(f"✅ Found Reddit post: {ticker} | {text[:50]}...")
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

# ===== Scanner =====
def scanner():
    print("\n🔥 SCANNER THREAD STARTED IMMEDIATELY 🔥\n")
    while True:
        try:
            print("\n" + "="*50)
            print("🔥 SCANNING FOR NEW MENTIONS...")
            print("="*50 + "\n")

            twitter_data = scrape_twitter()
            reddit_data = scrape_reddit()
            combined = twitter_data + reddit_data

            if combined:
                save_to_csv(combined)
                for source, ticker, text in combined:
                    mentions.append({
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "source": source,
                        "ticker": ticker,
                        "text": text
                    })
                    recent_mentions.append((datetime.datetime.now(), ticker))
                print(f"✅ Added {len(combined)} mentions to feed.")
            else:
                print("❌ No new mentions found this cycle.")
        except Exception as e:
            print(f"[CRASH] Scanner loop error: {e}")
        time.sleep(CHECK_INTERVAL)

# ===== Flask Dashboard =====
app = Flask(__name__)
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Stock Pump Scanner</title>
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
<h1>🔥 Stock Pump Scanner Dashboard</h1>
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

# ===== Always Start Scanner and Run Flask =====
if __name__ == '__main__':
    threading.Thread(target=scanner, daemon=True).start()
    port = int(os.environ.get('PORT', 8000))  # ✅ Dynamic port for Render
    app.run(host='0.0.0.0', port=port)

