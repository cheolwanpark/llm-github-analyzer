from common.redis import get_redis
from common.analyzer import Analyzer, AnalyzerStatus
from common.query import QueryStatus, QueryResult
from repo import Repository
from codedb import CodeDB
from agent import Agent
from time import sleep

def main():
    query = None
    try:
        analyzer = Analyzer.from_env()
        repo = Repository(analyzer.github_url)
        codedb = CodeDB(repo=repo)
        agent = Agent(codedb)

        if not codedb.exists():
            analyzer.set_status(AnalyzerStatus.CLONING)
            repo.clone()

        analyzer.set_status(AnalyzerStatus.PROCESSING)
        codedb.build()

        analyzer.set_status(AnalyzerStatus.READY)
        while True:
            query = analyzer.pull_query()
            if query is None:
                sleep(1.0)
                continue
            result = agent.answer(query)
            result = QueryResult(query.query, result)
            query.set_result(result)

    except Exception as e:
        analyzer.set_status(AnalyzerStatus.ERROR)
        if query is not None:
            query.set_status(QueryStatus.ERROR)
        raise e

def main_test():
    from common.query import Query
    github_url = "https://github.com/cheolwanpark/llm-github-analyzer"
    query = Query("testquery", "Where should I start reading code?")
    repo = Repository(github_url)
    codedb = CodeDB(repo=repo)
    agent = Agent(codedb)

    if not codedb.exists():
        repo.clone()
    codedb.build()
    
    result = agent.answer(query)
    print("\nanswer:")
    print(result["answers"][0])
    print("\n\n")
    
    result = QueryResult(query.query, result)
    print(result.to_json(indent=2))
    

        
if __name__ == "__main__":
    # main()
    main_test()
