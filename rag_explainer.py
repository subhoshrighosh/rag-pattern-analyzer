import requests


# Build the prompt from the inputs

def build_prompt(user_code: str, detected_pattern: str, documentation_text: str) -> str:
    return (
        f"Detected pattern: {detected_pattern}\n"
        f"Documentation:\n{documentation_text}\n\n"
        f"User Java code:\n{user_code}\n\n"
        "Please explain how this code fits the pattern and any relevant details."
    )


# Send prompt to local Ollama server and return response text

def generate_explanation(user_code: str, detected_pattern: str, documentation_text: str) -> str:
    prompt = build_prompt(user_code, detected_pattern, documentation_text)
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    url = "http://localhost:11434/api/generate"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    # when stream is false, ollama returns {'response': '...'}
    return data.get("response", "")


if __name__ == "__main__":
    # simple demo
    code = (
        "public class Test { private static Test instance; private Test() {} "
        "public static Test getInstance() { if (instance==null) instance=new Test(); "
        "return instance;} }"
    )
    doc = "Singleton pattern ensures one instance..."
    pattern = "Singleton"
    explanation = generate_explanation(code, pattern, doc)
    print(explanation)
