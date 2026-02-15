import requests
import time
import os
import random
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔗 ADD COMMUNITY URLs HERE
COMMUNITY_URLS = [
  	"https://zealy.io/cw/verasity/questboard/sprints"
	"https://zealy.io/cw/reswap/questboard"
	"https://zealy.io/cw/coinquant"
	"https://zealy.io/cw/rubberversex/questboard"
	"https://zealy.io/cw/dappscope/questboard"
	"https://zealy.io/cw/cosmofox/questboard/sprints"
	"https://zealy.io/cw/coingarage/inbox"
	"https://zealy.io/cw/betsiocommunity/leaderboard/b5715676-f433-4e91-8753-05c734c4771a"
	"https://zealy.io/cw/silvanabook-7757/leaderboard/16204e11-6bf1-48f9-9317-66fc6609946e"
	"https://zealy.io/cw/propbase/questboard/66dd9380-5bc8-43b1-b27b-9c0ea003342d/9465ee18-c83c-4d5d-95ef-37568625bc80"
]

# Extract community slug automatically
def extract_slug(url):
    return url.rstrip("/").split("/")[-1]

communities = [extract_slug(url) for url in COMMUNITY_URLS]

seen_quests = set()
seen_sprints = set()
xp_cache = {}

headers_list = [
    {"User-Agent": "Mozilla/5.0"},
    {"User-Agent": "Chrome/120.0"},
    {"User-Agent": "Safari/537.36"},
]

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)

def stealth_get(url):
    try:
        headers = random.choice(headers_list)
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 429:
            print("⚠️ Rate limited. Cooling down...")
            time.sleep(30)
            return None
        return r.json()
    except:
        return None

def check_quests(community):
    global seen_quests, xp_cache

    url = f"https://api.zealy.io/communities/{community}/quests"
    data = stealth_get(url)

    if not data:
        return

    for q in data:
        qid = q.get("id")
        title = q.get("title")
        xp = q.get("xp")
        status = q.get("status")

        # NEW QUEST DETECTED
        if qid not in seen_quests and status != "ARCHIVED":
            seen_quests.add(qid)
            send_telegram(
                f"🚨 NEW QUEST\n\nCommunity: {community}\nTitle: {title}\nXP: {xp}"
            )

        # XP CHANGE DETECTED
        if qid in xp_cache and xp_cache[qid] != xp:
            send_telegram(
                f"🎯 XP UPDATED\n\n{title}\nCommunity: {community}\nNew XP: {xp}"
            )

        xp_cache[qid] = xp

def check_sprints(community):
    global seen_sprints

    url = f"https://api.zealy.io/communities/{community}/sprints"
    data = stealth_get(url)

    if not data:
        return

    for sprint in data:
        sid = sprint.get("id")
        name = sprint.get("name")

        if sid not in seen_sprints:
            seen_sprints.add(sid)
            send_telegram(
                f"🔥 NEW SPRINT\n\nCommunity: {community}\nSprint: {name}"
            )

def discover_new_communities():
    """
    Auto-discover trending communities from Zealy explore
    """
    url = "https://api.zealy.io/communities/explore"
    data = stealth_get(url)

    if not data:
        return

    for c in data[:10]:
        slug = c.get("slug")
        if slug and slug not in communities:
            communities.append(slug)
            send_telegram(f"🆕 New Community Discovered: {slug}")

send_telegram("✅ Stealth Zealy Monitor Started")

while True:

    # auto discovery every ~10 minutes
    if random.randint(1, 200) == 50:
        discover_new_communities()

    for community in communities:

        check_quests(community)
        check_sprints(community)

        # human-like delay between communities
        time.sleep(random.uniform(1.5, 3.5))

    # randomized main loop delay (stealth)
    time.sleep(random.uniform(2.5, 4))
