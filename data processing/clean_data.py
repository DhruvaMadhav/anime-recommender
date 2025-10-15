import json

INPUT_FILE = "top_2000_anime.json"
OUTPUT_FILE = "top_2000_cleaned.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    anime_data = json.load(f)

cleaned_data = []

for anime in anime_data:
    mal_id = anime.get("mal_id")
    title = anime.get("title_english") or anime.get("title")
    type = anime.get("type")
    episodes = anime.get("episodes")
    status = anime.get("status")
    score = anime.get("score")
    rank = anime.get("rank")
    members = anime.get("members")
    synopsis = anime.get("synopsis")
    poster = anime.get("images", {}).get("jpg", {}).get("image_url", "")
    source = anime.get("source")

    studios = [
        {"id": s.get("mal_id"), "name": s.get("name")}
        for s in anime.get("studios", [])
    ]
    genres = [
        {"id": g.get("mal_id"), "name": g.get("name")}
        for g in anime.get("genres", [])
    ]
    themes = [
        {"id": t.get("mal_id"), "name": t.get("name")}
        for t in anime.get("themes", [])
    ]

    demographics = [
        {"id": d.get("mal_id"), "name": d.get("name")}
        for d in anime.get("demographics", [])
    ]

    # --- Relations ---
    prequels, sequels = [], []
    spinoffs, side_stories = [], []
    alternatives = []
    parent_stories, full_stories = [], []

    for rel in anime.get("relations", []):
        rel_type = rel.get("relation", "").lower()

        if rel_type == "prequel":
            prequels += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]
        elif rel_type == "sequel":
            sequels += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]
        elif rel_type == "side story":
            side_stories += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]
        elif rel_type == "spin-off":
            spinoffs += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]
        elif rel_type in ["alternative version", "alternative setting"]:
            alternatives += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]
        elif rel_type == "parent story":
            parent_stories += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]
        elif rel_type == "full story":
            full_stories += [{"id": e["mal_id"], "name": e["name"]} for e in rel.get("entry", [])]

    # Append cleaned anime data
    cleaned_data.append({
        "mal_id": mal_id,
        "title": title,
        "episodes": episodes,
        "type": type,
        "status": status,
        "score": score,
        "rank": rank,
        "members": members,
        "synopsis": synopsis,
        "source": source,
        "studios": studios,
        "genres": genres,
        "themes": themes,
        "demographics": demographics,
        "poster": poster,
        "relations": {
            "prequels": prequels,
            "sequels": sequels,
            "side_stories": side_stories,
            "spinoffs": spinoffs,
            "alternatives": alternatives,
            "parent_story": parent_stories,
            "full_story": full_stories
        }
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

print(f"✅ Saved cleaned dataset: {len(cleaned_data)} entries → {OUTPUT_FILE}")

def find_root(anime_id, anime_dict, visited=None):
    if visited is None:
        visited = set()

    if anime_id in visited:
        return anime_id  # prevent infinite loops
    visited.add(anime_id)

    anime = anime_dict.get(anime_id)
    if not anime:
        return anime_id

    relations = anime.get("relations", {})

    # Only relations that define the "root" of the franchise
    root_relations = []
    root_relations += relations.get("prequels", [])
    root_relations += relations.get("parent_story", [])
    root_relations += relations.get("full_story", [])
    root_relations += relations.get("alternatives", [])  # includes alt version/setting if stored

    if not root_relations:
        return anime_id  # this is the root

    # Take the first one (usually only one)
    next_id = root_relations[0]["id"]
    return find_root(next_id, anime_dict, visited)



# Build anime dictionary for lookup
anime_dict = {a["mal_id"]: a for a in cleaned_data}

root_map = {a["mal_id"]: find_root(a["mal_id"], anime_dict) for a in cleaned_data}

with open("root_map.json", "w", encoding="utf-8") as f:
    json.dump(root_map, f, ensure_ascii=False, indent=2)


ROOT_MAP_FILE = "root_map.json"
print(f"✅ Saved root_map with {len(root_map)} entries → {ROOT_MAP_FILE}")
