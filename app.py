import pandas as pd
from flask import Flask, render_template, request
from recommender import recommend

app = Flask(__name__)
import pickle

# Load DataFrame
with open('new_df.pkl', 'rb') as f:
    new_df = pickle.load(f)

# Load similarity matrix
with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)


@app.route('/', methods=['GET', 'POST'])
def home():
    options = new_df['English name']
    recommended = []

    if request.method == 'POST':
        selected_option = request.form.get('options')
        print(f"Selected option: {selected_option}")  # Debugging line
        if selected_option:
            try:
                animes, posters = recommend(selected_option)
                recommended = list(zip(animes, posters))
            except Exception as e:
                print(f"Error in recommend function: {e}")  # Debugging line

    return render_template('index.html', options=options, recommended=recommended)

if __name__ == '__main__':
    app.run(debug=True)
