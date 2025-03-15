from common.query import Query, QueryResult
from repo import Repository
from codedb import CodeDB
from agent import Agent
    
if __name__ == "__main__":
    github_url = "https://github.com/deepseek-ai/DeepSeek-V3"
    query = Query("testquery", \
'''Generate onboarding guide for the project. Include following components
1. Which technologies are used? only important components, avoid including common ones such as standard libraries.
2. Explanation of Project Directory structure.
3. Import Functions and Classes
4. How to get start.
''')
    repo = Repository(github_url)
    codedb = CodeDB(repo=repo)
    agent = Agent(codedb)

    if not codedb.exists():
        repo.clone()
    codedb.build(threads=8)
    
    result = agent.answer(query)
    print("\nanswer:")
    print(result["answer"])
    print("\n\n")

    result = QueryResult(query.query, result)
    print(result.to_json(indent=2))