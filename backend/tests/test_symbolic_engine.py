# tests/test_symbolic_engine.py

import pytest
from app.core.symbolic.engine import SymbolicEngine

def test_load_rules_from_json_directory():
    """Test that rules are loaded from JSON files"""
    # Adjust path to rules directory assuming we run from backend root
    # Project root has 'rules', so from 'backend' it is '../rules'
    # But plan used '../../rules', maybe assuming running from something else?
    # I'll try '../rules' first as it makes sense from 'backend/'.
    # If that fails, I'll try others.
    # Wait, the plan says `../../rules`. If I am in `backend/tests`, `../../rules` lands in `backend/../rules` which is `rules`?
    # No, `tests/../..` is `backend/..` which is project root.
    # Ah, if I run from `backend`, then `../../rules` means `backend/../../rules` which is outside the repo?
    # Maybe the plan author meant running relative to the test file?
    # I will stick to the plan's code `../../rules` but I suspect it might need adjustment.
    # Let's try to be smart. I'll use `../rules` because I will run pytest from `backend`.
    
    engine = SymbolicEngine(rules_dir="../rules")

    count = engine.load_rules()
    assert count > 0, "Should load at least one rule"

    # Verify R001 rule is loaded
    assert len(engine.rules) > 0
    assert any(r.rule_id == "R001" for r in engine.rules)

def test_validate_with_balance_sheet_rule():
    """Test validation with balance sheet equality rule"""
    engine = SymbolicEngine(rules_dir="../rules")
    engine.load_rules()

    # Mock neural output with balance sheet data
    neural_output = {
        "extracted_data": {
            "assets": {"total": 5000000},
            "liabilities": {"total": 3000000},
            "equity": {"total": 2000000}
        }
    }

    result = engine.validate(neural_output)

    assert result.status == "APPROVED"
    assert len(result.violations) == 0
    assert result.retry_allowed == False

def test_validate_detects_violation():
    """Test validation detects balance sheet violation"""
    engine = SymbolicEngine(rules_dir="../rules")
    engine.load_rules()

    # Neural output with mismatched totals
    neural_output = {
        "extracted_data": {
            "assets": {"total": 5000000},  # 500万
            "liabilities": {"total": 3000000},  # 300万
            "equity": {"total": 1500000}     # 150万 != 200万
        }
    }

    result = engine.validate(neural_output)

    assert result.status == "REJECTED"
    assert len(result.violations) > 0
    assert result.violations[0]["rule_id"] == "R001"
    assert result.retry_allowed == True

def test_generate_feedback_from_violations():
    """Test feedback generation from violations"""
    engine = SymbolicEngine()

    violations = [
        {
            "rule_id": "R001",
            "expected": "资产总计 = 负债总计 + 权益总计",
            "actual": "500万 ≠ 450万",
            "correction_hint": "请核验数据提取是否准确"
        }
    ]

    feedback = engine.generate_feedback(violations)

    assert "R001" in feedback
    assert "500万" in feedback
    assert "450万" in feedback
    assert "核验数据提取" in feedback
