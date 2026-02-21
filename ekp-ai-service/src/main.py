from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import documents, qa, health, agent
from src.config import settings

app = FastAPI(
    title="EKP AI Service",
    description="Enterprise Knowledge Platform - AI Service for RAG-based Q&A",
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
app.include_router(agent.router, prefix="/api/v1", tags=["Agent"])


@app.on_event("startup")
async def startup_event():
    print("EKP AI Service 启动中...")
    print(f"本地 LLM URL: {settings.local_llm_url}")
    print(f"模型: {settings.llm_model}")
    print("EKP AI Service 启动完成！")


@app.on_event("shutdown")
async def shutdown_event():
    print("EKP AI Service 关闭中...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
