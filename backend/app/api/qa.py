"""
智能问答 API 接口
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class QuestionRequest(BaseModel):
    """问答请求"""
    question: str
    audit_id: Optional[str] = None
    context: Optional[str] = None


class AnswerResponse(BaseModel):
    """问答响应"""
    answer: str
    sources: Optional[List[dict]] = None
    confidence: Optional[float] = None


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    智能问答接口
    
    基于审计上下文回答用户问题
    """
    # TODO: 实现基于 DeepSeek R1 的问答逻辑
    return AnswerResponse(
        answer="这是一个占位响应。完整实现将使用 DeepSeek R1 进行推理。",
        sources=[],
        confidence=0.0
    )
