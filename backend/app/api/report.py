"""
报告导出 API 接口
生成和导出审计报告
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict
from datetime import datetime
import uuid

from app.models.schemas import (
    ReportRequest,
    ReportStatus,
    TaskStatus
)

router = APIRouter()

# 内存存储（MVP阶段）
reports_db: Dict[str, ReportStatus] = {}


async def generate_report_async(report_id: str, audit_id: str, format: str):
    """
    后台异步生成报告
    """
    try:
        if report_id in reports_db:
            reports_db[report_id].status = TaskStatus.PROCESSING
        
        # TODO: 实现 PDF 报告生成
        # from app.services.report import ReportService
        # report_service = ReportService()
        # file_path = await report_service.generate(audit_id)
        
        # 模拟生成完成
        if report_id in reports_db:
            reports_db[report_id].status = TaskStatus.COMPLETED
            reports_db[report_id].download_url = f"/api/v1/report/download/{report_id}"
            
    except Exception as e:
        if report_id in reports_db:
            reports_db[report_id].status = TaskStatus.FAILED


@router.post("/generate", response_model=ReportStatus)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """
    生成审计报告
    
    支持 PDF 格式导出
    后台异步生成，通过轮询获取状态
    """
    if request.format not in ["pdf", "docx", "html"]:
        raise HTTPException(
            status_code=400,
            detail="不支持的报告格式，仅支持: pdf, docx, html"
        )
    
    report_id = str(uuid.uuid4())
    
    report_status = ReportStatus(
        report_id=report_id,
        audit_id=request.audit_id,
        status=TaskStatus.PENDING
    )
    
    reports_db[report_id] = report_status
    
    # 添加后台生成任务
    background_tasks.add_task(
        generate_report_async,
        report_id,
        request.audit_id,
        request.format
    )
    
    return report_status


@router.get("/status/{report_id}", response_model=ReportStatus)
async def get_report_status(report_id: str):
    """
    获取报告生成状态
    """
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return reports_db[report_id]


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """
    下载审计报告
    """
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    report = reports_db[report_id]
    
    if report.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"报告尚未生成完成，当前状态: {report.status}"
        )
    
    # TODO: 返回实际文件
    # return FileResponse(file_path, filename=f"audit_report_{report_id}.pdf")
    
    return {
        "message": "报告下载功能开发中",
        "report_id": report_id,
        "status": report.status
    }


@router.get("/list")
async def list_reports(limit: int = 10, offset: int = 0):
    """
    获取报告列表
    """
    reports = list(reports_db.values())
    return {
        "total": len(reports),
        "items": reports[offset:offset + limit]
    }
