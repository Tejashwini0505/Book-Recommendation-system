"""
Book Recommendation Engine - Serving API
------------------------------------------
A small Flask REST API that loads the trained TensorFlow model + embeddings
and serves recommendations. The Node.js/Express backend calls this service
over HTTP (REST), which is what fulfils the "Integrated the AI model with
Node.js/Express backend ... using REST APIs" part of the project.

Run:
    cd ml-model
    python app.py
Serves on: http://localhost:5001
"""

import os
import json
import pickle
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity

MODEL_DIR = "model"

app = Flask(__name__)
CORS(app)

# ---- Load model artifacts at startup ----
print("Loading model artifacts...")
encoder = tf.keras.models.load_model(os.path.join(MODEL_DIR, "encoder.keras"))

with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

embeddings = np.load(os.path.join(MODEL_DIR, "embeddings.npy"))

with open(os.path.join(MODEL_DIR, "books_meta.json"), "r") as f:
    books_meta = json.load(f)

with open(os.path.join(MODEL_DIR, "metrics.json"), "r") as f:
    metrics = json.load(f)

titles_lower = [b["title"].lower() for b in books_meta]
print(f"Loaded {len(books_meta)} books. Model ready.")


def get_recommendations_by_index(idx, top_n=5):
    sims = cosine_similarity([embeddings[idx]], embeddings)[0]
    ranked = np.argsort(sims)[::-1]
    ranked = [i for i in ranked if i != idx][:top_n]
    return [
        {
            "title": books_meta[i]["title"],
            "authors": books_meta[i]["authors"],
            "categories": books_meta[i]["categories"],
            "average_rating": books_meta[i]["average_rating"],
            "similarity_score": float(sims[i]),
        }
        for i in ranked
    ]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "books_loaded": len(books_meta), "metrics": metrics})


@app.route("/recommend", methods=["POST"])
def recommend_by_title():
    """Recommend similar books based on a title the user already likes."""
    data = request.get_json(force=True)
    title = (data.get("title") or "").strip().lower()
    top_n = int(data.get("top_n", 5))

    if not title:
        return jsonify({"error": "title is required"}), 400

    if title not in titles_lower:
        # fuzzy fallback: partial match
        matches = [i for i, t in enumerate(titles_lower) if title in t]
        if not matches:
            return jsonify({"error": f"Book '{title}' not found in catalogue"}), 404
        idx = matches[0]
    else:
        idx = titles_lower.index(title)

    recs = get_recommendations_by_index(idx, top_n)
    return jsonify({"based_on": books_meta[idx]["title"], "recommendations": recs})


@app.route("/recommend_by_genre", methods=["POST"])
def recommend_by_genre():
    """Recommend top-rated books in a given genre/category."""
    data = request.get_json(force=True)
    genre = (data.get("genre") or "").strip().lower()
    top_n = int(data.get("top_n", 5))

    if not genre:
        return jsonify({"error": "genre is required"}), 400

    matches = [b for b in books_meta if genre in str(b["categories"]).lower()]
    matches = sorted(matches, key=lambda b: b.get("average_rating", 0), reverse=True)[:top_n]

    if not matches:
        return jsonify({"error": f"No books found for genre '{genre}'"}), 404

    return jsonify({"genre": genre, "recommendations": matches})


@app.route("/recommend_by_text", methods=["POST"])
def recommend_by_text():
    """Recommend books based on a free-text description of interests,
    e.g. 'I like dark fantasy with strong female leads'."""
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    top_n = int(data.get("top_n", 5))

    if not text:
        return jsonify({"error": "text is required"}), 400

    vec = vectorizer.transform([text]).toarray().astype("float32")
    user_embedding = encoder.predict(vec, verbose=0)
    sims = cosine_similarity(user_embedding, embeddings)[0]
    ranked = np.argsort(sims)[::-1][:top_n]

    recs = [
        {
            "title": books_meta[i]["title"],
            "authors": books_meta[i]["authors"],
            "categories": books_meta[i]["categories"],
            "average_rating": books_meta[i]["average_rating"],
            "similarity_score": float(sims[i]),
        }
        for i in ranked
    ]
    return jsonify({"query": text, "recommendations": recs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
