"""
数据库连接配置
提供 SQLAlchemy 引擎和会话工厂
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


# 根据数据库类型配置引擎参数
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite 不支持连接池参数
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite 需要此配置
        echo=settings.DEBUG  # 开发模式下打印 SQL
    )
else:
    # PostgreSQL 等数据库使用连接池
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # 连接健康检查
        pool_size=5,
        max_overflow=10,
        echo=settings.DEBUG  # 开发模式下打印 SQL
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    获取数据库会话的依赖注入函数

    用法:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
