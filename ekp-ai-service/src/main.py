from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import documents, qa, health
from src.config import settings
from src.services.rag_anything_service import rag_anything_service

app = FastAPI(
    title="EKP AI Service",
    description="Enterprise Knowledge Platform - AI Service for RAG-based Q&A with RAG-Anything",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["Q&A"])


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    print("正在初始化应用...")
    
    print("初始化 RAG-Anything 服务...")
    try:
        await rag_anything_service.initialize()
        print("RAG-Anything 服务初始化完成！")
    except Exception as e:
        print(f"RAG-Anything 服务初始化失败: {e}")
        print("将在首次使用时初始化...")
    
    print("应用初始化完成！")


@app.on_event("shutdown")
async def shutdown_event():
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
