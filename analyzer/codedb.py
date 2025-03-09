import tiktoken
from concurrent.futures import ThreadPoolExecutor
import json
import numpy as np
from dataclasses import dataclass, asdict
from typing import Union
from redis.commands.search.field import TextField, TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search import Search
from redis.commands.search.query import Query

from sentence_transformers import SentenceTransformer
from repo import Repository
from parsing import parse, CodeChunk, ClassChunk, FunctionChunk
from common.redis import get_redis
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


def _get_summarization_prompt(chunks: list[Union[FunctionChunk, ClassChunk]]) -> tuple[str, str]:
    system = \
'''You are a code summarizer for a retrieval augmented generation (RAG) system. Your task is to analyze each provided code block—which may contain functions, classes, or other programming constructs—and generate a concise yet information-rich summary. Each summary should capture:
- The primary purpose of the code.
- Key functionalities, inputs, and outputs.
- Significant algorithms, design patterns, or data structures used.
- Noteworthy implementation details or constraints.

The code blocks are provided as text with each block delimited by the markers `<|START|>` and `<|END|>`. Use these markers to identify and extract each code block for analysis.

**Important:** Your final output must be a single string containing the summaries for all code blocks separated by the delimiter `<|sep|>`, and no additional text or information.
'''

    chunks = map(lambda chunk: f"<|START|>{chunk.body}<|END|>", chunks)
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

@dataclass
class CodeRecord:
    type: str
    path: str
    name: str
    body: str
    description: str

@dataclass
class QueryResult:
    score: float
    rec: CodeRecord

class CodeDB:
    def __init__(
            self,
            repo: Repository
    ):
        self.redis = get_redis()
        self.repo = repo
        self.embedder = SentenceTransformer("sentence-transformer")
        self.index = None
    
    def exists(self) -> bool:
        try:
            self.redis.ft(self._redis_index_name).info()
            return True
        except:
            return False
    
    def build(self, threads: int = 16):
        self.index = self._build(threads)
    
    def search(self, query: str, n: int = 1) -> list[QueryResult]:
        encoded_query = self._encode([query])[0]
        query = (
            Query(f"(*)=>[KNN {n} @embedding $query_vector AS score]")
                .sort_by("score")
                .return_fields("score", "$.type", "$.path", "$.name", "$.body", "$.description")
                .dialect(2)
        )
        docs = self.index.search(
            query,
            {
                'query_vector': np.array(encoded_query, dtype=np.float32).tobytes()
            }
        ).docs
        
        def doc2qresult(doc) -> QueryResult:
            return QueryResult(
                score=doc.score,
                rec=CodeRecord(
                    type=doc["$.type"],
                    path=doc["$.path"],
                    name=doc["$.name"],
                    body=doc["$.body"],
                    description=doc["$.description"]
                )
            )

        return list(map(doc2qresult, docs))
    
    def _encode(self, s: list[str]) -> list[list[np.float32]]:
        return self.embedder.encode(
            s,
            precision='float32'
        ).astype(np.float32).tolist()
    
    def _build(self, threads: int) -> Search:
        if self.exists():
            index = self.redis.ft(self._redis_index_name)
            print("use existing index")
            return index
        
        print("parsing repository")
        recs = self._extract_records(parse(self.repo))
        splitted_recs = self._split_chunks(recs)

        def generate_descriptions(bodies: list[Union[FunctionChunk, ClassChunk]]):
            system, user = _get_summarization_prompt(bodies)
            llm = _get_llm(system, user)
            result = llm.prompt(system, user)
            result = result.split("<|sep|>")
            return result if len(result) == len(bodies) else [""]*len(bodies)

        print("generate descriptions")
        with ThreadPoolExecutor(max_workers=threads) as executor:
            descriptions = list(executor.map(generate_descriptions, splitted_recs))
        print("encode descriptions")
        descriptions = sum(descriptions, [])
        embeddings = self._encode(descriptions)
        embedding_dim = len(embeddings[0])

        print("push records to redis")
        remains = range(len(recs))
        while len(remains) > 0:
            pipeline = self.redis.pipeline()
            for i in remains:
                key = self._codechunk_key(i)
                recs[i].description = descriptions[i]
                rec = asdict(recs[i])
                rec["embedding"] = embeddings[i]
                pipeline.json().set(key, "$", rec)
            status = pipeline.execute()
            remains = list(map(lambda x: x[0], filter(lambda x: not x[1], enumerate(status))))
        del recs[:]
        del recs
        del descriptions[:]
        del descriptions
        
        print("build index for searching")
        schema = (
            # TextField("$.path", as_name="path", no_stem=True, no_index=True,),
            # TagField("$.type", as_name="type", no_index=True),
            # TextField("$.name", as_name="name", no_stem=True, no_index=True),
            # TextField("$.body", as_name="body", no_stem=True, no_index=True),
            # TextField("$.description", as_name="description", no_stem=True, no_index=True),
            VectorField(
                "$.embedding",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": embedding_dim,
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name="embedding",
            ),
        )
        definition = IndexDefinition(prefix=self._codechunk_prefix, index_type=IndexType.JSON)
        index = self.redis.ft(self._redis_index_name)
        index.create_index(fields=schema, definition=definition)
        self.redis.bgsave()
        print("done")
        return index

    def _extract_records(self, codes: list[CodeChunk]) -> list[CodeRecord]:
        def to_record(path: str, chunk: Union[FunctionChunk, ClassChunk]):
            return CodeRecord(
                "function" if isinstance(chunk, FunctionChunk) else "class",
                path,
                chunk.name,
                chunk.body,
                ""
            )

        chunks = []
        for code in codes:
            path = code.path
            chunks.extend(map(lambda chunk: to_record(path, chunk), code.classes))
            chunks.extend(map(lambda chunk: to_record(path, chunk), code.functions))
        return chunks
    
    def _split_chunks(self, chunks: list[CodeRecord], max_tokens=30*1000) -> list[list[CodeRecord]]:
        r = []
        sub = []
        tokens = 0
        for chunk in chunks:
            cnt = _count_tokens(chunk.body)
            if tokens + cnt > max_tokens:
                r.append(sub)
                sub = [chunk]
                tokens = cnt
                continue
            sub.append(chunk)
            tokens += cnt
        r.append(sub)
        return r 

    @property
    def _redis_prefix(self) -> str:
        return f"codedb:{self.repo.id}:"
    @property
    def _redis_index_name(self) -> str:
        return f"{self._redis_prefix}index"
    @property
    def _codechunk_prefix(self) -> str:
        return f"{self._redis_prefix}codechunk:"
    def _codechunk_key(self, idx: int) -> str:
        return f"{self._codechunk_prefix}{idx}"

