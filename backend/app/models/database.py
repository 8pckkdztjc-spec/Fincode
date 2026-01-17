"""
SQLAlchemy ORM 数据库模型
定义 Document、Audit 和 Report 表结构
"""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid
import enum


Base = declarative_base()


class TaskStatusEnum(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskSeverityEnum(str, enum.Enum):
    """风险严重程度枚举"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


def generate_uuid():
    """生成 UUID 字符串"""
    return str(uuid.uuid4())


class Document(Base):
    """
    文档表
    存储上传的财务报表文档信息及解析结果
    """
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(512), nullable=False, comment="存储路径")
    document_type = Column(String(50), default="balance_sheet", comment="文档类型")
    period = Column(String(20), nullable=True, comment="报表期间")
    company_name = Column(String(255), nullable=True, comment="公司名称")
    status = Column(String(20), default="pending", comment="处理状态")

    # 财务指标 JSON 存储
    indicators = Column(JSON, nullable=True, comment="财务指标")
    raw_markdown = Column(Text, nullable=True, comment="解析后的Markdown")

    # 校验状态
    balance_check_passed = Column(Integer, default=0, comment="勾稽校验是否通过")
    confidence = Column(String(20), default="medium", comment="置信度")

    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 错误信息
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 关联审计记录
    audits = relationship("Audit", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class Audit(Base):
    """
    审计任务表
    存储审计任务信息及结果
    """
    __tablename__ = "audits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    status = Column(String(20), default="pending", comment="审计状态")
    risk_score = Column(Float, nullable=True, comment="风险评分 0-100")

    # 违规和推理链 JSON 存储
    violations = Column(JSON, default=list, comment="违规列表")
    reasoning_chain = Column(JSON, default=list, comment="推理链")

    # 纠偏次数
    retry_count = Column(Integer, default=0, comment="纠偏重试次数")

    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关联文档
    document = relationship("Document", back_populates="audits")

    # 关联报告
    reports = relationship("Report", back_populates="audit")

    def __repr__(self):
        return f"<Audit(id={self.id}, document_id={self.document_id}, status={self.status})>"


class Report(Base):
    """
    审计报告表
    存储生成的审计报告信息
    """
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False)
    format = Column(String(10), default="pdf", comment="报告格式")
    status = Column(String(20), default="pending", comment="生成状态")
    file_path = Column(String(512), nullable=True, comment="报告文件路径")

    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")

    # 关联审计
    audit = relationship("Audit", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, audit_id={self.audit_id}, format={self.format})>"
