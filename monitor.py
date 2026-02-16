import requests
import time
import re

CHECK_INTERVAL = 300   # check every 5 minutes

def extract_slug(url):
    match = re.search(r'zealy\.io/cw/([^/]+)', url)
    if match:
        return match.group(1)
    return None

def build_api(slug):
    return f"https://api.zealy.io/public/communities/{slug}/quests"

def load_urls():
    with open("urls.txt") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_quests(api_url):
    try:
        r = requests.get(api_url, timeout=20)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def monitor():
    urls = load_urls()
    seen = {}

    print("Monitoring Zealy communities...")

    while True:
        for url in urls:
            slug = extract_slug(url)
            if not slug:
                continue

            api = build_api(slug)
            data = fetch_quests(api)

            if not data:
                continue

            quests = data.get("quests", [])
            quest_ids = {q["id"] for q in quests}

            if slug not in seen:
                seen[slug] = quest_ids
                print(f"Tracking {slug} ({len(quest_ids)} quests)")
            else:
                new = quest_ids - seen[slug]
                if new:
                    print(f"\n🔥 NEW QUESTS in {slug}:")
                    for q in quests:
                        if q["id"] in new:
                            print("•", q["title"])
                    seen[slug] = quest_ids

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
