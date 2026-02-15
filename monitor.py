import requests
import time
import os

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Updated list of Zealy URLs to monitor
COMMUNITY_URLS = [
    "https://zealy.io/cw/verasity/questboard/sprints",
    "https://zealy.io/cw/reswap/questboard",
    "https://zealy.io/cw/coinquant",
    "https://zealy.io/cw/rubberversex/questboard",
    "https://zealy.io/cw/dappscope/questboard",
    "https://zealy.io/cw/cosmofox/questboard/sprints",
    "https://zealy.io/cw/coingarage/inbox",
    "https://zealy.io/cw/betsiocommunity/leaderboard/b5715676-f433-4e91-8753-05c734c4771a",
    "https://zealy.io/cw/silvanabook-7757/leaderboard/16204e11-6bf1-48f9-9317-66fc6609946e",
    "https://zealy.io/cw/propbase/questboard/66dd9380-5bc8-43b1-b27b-9c0ea003342d/9465ee18-c83c-4d5d-95ef-37568625bc80"
]

CHECK_INTERVAL = 2  # in seconds
seen_quests = {}

# --- FUNCTIONS ---

def send_telegram(message):
    """Send a message via Telegram bot (fail-proof)."""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code != 200:
            print(f"❌ Telegram send failed: {resp.text}")
    except Exception as e:
        print("❌ Telegram exception:", e)

def fetch_quests(community_url):
    """Fetch quests from a Zealy community URL."""
    try:
        api_url = community_url.rstrip("/") + "/api/quests"
        r = requests.get(api_url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data
        else:
            print("⚠️ Unexpected JSON structure:", data)
            return []
    except Exception as e:
        print(f"❌ Failed to fetch quests for {community_url}: {e}")
        return []

def check_community(community_url):
    """Check quests for a single community and notify Telegram."""
    quests = fetch_quests(community_url)
    for q in quests:
        if isinstance(q, dict):
            qid = q.get("id")
            title = q.get("title", "No title")
            reward = q.get("reward", "No reward")
            key = f"{community_url}_{qid}"
            if key not in seen_quests:
                seen_quests[key] = True
                send_telegram(f"✅ New Quest Detected:\n{title}\nReward: {reward}\n{community_url}")
        else:
            print("⚠️ Skipping quest because it's not a dict:", q)

# --- MAIN LOOP ---
def main():
    send_telegram("🚀 Stealth Zealy Monitor Started")
    print("🚀 Stealth Zealy Monitor Started")
    while True:
        for community in COMMUNITY_URLS:
            check_community(community)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
