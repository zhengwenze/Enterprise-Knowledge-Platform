from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EKP AI Service"
    app_version: str = "0.2.0"
    debug: bool = True

    database_url: str = "postgresql://ekp_user:ekp_password@localhost:5432/ekp_db"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    # LLM 模式选择
    use_local_llm: bool = True  # True = 使用本地模型，False = 使用 OpenAI API

    # 本地 LLM 配置（Ollama）
    local_llm_url: str = "http://localhost:11434"
    local_llm_model: str = "qwen2.5:7b"  # 或 llama3.1, chatglm3 等

    # OpenAI API 配置（可选）
    openai_api_key: str = ""
    openai_base_url: str = ""

    # 模型配置
    llm_model: str = "qwen2.5:7b"  # 本地模型名或 gpt-4o-mini
    vision_model: str = "llava:7b"  # 本地视觉模型或 gpt-4o
    embedding_model: str = "BAAI/bge-large-zh"  # 本地嵌入模型
    embedding_dimension: int = 1024  # bge-large-zh 维度

    # RAG-Anything 配置
    rag_working_dir: str = "./rag_storage"
    rag_parser: str = "mineru"
    rag_parse_method: str = "auto"
    enable_image_processing: bool = True
    enable_table_processing: bool = True
    enable_equation_processing: bool = True

    # 文档处理配置
    chunk_size: int = 1000
    chunk_overlap: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
