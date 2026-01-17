"""
LangGraph 审计流程图定义
编排神经-符号双引擎协同工作流
"""

from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from app.core.neural.engine import InferenceEngineFactory
from app.core.symbolic.engine import SymbolicEngine


class AuditState(TypedDict):
    """审计流程状态定义"""
    raw_document: str           # 原始文档内容
    extracted_data: Optional[Dict[str, Any]]        # 提取的结构化数据
    neural_output: Optional[Dict[str, Any]]         # 神经引擎输出
    validation_result: str      # APPROVED / REJECTED
    violations: List[Dict[str, Any]]      # 违规列表
    feedback_history: List[str] # 纠偏历史
    retry_count: int            # 重试次数
    final_report: Optional[Dict[str, Any]]  # 最终报告


MAX_RETRIES = 3  # 最大纠偏重试次数


class AuditOrchestrator:
    def __init__(self):
        # Use factory to create the neural engine adapter
        self.neural_engine = InferenceEngineFactory.create()
        self.symbolic_engine = SymbolicEngine()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AuditState)

        workflow.add_node("neural_analyze", self.neural_analyze_node)
        workflow.add_node("symbolic_validate", self.symbolic_validate_node)
        workflow.add_node("inject_feedback", self.inject_feedback_node)
        workflow.add_node("generate_report", self.generate_report_node)

        workflow.set_entry_point("neural_analyze")

        workflow.add_edge("neural_analyze", "symbolic_validate")
        
        workflow.add_conditional_edges(
            "symbolic_validate",
            self.should_retry,
            {
                "retry": "inject_feedback",
                "end": "generate_report"
            }
        )

        workflow.add_edge("inject_feedback", "neural_analyze")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    async def run(self, initial_state: dict) -> dict:
        state = {
            "extracted_data": {},
            "neural_output": {},
            "validation_result": "PENDING",
            "violations": [],
            "feedback_history": [],
            "retry_count": 0,
            "final_report": None,
            **initial_state
        }
        return await self.graph.ainvoke(state)

    async def neural_analyze_node(self, state: AuditState) -> dict:
        feedback = state["feedback_history"][-1] if state["feedback_history"] else None
        
        result = await self.neural_engine.analyze(
            data={"raw_text": state["raw_document"]}, # Adapter expects dict
            feedback=feedback
        )
        
        return {
            "neural_output": result,
            "extracted_data": result.get("extracted_data", {}) 
        }

    async def symbolic_validate_node(self, state: AuditState) -> dict:
        # Symbolic engine returns ValidationResult dataclass, need to handle it
        result = self.symbolic_engine.validate(state["neural_output"])
        
        # Check if result is dataclass or dict (mock returns dict, real returns dataclass)
        if hasattr(result, 'status'):
            status = result.status
            violations = result.violations
        else:
            status = result.get("status", "REJECTED")
            violations = result.get("violations", [])

        return {
            "validation_result": status,
            "violations": violations
        }

    async def inject_feedback_node(self, state: AuditState) -> dict:
        violations = state["violations"]
        
        # Use symbolic engine to generate feedback text if available
        if hasattr(self.symbolic_engine, 'generate_feedback'):
            new_feedback = self.symbolic_engine.generate_feedback(violations)
        else:
            new_feedback = f"Fix violations: {violations}"
        
        return {
            "feedback_history": state["feedback_history"] + [new_feedback],
            "retry_count": state["retry_count"] + 1
        }

    async def generate_report_node(self, state: AuditState) -> dict:
        report = {
            "status": state["validation_result"],
            "details": state["neural_output"],
            "violations": state["violations"]
        }
        return {"final_report": report}

    def should_retry(self, state: AuditState) -> str:
        """
        判断是否需要重试
        
        Returns:
            "retry" - 需要重试
            "end" - 结束流程
        """
        if state["validation_result"] == "APPROVED":
            return "end"
        
        if state["retry_count"] >= MAX_RETRIES:
            return "end"
        
        return "retry"
