"""
FinCode 配置管理模块
基于 pydantic-settings 管理应用配置
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "FinCode API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # 推理引擎配置
    INFERENCE_MODE: str = "api"  # api / local
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    LOCAL_MODEL_PATH: str = ""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./fincode.db"
    
    # 文件存储配置
    UPLOAD_DIR: Path = Path("./uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".xlsx", ".xls"}
    
    # 审计配置
    MAX_RETRY_COUNT: int = 3  # 最大纠偏重试次数
    BALANCE_TOLERANCE: float = 0.01  # 勾稽校验容差
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()

# 确保上传目录存在
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
