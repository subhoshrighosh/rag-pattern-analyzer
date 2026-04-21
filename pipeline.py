from retriever import load_index, load_labels, predict_pattern
from rag_explainer import generate_explanation
from sentence_transformers import SentenceTransformer


def load_doc(pattern: str) -> str:
    try:
        with open(f"docs/{pattern}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def run_pipeline(code: str):
    index = load_index()
    labels = load_labels()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    pattern, score = predict_pattern(code, index, labels, model)
    documentation = load_doc(pattern) if pattern else ""
    explanation = generate_explanation(code, pattern, documentation)

    print(f"Detected pattern: {pattern}")
    print(f"Similarity score: {score}")
    print("--- explanation ---")
    print(explanation)


if __name__ == "__main__":
    sample_code = (
        "public class Demo { private static Demo instance; private Demo() {} "
        "public static Demo getInstance() { if (instance==null) instance=new Demo(); "
        "return instance;} }"
    )
    run_pipeline(sample_code)
