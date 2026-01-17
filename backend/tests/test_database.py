"""
数据库连接测试
"""

import pytest


def test_database_engine_exists():
    """测试数据库引擎存在"""
    from app.core.database import engine
    assert engine is not None


def test_session_local_exists():
    """测试会话工厂存在"""
    from app.core.database import SessionLocal
    assert SessionLocal is not None


def test_get_db_generator():
    """测试 get_db 生成器"""
    from app.core.database import get_db
    gen = get_db()
    db = next(gen)
    assert db is not None
    try:
        next(gen)
    except StopIteration:
        pass  # 预期行为
