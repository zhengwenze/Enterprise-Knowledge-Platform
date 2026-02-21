from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EKP AI Service"
    app_version: str = "0.2.0"
    debug: bool = True

    database_url: str = "postgresql://ekp_user:ekp_password@localhost:5432/ekp_db"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    use_local_llm: bool = True
    local_llm_url: str = "http://host.docker.internal:11434"
    local_llm_model: str = "qwen2.5:7b"

    openai_api_key: str = ""
    openai_base_url: str = ""

    llm_model: str = "qwen2.5:7b"
    vision_model: str = "llava:7b"
    embedding_model: str = "BAAI/bge-large-zh"
    embedding_dimension: int = 1024

    rag_working_dir: str = "./rag_storage"
    rag_parser: str = "mineru"
    rag_parse_method: str = "auto"
    enable_image_processing: bool = True
    enable_table_processing: bool = True
    enable_equation_processing: bool = True

    chunk_size: int = 1000
    chunk_overlap: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
