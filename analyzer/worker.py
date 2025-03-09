from common.redis import get_redis
from common.analyzer import Analyzer, AnalyzerStatus
from common.query import QueryStatus, QueryResult
from repo import Repository
from codedb import CodeDB
from time import sleep

def main():
    query = None
    try:
        analyzer = Analyzer.from_env()
        analyzer.set_status(AnalyzerStatus.CLONING)
        repo = Repository(analyzer.github_url)

        analyzer.set_status(AnalyzerStatus.PROCESSING)
        # codedb = CodeDB(repo=repo)

        analyzer.set_status(AnalyzerStatus.READY)
        while True:
            query = analyzer.pull_query()
            if query is None:
                sleep(1.0)
                continue
            query.set_status(QueryStatus.PROCESSING)
            result = "TBD"
            result = QueryResult(query.query, result)
            query.set_result(result)

    except Exception as e:
        analyzer.set_status(AnalyzerStatus.ERROR)
        if query is not None:
            query.set_status(QueryStatus.ERROR)
        print(e)
        
if __name__ == "__main__":
    main()
