import json
import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------
# 0️⃣ Setup NLTK
# -----------------------
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# -----------------------
# 1️⃣ Preprocess Synopsis
# -----------------------
def preprocess_synopsis(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2]
    return " ".join(tokens)

# -----------------------
# 2️⃣ Load Data
# -----------------------
with open("top_2000_cleaned.json", "r", encoding="utf-8") as f:
    anime_list = json.load(f)

with open("root_map.json", "r", encoding="utf-8") as f:
    root_map = json.load(f)

# -----------------------
# 3️⃣ Build Hybrid Text
# -----------------------
for anime in anime_list:
    anime['clean_synopsis'] = preprocess_synopsis(anime.get('synopsis', ''))
    type = anime.get('type')
    source = anime.get('source')
    
    genres = [g['name'] for g in anime.get('genres', [])]
    studios = [s['name'] for s in anime.get('studios', [])]
    themes = [t['name'] for t in anime.get('themes', [])]
    demographics = [d['name'] for d in anime.get('demographics', [])]

    hybrid_text = anime['clean_synopsis']
    hybrid_text += " Type: " + type * 2
    hybrid_text += " Source: " + source * 2
    if genres:
        genre_text = ", ".join(genres)
        hybrid_text += " Genres: " + genre_text * 4
    if studios:
        studio_text = ", ".join(studios)
        hybrid_text += " Studios: " + studio_text * 2
    if themes:
        theme_text = ", ".join(themes)
        hybrid_text += " Themes: " + theme_text * 3
    if demographics:
        demo_text = ", ".join(demographics)
        hybrid_text += " Demographics: " + demo_text * 3

    anime['hybrid_text'] = hybrid_text


# -----------------------
# 4️⃣ Generate Embeddings
# -----------------------
model = SentenceTransformer('all-MiniLM-L6-v2')
texts = [anime['hybrid_text'] for anime in anime_list]

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

# -----------------------
# 5️⃣ Save Vector Database
# -----------------------
# 5a. Save embeddings
np.save("anime_vectors.npy", embeddings)

# 5b. Save metadata
metadata = [
    {
        "mal_id": anime['mal_id'],
        "title": anime.get('title_english') or anime.get('title'),
        "score": anime['score'],
        "root_id": root_map.get(str(anime['mal_id']), anime['mal_id']),
        "genres": [g['name'] for g in anime.get('genres', [])],
        "studios": [s['name'] for s in anime.get('studios', [])],
        "themes": [t['name'] for t in anime.get('themes', [])],
        "demographics": [d['name'] for d in anime.get('demographics', [])],
        "poster": anime.get('poster', '')
    }
    for anime in anime_list
]

with open("anime_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"✅ Pipeline complete! Vectors saved: {embeddings.shape}, metadata saved: {len(metadata)} entries")
