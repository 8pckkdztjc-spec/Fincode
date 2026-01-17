import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.core.orchestrator.graph import AuditOrchestrator, AuditState

@pytest.fixture
def orchestrator():
    """Create an orchestrator instance with mocked engines"""
    # Patch the factory and symbolic engine
    with patch("app.core.orchestrator.graph.InferenceEngineFactory") as MockFactory:
        with patch("app.core.orchestrator.graph.SymbolicEngine") as MockSymbolic:
            # Setup Neural Engine Mock
            mock_neural = MagicMock()
            mock_neural.analyze = AsyncMock(return_value={"analysis": "done", "extracted_data": {}})
            MockFactory.create.return_value = mock_neural
            
            # Setup Symbolic Engine Mock
            mock_symbolic_instance = MockSymbolic.return_value
            # Default behavior: Valid
            mock_symbolic_instance.validate.return_value = {"status": "APPROVED", "violations": []}
            mock_symbolic_instance.generate_feedback.return_value = "Mock Feedback"
            
            orch = AuditOrchestrator()
            return orch

@pytest.mark.asyncio
async def test_audit_flow_success(orchestrator):
    """Test the happy path where validation passes immediately"""
    # Setup
    orchestrator.symbolic_engine.validate.return_value = {"status": "APPROVED", "violations": []}
    
    # Execute
    initial_state = {
        "raw_document": "Valid document content",
        "retry_count": 0,
        "feedback_history": []
    }
    result = await orchestrator.run(initial_state)
    
    # Verify
    assert result["validation_result"] == "APPROVED"
    assert result["retry_count"] == 0
    assert result["final_report"] is not None
    orchestrator.neural_engine.analyze.assert_called()
    orchestrator.symbolic_engine.validate.assert_called()

@pytest.mark.asyncio
async def test_audit_flow_retry_logic(orchestrator):
    """Test that feedback loop works when validation fails"""
    # Setup: Fail first time (REJECTED), then Pass (APPROVED)
    orchestrator.symbolic_engine.validate.side_effect = [
        {"status": "REJECTED", "violations": [{"rule": "R1"}]},
        {"status": "APPROVED", "violations": []}
    ]
    
    # Execute
    initial_state = {
        "raw_document": "Problematic document",
        "retry_count": 0,
        "feedback_history": []
    }
    result = await orchestrator.run(initial_state)
    
    # Verify
    assert result["validation_result"] == "APPROVED"
    assert result["retry_count"] == 1
    assert len(result["feedback_history"]) > 0
