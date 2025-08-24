import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Paths
PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

VECTOR_PATH = os.path.join(PROCESSED_DIR, "vectorizer.pkl")
TFIDF_PATH = os.path.join(PROCESSED_DIR, "tfidf_matrix.npy")   # permanent format
META_PATH = os.path.join(PROCESSED_DIR, "meta.json")

# Load problems
with open("problems.json", "r", encoding="utf-8") as f:
    problems = json.load(f)

print(f"Loaded {len(problems)} problems from problems.json")

# Prepare text data
texts = [p["title"] + " " + " ".join(p.get("tags", [])) for p in problems]

# Vectorize
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(texts)

print(f"Built TF-IDF matrix with shape {tfidf_matrix.shape}")

# Save vectorizer
with open(VECTOR_PATH, "wb") as f:
    pickle.dump(vectorizer, f)

# Save matrix permanently as .npy (dense array)
np.save(TFIDF_PATH, tfidf_matrix.toarray())

# Save meta
with open(META_PATH, "w", encoding="utf-8") as f:
    json.dump(problems, f, indent=2)

print(f"✅ Saved vectorizer, tfidf_matrix.npy, and meta.json to {PROCESSED_DIR}/")
