# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**FinCode - 神经符号协同财务审计助手**：面向中小企业的智能财务审计系统，采用神经-符号双引擎架构。

- **神经引擎**：DeepSeek-R1 大语言模型，负责语义理解与推理
- **符号引擎**：Zen Engine 规则引擎，执行硬编码审计规则，确保"零幻觉"
- **约束反馈机制**：双引擎协同工作，最多3次迭代纠偏

## 开发命令

### 后端 (FastAPI + Python 3.11+)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 运行测试
pytest tests/
pytest tests/test_engine.py -k "test_specific_function"  # 单个测试
```

### 前端 (React + TypeScript + Vite)
```bash
cd frontend
npm install
npm run dev      # 启动开发服务器 http://localhost:5173
npm run build    # 生产构建
npm run lint     # ESLint检查
```

### Docker 一键启动
```bash
docker-compose up -d
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 架构概览

```
fincode/
├── backend/                    # Python后端服务
│   ├── app/
│   │   ├── api/               # FastAPI路由 (audit.py, qa.py, report.py)
│   │   ├── core/              # 核心双引擎
│   │   │   ├── neural/        # 神经引擎 (DeepSeek适配器)
│   │   │   ├── symbolic/      # 符号引擎 (Zen Engine规则校验)
│   │   │   └── orchestrator/  # LangGraph流程编排
│   │   ├── services/          # 业务服务层
│   │   └── models/            # Pydantic数据模型
│   └── tests/
├── frontend/                   # React前端
│   ├── src/
│   │   ├── components/        # Dashboard, Trace, Chat 组件
│   │   ├── services/api.ts    # 后端API封装
│   │   └── App.tsx            # 主应用
├── rules/                      # 审计规则库 (JSON格式)
│   ├── accounting/            # 会计准则规则
│   ├── tax/                   # 税法规则
│   └── internal_control/      # 内控规则
└── docker-compose.yml
```

## 关键技术决策

1. **双引擎架构**：神经引擎分析 → 符号引擎校验 → REJECTED则反馈纠偏（最多3次）
2. **推理模式切换**：环境变量 `INFERENCE_MODE=api|local` 控制
3. **规则引擎**：Zen Engine (Rust) 的 Python 绑定，规则定义为 JSON 表达式树
4. **前后端分离**：Vite 开发代理转发 `/api` 到后端

## 环境变量

必须配置 `.env`（参考 `.env.example`）：
- `INFERENCE_MODE`: `api`（调用DeepSeek API）或 `local`（vLLM本地部署）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（api模式必须）
- `DATABASE_URL`: PostgreSQL连接字符串

## API 端点

- `POST /api/v1/audit/upload` - 上传财务报表（PDF/Excel，≤10MB）
- `POST /api/v1/audit/start` - 启动审计任务
- `GET /api/v1/audit/{task_id}` - 查询审计结果
- `POST /api/v1/qa/ask` - 智能问答
- `POST /api/v1/report/generate` - 导出审计报告

## 规则定义格式

规则使用 JSON 表达式树，支持 JSONPath 选择器和容差配置：
```json
{
  "rule_id": "R001",
  "severity": "CRITICAL",
  "expression": {
    "operator": "equals",
    "left": "$.assets.total",
    "right": { "operator": "add", "operands": ["$.liabilities.total", "$.equity.total"] },
    "tolerance": 0.01
  }
}
```

## 设计文档

详细技术方案参见根目录 `FinCode最终版设计指导文档.md`，包含需求分析、架构设计、开发计划。
