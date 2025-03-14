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
    query = Query("testquery", \
'''You are an expert project assistant. Your task is to create a comprehensive, well-formatted onboarding guide for a new project collaborator using our project's code repository as reference. Use the repository’s documentation, commit history, and code structure details to generate a markdown document that includes:\n
1. Project Overview: A brief introduction including the project’s goals, scope, and context.
2. Important Function and Classes to look first
Ensure that the output is formatted in markdown with clear headers, bullet lists, and code blocks where appropriate. Use the retrieval capabilities to extract current and relevant details from the repository, ensuring the information is accurate and helpful for a newcomer.'
''')
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
    main()
    # main_test()
