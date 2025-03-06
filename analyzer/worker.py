from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus
from common.analyzer_result import AnalyzerResult
from repo import Repository
from prompt import Prompter

def main():
    redis = Redis()
    analyzer = Analyzer.from_env(redis)

    try:
        analyzer.set_status(AnalyzerStatus.CLONING)
        repo = Repository(analyzer.github_url)

        analyzer.set_status(AnalyzerStatus.PROCESSING)
        prompter = Prompter(repo)

        analyzer.set_status(AnalyzerStatus.READY)

        result = AnalyzerResult(
            repo_metadata=prompter.repo_metadata
        )
        analyzer.set_result(result)
        analyzer.set_status(AnalyzerStatus.DONE)
    except:
        analyzer.set_status(AnalyzerStatus.ERROR)
        
if __name__ == "__main__":
    main()
