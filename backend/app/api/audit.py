"""
审计相关 API 接口
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class AuditStartRequest(BaseModel):
    """审计启动请求"""
    document_id: str
    rules: Optional[List[str]] = None


class AuditResult(BaseModel):
    """审计结果"""
    audit_id: str
    status: str
    risk_score: Optional[float] = None
    violations: Optional[List[dict]] = None
    reasoning_chain: Optional[List[str]] = None


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    上传财务报表文档
    
    支持 PDF 和 Excel 格式
    """
    # TODO: 实现文档上传和解析逻辑
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    allowed_extensions = {".pdf", ".xlsx", ".xls"}
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式，请上传 PDF 或 Excel 文件"
        )
    
    return {
        "document_id": "doc_placeholder",
        "filename": file.filename,
        "status": "uploaded",
        "message": "文档上传成功，等待解析"
    }


@router.post("/start", response_model=AuditResult)
async def start_audit(request: AuditStartRequest):
    """
    启动审计流程
    
    触发神经-符号双引擎协同审计
    """
    # TODO: 实现 LangGraph 审计流程编排
    return AuditResult(
        audit_id="audit_placeholder",
        status="processing",
        risk_score=None,
        violations=None,
        reasoning_chain=None
    )


@router.get("/result/{audit_id}", response_model=AuditResult)
async def get_audit_result(audit_id: str):
    """
    获取审计结果
    
    返回完整的审计报告，包括风险评分和推理链
    """
    # TODO: 从数据库获取审计结果
    return AuditResult(
        audit_id=audit_id,
        status="completed",
        risk_score=72.0,
        violations=[
            {
                "rule_id": "R001",
                "severity": "WARNING",
                "description": "应收账款周转率异常偏低",
                "suggestion": "建议核查应收账款账龄分布"
            }
        ],
        reasoning_chain=[
            "步骤 1: 从资产负债表中提取关键财务指标",
            "步骤 2: 计算应收账款周转率",
            "步骤 3: 与行业基准对比分析"
        ]
    )
