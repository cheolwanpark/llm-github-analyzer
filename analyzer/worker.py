from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus
from common.query import QueryStatus, QueryResult
from repo import Repository
from prompt import Prompter
from llm import LLM
from time import sleep
import os

def main():
    query = None
    api_key = os.environ.get("LLM_API_KEY", "API_KEY")
    try:
        redis = Redis()
        analyzer = Analyzer.from_env(redis)
        analyzer.set_status(AnalyzerStatus.CLONING)
        repo = Repository(analyzer.github_url)

        analyzer.set_status(AnalyzerStatus.PROCESSING)
        prompter = Prompter(repo, llm=LLM(api_key=api_key))

        analyzer.set_status(AnalyzerStatus.READY)
        while True:
            query = analyzer.pull_query()
            if query is None:
                sleep(1.0)
                continue
            query.set_status(QueryStatus.PROCESSING)
            result = prompter.prompt(query)
            result = QueryResult(query.query, result)
            query.set_result(result)

    except Exception as e:
        analyzer.set_status(AnalyzerStatus.ERROR)
        if query is not None:
            query.set_status(QueryStatus.ERROR)
        print(e)
        
if __name__ == "__main__":
    main()
