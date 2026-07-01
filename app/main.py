from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import os

from app.rag_service import answer_question

app = FastAPI(title="就業規則RAGチャットボット")

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

class SourceInfo(BaseModel):
    source_file: str
    article_no: str | None = None
    article_title: str | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = answer_question(request.question)
        return ChatResponse(
            answer=result["answer"],
            sources=[SourceInfo(**s) for s in result["sources"]]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, encoding="utf-8") as f:
        return f.read()