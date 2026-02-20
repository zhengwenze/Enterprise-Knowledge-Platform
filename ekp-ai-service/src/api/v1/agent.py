from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import asyncio

from src.database import get_db
from src.agents.react_agent import ReActAgent
from src.agents.tools import (
    DocumentSearchTool,
    DocumentUploadTool,
    DocumentListTool,
    CalculatorTool,
    CurrentTimeTool,
)

router = APIRouter(prefix="/agent", tags=["agent"])

_agents: Dict[str, ReActAgent] = {}


class AgentQueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    stream: bool = False


class AgentQueryResponse(BaseModel):
    answer: str
    steps: List[Dict[str, Any]]
    tools_used: List[str]
    session_id: str


class AgentSessionResponse(BaseModel):
    session_id: str
    history: List[Dict[str, str]]


class AgentClearRequest(BaseModel):
    session_id: str = "default"


def get_agent(session_id: str, db: Session) -> ReActAgent:
    if session_id not in _agents:
        tools = [
            DocumentSearchTool(),
            DocumentUploadTool(),
            DocumentListTool(db),
            CalculatorTool(),
            CurrentTimeTool(),
        ]
        _agents[session_id] = ReActAgent(tools=tools, db_session=db)
    return _agents[session_id]


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(
    request: AgentQueryRequest,
    db: Session = Depends(get_db),
):
    agent = get_agent(request.session_id, db)

    try:
        result = await agent.run(request.question)

        return AgentQueryResponse(
            answer=result["answer"],
            steps=result["steps"],
            tools_used=result["tools_used"],
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_agent_stream(
    request: AgentQueryRequest,
    db: Session = Depends(get_db),
):
    agent = get_agent(request.session_id, db)

    async def generate():
        try:
            result = await agent.run(request.question)

            for step in result["steps"]:
                yield f"data: {json.dumps({'type': 'step', 'data': step}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: {json.dumps({'type': 'answer', 'data': result['answer']}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/session/{session_id}", response_model=AgentSessionResponse)
async def get_session(session_id: str):
    if session_id not in _agents:
        return AgentSessionResponse(session_id=session_id, history=[])

    agent = _agents[session_id]
    return AgentSessionResponse(
        session_id=session_id,
        history=agent.get_history(),
    )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in _agents:
        _agents[session_id].clear_history()
        del _agents[session_id]
    return {"message": "Session cleared", "session_id": session_id}


@router.get("/tools")
async def list_tools():
    from src.agents.tools import (
        DocumentSearchTool,
        DocumentUploadTool,
        DocumentListTool,
        CalculatorTool,
        CurrentTimeTool,
    )

    tools = [
        DocumentSearchTool(),
        DocumentUploadTool(),
        CalculatorTool(),
        CurrentTimeTool(),
    ]

    return {"tools": [tool.get_schema() for tool in tools]}
