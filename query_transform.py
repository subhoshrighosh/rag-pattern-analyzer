import requests


def build_rewrite_prompt(history, current_question):
    recent = history[-5:]

    lines = []

    # Role
    lines.append("### ROLE ###")
    lines.append("You are a query rewriting assistant.\n")

    # Instructions
    lines.append("### TASK ###")
    lines.append(
        "Rewrite the user's latest question into a fully self-contained question."
    )
    lines.append(
        "Resolve ambiguous references like 'it', 'its', 'this', 'that pattern'."
    )
    lines.append(
        "Do NOT answer the question."
    )
    lines.append(
        "Return ONLY the rewritten question."
    )
    lines.append(
        "If rewriting is not possible, return the original question exactly.\n"
    )

    # Conversation
    if recent:
        lines.append("### CONVERSATION HISTORY ###")
        for msg in recent:
            lines.append(f"{msg['role']}: {msg['content']}")
        lines.append("")

    # Current question
    lines.append("### CURRENT QUESTION ###")
    lines.append(current_question)
    lines.append("")
    lines.append("### REWRITTEN QUESTION ###")

    return "\n".join(lines)


def clean_rewritten(text: str) -> str:
    """Perform light cleanup on the model output.

    - Remove common prefixes like 'Rewritten question:'
    - Strip whitespace.
    - Drop any trailing explanation if present.
    """
    # remove labels
    for prefix in ["Rewritten question:", "Rewritten Question:"]:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    # take only first line if model added extra commentary
    text = text.splitlines()[0]
    return text.strip()


def rewrite_query(conversation_history, current_question):
    """Rewrite `current_question` using conversation context.

    Returns a self‑contained query. Falls back to original if output is
    empty or suspiciously short.
    """

    prompt = build_rewrite_prompt(conversation_history, current_question)
    payload = {"model": "mistral", "prompt": prompt, "stream": False}
    url = "http://localhost:11434/api/generate"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    rewritten = data.get("response", "")
    rewritten = clean_rewritten(rewritten)

    # if the rewritten text is empty or too short to be useful, fallback
    if not rewritten or len(rewritten) < 5:
        return current_question
    return rewritten


if __name__ == "__main__":
    history = [
        {"role": "user", "content": "Explain singleton"},
        {"role": "assistant", "content": "It's a creational pattern."},
    ]
    print(rewrite_query(history, "what about lazy init?"))
