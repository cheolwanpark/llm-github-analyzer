from typing import Iterable, Optional
import tiktoken
import re

_enc = tiktoken.encoding_for_model("gpt-4o")

def _encode(s: str) -> list[int]:
    return _enc.encode(s, disallowed_special=())

def count_tokens(s: str):
    return len(_encode(s))

def count_tokens_prompt(system: str, user: str):
    return count_tokens(system) + count_tokens(user)

def get_between(s: str, start: str, end: str) -> Optional[str]:
    match = re.search(f"(?<={start})([\s\S]*?)(?={end})", s)
    return match.group(0) if match else None

def get_content(s: str, tag: str) -> Optional[str]:
    return get_between(s, f"<{tag}>", f"<\/{tag}>")

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
    system = "You are an AI assistant specializing in generating search sentences for a vector database containing code summaries. Your task is to create search sentences that will help find relevant code summaries in a GitHub repository analyzer."
    user = \
f'''First, review the summarized README of the repository:

<readme_summary>
{readme}
</readme_summary>

Now, consider the user's query:

<user_query>
{query}
</user_query>

Your task is to generate up to {answer_n} distinct search sentences based on the user's query and the context provided in the README summary. Each search sentence should help find relevant code summaries in the vector database.

When creating the search sentences, follow these guidelines:
1. Keep each sentence vague enough, as we don't know exactly which summaries are in the vector database.
2. Incorporate common knowledge related to the query if the user's question doesn't provide enough information.
3. Avoid hallucination or making up specific details not present in the query or README summary.
4. Focus on key concepts, functions, or components mentioned in the query or README that are likely to be present in code summaries.
5. Use general programming terms and concepts that are likely to appear in code summaries.

Before providing your final output, wrap your thought process in <search_sentence_generation> tags. Follow these steps:
1. List key concepts from the README summary and user query.
2. Brainstorm potential search angles based on these concepts.
3. Draft initial search sentences.
4. Refine the sentences, ensuring they adhere to the guidelines provided.
5. Evaluate each sentence against the guidelines, noting how well it meets each criterion.

It's OK for this section to be quite long.

<search_sentence_generation>
[Your thought process for generating and refining search sentences]
</search_sentence_generation>

After your thought process, provide your final search sentences within <search_sentences> tags. Separate each sentence with "{sep_token}". Ensure that you generate at least one sentence, but no more than {answer_n} sentences.

Example output structure (do not use this content, it's just to illustrate the format):
<search_sentences>
Find code related to user authentication{sep_token}Locate database connection implementations{sep_token}Search for API endpoint definitions
</search_sentences>'''
    return system, user

def get_readme_summarization_prompt(readme: str, query: str) -> tuple[str, str]:
    system = "You are tasked with summarizing a README file for a GitHub project. This summary will be used to enhance user prompts and generate search sentences for a vector database. Your goal is to provide an accurate and concise summary based on the content of the README and the user's query."
    user = \
f'''Here is the content of the README file:

<readme>
{readme}
</readme>

Your task is to summarize this README file, keeping the following guidelines in mind:

1. Focus on extracting key information that is relevant to understanding the project, its purpose, features, and usage.
2. Avoid any form of hallucination or adding information not present in the original README.
3. Be concise but comprehensive, capturing the essence of the project.
4. Pay attention to any specific sections like installation instructions, usage examples, or API documentation if present.

Consider the following user query when creating your summary:

<user_query>
{query}
</user_query>

Tailor your summary to address aspects of the README that are most relevant to this query. Pull out information that directly relates to or answers the user's question.

Provide your summary in the following format:

<summary>
[Insert your concise summary here, focusing on information relevant to the user query]
</summary>

<key_points>
1. [First key point relevant to the user query]
2. [Second key point relevant to the user query]
3. [Continue with additional key points as needed]
</key_points>

Remember, your summary and key points should only contain information present in the original README. The search terms should be concise phrases or keywords that capture the main concepts discussed in the README and are relevant to the user's query.'''
    return system, user

def get_answer_generation_prompt(query: str, output_format: str, readme: str, directories: Iterable[str], codes: Iterable) -> tuple[str, str]:
    directories = "\n".join(map(lambda dir: f"- {dir}", directories))
    code_snippets = "\n".join(map(
        lambda x: f'<code_snippet path="{x.path}" name={x.name}>{x.body}</code_snippet>',
        codes
    ))
    system = "You are an AI assistant specialized in analyzing GitHub repositories. Your task is to generate an answer to a user's query about a specific GitHub project based on the provided information. You must strictly adhere to the given context and avoid any speculation or inclusion of information not explicitly provided."
    user = \
f'''Here's the information you have:

<readme_summary>
{readme}
</readme_summary>

<directory_list>
{directories}
</directory_list>

<code_snippets>
{code_snippets}
</code_snippets>

The user's query is:
<user_query>
{query}
</user_query>

To answer the query, follow these steps:

1. Carefully analyze the provided README summary, directory list (exclude hidden directories starts with .), and code snippets.
2. Focus only on the information directly related to the user's query.
3. If the query cannot be answered with the given information, exclude that part from answer.
4. Do not make assumptions or include any information not present in the provided context.
5. Use specific references to the code snippets when relevant. Refer to each snippet using its name and path. You can also directly include the body of code snippets. 

Format your response according to the following structure:
<output_format>
{output_format}
</output_format>

Remember:
- Stick strictly to the provided information.
- Do not hallucinate or include any details not explicitly given.
- If you cannot answer the query with the available information, say so clearly.
- Place your response between '<answer>' and '</answer>'

Now, please analyze the given information and provide your answer to the user's query.'''
    return system, user

def get_user_query_enhance_prompt(query: str, readme: str):
    system = 'You are an AI assistant tasked with enhancing user prompts for a GitHub project analyzer product. Your goal is to translate vague or general user prompts into more specific, structured prompts that will generate accurate and relevant information about a GitHub project.'
    user = \
f'''First, I will provide you with a summary of the project's README:

<readme_summary>
{readme}
</readme_summary>

Keep in mind the following constraints and requirements:
1. The enhanced prompt must generate structured output.
2. Only the summarized README, list of directories, and related code chunks (functions and classes body) are available to generate answers.
3. Do not try to generate any response that cannot be answered with the given context (summarized README, list of directories, and related code chunks).
4. The user prompt may be vague or general, so your task is to make it more specific and actionable.

To enhance the user prompt, follow these steps:
1. Analyze the user prompt to identify the main topic or question.
2. Determine which aspects of the project (e.g., structure, functionality, dependencies) the prompt is likely referring to.
3. Incorporate relevant keywords or concepts from the README summary into the enhanced prompt.
4. Structure the prompt to request specific, actionable information that can be derived from the available context.
5. Ensure the enhanced prompt will generate a response that can be presented in a structured format (e.g., lists, tables, or categorized sections).

Generate your enhanced prompt using the following format:
<enhanced_prompt>
[Your enhanced prompt here, structured to generate a specific and actionable response]
</enhanced_prompt>

<output_format>
[Specify the desired output format for the response, such as a list, table, or categorized sections]
</output_format>

Now, please enhance the following user prompt:

<user_prompt>
{query}
</user_prompt>
'''
    return system, user