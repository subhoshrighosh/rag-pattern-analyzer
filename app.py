import streamlit as st
from retriever import load_index, load_labels, predict_pattern
from rag_explainer import generate_explanation
from query_transform import rewrite_query
from sentence_transformers import SentenceTransformer


def load_doc(pattern: str) -> str:
    try:
        with open(f"docs/{pattern}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


@st.cache_resource

def load_resources():
    """Load and cache models and index for the app."""
    idx = load_index()
    lbls = load_labels()
    mdl = SentenceTransformer("all-MiniLM-L6-v2")
    return idx, lbls, mdl


# initialize resources
index, labels, model = load_resources()

# --- session state defaults --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts {role, content}
if "last_pattern" not in st.session_state:
    st.session_state.last_pattern = ""
if "last_doc" not in st.session_state:
    st.session_state.last_doc = ""


# helper ---------------------------------------------------------------------
def add_message(role: str, content: str):
    """Append a message to the conversation history."""
    st.session_state.history.append({"role": role, "content": content})


# --- Code Analysis Section --------------------------------------------------
st.title("Java Pattern Analyzer")
code_input = st.text_area("Paste Java code here", height=200)

if st.button("Analyze"):
    if not code_input.strip():
        st.warning("Please enter Java code to analyze.")
    else:
        pattern, score = predict_pattern(code_input, index, labels, model)
        documentation = load_doc(pattern) if pattern else ""
        explanation = generate_explanation(code_input, pattern, documentation)

        # store context for follow-ups
        st.session_state.last_pattern = pattern
        st.session_state.last_doc = documentation

        add_message("user", code_input)
        add_message("assistant", explanation)

        # --- Results Section -------------------------------------------------
        st.markdown("---")
        st.subheader("Results")
        st.write(f"**Detected pattern:** {pattern}")
        st.write(f"**Similarity score:** {score}")
        st.write("**Explanation:**")
        st.write(explanation)

# --- Follow-up Discussion Section ------------------------------------------
if st.session_state.last_pattern:
    st.markdown("---")
    st.subheader("Follow-up Discussion")
    follow_up = st.text_input("Ask a follow-up question")
    if st.button("Send") and follow_up.strip():
        # minimal rewrite context using only the detected pattern
        pattern_note = f"The conversation is about the {st.session_state.last_pattern} design pattern."
        rewrite_context = [{"role": "system", "content": pattern_note}]

        rewritten = rewrite_query(rewrite_context, follow_up)
        add_message("user", follow_up)

        # generate explanation using rewritten query
        resp = generate_explanation(
            rewritten, st.session_state.last_pattern, st.session_state.last_doc
        )
        add_message("assistant", resp)

        # display follow-up response immediately
        st.subheader("Follow-up Response")
        st.caption(f"Rewritten standalone question: {rewritten}")
        st.write(resp)

# --- Conversation History Section -----------------------------------------
st.markdown("---")
if st.session_state.history:
    st.subheader("Conversation")
    for msg in st.session_state.history:
        role = msg["role"].capitalize()
        st.markdown(f"**{role}:** {msg['content']}")
