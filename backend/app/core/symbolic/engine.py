# fincode/backend/app/core/symbolic/engine.py

import json
import os
from pathlib import Path
from typing import List, Optional, Any
from dataclasses import dataclass

# Try to import zen-engine, provide mock if not available
try:
    from zen_engine import ZenEngine
    ZEN_ENGINE_AVAILABLE = True
except ImportError:
    ZEN_ENGINE_AVAILABLE = False
    print("Warning: zen-engine not installed, using mock validation")

@dataclass
class ValidationResult:
    """校验结果"""
    status: str  # APPROVED / REJECTED
    violations: List[dict]
    retry_allowed: bool


@dataclass
class RuleDefinition:
    """规则定义"""
    rule_id: str
    name: str
    category: str
    severity: str  # CRITICAL / WARNING / INFO
    expression: dict
    correction_hint: str


class SymbolicEngine:
    """符号引擎 - 基于 Zen Engine 的规则校验"""

    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
        self.rules: List[RuleDefinition] = []
        self.zen_engine = None

        if ZEN_ENGINE_AVAILABLE:
            try:
                self.zen_engine = ZenEngine()
            except Exception as e:
                print(f"Warning: Failed to initialize Zen Engine: {e}")

    def load_rules(self, category: Optional[str] = None) -> int:
        """
        加载规则库

        Args:
            category: 规则类别（accounting/tax/internal_control）

        Returns:
            加载的规则数量
        """
        if not self.rules_dir.exists():
            print(f"Warning: Rules directory {self.rules_dir} does not exist")
            return 0

        loaded_count = 0

        for json_file in self.rules_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)

                rule = RuleDefinition(
                    rule_id=rule_data.get("rule_id", ""),
                    name=rule_data.get("name", ""),
                    category=rule_data.get("category", ""),
                    severity=rule_data.get("severity", "INFO"),
                    expression=rule_data.get("expression", {}),
                    correction_hint=rule_data.get("correction_hint", "")
                )

                if category is None or rule.category == category:
                    self.rules.append(rule)
                    loaded_count += 1

            except Exception as e:
                print(f"Warning: Failed to load rule from {json_file}: {e}")

        print(f"Loaded {loaded_count} rules from {self.rules_dir}")
        return loaded_count

    def _evaluate_expression(self, expression: dict, data: dict) -> Any:
        """
        评估规则表达式

        Args:
            expression: JSON 表达式树
            data: 输入数据

        Returns:
            评估结果
        """
        operator = expression.get("operator")

        if operator == "equals":
            left = self._resolve_value(expression.get("left"), data)
            right = self._resolve_value(expression.get("right"), data)
            tolerance = expression.get("tolerance", 0.01)

            if left is None or right is None:
                return False
                
            return abs(left - right) <= tolerance

        elif operator == "add":
            operands = expression.get("operands", [])
            result = 0
            for operand in operands:
                val = self._resolve_value(operand, data)
                if val is None:
                    return None
                result += val
            return result

        elif operator.startswith("$"):
            return self._resolve_value(expression, data)

        else:
            print(f"Warning: Unknown operator: {operator}")
            return None

    def _resolve_value(self, reference: Any, data: dict) -> Any:
        """
        解析值引用

        Args:
            reference: 可以是直接值或 JSON path
            data: 数据上下文

        Returns:
            解析后的值
        """
        if isinstance(reference, (int, float)):
            return float(reference)
        elif isinstance(reference, str) and reference.startswith("$."):
            parts = reference[2:].split(".")
            value = data
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        elif isinstance(reference, dict):
            return self._evaluate_expression(reference, data)
        else:
            return reference

    def validate(self, neural_output: dict) -> ValidationResult:
        """
        校验神经引擎输出

        Args:
            neural_output: 神经引擎的结构化输出

        Returns:
            校验结果，包含状态和违规详情
        """
        violations = []
        retry_allowed = False

        data = neural_output.get("extracted_data", {})

        for rule in self.rules:
            try:
                is_valid = self._evaluate_expression(rule.expression, data)

                if not is_valid:
                    expected = self._format_expression(rule.expression, data)
                    actual = self._format_actual(rule.expression, data)

                    violation = {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "expected": expected,
                        "actual": actual,
                        "correction_hint": rule.correction_hint
                    }
                    violations.append(violation)
                    
                    retry_allowed = True

            except Exception as e:
                print(f"Warning: Failed to validate rule {rule.rule_id}: {e}")

        if len(violations) == 0:
            status = "APPROVED"
        elif any(v.get("severity") == "CRITICAL" for v in violations):
            status = "REJECTED"
        else:
            status = "REJECTED"
            retry_allowed = True

        return ValidationResult(
            status=status,
            violations=violations,
            retry_allowed=retry_allowed
        )

    def _format_expression(self, expression: dict, data: dict) -> str:
        """格式化期望值的字符串表示"""
        operator = expression.get("operator")
        if operator == "equals":
            left = self._format_value(expression.get("left"), data)
            right = self._format_value(expression.get("right"), data)
            return f"{left} = {right}"
        return str(expression)

    def _format_actual(self, expression: dict, data: dict) -> str:
        """格式化实际值的字符串表示"""
        operator = expression.get("operator")
        if operator == "equals":
            left = self._format_value(expression.get("left"), data)
            right_val = self._evaluate_expression(expression.get("right"), data)
            right = self._format_number(right_val)
            return f"{left} ≠ {right}"
        return str(expression)

    def _format_value(self, value_ref: Any, data: dict) -> str:
        """格式化值为字符串"""
        if isinstance(value_ref, str) and value_ref.startswith("$."):
            value = self._resolve_value(value_ref, data)
            return self._format_number(value)
        elif isinstance(value_ref, dict):
            value = self._evaluate_expression(value_ref, data)
            return self._format_number(value)
        else:
            return str(value_ref)

    def _format_number(self, value: Any) -> str:
        """格式化数字为万元"""
        if isinstance(value, (int, float)):
            if value >= 10000:
                return f"{value / 10000:.0f}万"
            else:
                return str(value)
        return str(value)

    def generate_feedback(self, violations: List[dict]) -> str:
        """
        生成纠偏反馈

        Args:
            violations: 违规列表

        Returns:
            用于注入神经引擎的反馈文本
        """
        if not violations:
            return ""

        feedback_parts = ["以下规则校验失败，请重新分析："]
        for v in violations:
            feedback_parts.append(
                f"- [{v.get('rule_id')}] {v.get('expected')}, 实际: {v.get('actual')}. "
                f"提示: {v.get('correction_hint')}"
            )

        return "\n".join(feedback_parts)
