"""
FinCode FastAPI Application Entry Point
神经符号协同财务审计助手 - 应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, qa, report
from app.core.database import engine
from app.models.database import Base

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="FinCode API",
    description="神经符号协同财务审计助手 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(audit.router, prefix="/api/v1/audit", tags=["审计"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["问答"])
app.include_router(report.router, prefix="/api/v1/report", tags=["报告"])


@app.get("/", tags=["健康检查"])
async def root():
    """根路径健康检查"""
    return {
        "status": "ok",
        "service": "FinCode API",
        "version": "0.1.0",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
