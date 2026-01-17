import os
import httpx
from typing import Optional
from abc import ABC, abstractmethod

class InferenceEngineAdapter(ABC):
    """推理引擎适配器抽象基类"""
    
    @abstractmethod
    async def analyze(self, data: dict, feedback: Optional[str] = None) -> dict:
        """
        执行分析推理
        
        Args:
            data: 输入数据（文档解析结果）
            feedback: 符号引擎的纠偏反馈（可选）
            
        Returns:
            结构化分析结果，包含推理链
        """
        pass


class DeepSeekAPIAdapter(InferenceEngineAdapter):
    """DeepSeek R1 API 模式适配器"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词，定义输出格式"""
        return """你是一个专业的财务审计助手。请对给定的财务数据进行分析，并按照以下JSON格式返回结果：

{
  "conclusion": "分析结论（简短明确）",
  "confidence": 0.0-1.0,
  "reasoning_chain": [
    "步骤1: 具体分析过程",
    "步骤2: 计算过程",
    ...
  ],
  "extracted_data": {
    "资产总计": 数值,
    "负债总计": 数值,
    "权益总计": 数值
  }
}

要求：
1. reasoning_chain 必须包含至少3个步骤
2. confidence 基于数据完整性和一致性评估
3. 严格按照JSON格式返回，不要包含markdown标记
4. 如果有纠偏反馈，请在推理步骤中体现
"""
    
    def _build_user_prompt(self, data: dict, feedback: Optional[str] = None) -> str:
        """构建用户提示词"""
        prompt = f"请分析以下财务数据：\n\n{data}\n\n"
        if feedback:
            prompt += f"纠偏反馈：\n{feedback}\n\n"
        prompt += "请输出结构化JSON分析结果。"
        return prompt
    
    async def analyze(self, data: dict, feedback: Optional[str] = None) -> dict:
        """调用 DeepSeek R1 API 进行分析"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(data, feedback)
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": "deepseek-reasoner",  # DeepSeek R1 推理模型
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,  # 降低温度以提高一致性
                    "response_format": {"type": "json_object"}  # 强制 JSON 输出
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
            # 解析响应
            content = response.json()["choices"][0]["message"]["content"]
            
            # 尝试解析 JSON
            import json
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # 如果不是纯 JSON，尝试提取 JSON 部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {content}")
            
            return result
            
        except Exception as e:
            # 错误处理：返回降级结果
            return {
                "conclusion": f"分析失败: {str(e)}",
                "confidence": 0.0,
                "reasoning_chain": ["API 调用异常"],
                "extracted_data": {}
            }

    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()


class LocalModelAdapter(InferenceEngineAdapter):
    """本地私有化模型适配器 (vLLM)"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        # TODO: 初始化 vLLM 推理引擎
    
    async def analyze(self, data: dict, feedback: Optional[str] = None) -> dict:
        """调用本地模型进行分析"""
        # TODO: 实现本地推理逻辑
        return {
            "conclusion": "本地模型分析占位",
            "confidence": 0.0,
            "reasoning_chain": [],
            "extracted_data": {}
        }


class InferenceEngineFactory:
    """推理引擎工厂类"""
    
    @staticmethod
    def create() -> InferenceEngineAdapter:
        """
        根据环境变量创建推理引擎适配器
        
        INFERENCE_MODE=api -> DeepSeekAPIAdapter
        INFERENCE_MODE=local -> LocalModelAdapter
        """
        mode = os.getenv("INFERENCE_MODE", "api")
        
        if mode == "api":
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
            return DeepSeekAPIAdapter(api_key)
        elif mode == "local":
            model_path = os.getenv("LOCAL_MODEL_PATH", "")
            if not model_path:
                raise ValueError("LOCAL_MODEL_PATH 环境变量未设置")
            return LocalModelAdapter(model_path)
        else:
            raise ValueError(f"不支持的推理模式: {mode}")
