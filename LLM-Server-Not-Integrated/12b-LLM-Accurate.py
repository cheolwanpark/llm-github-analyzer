from flask import Flask, request, jsonify
import requests
# every time you run this code, you will need to run command: ngrok http --domain=quiet-vigorously-squirrel.ngrok-free.app 5000
# to get the ngrok setup.
# Ngrok Public API URL (Your friends will use this)
NGROK_URL = "https://quiet-vigorously-squirrel.ngrok-free.app"

# LM Studio Local API (Do not change)
LM_STUDIO_API = "http://127.0.0.1:1234/v1/chat/completions"

# API Keys (Only share with trusted friends)
API_KEYS = {"friend1": "mysecretkey123", "friend2": "anotherkey456"}

app = Flask(__name__)

# ====================== CODE SUMMARIZATION FUNCTION ======================
def summarize_code_blocks(code_blocks):
    """
    Summarizes multiple code blocks using Gemma 3-12B IT via LM Studio API.
    """
    system_prompt = """
    You are an AI code summarizer specialized in extracting detailed and structured summaries from programming code. 
    Your task is to analyze each provided code block and generate a **detailed** and **insightful** summary, capturing:
    - **Primary purpose**: Explain the function/class and its intended use.
    - **Inputs & Outputs**: Describe function parameters, return values, and expected behavior.
    - **Algorithmic Logic**: Explain loops, recursion, conditions, and key steps.
    - **Data Structures & Patterns**: Identify key data structures or design patterns used.
    - **Complexity Analysis**: Provide Big-O complexity if applicable.
    - **Potential Issues or Edge Cases**: Highlight constraints, limitations, and edge cases.

    Each code block is enclosed between `<|START|>` and `<|END|>`. Your response **must** be a structured summary for each code block, 
    strictly separated by `<|sep|>`, with no additional text.
    """

    user_prompt = "Please analyze and summarize the following code blocks with **detailed explanations**:\n\n"

    for code in code_blocks:
        user_prompt += f"<|START|>\n{code}\n<|END|>\n\n"

    payload = {
        "model": "gemma-3-12b-it",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(LM_STUDIO_API, json=payload)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "Error fetching response"

# ====================== REPO STRUCTURE ANALYSIS FUNCTION ======================
def analyze_repo_structure(repo_tree):
    """
    Analyzes the folder structure of a GitHub repository and provides a structured summary.
    """
    system_prompt = """
    You are an AI trained in software repository analysis. Your task is to analyze a GitHub repository folder structure 
    and provide a structured summary.

    **Instructions:**
    - Identify the **purpose** of each folder.
    - Describe **dependencies** between folders.
    - Explain how different folders **relate** to each other.
    - If a `tests/` or `docs/` folder exists, explain its significance.
    - Provide a **concise but informative** response.
    - Based on their names and formats, have a detailed description for the files inside of each folder.

    **Example Input Format:**
    ```
    src/
        app.py
        utils.py
    tests/
        test_app.py
    docs/
        README.md
    ```

    **Example Output Format:**
    - `src/` contains core application logic.
    - `tests/` has unit tests for validating functionality.
    - `docs/` provides project documentation.

    **Stick to factual, structured analysis. Avoid speculation.**
    """

    user_prompt = f"Analyze the following repository structure:\n\n```\n{repo_tree}\n```"

    payload = {
        "model": "gemma-3-12b-it",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(LM_STUDIO_API, json=payload)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "Error fetching response"

# ====================== BASELINE CODE SUMMARIZATION FUNCTION ======================
def baseline_summarize_code_blocks(code_blocks):
    """
    A baseline function that simply requests the AI model to summarize the given code blocks 
    without detailed structure or specific instructions.
    """
    user_prompt = "Summarize the following code:\n\n"

    for code in code_blocks:
        user_prompt += f"```\n{code}\n```\n\n"

    payload = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(LM_STUDIO_API, json=payload)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "Error fetching response"

# ====================== BASELINE REPO STRUCTURE ANALYSIS FUNCTION ======================
def baseline_analyze_repo_structure(repo_tree):
    """
    A baseline function that simply requests the AI model to describe the given repository 
    structure without detailed structuring or specific guidance.
    """
    user_prompt = f"Describe the following repository structure:\n\n```\n{repo_tree}\n```"

    payload = {
        "model": "meta-llama-3.1-8b-instruct",
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(LM_STUDIO_API, json=payload)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "Error fetching response"


# ====================== SECURE API ROUTES ======================


@app.route("/baseline_summarize_code", methods=["POST"])
def baseline_summarize_code():
    """Handles baseline code summarization requests."""

    api_key = request.headers.get("X-API-Key")
    if api_key not in API_KEYS.values():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if "code_blocks" not in data:
        return jsonify({"error": "Missing 'code_blocks' field"}), 400

    summary = baseline_summarize_code_blocks(data["code_blocks"])
    return jsonify({"summary": summary})

@app.route("/baseline_analyze_repo", methods=["POST"])
def baseline_analyze_repo():
    """Handles baseline repository structure analysis requests."""

    api_key = request.headers.get("X-API-Key")
    if api_key not in API_KEYS.values():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if "repo_tree" not in data:
        return jsonify({"error": "Missing 'repo_tree' field"}), 400

    analysis = baseline_analyze_repo_structure(data["repo_tree"])
    return jsonify({"analysis": analysis})

@app.route("/chat", methods=["POST"])
def proxy_request():
    """Proxies a chat request to LM Studio with API key authentication."""
    
    api_key = request.headers.get("X-API-Key")
    if api_key not in API_KEYS.values():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    response = requests.post(LM_STUDIO_API, json=data)
    return jsonify(response.json()), response.status_code

@app.route("/summarize_code", methods=["POST"])
def summarize_code():
    """Handles code summarization requests."""
    
    api_key = request.headers.get("X-API-Key")
    if api_key not in API_KEYS.values():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if "code_blocks" not in data:
        return jsonify({"error": "Missing 'code_blocks' field"}), 400

    summary = summarize_code_blocks(data["code_blocks"])
    return jsonify({"summary": summary})

@app.route("/analyze_repo", methods=["POST"])
def analyze_repo():
    """Handles repository structure analysis requests."""
    
    api_key = request.headers.get("X-API-Key")
    if api_key not in API_KEYS.values():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if "repo_tree" not in data:
        return jsonify({"error": "Missing 'repo_tree' field"}), 400

    analysis = analyze_repo_structure(data["repo_tree"])
    return jsonify({"analysis": analysis})

# ====================== START SECURE SERVER ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Open API on port 5000
