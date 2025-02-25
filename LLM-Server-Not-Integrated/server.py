from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from config import OPENAI_API_KEY  # Import API Key from config file
import logging

#  Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

#  Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

#  Memory to store code chunks for analysis
repo_analysis_memory = {}

###  Request Models
class RepoStructureRequest(BaseModel):
    structure: dict  # Folder names & files

class CodeChunkRequest(BaseModel):
    total_files: int = None  # Only for first request
    filename: str
    code: str
    repo_id: str

###  Endpoint 1: Analyze Repository Structure
@app.post("/analyze")
def analyze_repo_structure(request: RepoStructureRequest):
    """
    Receives a repository structure (folders & files) and generates a structured summary.
    """
    try:
        logging.info("Analyzing repository structure...")

        #  Enhanced System Prompt for OpenAI
        system_prompt = """
        You are an AI trained in software repository analysis. Your task is to analyze the folder structure of a GitHub repository and provide a structured summary.
        
        **Instructions:**
        - Describe the possible dependencies between folders.
        - Examine the given folder structure.
        - Identify the **purpose** of each folder.
        - Explain how different folders **relate** to each other.
        - Highlight any **dependencies** between folders.
        - If a `tests` or `docs` folder exists, explain its significance.
        - Provide a **concise but informative** response.

        Example input Format:
        - `src/` main.py, helper.py
        - `tests/` unit_tests.py
        - `docs/` README.md
        Example ouput Format: (You should give a more detailed output)
        - `src/` contains the main application logic.
        - `tests/` contains unit tests that validate functionality.
        - `docs/` includes documentation files that explain how to use the project.

        **Do not include unnecessary speculation. Stick to factual, structured analysis.**
        """

        #  Send request to OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": f"Repository structure:\n{request.structure}"}
            ]
        )

        response_text = completion.choices[0].message.content
        logging.info(f"Generated summary: {response_text}")

        return {"summary": response_text}

    except Exception as e:
        logging.error(f"Error processing repository structure: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze repository structure.")

###  Endpoint 2: Analyze Detailed Code
@app.post("/analyze_detailed")
def analyze_code_chunk(request: CodeChunkRequest):
    """
    Receives code chunks, stores them, and once all chunks are received, provides a structured summary.
    """
    try:
        repo_id = request.repo_id  # Unique ID per repo

        if repo_id not in repo_analysis_memory:
            repo_analysis_memory[repo_id] = {"expected_files": None, "received_files": 0, "files": []}

        repo_memory = repo_analysis_memory[repo_id]

        # If it's the first request, set expected number of files
        if request.total_files:
            repo_memory["expected_files"] = request.total_files

        #  Store received file data
        repo_memory["files"].append({"filename": request.filename, "code": request.code})
        repo_memory["received_files"] += 1

        logging.info(f"Received {repo_memory['received_files']}/{repo_memory['expected_files']} files.")

        #  If all files received, summarize
        if repo_memory["received_files"] == repo_memory["expected_files"]:
            logging.info("All files received, generating analysis...")

            #  Enhanced System Prompt for OpenAI
            system_prompt = """
            You are an AI expert in software analysis. Your job is to analyze multiple code files from a repository and provide a structured summary.
            
            **Instructions:**
            - Examine the imports of the files to understand their **interdependencies**.
            - Identify the **main logic** file and any **utility functions**.
            - For each file, summarize its **purpose** in 1-2 sentences.
            - If a file is **critical** to the project's function, note it as a high priority.
            - If files are **interdependent**, highlight the relationships.
            - Provide a ranked list based on **priority** (e.g., main logic, utility functions, tests, etc.).
            - Use **concise, technical language**—avoid generic summaries.

            **Output Format:**
            - **File:** `main.py` → This is the entry point of the application.
            - **File:** `utils.py` → Contains helper functions for mathematical operations.
            - **File:** `test_main.py` → Tests the core functionality.

            **Do not speculate on functionality unless code is unclear. Stick to concrete analysis.**
            """

            #  Send request to OpenAI API
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": f"Files received:\n{repo_memory['files']}"}
                ]
            )

            response_text = completion.choices[0].message.content
            logging.info(f"Generated code analysis: {response_text}")

            #  Clean up memory
            del repo_analysis_memory[repo_id]

            return {"detailed_analysis": response_text}

        return {"message": f"File {request.filename} received. Waiting for {repo_memory['expected_files'] - repo_memory['received_files']} more files."}

    except Exception as e:
        logging.error(f"Error processing code analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze code.")

###  Root endpoint to verify server is running
@app.get("/")
def root():
    return {"message": "FastAPI GitHub Analyzer is running!"}


# Run the FastAPI server when executing the script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
