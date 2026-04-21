import os
import pickle
from typing import List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Module for generating embeddings and building a FAISS index
# Using cosine similarity requires vectors to be length-normalized and using an
# inner product (IP) index. FAISS provides a utility function
# `faiss.normalize_L2` which efficiently normalizes rows in-place. We apply
# this before indexing so that inner products correspond to cosine similarity.

# model name constant simplifies swapping to a different embedding model later
MODEL_NAME = "all-MiniLM-L6-v2"


def embed(text: str, model: SentenceTransformer) -> np.ndarray:
    """Return the embedding for a single text as a NumPy array."""
    return model.encode([text], convert_to_numpy=True)[0]


def collect_java_files(root_dir: str) -> List[str]:
    java_paths = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".java"):
                java_paths.append(os.path.join(dirpath, fname))
    return java_paths


def load_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_label(path: str, root: str = "patterns") -> str:
    # label is the directory directly under root
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    return parts[0] if parts else ""


def build_embeddings(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    """Encode a list of texts and return numpy embeddings."""
    return model.encode(texts, convert_to_numpy=True)


def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Create a FAISS index using inner product.

    Embeddings must already be L2-normalized so that inner product becomes
    cosine similarity. Normalization should be done prior to calling this
    function.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def save_index(index: faiss.IndexFlatIP, path: str = "pattern_index.faiss"):
    faiss.write_index(index, path)


def save_labels(labels: List[str], path: str = "labels.pkl"):
    with open(path, "wb") as f:
        pickle.dump(labels, f)


def build_index(root: str = "patterns") -> Tuple[faiss.IndexFlatIP, List[str]]:
    java_files = collect_java_files(root)
    if not java_files:
        print("no java files found")
        return None, []

    texts = [load_file(p) for p in java_files]
    model = SentenceTransformer(MODEL_NAME)
    embeddings = build_embeddings(texts, model)

    # defensive checks
    if embeddings.size == 0:
        raise ValueError("Embeddings array is empty; no texts were encoded.")
    if embeddings.shape[0] != len(java_files):
        raise ValueError(
            f"Number of embeddings ({embeddings.shape[0]}) does not match number "
            f"of source files ({len(java_files)})."
        )

    # normalize embeddings to unit length for cosine similarity using FAISS helper
    # The function operates in-place and is faster than manual NumPy loops.
    faiss.normalize_L2(embeddings)

    index = create_faiss_index(embeddings)

    labels = [extract_label(p, root) for p in java_files]
    save_index(index)
    save_labels(labels)

    print(f"indexed {len(java_files)} files")
    return index, labels


if __name__ == "__main__":
    build_index()
