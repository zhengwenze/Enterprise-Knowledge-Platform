from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import asyncio

from src.database import get_db
from src.redis_client import get_redis
from src.agents.react_agent import ReActAgent
from src.agents.tools import (
    DocumentSearchTool,
    DocumentUploadTool,
    DocumentListTool,
    CalculatorTool,
    CurrentTimeTool,
)
from src.services.memory_service import WorkingMemoryService
from src.services.cache_service import QACacheService

router = APIRouter(prefix="/agent", tags=["agent"])

_agents: Dict[str, ReActAgent] = {}


class AgentQueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    stream: bool = False
    use_cache: bool = True


class AgentQueryResponse(BaseModel):
    answer: str
    steps: List[Dict[str, Any]]
    tools_used: List[str]
    session_id: str
    cached: bool = False


class AgentSessionResponse(BaseModel):
    session_id: str
    history: List[Dict[str, str]]


class AgentClearRequest(BaseModel):
    session_id: str = "default"


class HotQuestionsResponse(BaseModel):
    questions: List[Dict[str, Any]]


async def get_agent_with_memory(
    session_id: str,
    db: Session,
    redis,
) -> ReActAgent:
    if session_id not in _agents:
        tools = [
            DocumentSearchTool(),
            DocumentUploadTool(),
            DocumentListTool(db),
            CalculatorTool(),
            CurrentTimeTool(),
        ]
        _agents[session_id] = ReActAgent(tools=tools, db_session=db)
        
        memory_service = WorkingMemoryService(redis)
        history = await memory_service.get_messages(session_id)
        _agents[session_id].conversation_history = history
    
    return _agents[session_id]


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(
    request: AgentQueryRequest,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
):
    cache_service = QACacheService(redis)
    
    if request.use_cache:
        cached = await cache_service.get_cached_answer(request.question)
        if cached:
            return AgentQueryResponse(
                answer=cached["answer"],
                steps=[],
                tools_used=[],
                session_id=request.session_id,
                cached=True,
            )

    agent = await get_agent_with_memory(request.session_id, db, redis)
    memory_service = WorkingMemoryService(redis)

    try:
        await memory_service.add_message(
            session_id=request.session_id,
            role="user",
            content=request.question,
        )
        
        result = await agent.run(request.question)
        
        await memory_service.add_message(
            session_id=request.session_id,
            role="assistant",
            content=result["answer"],
            metadata={"tools_used": result["tools_used"]},
        )
        
        await cache_service.cache_answer(
            question=request.question,
            answer=result["answer"],
            sources=[],
        )
        
        await cache_service.add_to_hot_questions(
            question=request.question,
            answer=result["answer"],
        )

        return AgentQueryResponse(
            answer=result["answer"],
            steps=result["steps"],
            tools_used=result["tools_used"],
            session_id=request.session_id,
            cached=False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def query_agent_stream(
    request: AgentQueryRequest,
    db: Session = Depends(get_db),
    redis = Depends(get_redis),
):
    agent = await get_agent_with_memory(request.session_id, db, redis)
    memory_service = WorkingMemoryService(redis)

    async def generate():
        try:
            await memory_service.add_message(
                session_id=request.session_id,
                role="user",
                content=request.question,
            )
            
            result = await agent.run(request.question)

            for step in result["steps"]:
                yield f"data: {json.dumps({'type': 'step', 'data': step}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: {json.dumps({'type': 'answer', 'data': result['answer']}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
            await memory_service.add_message(
                session_id=request.session_id,
                role="assistant",
                content=result["answer"],
                metadata={"tools_used": result["tools_used"]},
            )

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/session/{session_id}", response_model=AgentSessionResponse)
async def get_session(
    session_id: str,
    redis = Depends(get_redis),
):
    memory_service = WorkingMemoryService(redis)
    history = await memory_service.get_all_messages(session_id)
    
    formatted_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]
    
    return AgentSessionResponse(
        session_id=session_id,
        history=formatted_history,
    )


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    redis = Depends(get_redis),
):
    memory_service = WorkingMemoryService(redis)
    await memory_service.clear_session(session_id)
    
    if session_id in _agents:
        _agents[session_id].clear_history()
        del _agents[session_id]
    
    return {"message": "Session cleared", "session_id": session_id}


@router.get("/tools")
async def list_tools():
    from src.agents.tools import (
        DocumentSearchTool,
        DocumentUploadTool,
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


@router.get("/hot-questions", response_model=HotQuestionsResponse)
async def get_hot_questions(
    limit: int = 10,
    redis = Depends(get_redis),
):
    cache_service = QACacheService(redis)
    questions = await cache_service.get_hot_questions(limit)
    
    return HotQuestionsResponse(questions=questions)


@router.get("/stats/{question}")
async def get_question_stats(
    question: str,
    redis = Depends(get_redis),
):
    cache_service = QACacheService(redis)
    count = await cache_service.get_question_stats(question)
    
    return {"question": question, "hit_count": count}
