import pickle
from typing import Tuple, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from embedding import MODEL_NAME


# Load FAISS index from disk (constructed as IndexFlatIP for cosine similarity)

def load_index(path: str = "pattern_index.faiss") -> faiss.IndexFlatIP:
    return faiss.read_index(path)


# Load labels list from pickle

def load_labels(path: str = "labels.pkl") -> list:
    with open(path, "rb") as f:
        return pickle.load(f)


# Compute embedding for a query string using provided model
# We will normalize this vector to unit length before searching so that
# inner-product in the IP index corresponds to cosine similarity.

def embed_query(text: str, model: SentenceTransformer) -> np.ndarray:
    return model.encode([text], convert_to_numpy=True)


# Predict pattern and similarity score

def predict_pattern(code: str, index: faiss.IndexFlatIP, labels: list,
                    model: SentenceTransformer) -> Tuple[Optional[str], float]:
    # ensure the index has entries
    if index.ntotal == 0:
        raise ValueError("FAISS index is empty. Build the index before searching.")

    vec = embed_query(code, model)
    # normalize query vector to unit length; required for cosine similarity
    faiss.normalize_L2(vec)
    D, I = index.search(vec, 1)
    score = float(D[0][0])  # cosine similarity in [-1,1]
    label = labels[I[0][0]] if I.size and I[0][0] < len(labels) else None
    return label, score


if __name__ == "__main__":
    idx = load_index()
    lbls = load_labels()
    mdl = SentenceTransformer(MODEL_NAME)

    sample = (
        "public class Test { private static Test instance; private Test() {} "
        "public static Test getInstance() { if (instance==null) instance=new Test(); "
        "return instance;} }"
    )
    pattern, sim = predict_pattern(sample, idx, lbls, mdl)
    print(f"predicted pattern: {pattern}, score: {sim}")
