"""
SQLAlchemy ORM 模型测试
测试数据库模型的创建和基本操作
"""

import pytest
from datetime import datetime


def test_document_model_exists():
    """测试 Document 模型存在"""
    from app.models.database import Document
    assert Document is not None


def test_audit_model_exists():
    """测试 Audit 模型存在"""
    from app.models.database import Audit
    assert Audit is not None


def test_report_model_exists():
    """测试 Report 模型存在"""
    from app.models.database import Report
    assert Report is not None


def test_document_model_fields():
    """测试 Document 模型字段"""
    from app.models.database import Document
    doc = Document(
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        status="pending",
        document_type="balance_sheet",
        confidence="medium"
    )
    assert doc.filename == "test.pdf"
    assert doc.file_path == "/uploads/test.pdf"
    assert doc.status == "pending"
    assert doc.document_type == "balance_sheet"
    assert doc.confidence == "medium"


def test_document_model_optional_fields():
    """测试 Document 模型可选字段"""
    from app.models.database import Document
    doc = Document(
        filename="annual_report.pdf",
        file_path="/uploads/annual_report.pdf",
        document_type="income_statement",
        period="2024-Q4",
        company_name="测试公司",
        status="completed"
    )
    assert doc.document_type == "income_statement"
    assert doc.period == "2024-Q4"
    assert doc.company_name == "测试公司"


def test_audit_model_fields():
    """测试 Audit 模型字段"""
    from app.models.database import Audit
    audit = Audit(
        document_id="test-doc-id",
        status="processing",
        retry_count=0
    )
    assert audit.document_id == "test-doc-id"
    assert audit.status == "processing"
    assert audit.retry_count == 0


def test_audit_model_with_risk_score():
    """测试 Audit 模型风险评分字段"""
    from app.models.database import Audit
    audit = Audit(
        document_id="test-doc-id",
        status="completed",
        risk_score=75.5
    )
    assert audit.risk_score == 75.5


def test_report_model_fields():
    """测试 Report 模型字段"""
    from app.models.database import Report
    report = Report(
        audit_id="test-audit-id",
        format="pdf",
        status="pending"
    )
    assert report.audit_id == "test-audit-id"
    assert report.format == "pdf"
    assert report.status == "pending"


def test_task_status_enum():
    """测试任务状态枚举"""
    from app.models.database import TaskStatusEnum
    assert TaskStatusEnum.PENDING == "pending"
    assert TaskStatusEnum.PROCESSING == "processing"
    assert TaskStatusEnum.COMPLETED == "completed"
    assert TaskStatusEnum.FAILED == "failed"


def test_risk_severity_enum():
    """测试风险严重程度枚举"""
    from app.models.database import RiskSeverityEnum
    assert RiskSeverityEnum.CRITICAL == "critical"
    assert RiskSeverityEnum.WARNING == "warning"
    assert RiskSeverityEnum.INFO == "info"


def test_generate_uuid_function():
    """测试 UUID 生成函数"""
    from app.models.database import generate_uuid
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()
    assert uuid1 is not None
    assert uuid2 is not None
    assert uuid1 != uuid2  # 每次生成不同的 UUID
    assert len(uuid1) == 36  # UUID 格式长度


def test_base_declarative_exists():
    """测试 Base 声明基类存在"""
    from app.models.database import Base
    assert Base is not None


def test_document_table_name():
    """测试 Document 表名"""
    from app.models.database import Document
    assert Document.__tablename__ == "documents"


def test_audit_table_name():
    """测试 Audit 表名"""
    from app.models.database import Audit
    assert Audit.__tablename__ == "audits"


def test_report_table_name():
    """测试 Report 表名"""
    from app.models.database import Report
    assert Report.__tablename__ == "reports"


def test_document_column_defaults():
    """测试 Document 列默认值配置"""
    from app.models.database import Document
    # 验证列定义中包含正确的默认值
    columns = {c.name: c for c in Document.__table__.columns}

    assert columns["document_type"].default.arg == "balance_sheet"
    assert columns["status"].default.arg == "pending"
    assert columns["confidence"].default.arg == "medium"
    assert columns["balance_check_passed"].default.arg == 0


def test_audit_column_defaults():
    """测试 Audit 列默认值配置"""
    from app.models.database import Audit
    columns = {c.name: c for c in Audit.__table__.columns}

    assert columns["status"].default.arg == "pending"
    assert columns["retry_count"].default.arg == 0


def test_report_column_defaults():
    """测试 Report 列默认值配置"""
    from app.models.database import Report
    columns = {c.name: c for c in Report.__table__.columns}

    assert columns["format"].default.arg == "pdf"
    assert columns["status"].default.arg == "pending"


def test_document_repr():
    """测试 Document __repr__ 方法"""
    from app.models.database import Document
    doc = Document(
        id="test-id",
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        status="pending"
    )
    repr_str = repr(doc)
    assert "Document" in repr_str
    assert "test-id" in repr_str
    assert "test.pdf" in repr_str


def test_audit_repr():
    """测试 Audit __repr__ 方法"""
    from app.models.database import Audit
    audit = Audit(
        id="audit-id",
        document_id="doc-id",
        status="processing"
    )
    repr_str = repr(audit)
    assert "Audit" in repr_str
    assert "audit-id" in repr_str
    assert "doc-id" in repr_str


def test_report_repr():
    """测试 Report __repr__ 方法"""
    from app.models.database import Report
    report = Report(
        id="report-id",
        audit_id="audit-id",
        format="pdf"
    )
    repr_str = repr(report)
    assert "Report" in repr_str
    assert "report-id" in repr_str
    assert "pdf" in repr_str
