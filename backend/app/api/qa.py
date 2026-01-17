"""
智能问答 API 接口
基于审计上下文的自然语言问答
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.schemas import (
    QuestionRequest,
    AnswerResponse,
    AnswerSource,
    TaskStatus
)

router = APIRouter()


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    智能问答接口
    
    基于审计上下文回答用户问题
    支持关联特定审计任务的上下文感知问答
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    # TODO: 集成 DeepSeek R1 进行问答推理
    # from app.core.neural.engine import InferenceEngineFactory
    # engine = InferenceEngineFactory.create()
    # response = await engine.analyze({"question": request.question})
    
    # 模拟问答响应
    answer = _generate_mock_answer(request.question, request.audit_id)
    
    return answer


def _generate_mock_answer(question: str, audit_id: Optional[str] = None) -> AnswerResponse:
    """生成模拟问答响应（开发阶段）"""
    
    # 预定义问答对
    qa_pairs = {
        "资产负债": AnswerResponse(
            question=question,
            answer="资产负债表勾稽关系是指：资产总计 = 负债总计 + 所有者权益总计。"
                   "这是会计恒等式的基本体现，任何资产的形成都有其资金来源，"
                   "要么来自负债（外部借入），要么来自所有者权益（所有者投入或留存收益）。",
            sources=[
                AnswerSource(
                    title="会计准则第30号",
                    source_type="knowledge",
                    reference="企业会计准则"
                )
            ],
            confidence=0.95,
            reasoning="基于会计基础理论知识库检索得出结论"
        ),
        "异常": AnswerResponse(
            question=question,
            answer="根据审计结果，应收账款周转率为 2.3，低于行业均值 5.0。"
                   "这可能表明：1) 信用政策过于宽松；2) 客户付款能力下降；3) 存在坏账风险。"
                   "建议核查应收账款账龄分布，重点关注超期 90 天以上的账款。",
            sources=[
                AnswerSource(
                    title="审计结果 R012",
                    source_type="document",
                    reference=audit_id
                )
            ],
            confidence=0.87,
            reasoning="基于审计结果 R012 规则触发的异常分析"
        ),
        "风险": AnswerResponse(
            question=question,
            answer="当前审计发现 2 项风险：\n"
                   "1. 【严重】资产负债表勾稽不平衡，差额 5 万元\n"
                   "2. 【警告】应收账款周转异常偏低\n"
                   "综合风险评分为 72 分（中等风险），建议重点关注数据准确性。",
            sources=[
                AnswerSource(
                    title="风险评估报告",
                    source_type="document",
                    reference=audit_id
                )
            ],
            confidence=0.92,
            reasoning="综合审计规则校验结果生成风险评估"
        )
    }
    
    # 关键词匹配
    for keyword, response in qa_pairs.items():
        if keyword in question:
            response.question = question
            return response
    
    # 默认响应
    return AnswerResponse(
        question=question,
        answer="感谢您的提问。目前系统正在开发阶段，完整的智能问答功能将在集成 DeepSeek R1 后上线。"
               "您可以尝试询问关于'资产负债'、'异常'或'风险'相关的问题。",
        sources=[],
        confidence=0.5,
        reasoning="未匹配到预定义问答对，返回通用响应"
    )


@router.get("/history/{audit_id}")
async def get_qa_history(audit_id: str, limit: int = 20):
    """
    获取问答历史
    
    返回指定审计任务的问答记录
    """
    # TODO: 从数据库获取问答历史
    return {
        "audit_id": audit_id,
        "history": [],
        "total": 0
    }
