from typing import Iterable
import tiktoken

_enc = tiktoken.encoding_for_model("gpt-4o")

def _encode(s: str) -> list[int]:
    return _enc.encode(s, disallowed_special=())

def count_tokens(s: str):
    return len(_encode(s))

def count_tokens_prompt(system: str, user: str):
    return count_tokens(system) + count_tokens(user)

sep_token = '###'

def get_summarization_prompt(bodies: Iterable[str]) -> tuple[str, str]:
    bodies = sep_token.join(bodies)
    system = \
f'''You are a code summarizer for a retrieval augmented generation (RAG) system. Your task is to analyze each provided code block—which may contain functions, classes, or other programming constructs—and generate a concise yet information-rich summary. Each summary should capture:
- The primary purpose of the code.
- Key functionalities, inputs, and outputs.
- Significant algorithms, design patterns, or data structures used.
- Noteworthy implementation details or constraints.

The code blocks are provided as text with each block delimited by the delimiter `{sep_token}`. Use these markers to identify and extract each code block for analysis.

**Important:** Your final output must be a single string containing the summaries for all code blocks separated by the delimiter `{sep_token}`, and no additional text or information.
**Important:** The number of summaries must be same with the number of code blocks.
'''
    user = \
f'''Please generate summaries for the following text containing multiple code blocks. Each code block is delimited by the delimiter `{sep_token}`. For every code block, produce a summary that includes all the critical information such as what the code does, how it does it, key functions or classes, and any important details that would be useful for retrieval and query purposes. Ensure that the summaries are concise yet rich in detail.

Remember: The final output must strictly be a single string with each summary separated by the delimiter `{sep_token}` and should not include any extra text or information.

Example Output:
Function 'calculate_factorial' computes the factorial of a number using recursion and handles edge cases effectively.{sep_token}Class 'BinarySearchTree' implements a binary search tree with methods for node insertion, deletion, and search, while supporting in-order traversal for sorted output.

Text with Code Blocks:
{bodies}
'''
    return system, user

def get_codedb_query_generation_prompt(query: str, readme: str, answer_n: int) -> tuple[str, str]:
    system = \
f'''You are an assistant that transforms a user query along with a summarized README into one or more RAG queries for code similarity search. Use common programming knowledge not explicitly mentioned in the query—such as programs typically starting at a main function or web servers having an app instance with GET and POST endpoints—to enrich the result. Incorporate key details from the summarized README to guide your transformation. The output should align with the detail level found in code descriptions (for example, DTO definitions, REST endpoint implementations, or utility function logic) and be vague enough to capture similar code structures while excluding unrelated documentation. You may generate up to {answer_n} queries separated by {sep_token}.
'''
    user = \
f'''Below is the summarized README content:

{readme}

User Query: {query}

Convert the following user query and summarized README into one or more RAG queries tailored for retrieving code descriptions from a vector database. Output your result as a single query or multiple queries separated by {sep_token}.
'''
    return system, user

def get_codedb_query_generation_prompt_from_codes(bodies: Iterable[str], readme: str, answer_n: int) -> tuple[str, str]:
    bodies = sep_token.join(bodies)
    system = \
f'''You are an assistant that generates RAG query sentences from provided code bodies and a summarized readme of the project. Your queries will be used in a similarity search with a vector database containing code descriptions only (e.g., class definitions, function summaries, endpoint descriptions). Analyze the given code bodies (delimited by the delimiter `{sep_token}`) and the summarized readme text and generate queries that capture the code’s functionality, structure, and purpose. Use common programming knowledge (for example, noting that programs generally start at main, or that web servers typically define app instances with GET/POST endpoints) to enhance the query. Generate up to {answer_n} distinct queries, each in a single complete sentence. Separate multiple queries with the token {sep_token}. Do not include any additional text beyond the queries. Ensure your queries are strictly related to code descriptions and the summarized readme, and avoid including irrelevant or non-code documentation details.
'''
    user = \
f'''Below is the summarized README content:

{readme}

Below is the code bodies:

{bodies}

Given the following code bodies delimited by the delimiter `{sep_token}` and a summarized readme, generate one or more RAG query sentences that will be used to retrieve similar code descriptions. The output must be a single query or multiple queries separated by {sep_token}, without any quotes or extra information.
'''
    return system, user

def get_readme_summarization_prompt(readme: str, query: str) -> tuple[str, str]:
    system = \
'''You are an expert at distilling complex README files into concise summaries. When provided with a project's README and a specific query, produce a clear, well-structured markdown summary that includes all the information necessary to fully address the user query. Focus solely on the content relevant to the query, ensuring the summary is comprehensive yet succinct. Avoid extraneous details or direct quotations—only include a synthesized summary that captures the essential points.
'''
    user = \
f'''Below is the project's README content:

{readme}

User Query: {query}

Please generate a summarized version of the README that includes all the information required to fully respond to the user query, focusing on the relevant aspects.
''' if readme != "" else \
f'''User Query: {query}

Note: There is no README file available for this project.

Please generate a summary based solely on the available project context and details that are relevant to the user query.
'''
    return system, user

def get_answer_generation_prompt(readme: str, query: str, bodies: Iterable[str]) -> tuple[str, str]:
    bodies = sep_token.join(bodies)
    system = \
f'''You are provided with context that includes a summarized README and related code bodies. The code bodies are delimited by the token {sep_token}. The summarized README contains key project details such as purpose, usage instructions, and important notes, while the code bodies consist of relevant functions and classes.

Your task is to answer the following user query by integrating and using all necessary details from the provided context. Ensure your answer is concise yet complete, drawing on both the summarized README and the code bodies. Maintain clarity and adhere to any formatting guidelines provided.
'''
    user = \
f'''Answer the following query using the context provided below. Your answer must be concise and contain all the information requested.

User Query: {query}

Context:
Summarized README:

{readme}

Code Bodies:

{bodies}

Please ensure your response is complete and leverages the context provided.
'''
    return system, user