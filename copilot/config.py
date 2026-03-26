from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    #llm_model: str = "qwen/qwen3.5-122b-a10b"
    llm_model: str = "meta/llama-3.1-8b-instruct"
    embed_model: str = "nvidia/llama-nemotron-embed-1b-v2"

    corpus_dir: str = "corpus"
    index_dir: str = "outputs/index"
    logs_dir: str = "outputs/logs"
    runs_dir: str = "outputs/runs"

    chunk_size: int = 50
    chunk_overlap: int = 10
    top_k: int = 5
    max_react_steps: int = 8

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()