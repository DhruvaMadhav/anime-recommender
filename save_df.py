import pickle
from data_sampling import new_df
from vectorization import similarity
# Save DataFrame
with open('new_df.pkl', 'wb') as f:
    pickle.dump(new_df, f)

# Save similarity matrix
with open('similarity.pkl', 'wb') as f:
    pickle.dump(similarity, f)
