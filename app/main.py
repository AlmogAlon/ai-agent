import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import run_agent
from app.memory import get_history

app = FastAPI(title="Simple Tool-Calling Agent")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    response = run_agent(session_id, request.message)
    return ChatResponse(session_id=session_id, response=response)


@app.get("/history/{session_id}")
def history(session_id: str):
    return {"session_id": session_id, "history": get_history(session_id)}
