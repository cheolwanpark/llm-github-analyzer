from flask import Flask, request, jsonify
import requests

# every time you run this code, you will need to run command:
# ngrok http --domain=quiet-vigorously-squirrel.ngrok-free.app 5000
# to get the ngrok setup.

# Ngrok Public API URL (Your friends will use this)
NGROK_URL = "https://quiet-vigorously-squirrel.ngrok-free.app"

# LM Studio Local API (Do not change)
LM_STUDIO_API = "http://127.0.0.1:1234/v1/chat/completions"

# API Keys (Only share with trusted friends)
API_KEYS = {"friend1": "mysecretkey123", "friend2": "anotherkey456"}

app = Flask(__name__)

# Model names
MODEL_12B = "gemma-3-12b-it"
MODEL_8B = "meta-llama-3.1-8b-instruct"

# ====================== TOKEN ESTIMATION FUNCTIONS ======================
def estimate_token_count(input_data):
    """
    Estimates the number of tokens in the input.
    - If input_data is a list (code blocks), return a list of token counts per block.
    - If input_data is a string (repo structure), return a single token count.
    """
    if isinstance(input_data, list):
        return [len(block.split()) for block in input_data]  # Token estimation per block
    elif isinstance(input_data, str):
        return len(input_data.split())  # Token estimation for repo structure
    return 0  # Default case

# ====================== PRIMARY SUMMARIZATION FUNCTION ======================
def generate_summary(text, model, system_prompt):
    """
    Generates a summary using the specified model and system prompt.
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }
    response = requests.post(LM_STUDIO_API, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error fetching response"

# ====================== EXPANSION FUNCTION (For Medium-Length Inputs) ======================
def expand_code_summary(summary, model):
    """
    Expands an existing summary using the 12B model to add more detail.
    """
    code_expansion_prompt = """
    You are an AI specializing in **enhancing** and **expanding** code summaries while maintaining **clarity, conciseness, and factual accuracy**. 
    Your task is to **improve an existing concise summary** by **adding only essential missing details**. Do NOT remove or replace any part of the original summary.

    **Key Rules for Expansion (Code Summarization):**
    - **Do NOT delete or replace any part of the original summary.**
    - **Expand only where necessary**, adding **critical missing details** while keeping the response concise.
    - **Prioritize fast response times**—avoid overly long explanations.

    **Expansion Instructions (Code Summarization):**
    - **Primary Purpose:** Expand on the **usefulness and real-world applications** of the function/class, keeping it concise.
    - **Inputs & Outputs:** Add **missing details** about function parameters, expected data types, return values, and variations.
    - **Algorithmic Logic:** Identify **missing key steps** in loops, recursion, conditions, and computational logic.
    - **Dependency Analysis:** Highlight **connections with other parts of the code**, such as **global variables, APIs, databases, or external libraries**.
    - **Data Structures & Design Patterns:** Specify **which data structures (lists, dicts, trees, etc.) or design patterns (Factory, Singleton, etc.)** are used.
    - **Complexity Analysis:** If missing, provide a **concise** time/space complexity estimate (**Big-O notation**).
    - **Potential Issues & Edge Cases:** Point out **critical constraints, limitations, or special cases**.
    - **Optimization Opportunities:** Suggest **only the most impactful improvements** without unnecessary elaboration.
    - **Security Concerns & Best Practices:** Highlight **any security risks (e.g., SQL injection, buffer overflow) and best practices**.

    **Formatting Rules:**
    - **Strictly follow the original structure** of the summary.
    - **Add only essential missing details**—avoid redundancy or excessive verbosity.
    - **Ensure responses remain well-organized, structured, and easy to read.**

    **Your expansion should be concise, insightful, and focused on fast response times. Do NOT generate overly detailed explanations. Only ADD missing details—never delete or replace existing content.**
    """

    user_prompt = f"Enhance and expand the following summary while preserving its structure and key details:\n\n{summary}"
    return generate_summary(user_prompt, model, code_expansion_prompt)


def expand_repo_summary(summary, model):
    """
    Expands an existing summary using the 12B model to add more detail.
    """


    # System prompt for repository analysis expansion
    repo_expansion_prompt = """
    You are an AI specializing in **enhancing repository analysis summaries** while ensuring **clarity, conciseness, and factual accuracy**. 
    Your task is to **improve an existing concise repository analysis** by **adding only essential missing details**. Do NOT remove or replace any part of the original summary.

    **Key Rules for Expansion (Repository Analysis):**
    - **Do NOT delete or replace any part of the original summary.**
    - **Expand only where necessary**, adding **critical missing details** while keeping the response concise.
    - **Prioritize fast response times**—avoid overly long explanations.

    **Expansion Instructions (Repository Analysis):**
    - **Purpose of Each Folder:** Expand on the **role of each folder** in the project.
    - **Inter-folder Dependencies:** Explain **how folders depend on each other** and **which services rely on shared modules**.
    - **Tests & Documentation:** If present, explain **their significance and how they contribute to maintainability**.
    - **Technology & Frameworks Used:** Identify **key programming languages, libraries, or frameworks** used in the repository.
    - **Build & Deployment Process:** If applicable, describe **how CI/CD, Docker, Kubernetes, or Terraform scripts** are used.
    - **Potential Scalability Issues:** If relevant, highlight **any concerns with repository structure** that might cause scaling problems.
    - **Security Considerations:** Identify **potential security risks in configurations (e.g., unencrypted secrets, open database ports)**.
    - **Best Practices & Optimization:** Suggest **improvements in folder structure or modularization** if necessary.

    **Formatting Rules:**
    - **Strictly follow the original structure** of the summary.
    - **Add only essential missing details**—avoid redundancy or excessive verbosity.
    - **Ensure responses remain well-organized, structured, and easy to read.**

    **Your expansion should be concise, insightful, and focused on fast response times. Do NOT generate overly detailed explanations. Only ADD missing details—never delete or replace existing content.**
    """

    # Determine if input is a **code summary** or a **repository summary**
    # TODO check whether the input is a code summary or a repository summary

    user_prompt = f"Enhance and expand the following summary while preserving its structure and key details:\n\n{summary}"
    return generate_summary(user_prompt, model, repo_expansion_prompt)

# ====================== CODE SUMMARIZATION FUNCTION (UPDATED) ======================
def summarize_code_blocks(code_blocks):
    """
    Summarizes all code blocks in a single request using the correct model based on token count.
    The entire input is processed at once, ensuring each block is enclosed between <|START|> and <|END|>,
    and all responses are strictly separated by `<|sep|>`.
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

    # Format input: Enclose each code block properly and separate them with `<|sep|>`
    formatted_code = "<|sep|>".join([f"<|START|>\n{code}\n<|END|>" for code in code_blocks])

    # Estimate total token count for the entire input
    total_token_count = estimate_token_count(formatted_code)

    # Choose model based on total token count
    if total_token_count < 100:
        model = MODEL_12B
        summary = generate_summary(formatted_code, model, system_prompt)
    elif 100 <= total_token_count <= 800:
        initial_summary = generate_summary(formatted_code, MODEL_8B, system_prompt)
        summary = expand_code_summary(initial_summary, MODEL_12B)
    else:
        model = MODEL_8B
        summary = generate_summary(formatted_code, model, system_prompt)

    return summary  # Final structured summary
 # Ensure proper separation in response

