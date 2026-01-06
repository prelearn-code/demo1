"""
全局配置管理
使用 Pydantic Settings 从环境变量加载配置
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # Ollama 配置
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama 服务地址"
    )
    ollama_model: str = Field(
        default="qwen2.5-coder:7b",
        description="使用的模型名称"
    )

    # Agent 配置
    max_iterations: int = Field(
        default=5,
        description="最大迭代次数(防止死循环)"
    )
    temperature: float = Field(
        default=0.0,
        description="生成温度,0表示确定性输出"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
