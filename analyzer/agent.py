from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, TypeVar
from llm import LLM
from common.query import Query, QueryStatus
from codedb import CodeDB, QueryResult, CodeRecord
from prompt import (
    sep_token,
    count_tokens,
    get_content,
    count_tokens_prompt,
    get_codedb_query_generation_prompt, 
    get_readme_summarization_prompt,
    get_answer_generation_prompt,
    get_user_query_enhance_prompt
)

T = TypeVar('T')
def _unique_by_key(iterable: Iterable[T], key=lambda x: x) -> list[T]:
    seen = set()
    result = []
    for item in iterable:
        k = key(item)
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result

class Agent:
    def __init__(self, codedb: CodeDB):
        self.small_llm = LLM(model="qwen25-coder-32b-instruct")
        self.small_limit = 30*1000
        self.med_llm = LLM(model="llama3.3-70b-instruct-fp8")
        self.large_llm = LLM(model="llama3.1-405b-instruct-fp8")
        self.codedb = codedb
        self.repo = codedb.repo
    
    def answer(self, q: Query) -> dict:
        q.set_status(QueryStatus.GEN_README)

        if self.codedb.readme != "":
            system, user = get_readme_summarization_prompt(self.codedb.readme, q.query)
            response = self.large_llm.prompt(system, user)
            summary = get_content(response, "summary")
            key_points = get_content(response, "key_points")
            readme = f"{summary}\n# Key Points\n{key_points}"
        else:
            readme = ""

        q.set_status(QueryStatus.ENHANCE_PROMPT)
        system, user = get_user_query_enhance_prompt(q.query, readme)
        response = self.large_llm.prompt(system, user)
        enhanced_query = get_content(response, "enhanced_prompt")
        output_format = get_content(response, "output_format")
        
        q.set_status(QueryStatus.GEN_CODE_CONTEXT)

        SEARCH_SENTENCES = 8
        RETRIEVE_N = 16

        system, user = get_codedb_query_generation_prompt(enhanced_query, readme, SEARCH_SENTENCES)
        response = self.large_llm.prompt(system, user)
        search_sentences = get_content(response, "search_sentences").strip().split(sep_token)
        search_results: list[QueryResult] = []
        for search_sentence in search_sentences:
            search_results.extend(self.codedb.search(search_sentence, 8))
        search_results.sort(key=lambda q: q.score, reverse=True)
        search_results = _unique_by_key(search_results, key=lambda r: f"{r.rec.path}:{r.rec.name}")[:RETRIEVE_N]
        codes = map(
            lambda x: x.rec,
            search_results
        )

        q.set_status(QueryStatus.ANSWERING)

        system, user = get_answer_generation_prompt(
            enhanced_query,
            output_format,
            readme,
            self.codedb.directories,
            codes
        )
        response = self.large_llm.prompt(system, user, temperature=0.3)
        answer = get_content(response, "answer")
        
        return {
            "answer": answer,
            "enhanced_query": enhanced_query,
            "output_format": output_format,
            "summarized_readme": readme,
            "search_sentences": search_sentences,
            "search_results": list(map(lambda r: {
                "score": r.score,
                "path": r.rec.path,
                "name": r.rec.name,
                "desc": r.rec.description,
            }, search_results))
        }

    def _bulk_prompt(self, prompts: Iterable[tuple[str, str]], use_large=False, threads: int = 16) -> Iterable[str]:
        def prompt(prompt: tuple[str, str]) -> str:
            n_tokens = count_tokens_prompt(*prompt)
            if n_tokens < self.small_limit:
                return self.small_llm.prompt(*prompt)
            elif use_large:
                return self.large_llm.prompt(*prompt)
            else:
                return self.med_llm.prompt(*prompt)
        with ThreadPoolExecutor(max_workers=threads) as executor:
            return executor.map(prompt, prompts)
    
    