# ====================== REPOSITORY STRUCTURE ANALYSIS FUNCTION (UPDATED) ======================
def analyze_repo_structure(repo_tree):
    """
    Analyzes the folder structure of a GitHub repository and provides a structured summary.
    Uses dynamic model selection based on token count.
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
    
    token_count = estimate_token_count(repo_tree)  # Estimate token count for repo_tree

    if token_count < 30:
        model = MODEL_12B
    elif 30 <= token_count <= 2000:
        initial_summary = generate_summary(repo_tree, MODEL_8B, system_prompt)
        return expand_repo_summary(initial_summary, MODEL_12B)
    else:
        model = MODEL_8B

    return generate_summary(repo_tree, model, system_prompt)

# ====================== BASELINE FUNCTIONS (UPDATED TO USE MODEL_8B) ======================
def baseline_summarize_code_blocks(code_blocks):
    """
    A baseline function that simply requests the AI model to summarize the given code blocks 
    without detailed structure or specific instructions.
    """
    user_prompt = "Summarize the following code:\n\n"
    for code in code_blocks:
        user_prompt += f"```\n{code}\n```\n\n"
    return generate_summary(user_prompt, MODEL_8B, "Provide a basic code summary.")

def baseline_analyze_repo_structure(repo_tree):
    """
    A baseline function that simply requests the AI model to describe the given repository 
    structure without detailed structuring or specific guidance.
    """
    user_prompt = f"Describe the following repository structure:\n\n```\n{repo_tree}\n```"
    return generate_summary(user_prompt, MODEL_8B, "Provide a basic analysis of the repository structure.")

# ====================== SECURE API ROUTES (UNCHANGED) ======================


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
