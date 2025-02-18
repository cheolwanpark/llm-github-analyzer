from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus
from urllib.parse import unquote

app = FastAPI()
redis = Redis()

@app.get("/analyze")
def analyze(github_url: str = Query(description="GitHub repository URL to analyze")):
    analyzer = Analyzer.new(redis, unquote(github_url))
    analyzer.set_status(AnalyzerStatus.REQUESTED)
    analyzer.spawn_container()
    analyzer.set_status(AnalyzerStatus.SPAWNED)
    return JSONResponse({"analysis_id": analyzer.id})

@app.get("/progress/{request_id}")
def progress(request_id: str):
    analyzer = Analyzer.from_id(redis, request_id)
    status = analyzer.get_status()
    if status is None:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return JSONResponse({"request_id": request_id, "progress": status.value})
