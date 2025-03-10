from concurrent.futures import ThreadPoolExecutor
from typing import Iterable
from llm import LLM
from common.query import Query, QueryStatus
from codedb import CodeDB, QueryResult, CodeRecord
from prompt import (
    sep_token,
    count_tokens,
    count_tokens_prompt,
    get_codedb_query_generation_prompt, 
    get_codedb_query_generation_prompt_from_codes,
    get_readme_summarization_prompt,
    get_answer_generation_prompt
)

class Agent:
    def __init__(self, codedb: CodeDB):
        self.small_llm = LLM(model="qwen25-coder-32b-instruct")
        self.small_limit = 30*1000
        self.large_llm = LLM(model="llama3.3-70b-instruct-fp8")
        self.large_limit = 100*1000
        self.codedb = codedb
        self.repo = codedb.repo
    
    def answer(self, q: Query) -> dict:
        q.set_status(QueryStatus.GEN_README)

        readme = self.repo.readme
        system, user = get_readme_summarization_prompt(readme.read() if readme is not None else "", q.query)
        readme = self.large_llm.prompt(system, user)

        q.set_status(QueryStatus.GEN_CODE_CONTEXT)

        system, user = get_codedb_query_generation_prompt(q.query, readme, 8)
        first_queries = self.small_llm.prompt(system, user).split(sep_token)
        first_result: list[QueryResult] = []
        for query in first_queries:
            first_result.extend(self.codedb.search(query, 2))
        d = dict()
        for result in first_result:
            d[f"{result.rec.path}:{result.rec.name}"] = result.rec

        splitted_codes = self._split_codes(
            d.values(), 
            prompt_tokens=count_tokens_prompt(*get_codedb_query_generation_prompt_from_codes([], readme, 4))
        )
        prompts = map(
            lambda codes: get_codedb_query_generation_prompt_from_codes(
                map(
                    lambda x: x.body, 
                    codes
                ), 
                readme,
                4
            ), 
            splitted_codes
        )
        responses = self._bulk_prompt(prompts)
        second_queries = sum(map(lambda r: r.split(sep_token), responses), [])
        second_result: list[QueryResult] = []
        for query in second_queries:
            second_result.extend(self.codedb.search(query, 2))
        for result in second_result:
            d[f"{result.rec.path}:{result.rec.name}"] = result.rec

        q.set_status(QueryStatus.ANSWERING)
        
        codes = d.values()
        splitted_codes = self._split_codes(
            codes,
            prompt_tokens=count_tokens_prompt(*get_answer_generation_prompt(readme, query, []))
        )
        prompts = map(
            lambda codes: get_answer_generation_prompt(
                readme,
                query,
                map(
                    lambda x: x.body,
                    codes
                )
            ),
            splitted_codes
        )
        answers = self._bulk_prompt(prompts)
        
        return {
            "answers": list(answers),
            "summarized_readme": readme,
            "first_queries": first_queries,
            "first_result": list(map(lambda r: {
                "score": r.score,
                "path": r.rec.path,
                "name": r.rec.name,
                "desc": r.rec.description,
            }, first_result)),
            "second_queries": second_queries,
            "second_result": list(map(lambda r: {
                "score": r.score,
                "path": r.rec.path,
                "name": r.rec.name,
                "desc": r.rec.description,
            }, second_result)),
            "context_codes": list(map(lambda r: {
                "path": r.path,
                "name": r.name,
                "desc": r.description,
            }, codes))
        }

    def _bulk_prompt(self, prompts: Iterable[tuple[str, str]], threads: int = 16) -> Iterable[str]:
        def prompt(prompt: tuple[str, str]) -> str:
            n_tokens = count_tokens_prompt(*prompt)
            if n_tokens < self.small_limit:
                return self.small_llm.prompt(*prompt)
            else:
                return self.large_llm.prompt(*prompt)
        with ThreadPoolExecutor(max_workers=threads) as executor:
            return executor.map(prompt, prompts)
    
    def _split_codes(self, codes: list[CodeRecord], prompt_tokens: int) -> list[list[CodeRecord]]:
        max_tokens = self.small_limit - prompt_tokens

        tokens = 0
        r = []
        sub = []
        tokens = 0
        for code in codes:
            cnt = count_tokens(code.body)
            if tokens + cnt > max_tokens:
                r.append(sub)
                sub = [code]
                tokens = cnt
                continue
            sub.append(code)
            tokens += cnt
        r.append(sub)
        return r
