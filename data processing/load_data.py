import requests
import time
import json
import os

BASE_URL = "https://api.jikan.moe/v4"
TOP_URL = f"{BASE_URL}/top/anime?page="
DETAIL_URL = f"{BASE_URL}/anime"
OUTPUT_FILE = "top_2000_anime.json"

# Load existing progress if file exists
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_anime_data = json.load(f)
else:
    all_anime_data = []

MAX_PAGES = 80   # 25 * 80 = 2000 anime
START_PAGE = len(all_anime_data) // 25 + 1  # resume if partially complete

print(f"Starting from page {START_PAGE}...")

for page in range(START_PAGE, MAX_PAGES + 1):
    print(f"\n📄 Fetching top anime page {page}...")
    response = requests.get(f"{TOP_URL}{page}")
    data = response.json()

    if "data" not in data or len(data["data"]) == 0:
        print("No more anime found.")
        break

    for anime in data["data"]:
        anime_id = anime["mal_id"]
        title = anime.get("title", "Unknown")
        print(f"  → Fetching details for {title} (ID {anime_id})")

        try:
            details_resp = requests.get(f"{DETAIL_URL}/{anime_id}/full")
            details = details_resp.json()
            if "data" in details:
                all_anime_data.append(details["data"])
        except Exception as e:
            print(f"⚠️ Error fetching {anime_id}: {e}")

        time.sleep(0.4)  # safe delay (Jikan rate limit ≈ 3 req/sec)

    # Save progress every 10 pages
    if page % 10 == 0 or page == MAX_PAGES:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_anime_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Progress saved ({len(all_anime_data)} anime so far)")

    time.sleep(1)

print(f"\n✅ Done! Saved {len(all_anime_data)} anime to {OUTPUT_FILE}")
