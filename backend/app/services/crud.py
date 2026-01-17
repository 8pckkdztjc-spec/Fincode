"""
CRUD 操作服务
提供 Document、Audit、Report 的数据库操作
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import Document, Audit, Report


class DocumentCRUD:
    """文档 CRUD 操作"""

    @staticmethod
    def create(db: Session, document_id: str, filename: str, file_path: str) -> Document:
        """创建文档记录"""
        doc = Document(
            id=document_id,
            filename=filename,
            file_path=file_path,
            status="pending"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get(db: Session, document_id: str) -> Optional[Document]:
        """获取单个文档"""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def update(db: Session, document_id: str, **kwargs) -> Optional[Document]:
        """更新文档"""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            for key, value in kwargs.items():
                if hasattr(doc, key):
                    setattr(doc, key, value)
            doc.updated_at = datetime.now()
            db.commit()
            db.refresh(doc)
        return doc

    @staticmethod
    def list(db: Session, limit: int = 10, offset: int = 0) -> List[Document]:
        """获取文档列表"""
        return db.query(Document).order_by(Document.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取文档总数"""
        return db.query(Document).count()


class AuditCRUD:
    """审计任务 CRUD 操作"""

    @staticmethod
    def create(db: Session, audit_id: str, document_id: str) -> Audit:
        """创建审计记录"""
        audit = Audit(
            id=audit_id,
            document_id=document_id,
            status="pending"
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def get(db: Session, audit_id: str) -> Optional[Audit]:
        """获取单个审计任务"""
        return db.query(Audit).filter(Audit.id == audit_id).first()

    @staticmethod
    def update(db: Session, audit_id: str, **kwargs) -> Optional[Audit]:
        """更新审计任务"""
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if audit:
            for key, value in kwargs.items():
                if hasattr(audit, key):
                    setattr(audit, key, value)
            db.commit()
            db.refresh(audit)
        return audit

    @staticmethod
    def list(db: Session, limit: int = 10, offset: int = 0) -> List[Audit]:
        """获取审计任务列表"""
        return db.query(Audit).order_by(Audit.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def count(db: Session) -> int:
        """获取审计任务总数"""
        return db.query(Audit).count()


class ReportCRUD:
    """报告 CRUD 操作"""

    @staticmethod
    def create(db: Session, report_id: str, audit_id: str, format: str = "pdf") -> Report:
        """创建报告记录"""
        report = Report(
            id=report_id,
            audit_id=audit_id,
            format=format,
            status="pending"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get(db: Session, report_id: str) -> Optional[Report]:
        """获取单个报告"""
        return db.query(Report).filter(Report.id == report_id).first()

    @staticmethod
    def update(db: Session, report_id: str, **kwargs) -> Optional[Report]:
        """更新报告"""
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            for key, value in kwargs.items():
                if hasattr(report, key):
                    setattr(report, key, value)
            db.commit()
            db.refresh(report)
        return report

    @staticmethod
    def list(db: Session, limit: int = 10, offset: int = 0) -> List[Report]:
        """获取报告列表"""
        return db.query(Report).order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
