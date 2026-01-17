"""
文档解析服务
基于 Docling 实现 PDF/Excel 财务报表解析
包含勾稽自校验机制
"""

from pathlib import Path
from typing import Optional, Dict, Any
import re

from app.models.schemas import (
    FinancialIndicators,
    ParsedDocument,
    TaskStatus,
    ConfidenceLevel
)
from app.core.config import settings


class DocumentParser:
    """
    文档解析器
    
    基于 Docling 解析财务报表，提取关键指标
    包含勾稽自校验机制，在感知层过滤低质量数据
    """
    
    def __init__(self):
        self._converter = None
        self._docling_available = False
        self._init_docling()
    
    def _init_docling(self):
        """初始化 Docling（延迟加载）"""
        try:
            from docling.document_converter import DocumentConverter
            self._converter = DocumentConverter()
            self._docling_available = True
        except ImportError:
            # Docling 未安装，使用 mock 模式
            self._docling_available = False
    
    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        解析财务报表文档
        
        Args:
            file_path: 文档路径
            
        Returns:
            ParsedDocument 解析结果
        """
        document_id = file_path.stem.split("_")[0]  # 从文件名提取 ID
        
        try:
            if self._docling_available and self._converter:
                # 使用 Docling 解析
                result = self._converter.convert(str(file_path))
                markdown_content = result.document.export_to_markdown()
                
                # 提取财务指标
                indicators = self._extract_indicators_from_markdown(markdown_content)
                
                return ParsedDocument(
                    document_id=document_id,
                    document_type="balance_sheet",
                    raw_markdown=markdown_content,
                    indicators=indicators,
                    parse_status=TaskStatus.COMPLETED
                )
            else:
                # Mock 模式：返回模拟数据
                return self._create_mock_parsed_document(document_id)
                
        except Exception as e:
            return ParsedDocument(
                document_id=document_id,
                parse_status=TaskStatus.FAILED,
                error_message=str(e)
            )
    
    def _extract_indicators_from_markdown(self, markdown: str) -> FinancialIndicators:
        """
        从 Markdown 内容提取财务指标
        
        TODO: 实现更精确的表格解析和数值提取
        """
        # 简单的数值提取逻辑（实际需要更复杂的解析）
        indicators = FinancialIndicators()
        
        # 尝试提取常见财务指标
        patterns = {
            "total_assets": [r"资产总[计额]\s*[：:]\s*([\d,\.]+)", r"总资产\s*[：:]\s*([\d,\.]+)"],
            "current_assets": [r"流动资产[合计]*\s*[：:]\s*([\d,\.]+)"],
            "non_current_assets": [r"非流动资产[合计]*\s*[：:]\s*([\d,\.]+)"],
            "total_liabilities": [r"负债[总合][计额]\s*[：:]\s*([\d,\.]+)"],
            "current_liabilities": [r"流动负债[合计]*\s*[：:]\s*([\d,\.]+)"],
            "non_current_liabilities": [r"非流动负债[合计]*\s*[：:]\s*([\d,\.]+)"],
            "total_equity": [r"所有者权益[合计]*\s*[：:]\s*([\d,\.]+)", r"股东权益[合计]*\s*[：:]\s*([\d,\.]+)"],
            "cash": [r"货币资金\s*[：:]\s*([\d,\.]+)"],
            "receivables": [r"应收[账帐]款\s*[：:]\s*([\d,\.]+)"],
            "inventory": [r"存货\s*[：:]\s*([\d,\.]+)"]
        }
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, markdown)
                if match:
                    value_str = match.group(1).replace(",", "")
                    try:
                        setattr(indicators, field, float(value_str))
                    except ValueError:
                        pass
                    break
        
        # 执行勾稽自校验
        self._validate_balance(indicators)
        
        return indicators
    
    def _validate_balance(self, indicators: FinancialIndicators) -> None:
        """
        勾稽自校验
        
        在感知层过滤低质量数据，减轻符号引擎压力
        """
        tolerance = settings.BALANCE_TOLERANCE
        
        # 1. 资产分项校验：流动 + 非流动 = 总计
        if indicators.total_assets > 0:
            asset_sum = indicators.current_assets + indicators.non_current_assets
            indicators.asset_breakdown_valid = abs(asset_sum - indicators.total_assets) / indicators.total_assets < tolerance
        
        # 2. 负债分项校验：流动 + 非流动 = 总计
        if indicators.total_liabilities > 0:
            liability_sum = indicators.current_liabilities + indicators.non_current_liabilities
            indicators.liability_breakdown_valid = abs(liability_sum - indicators.total_liabilities) / indicators.total_liabilities < tolerance
        
        # 3. 核心勾稽：资产 = 负债 + 权益
        if indicators.total_assets > 0:
            liability_equity_sum = indicators.total_liabilities + indicators.total_equity
            balance_diff = abs(indicators.total_assets - liability_equity_sum)
            indicators.balance_check_passed = balance_diff / indicators.total_assets < tolerance
        
        # 确定置信度等级
        if indicators.balance_check_passed and indicators.asset_breakdown_valid and indicators.liability_breakdown_valid:
            indicators.confidence = ConfidenceLevel.HIGH
        elif indicators.balance_check_passed:
            indicators.confidence = ConfidenceLevel.MEDIUM
        else:
            indicators.confidence = ConfidenceLevel.LOW  # 触发人工复核
    
    def _create_mock_parsed_document(self, document_id: str) -> ParsedDocument:
        """创建模拟解析结果（开发阶段使用）"""
        indicators = FinancialIndicators(
            total_assets=5000000.0,
            current_assets=3000000.0,
            non_current_assets=2000000.0,
            total_liabilities=3000000.0,
            current_liabilities=2000000.0,
            non_current_liabilities=1000000.0,
            total_equity=2000000.0,
            cash=500000.0,
            receivables=800000.0,
            inventory=400000.0
        )
        
        # 执行勾稽自校验
        self._validate_balance(indicators)
        
        return ParsedDocument(
            document_id=document_id,
            document_type="balance_sheet",
            period="2025-12",
            company_name="示例公司（模拟数据）",
            raw_markdown="# 资产负债表\n\n*此为模拟数据，Docling 未安装*",
            indicators=indicators,
            parse_status=TaskStatus.COMPLETED
        )
    
    def extract_balance_sheet(self, parsed_data: dict) -> FinancialIndicators:
        """
        提取资产负债表关键指标
        
        Args:
            parsed_data: 解析后的文档数据
            
        Returns:
            FinancialIndicators 财务指标
        """
        if "indicators" in parsed_data:
            return parsed_data["indicators"]
        
        if "raw_markdown" in parsed_data:
            return self._extract_indicators_from_markdown(parsed_data["raw_markdown"])
        
        return FinancialIndicators()


# 全局实例
document_parser = DocumentParser()
