"""
审计相关 API 接口
实现文件上传、审计启动和结果查询
使用 SQLAlchemy 数据库持久化
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pathlib import Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from app.models.schemas import (
    DocumentUploadResponse,
    AuditStartRequest,
    AuditResult,
    TaskStatus,
    ValidationViolation,
    RiskSeverity
)
from app.services.storage import file_storage
from app.services.crud import DocumentCRUD, AuditCRUD
from app.core.config import settings
from app.core.database import get_db

router = APIRouter()


async def parse_document_async(document_id: str, file_path: Path):
    """
    后台异步解析文档任务

    注意: BackgroundTask 无法直接使用依赖注入的 db session，需要创建新的 session
    """
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        # 更新状态为处理中
        DocumentCRUD.update(db, document_id, status="processing")

        # TODO: 集成 Docling 解析
        # from app.services.document import document_parser
        # parsed_data = await document_parser.parse(file_path)

        # 模拟解析完成
        DocumentCRUD.update(db, document_id, status="completed")

    except Exception as e:
        DocumentCRUD.update(db, document_id, status="failed", error_message=str(e))
    finally:
        db.close()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    上传财务报表文档

    支持 PDF 和 Excel 格式
    使用 UUID + MD5 统一文件命名
    后台异步解析文档
    """
    # 验证文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 验证文件扩展名
    if not file_storage.validate_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，仅支持: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 验证文件大小（需要先读取）
    content = await file.read()
    if not file_storage.validate_size(len(content)):
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大允许 {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # 重置文件指针
    await file.seek(0)

    # 保存文件
    try:
        document_id, storage_path = await file_storage.save_upload(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # 创建数据库记录
    DocumentCRUD.create(db, document_id, file.filename, str(storage_path))

    # 添加后台解析任务
    if background_tasks:
        background_tasks.add_task(parse_document_async, document_id, storage_path)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status=TaskStatus.PENDING,
        message="文档上传成功，正在后台解析"
    )


@router.get("/document/{document_id}")
async def get_document_status(document_id: str, db: Session = Depends(get_db)):
    """
    获取文档解析状态
    """
    doc = DocumentCRUD.get(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "file_path": doc.file_path,
        "created_at": doc.created_at
    }


@router.post("/start", response_model=AuditResult)
async def start_audit(
    request: AuditStartRequest,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    启动审计流程

    触发神经-符号双引擎协同审计
    """
    # 验证文档是否存在
    doc = DocumentCRUD.get(db, request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 验证文档是否已解析完成
    if doc.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"文档尚未解析完成，当前状态: {doc.status}"
        )

    # 创建审计任务
    audit_id = str(uuid.uuid4())
    AuditCRUD.create(db, audit_id, request.document_id)
    AuditCRUD.update(db, audit_id, status="processing")

    audit = AuditCRUD.get(db, audit_id)

    # TODO: 添加后台审计任务
    # background_tasks.add_task(run_audit_async, audit_id, request.document_id)

    return AuditResult(
        audit_id=audit.id,
        document_id=audit.document_id,
        status=TaskStatus.PROCESSING,
        risk_score=None
    )


@router.get("/result/{audit_id}", response_model=AuditResult)
async def get_audit_result(audit_id: str, db: Session = Depends(get_db)):
    """
    获取审计结果

    返回完整的审计报告，包括风险评分和推理链
    """
    audit = AuditCRUD.get(db, audit_id)

    if not audit:
        # 返回模拟数据用于开发测试
        return AuditResult(
            audit_id=audit_id,
            document_id="demo_doc",
            status=TaskStatus.COMPLETED,
            risk_score=72.0,
            violations=[
                ValidationViolation(
                    rule_id="R001",
                    rule_name="资产负债表勾稽平衡",
                    severity=RiskSeverity.CRITICAL,
                    expected="资产总计 = 负债总计 + 权益总计",
                    actual="500万 ≠ 495万",
                    correction_hint="请核验数据提取是否准确"
                ),
                ValidationViolation(
                    rule_id="R012",
                    rule_name="应收账款周转异常",
                    severity=RiskSeverity.WARNING,
                    expected="周转率 > 行业均值",
                    actual="周转率 = 2.3 (行业均值 = 5.0)",
                    correction_hint="建议核查应收账款账龄分布"
                )
            ],
            reasoning_chain=[
                "步骤 1: 从资产负债表中提取关键财务指标",
                "步骤 2: 执行勾稽平衡检验 (资产 = 负债 + 权益)",
                "步骤 3: 计算应收账款周转率并与行业基准对比",
                "步骤 4: 符号引擎校验发现 R001 规则违规",
                "步骤 5: 生成风险评分和审计建议"
            ],
            retry_count=0
        )

    # 从数据库记录构建返回值
    return AuditResult(
        audit_id=audit.id,
        document_id=audit.document_id,
        status=TaskStatus(audit.status),
        risk_score=audit.risk_score,
        violations=audit.violations or [],
        reasoning_chain=audit.reasoning_chain or [],
        retry_count=audit.retry_count
    )


@router.get("/list")
async def list_audits(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    """
    获取审计任务列表
    """
    audits = AuditCRUD.list(db, limit, offset)
    total = AuditCRUD.count(db)
    return {
        "total": total,
        "items": [
            {
                "audit_id": a.id,
                "document_id": a.document_id,
                "status": a.status,
                "risk_score": a.risk_score,
                "created_at": a.created_at
            }
            for a in audits
        ]
    }
