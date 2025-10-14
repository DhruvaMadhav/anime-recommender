from recommenders.recommender import recommend_by_title

recs = recommend_by_title("Gurren Lagann")
for r in recs:
    print(r['title'])