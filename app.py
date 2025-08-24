from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pickle
import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity

# Paths
PROCESSED_DIR = "processed"
VECTOR_PATH = os.path.join(PROCESSED_DIR, "vectorizer.pkl")
TFIDF_PATH_NPY = os.path.join(PROCESSED_DIR, "tfidf_matrix.npy")
TFIDF_PATH_NPZ = os.path.join(PROCESSED_DIR, "tfidf_matrix.npz")
META_PATH = os.path.join(PROCESSED_DIR, "meta.json")

app = FastAPI(title="DSA Search Engine")

# Enable CORS (React frontend support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load search index
print("Loading search index...")
try:
    # Load vectorizer
    with open(VECTOR_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    # Try .npy first
    if os.path.exists(TFIDF_PATH_NPY):
        tfidf_matrix = np.load(TFIDF_PATH_NPY)
    elif os.path.exists(TFIDF_PATH_NPZ):
        tfidf_matrix = np.load(TFIDF_PATH_NPZ)["arr_0"]
    else:
        raise FileNotFoundError("No tfidf_matrix file found")

    # Load metadata
    with open(META_PATH, "r", encoding="utf-8") as f:
        problems = json.load(f)

    print(f"✅ Loaded {len(problems)} problems into search index")

except Exception as e:
    print(f"❌ Error loading processed files: {e}")
    vectorizer, tfidf_matrix, problems = None, None, []


@app.get("/search")
def search(query: str = Query(..., min_length=1)):
    """Search problems using TF-IDF + cosine similarity"""
    if vectorizer is None or tfidf_matrix is None:
        return {"error": "Search index not available. Run process.py first."}

    # Transform query
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, tfidf_matrix)[0]

    # Top 10 results
    top_indices = sims.argsort()[::-1][:10]
    results = []
    for idx in top_indices:
        if sims[idx] > 0:  # ignore completely irrelevant
            results.append({
                "title": problems[idx]["title"],
                "url": problems[idx]["url"],
                "tags": problems[idx].get("tags", []),
                "similarity": float(sims[idx]),
            })

    return {"query": query, "results": results}
