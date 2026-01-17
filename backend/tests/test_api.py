"""
API 接口测试
测试文件上传、审计启动和结果查询接口
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO

# 导入应用
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


client = TestClient(app)


class TestHealthCheck:
    """健康检查接口测试"""
    
    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_health(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuditAPI:
    """审计 API 测试"""
    
    def test_upload_invalid_extension(self):
        """测试上传不支持的文件类型"""
        file_content = b"test content"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/v1/audit/upload", files=files)
        assert response.status_code == 400
        assert "不支持的文件格式" in response.json()["detail"]
    
    def test_upload_valid_pdf(self):
        """测试上传 PDF 文件"""
        # 模拟 PDF 文件
        file_content = b"%PDF-1.4 test content"
        files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
        
        response = client.post("/api/v1/audit/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "pending"
        assert len(data["document_id"]) == 36  # UUID 长度
    
    def test_get_audit_result_demo(self):
        """测试获取示例审计结果"""
        response = client.get("/api/v1/audit/result/demo_audit_id")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert data["risk_score"] is not None
        assert len(data["violations"]) > 0
        assert len(data["reasoning_chain"]) > 0
    
    def test_list_audits(self):
        """测试获取审计列表"""
        response = client.get("/api/v1/audit/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "items" in data


class TestQAAPI:
    """问答 API 测试"""
    
    def test_ask_empty_question(self):
        """测试空问题"""
        response = client.post(
            "/api/v1/qa/ask",
            json={"question": ""}
        )
        assert response.status_code == 400
    
    def test_ask_valid_question(self):
        """测试有效问题"""
        response = client.post(
            "/api/v1/qa/ask",
            json={"question": "什么是资产负债表勾稽关系？"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "confidence" in data
    
    def test_ask_risk_question(self):
        """测试风险相关问题"""
        response = client.post(
            "/api/v1/qa/ask",
            json={"question": "当前审计有什么风险？"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "风险" in data["answer"]


class TestReportAPI:
    """报告 API 测试"""
    
    def test_generate_report(self):
        """测试生成报告"""
        response = client.post(
            "/api/v1/report/generate",
            json={
                "audit_id": "test_audit_id",
                "format": "pdf"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "report_id" in data
        assert data["status"] == "pending"
    
    def test_generate_invalid_format(self):
        """测试无效格式"""
        response = client.post(
            "/api/v1/report/generate",
            json={
                "audit_id": "test_audit_id",
                "format": "invalid"
            }
        )
        assert response.status_code == 400
    
    def test_list_reports(self):
        """测试获取报告列表"""
        response = client.get("/api/v1/report/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "items" in data
