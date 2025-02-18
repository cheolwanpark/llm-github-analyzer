from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus

def main():
    redis = Redis()
    analyzer = Analyzer.from_env(redis)
    analyzer.set_status(AnalyzerStatus.PROCESSING)
    analyzer.set_status(AnalyzerStatus.DONE)
        
if __name__ == "__main__":
    main()
