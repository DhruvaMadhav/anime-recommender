import os
import pickle
import requests
from dotenv import load_dotenv

# Load DataFrame
with open('new_df.pkl', 'rb') as f:
    new_df = pickle.load(f)

# Load similarity matrix
with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

def get_poster(anime_id):
    load_dotenv()
    client_id = os.getenv('client_id')

    url = f'https://api.myanimelist.net/v2/anime/{anime_id}'

    headers = {
        'X-MAL-CLIENT-ID': client_id
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        poster_url = json_data.get('main_picture', {}).get('large')
        return poster_url

def recommend(anime):
    anime_index = new_df[new_df['English name'] == anime].index[0]
    distances = similarity[anime_index]
    anime_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])
    recommended_anime = []
    anime_posters = []
    links = []
    i = 0
    while len(recommended_anime) < 5:
      new_anime_id = int(new_df.iloc[anime_list[i][0]]['MAL_ID'])
      new_anime = new_df.iloc[anime_list[i][0]]['English name']
      if new_anime[:len(anime)] != anime[:len(anime)]:
        json_data = get_poster(new_anime_id)
        recommended_anime.append(new_anime)
        anime_posters.append(json_data)
        links.append(f"https://myanimelist.net/anime/{new_anime_id}")
      i += 1
    return (recommended_anime,anime_posters,links)
