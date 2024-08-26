import pandas as pd

animes = pd.read_csv('/Users/dhruvamadhav/Downloads/anime.csv')
anime = animes[['MAL_ID','English name','Type','Studios']]
synopsis = pd.read_csv('/Users/dhruvamadhav/Downloads/anime_with_synopsis.csv')
anime = anime.merge(synopsis.drop(['Name'],axis=1),on='MAL_ID')
anime = anime[~anime.isin(['Unknown']).any(axis=1)]
anime = anime[anime['Type']=='TV']
anime = anime[anime['Score'] >= '7']
anime = anime.reset_index(drop=True)

anime['sypnopsis'] = anime['sypnopsis'].str.split(' ')
anime['Genres'] = anime['Genres'].apply(lambda x: "".join([i.replace(' ','') for i in x]))
anime['Genres'] = anime['Genres'].str.split(',')
anime['Studios'] = anime['Studios'].apply(lambda x: "".join([i.replace(' ','') for i in x]))
anime['Studios'] = anime['Studios'].str.split(',')
anime['tags'] = anime['Studios'] + anime['Genres'] + anime['sypnopsis']

new_df = anime[['MAL_ID','English name','tags']]
new_df['tags'] =new_df['tags'].apply(lambda x: [i.lower() for i in x])
new_df['tags'] = new_df['tags'].apply(lambda x: ' '.join(x))

print(new_df.head(5))
