import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from collections import Counter, defaultdict

# -----------------------
# 1️⃣ Load vector database
# -----------------------
vectors = np.load("anime_vectors.npy")

with open("anime_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open("root_map.json", "r", encoding="utf-8") as f:
    root_map = json.load(f)

# Build helper mappings
title_to_idx = {m['title'].lower(): i for i, m in enumerate(metadata)}
malid_to_root = {m['mal_id']: m['root_id'] for m in metadata}
malid_to_title = {m['mal_id']: m['title'] for m in metadata}
poster_root = {m['mal_id']: m['poster'] for m in metadata}

# -----------------------
# 2️⃣ Recommendation Function
# -----------------------
def recommend_by_title(title, top_k=10, alpha=0.8, beta=0.2):
    """
    Recommend anime based on hybrid embeddings, balancing similarity and score.
    
    Args:
        title (str): Input anime title.
        top_k (int): Number of recommendations to return.
        alpha (float): Weight for similarity (0-1).
        beta (float): Weight for anime score (0-1). alpha + beta should be 1.

    Returns:
        list of dicts: Recommended anime with title, mal_id, poster, similarity, score.
    """
    title_key = title.lower()
    if title_key not in title_to_idx:
        return []

    query_idx = title_to_idx[title_key]
    query_vec = vectors[query_idx].reshape(1, -1)
    similarities = cosine_similarity(query_vec, vectors)[0]

    # Normalize scores to 0-1
    scores = np.array([m['score']/10 if m['score'] else 0 for m in metadata])

    # Combine similarity and score
    final_ranking = alpha * similarities + beta * scores
    sorted_indices = final_ranking.argsort()[::-1]

    # Get the root ID of the input anime
    input_root_id = malid_to_root.get(metadata[query_idx]['mal_id'], metadata[query_idx]['mal_id'])

    recommendations = []
    seen_roots = set()

    for idx in sorted_indices:
        rec_mal_id = metadata[idx]['mal_id']
        root_id = malid_to_root.get(rec_mal_id, rec_mal_id)

        # Skip the input's root and already recommended roots
        if root_id == input_root_id or root_id in seen_roots:
            continue

        seen_roots.add(root_id)
        root_title = malid_to_title.get(root_id, metadata[idx]['title'])
        poster = poster_root.get(root_id, metadata[idx]['poster'])
        score = metadata[idx]['score'] if metadata[idx]['score'] else 0
        similarity = float(similarities[idx])

        recommendations.append({
            "title": root_title,
            "mal_id": root_id,
            "score": score,
            "poster": poster,
            "similarity": similarity
        })

        if len(recommendations) >= top_k:
            break

    return recommendations