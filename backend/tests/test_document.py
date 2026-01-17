"""
文档解析服务测试
测试 Docling 解析和勾稽自校验逻辑
"""

import pytest
from pathlib import Path

from app.services.document import DocumentParser, document_parser
from app.models.schemas import ConfidenceLevel


class TestDocumentParser:
    """DocumentParser 测试类"""
    
    def test_init(self):
        """测试初始化"""
        parser = DocumentParser()
        assert parser is not None
    
    def test_mock_parsed_document(self):
        """测试模拟解析结果"""
        parser = DocumentParser()
        result = parser._create_mock_parsed_document("test_doc_123")
        
        assert result.document_id == "test_doc_123"
        assert result.document_type == "balance_sheet"
        assert result.indicators is not None
        assert result.indicators.total_assets == 5000000.0
    
    def test_balance_validation_pass(self):
        """测试勾稽校验通过"""
        from app.models.schemas import FinancialIndicators
        
        indicators = FinancialIndicators(
            total_assets=1000000.0,
            current_assets=600000.0,
            non_current_assets=400000.0,
            total_liabilities=600000.0,
            current_liabilities=400000.0,
            non_current_liabilities=200000.0,
            total_equity=400000.0
        )
        
        parser = DocumentParser()
        parser._validate_balance(indicators)
        
        assert indicators.balance_check_passed is True
        assert indicators.asset_breakdown_valid is True
        assert indicators.liability_breakdown_valid is True
        assert indicators.confidence == ConfidenceLevel.HIGH
    
    def test_balance_validation_fail(self):
        """测试勾稽校验失败"""
        from app.models.schemas import FinancialIndicators
        
        # 资产 ≠ 负债 + 权益
        indicators = FinancialIndicators(
            total_assets=1000000.0,
            current_assets=600000.0,
            non_current_assets=400000.0,
            total_liabilities=500000.0,  # 故意不平衡
            current_liabilities=300000.0,
            non_current_liabilities=200000.0,
            total_equity=400000.0
        )
        
        parser = DocumentParser()
        parser._validate_balance(indicators)
        
        assert indicators.balance_check_passed is False
        assert indicators.confidence == ConfidenceLevel.LOW
    
    def test_asset_breakdown_validation(self):
        """测试资产分项校验"""
        from app.models.schemas import FinancialIndicators
        
        # 流动资产 + 非流动资产 ≠ 资产总计
        indicators = FinancialIndicators(
            total_assets=1000000.0,
            current_assets=500000.0,  # 故意不平衡
            non_current_assets=400000.0,
            total_liabilities=600000.0,
            current_liabilities=400000.0,
            non_current_liabilities=200000.0,
            total_equity=400000.0
        )
        
        parser = DocumentParser()
        parser._validate_balance(indicators)
        
        assert indicators.asset_breakdown_valid is False
    
    def test_extract_indicators_from_markdown(self):
        """测试从 Markdown 提取指标"""
        parser = DocumentParser()
        
        markdown = """
        # 资产负债表
        
        资产总计：1000000
        流动资产合计：600000
        非流动资产合计：400000
        负债总计：600000
        所有者权益合计：400000
        """
        
        indicators = parser._extract_indicators_from_markdown(markdown)
        
        assert indicators.total_assets == 1000000.0
        assert indicators.current_assets == 600000.0
        assert indicators.total_liabilities == 600000.0


class TestGlobalDocumentParser:
    """测试全局 document_parser 实例"""
    
    def test_global_instance_exists(self):
        """测试全局实例存在"""
        assert document_parser is not None
    
    def test_global_instance_type(self):
        """测试全局实例类型"""
        assert isinstance(document_parser, DocumentParser)
