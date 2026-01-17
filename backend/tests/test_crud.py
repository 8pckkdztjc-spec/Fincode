"""
CRUD 操作服务测试
"""

import pytest


def test_document_crud_exists():
    """测试 DocumentCRUD 类存在"""
    from app.services.crud import DocumentCRUD
    assert DocumentCRUD is not None


def test_audit_crud_exists():
    """测试 AuditCRUD 类存在"""
    from app.services.crud import AuditCRUD
    assert AuditCRUD is not None


def test_report_crud_exists():
    """测试 ReportCRUD 类存在"""
    from app.services.crud import ReportCRUD
    assert ReportCRUD is not None


def test_document_crud_methods():
    """测试 DocumentCRUD 方法存在"""
    from app.services.crud import DocumentCRUD
    assert hasattr(DocumentCRUD, 'create')
    assert hasattr(DocumentCRUD, 'get')
    assert hasattr(DocumentCRUD, 'update')
    assert hasattr(DocumentCRUD, 'list')


def test_audit_crud_methods():
    """测试 AuditCRUD 方法存在"""
    from app.services.crud import AuditCRUD
    assert hasattr(AuditCRUD, 'create')
    assert hasattr(AuditCRUD, 'get')
    assert hasattr(AuditCRUD, 'update')
    assert hasattr(AuditCRUD, 'list')


def test_report_crud_methods():
    """测试 ReportCRUD 方法存在"""
    from app.services.crud import ReportCRUD
    assert hasattr(ReportCRUD, 'create')
    assert hasattr(ReportCRUD, 'get')
    assert hasattr(ReportCRUD, 'update')
    assert hasattr(ReportCRUD, 'list')
