import tiktoken
from repo import Repository
from parsing import parse, CodeChunk, ClassChunk, FunctionChunk
from typing import Union
from common.redis import Redis
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from llm import LLM

enc = tiktoken.encoding_for_model("gpt-4o")

def _encode(s: str) -> list[int]:
    return enc.encode(s, disallowed_special=())

def _count_tokens(s: str):
    return len(_encode(s))

def _get_llm(system: str, user: str):
    len = _count_tokens(system) + _count_tokens(user)
    if len > 32*1000:
        return LLM(model="llama3.3-70b-instruct-fp8")
    else:
        return LLM(model="qwen25-coder-32b-instruct")


def _get_summarization_prompt(chunks: list[str]) -> tuple[str, str]:
    system = \
'''You are a code summarizer for a retrieval augmented generation (RAG) system. Your task is to analyze each provided code block—which may contain functions, classes, or other programming constructs—and generate a concise yet information-rich summary. Each summary should capture:
- The primary purpose of the code.
- Key functionalities, inputs, and outputs.
- Significant algorithms, design patterns, or data structures used.
- Noteworthy implementation details or constraints.

The code blocks are provided as text with each block delimited by the markers `<|START|>` and `<|END|>`. Use these markers to identify and extract each code block for analysis.

**Important:** Your final output must be a single string containing the summaries for all code blocks separated by the delimiter `<|sep|>`, and no additional text or information.
'''

    chunks = map(lambda block: f"<|START|>{block}<|END|>", chunks)
    chunks = "\n".join(chunks)
    user = \
f'''Please generate summaries for the following text containing multiple code blocks. Each code block is delimited by `<|START|>` and `<|END|>` markers. For every code block, produce a summary that includes all the critical information such as what the code does, how it does it, key functions or classes, and any important details that would be useful for retrieval and query purposes. Ensure that the summaries are concise yet rich in detail.

Remember: The final output must strictly be a single string with each summary separated by the delimiter `<|sep|>` and should not include any extra text or information.

Example Output:
Function 'calculate_factorial' computes the factorial of a number using recursion and handles edge cases effectively. <|sep|> Class 'BinarySearchTree' implements a binary search tree with methods for node insertion, deletion, and search, while supporting in-order traversal for sorted output.

Text with Code Blocks:
{chunks}
'''
    return system, user

class CodeDB:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    def build(self, repo: Repository, threads=16):
        chunks = self._make_chunk_for_prompts(parse(repo))
        chunks = self._split_chunks(chunks)

        def _generate_descriptions(chunks: list[str]):
            system, user = _get_summarization_prompt(chunks)
            llm = _get_llm(system, user)
            result = llm.prompt(system, user)
            result = result.split("<|sep|>")
            return result if len(result) == len(chunks) else [""]*len(chunks)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            descriptions = list(executor.map(_generate_descriptions, chunks))
        descriptions = sum(descriptions, [])
    
        for i, tup in enumerate(zip(sum(chunks, []), descriptions)):
            code, desc = tup
            print(f"### CODE {i+1} ###\n{code}\n### DESCRIPTION {i+1} ###\n{desc}\n\n")
        
    def _make_chunk_for_prompts(self, codes: list[CodeChunk]):
        def convert(chunk: Union[FunctionChunk, ClassChunk]) -> str:
            return chunk.body
        chunks = []
        for code in codes:
            chunks.extend(code.classes)
            chunks.extend(code.functions)
        return list(map(convert, chunks))
    
    def _split_chunks(self, chunks: list[str], max_tokens=30*1000) -> list[list[str]]:
        r = []
        sub = []
        tokens = 0
        for chunk in chunks:
            cnt = _count_tokens(chunk)
            if tokens + cnt > max_tokens:
                r.append(sub)
                sub = [chunk]
                tokens = cnt
                continue
            sub.append(chunk)
            tokens += cnt
        r.append(sub)
        return r 
            

if __name__ == "__main__":
    redis = Redis()
    repo = Repository("https://github.com/cheolwanpark/llm-github-analyzer")
    # repo = Repository("https://github.com/huggingface/transformers")
    codedb = CodeDB(redis)
    codedb.build(repo)

