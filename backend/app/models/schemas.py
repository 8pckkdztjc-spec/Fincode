"""
FinCode 数据模型定义
Pydantic 模型用于 API 请求/响应和内部数据传递
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


# ================================
# 枚举定义
# ================================

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"         # 等待处理
    PROCESSING = "processing"   # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败


class ConfidenceLevel(str, Enum):
    """置信度等级"""
    HIGH = "high"       # 高置信度：所有校验通过
    MEDIUM = "medium"   # 中置信度：核心校验通过
    LOW = "low"         # 低置信度：需人工复核


class RiskSeverity(str, Enum):
    """风险严重程度"""
    CRITICAL = "critical"   # 严重
    WARNING = "warning"     # 警告
    INFO = "info"           # 提示


# ================================
# 财务数据模型
# ================================

class FinancialIndicators(BaseModel):
    """财务指标（含勾稽自校验状态）"""
    
    # 资产类
    total_assets: float = Field(0.0, description="资产总计")
    current_assets: float = Field(0.0, description="流动资产")
    non_current_assets: float = Field(0.0, description="非流动资产")
    cash: Optional[float] = Field(None, description="货币资金")
    receivables: Optional[float] = Field(None, description="应收账款")
    inventory: Optional[float] = Field(None, description="存货")
    
    # 负债类
    total_liabilities: float = Field(0.0, description="负债总计")
    current_liabilities: float = Field(0.0, description="流动负债")
    non_current_liabilities: float = Field(0.0, description="非流动负债")
    
    # 权益类
    total_equity: float = Field(0.0, description="所有者权益合计")
    
    # 自校验结果
    balance_check_passed: bool = Field(False, description="勾稽平衡校验是否通过")
    asset_breakdown_valid: bool = Field(False, description="资产分项校验是否通过")
    liability_breakdown_valid: bool = Field(False, description="负债分项校验是否通过")
    confidence: ConfidenceLevel = Field(ConfidenceLevel.MEDIUM, description="数据置信度")


# ================================
# 文档相关模型
# ================================

class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: str = Field(..., description="文档唯一ID")
    filename: str = Field(..., description="原始文件名")
    status: TaskStatus = Field(TaskStatus.PENDING, description="处理状态")
    message: str = Field("文档上传成功，等待解析", description="状态消息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class ParsedDocument(BaseModel):
    """解析后的文档"""
    document_id: str
    document_type: str = Field("balance_sheet", description="文档类型")
    period: Optional[str] = Field(None, description="报表期间")
    company_name: Optional[str] = Field(None, description="公司名称")
    raw_markdown: Optional[str] = Field(None, description="原始Markdown内容")
    indicators: Optional[FinancialIndicators] = Field(None, description="提取的财务指标")
    parse_status: TaskStatus = TaskStatus.PENDING
    error_message: Optional[str] = None


# ================================
# 审计相关模型
# ================================

class AuditStartRequest(BaseModel):
    """审计启动请求"""
    document_id: str = Field(..., description="文档ID")
    rules: Optional[List[str]] = Field(None, description="指定规则列表，空则使用全部")


class ValidationViolation(BaseModel):
    """规则违规详情"""
    rule_id: str = Field(..., description="规则编号")
    rule_name: str = Field(..., description="规则名称")
    severity: RiskSeverity = Field(..., description="严重程度")
    expected: str = Field(..., description="期望值/条件")
    actual: str = Field(..., description="实际值")
    correction_hint: str = Field(..., description="纠正建议")


class RiskItem(BaseModel):
    """风险项"""
    rule_id: str
    description: str
    severity: RiskSeverity
    suggestion: Optional[str] = None


class AuditResult(BaseModel):
    """审计结果"""
    audit_id: str = Field(..., description="审计任务ID")
    document_id: str = Field(..., description="关联文档ID")
    status: TaskStatus = Field(..., description="审计状态")
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="风险评分 0-100")
    violations: List[ValidationViolation] = Field(default_factory=list, description="违规列表")
    reasoning_chain: List[str] = Field(default_factory=list, description="推理链")
    retry_count: int = Field(0, description="纠偏重试次数")
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


# ================================
# 问答相关模型
# ================================

class QuestionRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    audit_id: Optional[str] = Field(None, description="关联的审计ID")
    context: Optional[str] = Field(None, description="额外上下文")


class AnswerSource(BaseModel):
    """回答来源"""
    title: str
    source_type: str  # document / rule / knowledge
    reference: Optional[str] = None


class AnswerResponse(BaseModel):
    """问答响应"""
    question: str
    answer: str
    sources: List[AnswerSource] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0, le=1)
    reasoning: Optional[str] = None


# ================================
# 报告相关模型
# ================================

class ReportRequest(BaseModel):
    """报告生成请求"""
    audit_id: str = Field(..., description="审计ID")
    format: str = Field("pdf", description="报告格式")
    include_reasoning: bool = Field(True, description="是否包含推理过程")
    include_recommendations: bool = Field(True, description="是否包含建议")


class ReportStatus(BaseModel):
    """报告状态"""
    report_id: str
    audit_id: str
    status: TaskStatus
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
