
import pytest
from app.core.neural.engine import DeepSeekAPIAdapter

@pytest.mark.asyncio
async def test_deepseek_api_analyze_returns_structured_output():
    """Test that DeepSeek API returns structured output with reasoning chain"""
    api_key = "test-key"
    adapter = DeepSeekAPIAdapter(api_key, base_url="https://api.deepseek.com/v1")

    # Mock response data from document parser
    test_data = {
        "assets": {"total": 5000000},
        "liabilities": {"total": 3000000},
        "equity": {"total": 2000000}
    }

    result = await adapter.analyze(test_data)

    # Verify output structure matches design spec
    assert "conclusion" in result
    assert "confidence" in result
    assert "reasoning_chain" in result
    assert isinstance(result["reasoning_chain"], list)
    assert len(result["reasoning_chain"]) >= 1
