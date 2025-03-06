from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse, Response
from common.redis import Redis
from common.analyzer import Analyzer, AnalyzerStatus, Query, QueryStatus
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

@app.get("/analyzer/{analyzer_id}")
def progress(analyzer_id: str):
    analyzer = Analyzer.from_id(redis, analyzer_id)
    if not analyzer.exists():
        raise HTTPException(status_code=404, detail="Analyzer not found")
    status = analyzer.get_status()
    return JSONResponse({
        "analyzer_id": analyzer_id,
        "progress": status.value
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
        return Response(status_code=204)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to delete Analyzer")
    

class CreateQueryDTO(BaseModel):
    analyzer_id: str
    query: str

@app.post("/query")
def create_query(dto: CreateQueryDTO = Body(description="User Query")):
    analyzer = Analyzer.from_id(redis, dto.analyzer_id)
    if not analyzer.exists():
        raise HTTPException(status_code=404, detail="Analyzer not found")
    if analyzer.get_status() != AnalyzerStatus.READY:
        raise HTTPException(status_code=400, detail="Analyzer is not Ready")
    query = Query.from_query(dto.query)
    analyzer.push_query(query)
    return JSONResponse({"query_id": query.id}, status_code=201)

@app.get("/query/{query_id}")
def progress(query_id: str):
    query = Query.from_id(query_id)
    if not query.exists():
        raise HTTPException(status_code=404, detail="Query not found")
    status = query.get_status()
    content = {
        "query_id": query.id,
        "progress": status.value
    }
    if status == QueryStatus.DONE:
        result = query.get_result()
        content["result"] = result.to_dict()
    return JSONResponse(content, status_code=200)


