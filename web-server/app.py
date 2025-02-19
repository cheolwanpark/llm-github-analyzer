from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus
from urllib.parse import unquote
from pydantic import BaseModel

app = FastAPI()
redis = Redis()

class CreateAnalyzerDTO(BaseModel):
    github_url: str

@app.post("/analyzer")
def create_analyze(dto: CreateAnalyzerDTO = Body(description="GitHub repository URL to analyze")):
    analyzer = Analyzer.new(redis, unquote(dto.github_url))
    analyzer.set_status(AnalyzerStatus.REQUESTED)
    analyzer.spawn_container()
    analyzer.set_status(AnalyzerStatus.SPAWNED)
    return JSONResponse({"analyzer_id": analyzer.id}, status_code=201)

@app.get("/analyzer/progress/{analyzer_id}")
def progress(analyzer_id: str):
    analyzer = Analyzer.from_id(redis, analyzer_id)
    if not analyzer.exists():
        raise HTTPException(status_code=404, detail="Analyzer not found")
    status = analyzer.get_status()
    return JSONResponse({
        "analyzer_id": analyzer_id,
        "progress": status.value
    }, status_code=200)

@app.get("/analyzer/result/{analyzer_id}")
def result(analyzer_id: str):
    analyzer = Analyzer.from_id(redis, analyzer_id)
    if not analyzer.exists():
        raise HTTPException(status_code=404, detail="Analyzer not found")
    result = analyzer.get_result()
    return JSONResponse({
        "analyzer_id": analyzer_id,
        "result": result.to_dict()
    }, status_code=200)

@app.delete("/analyzer/{analyzer_id}")
def delete_analyzer(analyzer_id: str):
    analyzer = Analyzer.from_id(redis, analyzer_id)
    if not analyzer.exists():
        raise HTTPException(status_code=404, detail="Analyzer not found")
    try:
        analyzer.delete()
        if analyzer.exists():
            raise "failed to delete"
        return JSONResponse({}, status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete Analyzer")


