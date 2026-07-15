"""
Book Recommendation Engine - Model Training
--------------------------------------------
Trains a TensorFlow content-based embedding model on a Kaggle books dataset,
then saves everything the Flask API needs to serve recommendations.

DATASET:
Download "7k Books with Metadata" from Kaggle:
https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata

Place the downloaded CSV at: ml-model/data/books.csv

Expected columns (this dataset ships with these; the loader below is
tolerant of small naming differences across similar Kaggle book datasets):
    title, authors, categories, description, average_rating,
    num_pages, ratings_count, published_year, isbn13

Run:
    cd ml-model
    python -m venv venv
    venv\\Scripts\\activate        (Windows)   OR   source venv/bin/activate (Mac/Linux)
    pip install -r requirements.txt
    python train_model.py
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = os.path.join("data", "books.csv")
MODEL_DIR = "model"
EMBEDDING_DIM = 64
TFIDF_MAX_FEATURES = 5000

os.makedirs(MODEL_DIR, exist_ok=True)


def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find {path}.\n"
            "Download the Kaggle dataset '7k Books with Metadata' "
            "(https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata) "
            "and save the CSV as ml-model/data/books.csv"
        )

    df = pd.read_csv(path)

    # Normalize column names across similar Kaggle book datasets
    rename_map = {
        "book_title": "title",
        "author": "authors",
        "genre": "categories",
        "genres": "categories",
        "desc": "description",
        "summary": "description",
        "rating": "average_rating",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    required = ["title", "authors", "categories", "description"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    if "average_rating" not in df.columns:
        df["average_rating"] = 0.0

    df = df.dropna(subset=["title", "description"]).reset_index(drop=True)
    df["description"] = df["description"].fillna("")
    df["categories"] = df["categories"].fillna("Unknown")
    df["authors"] = df["authors"].fillna("Unknown")
    df["average_rating"] = df["average_rating"].fillna(df["average_rating"].mean())

    # Keep it manageable / matches "1,000+ book records" scope from the project brief
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    return df


def build_text_features(df):
    # Combine description + category + author into one text blob per book
    df["combined_text"] = (
        df["description"].astype(str) + " " +
        df["categories"].astype(str) + " " +
        df["authors"].astype(str)
    )
    vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["combined_text"]).toarray().astype("float32")
    return tfidf_matrix, vectorizer


def build_autoencoder(input_dim, embedding_dim):
    """A simple TensorFlow autoencoder that learns a dense embedding
    for each book from its TF-IDF text features."""
    inputs = tf.keras.Input(shape=(input_dim,), name="tfidf_input")

    x = tf.keras.layers.Dense(256, activation="relu")(inputs)
    x = tf.keras.layers.Dropout(0.2)(x)
    embedding = tf.keras.layers.Dense(embedding_dim, activation="relu", name="embedding")(x)

    x = tf.keras.layers.Dense(256, activation="relu")(embedding)
    outputs = tf.keras.layers.Dense(input_dim, activation="sigmoid", name="reconstruction")(x)

    autoencoder = tf.keras.Model(inputs, outputs, name="book_autoencoder")
    encoder = tf.keras.Model(inputs, embedding, name="book_encoder")

    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder, encoder


def evaluate_genre_classification(embeddings, categories):
    """Proxy accuracy metric: how well the learned embeddings separate
    genres, using a small classifier head trained on top of them.
    This gives an honest, reproducible 'recommendation quality' number
    instead of a made-up figure."""
    primary_genre = categories.apply(lambda c: str(c).split(",")[0].strip())
    le = LabelEncoder()
    y = le.fit_transform(primary_genre)

    if len(set(y)) < 2:
        return None

    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, y, test_size=0.2, random_state=42, stratify=y if min(np.bincount(y)) > 1 else None
    )

    clf = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation="relu", input_shape=(embeddings.shape[1],)),
        tf.keras.layers.Dense(len(set(y)), activation="softmax"),
    ])
    clf.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    clf.fit(X_train, y_train, epochs=15, batch_size=32, verbose=0, validation_split=0.1)

    loss, acc = clf.evaluate(X_test, y_test, verbose=0)
    return acc


def main():
    print("Loading dataset...")
    df = load_dataset(DATA_PATH)
    print(f"Loaded {len(df)} books.")

    print("Building TF-IDF text features...")
    tfidf_matrix, vectorizer = build_text_features(df)

    print("Building & training TensorFlow autoencoder...")
    autoencoder, encoder = build_autoencoder(tfidf_matrix.shape[1], EMBEDDING_DIM)
    autoencoder.fit(
        tfidf_matrix, tfidf_matrix,
        epochs=25,
        batch_size=32,
        shuffle=True,
        validation_split=0.1,
        verbose=1,
    )

    print("Generating book embeddings...")
    embeddings = encoder.predict(tfidf_matrix, verbose=0)

    print("Evaluating recommendation quality (genre-separation proxy accuracy)...")
    accuracy = evaluate_genre_classification(embeddings, df["categories"])
    if accuracy is not None:
        print(f"Approx. recommendation accuracy: {accuracy * 100:.2f}%")

    print("Saving artifacts...")
    encoder.save(os.path.join(MODEL_DIR, "encoder.keras"))

    with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    np.save(os.path.join(MODEL_DIR, "embeddings.npy"), embeddings)

    meta_cols = ["title", "authors", "categories", "average_rating", "description"]
    df[meta_cols].to_json(os.path.join(MODEL_DIR, "books_meta.json"), orient="records")

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump({"accuracy": float(accuracy) if accuracy is not None else None,
                    "num_books": len(df)}, f)

    print("\nDone! Artifacts saved in ml-model/model/")
    print(" - encoder.keras       (TensorFlow embedding model)")
    print(" - vectorizer.pkl      (TF-IDF vectorizer)")
    print(" - embeddings.npy      (book embeddings matrix)")
    print(" - books_meta.json     (book metadata for lookup)")
    print(" - metrics.json        (training metrics)")


if __name__ == "__main__":
    main()
