from flask import Flask, render_template, request
from recommenders.recommender import recommend_by_title, metadata

app = Flask(__name__)

# Helper to get MAL URL
def mal_url(mal_id):
    return f"https://myanimelist.net/anime/{mal_id}"

@app.route('/', methods=['GET', 'POST'])
def home():
    # Dropdown options
    options = [m['title'] for m in metadata]
    recommended = []

    if request.method == 'POST':
        selected_option = request.form.get('options')
        if selected_option:
            try:
                recs = recommend_by_title(selected_option, top_k=10)
                # Convert to tuples: (title, poster, link)
                recommended = [(r['title'], r['poster'], mal_url(r['mal_id'])) for r in recs]
            except Exception as e:
                print(f"Error in recommendation: {e}")

    return render_template('index.html', options=options, recommended=recommended)


if __name__ == '__main__':
    app.run(debug=True)
