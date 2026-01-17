"""
审计业务服务
协调神经-符号双引擎执行审计流程
"""

from typing import Optional, List
from datetime import datetime
import uuid

from app.models.schemas import (
    AuditResult,
    TaskStatus,
    ValidationViolation,
    RiskSeverity,
    FinancialIndicators
)
from app.services.document import document_parser
from app.core.config import settings


class AuditService:
    """
    审计服务
    
    协调神经引擎和符号引擎执行审计流程
    """
    
    def __init__(self):
        # TODO: 初始化双引擎
        pass
    
    async def start_audit(
        self,
        document_id: str,
        indicators: FinancialIndicators,
        rules: Optional[List[str]] = None
    ) -> AuditResult:
        """
        启动审计流程
        
        Args:
            document_id: 文档ID
            indicators: 财务指标
            rules: 指定规则列表（可选）
            
        Returns:
            AuditResult 审计结果
        """
        audit_id = str(uuid.uuid4())
        
        # 初始化审计结果
        result = AuditResult(
            audit_id=audit_id,
            document_id=document_id,
            status=TaskStatus.PROCESSING,
            risk_score=None
        )
        
        try:
            # 1. 执行符号引擎规则校验
            violations = self._execute_rule_checks(indicators)
            result.violations = violations
            
            # 2. 计算风险评分
            result.risk_score = self._calculate_risk_score(violations, indicators)
            
            # 3. 生成推理链
            result.reasoning_chain = self._generate_reasoning_chain(indicators, violations)
            
            # 4. 标记完成
            result.status = TaskStatus.COMPLETED
            result.completed_at = datetime.now()
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.reasoning_chain.append(f"审计执行失败: {str(e)}")
        
        return result
    
    def _execute_rule_checks(self, indicators: FinancialIndicators) -> List[ValidationViolation]:
        """执行规则校验"""
        violations = []
        
        # R001: 资产负债表勾稽平衡
        if not indicators.balance_check_passed:
            diff = abs(indicators.total_assets - (indicators.total_liabilities + indicators.total_equity))
            violations.append(ValidationViolation(
                rule_id="R001",
                rule_name="资产负债表勾稽平衡",
                severity=RiskSeverity.CRITICAL,
                expected="资产总计 = 负债总计 + 权益总计",
                actual=f"差额 = {diff:,.2f}",
                correction_hint="请核验数据提取是否准确，或检查原始报表是否存在计算错误"
            ))
        
        # R002: 资产分项校验
        if not indicators.asset_breakdown_valid and indicators.total_assets > 0:
            violations.append(ValidationViolation(
                rule_id="R002",
                rule_name="资产分项校验",
                severity=RiskSeverity.WARNING,
                expected="流动资产 + 非流动资产 = 资产总计",
                actual=f"{indicators.current_assets:,.2f} + {indicators.non_current_assets:,.2f} ≠ {indicators.total_assets:,.2f}",
                correction_hint="请检查流动资产和非流动资产的分类是否准确"
            ))
        
        # R003: 负债分项校验
        if not indicators.liability_breakdown_valid and indicators.total_liabilities > 0:
            violations.append(ValidationViolation(
                rule_id="R003",
                rule_name="负债分项校验",
                severity=RiskSeverity.WARNING,
                expected="流动负债 + 非流动负债 = 负债总计",
                actual=f"{indicators.current_liabilities:,.2f} + {indicators.non_current_liabilities:,.2f} ≠ {indicators.total_liabilities:,.2f}",
                correction_hint="请检查流动负债和非流动负债的分类是否准确"
            ))
        
        # R004: 货币资金异常检测（示例）
        if indicators.cash and indicators.total_assets > 0:
            cash_ratio = indicators.cash / indicators.total_assets
            if cash_ratio > 0.5:
                violations.append(ValidationViolation(
                    rule_id="R004",
                    rule_name="货币资金占比异常",
                    severity=RiskSeverity.INFO,
                    expected="货币资金占比 < 50%",
                    actual=f"货币资金占比 = {cash_ratio * 100:.1f}%",
                    correction_hint="货币资金占比偏高，建议核查资金使用效率"
                ))
        
        return violations
    
    def _calculate_risk_score(
        self,
        violations: List[ValidationViolation],
        indicators: FinancialIndicators
    ) -> float:
        """
        计算风险评分 (0-100)
        
        0: 无风险
        100: 极高风险
        """
        base_score = 0
        
        # 根据违规严重程度计算分数
        severity_weights = {
            RiskSeverity.CRITICAL: 30,
            RiskSeverity.WARNING: 15,
            RiskSeverity.INFO: 5
        }
        
        for violation in violations:
            base_score += severity_weights.get(violation.severity, 0)
        
        # 根据置信度调整
        confidence_adjustments = {
            "high": 0,
            "medium": 5,
            "low": 15
        }
        base_score += confidence_adjustments.get(indicators.confidence.value, 0)
        
        # 限制在 0-100 范围内
        return min(max(base_score, 0), 100)
    
    def _generate_reasoning_chain(
        self,
        indicators: FinancialIndicators,
        violations: List[ValidationViolation]
    ) -> List[str]:
        """生成推理链"""
        chain = []
        
        chain.append(f"步骤 1: 从文档中提取财务指标，资产总计 = {indicators.total_assets:,.2f}")
        chain.append(f"步骤 2: 执行勾稽平衡检验 (资产 = 负债 + 权益)")
        
        if indicators.balance_check_passed:
            chain.append("步骤 3: 勾稽平衡检验通过")
        else:
            diff = indicators.total_assets - (indicators.total_liabilities + indicators.total_equity)
            chain.append(f"步骤 3: 勾稽平衡检验失败，差额 = {diff:,.2f}")
        
        chain.append(f"步骤 4: 执行 {len(violations)} 条规则校验")
        
        if violations:
            critical_count = sum(1 for v in violations if v.severity == RiskSeverity.CRITICAL)
            warning_count = sum(1 for v in violations if v.severity == RiskSeverity.WARNING)
            chain.append(f"步骤 5: 发现 {critical_count} 个严重问题，{warning_count} 个警告")
        else:
            chain.append("步骤 5: 所有规则校验通过")
        
        chain.append(f"步骤 6: 数据置信度 = {indicators.confidence.value}")
        
        return chain
    
    async def get_result(self, audit_id: str) -> Optional[AuditResult]:
        """获取审计结果"""
        # TODO: 从数据库获取
        return None


# 全局实例
audit_service = AuditService()
