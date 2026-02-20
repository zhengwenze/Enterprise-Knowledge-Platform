from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EKP AI Service"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = "postgresql://ekp_user:ekp_password@localhost:5432/ekp_db"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    openai_api_key: str = ""
    embedding_model: str = "BAAI/bge-large-zh"
    embedding_dimension: int = 1024

    chunk_size: int = 1000
    chunk_overlap: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
