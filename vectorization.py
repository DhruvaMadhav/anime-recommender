from data_sampling import new_df, anime
from snowballstemmer import EnglishStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize the stemmer
st = EnglishStemmer()

# Function to stem words in text
def stemmer(text):
    words = text.split()
    stemmed_words = [st.stemWord(word) for word in words]
    return " ".join(stemmed_words)

# Apply stemming to the tags column
new_df['tags'] = new_df['tags'].apply(stemmer)

# Initialize CountVectorizer with a maximum of 2000 features and English stopwords
cv = CountVectorizer(max_features=2000, stop_words='english')

# Process the 'Genres' and 'Studios' columns
anime['Genres'] = anime['Genres'].apply(lambda x: ' '.join([i.lower() for i in x]))
anime['Studios'] = anime['Studios'].apply(lambda x: ' '.join([i.lower() for i in x]))

# Vectorize the 'Genres' and 'Studios' columns
Genres = cv.fit_transform(anime['Genres']).multiply(2).toarray()
Studios = cv.fit_transform(anime['Studios']).toarray()

# Vectorize the 'tags' column and combine all features
vectors = cv.fit_transform(new_df['tags']).toarray()
vectors = np.hstack((vectors, Genres, Studios))

# Compute cosine similarity between the vectors
similarity = cosine_similarity(vectors)
