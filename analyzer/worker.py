from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus
from common.analyzer_result import AnalyzerResult
from repo import Repository

def main():
    redis = Redis()
    analyzer = Analyzer.from_env(redis)

    analyzer.set_status(AnalyzerStatus.CLONING)
    repo = Repository(analyzer.github_url)

    analyzer.set_status(AnalyzerStatus.PROCESSING)
    paths = repo.paths
    tree = repo.root.to_dict()
    result = AnalyzerResult(paths, tree)

    analyzer.set_result(result)
    analyzer.set_status(AnalyzerStatus.DONE)
        
if __name__ == "__main__":
    main()
