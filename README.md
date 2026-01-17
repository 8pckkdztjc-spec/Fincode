# FinCode - 神经符号协同财务审计助手

> **Neuro-Symbolic AI Financial Audit Assistant**  
> 基于 DeepSeek-R1 + Zen Engine 的智能财务合规审计系统

---

## 📋 项目简介

FinCode 是一款面向中小企业的智能财务审计助手，采用**神经-符号双引擎架构**：

- **神经引擎**：DeepSeek-R1 大语言模型，负责语义理解与推理
- **符号引擎**：Zen Engine 规则引擎，执行硬编码审计规则，确保"零幻觉"

核心特性：
- ✅ PDF/Excel 财务报表智能解析
- ✅ 勾稽平衡自动检验
- ✅ 思维链推理可视化
- ✅ 自然语言智能问答
- ✅ 一键生成审计报告

---

## 🛠 技术栈

| 层级 | 技术 | 版本 |
|:---|:---|:---|
| 神经引擎 | DeepSeek R1 API | - |
| 符号引擎 | Zen Engine | 1.x |
| 业务编排 | LangGraph | 0.2.x |
| 知识库 | KuzuDB | 0.4.x |
| 文档解析 | Docling | 2.x |
| 后端框架 | FastAPI | 0.109.x |
| 前端框架 | React + TypeScript | 18.x / 5.x |
| UI 组件 | Ant Design | 5.x |
| 数据库 | PostgreSQL | 15.x |

---

## 📁 目录结构

```
fincode/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # FastAPI 路由
│   │   ├── core/              # 核心模块
│   │   │   ├── neural/        # 神经引擎
│   │   │   ├── symbolic/      # 符号引擎
│   │   │   └── orchestrator/  # LangGraph 编排
│   │   ├── services/          # 业务服务
│   │   └── models/            # 数据模型
│   ├── tests/                 # 测试用例
│   └── requirements.txt
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # React 组件
│   │   ├── pages/             # 页面
│   │   └── services/          # API 调用
│   └── package.json
├── rules/                      # 审计规则库
│   ├── accounting/            # 会计准则规则
│   ├── tax/                   # 税法规则
│   └── internal_control/      # 内控规则
├── docker-compose.yml
└── README.md
```

---

## 🚀 快速启动

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 填写 DEEPSEEK_API_KEY

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 一键启动

```bash
docker-compose up -d
```

---

## 📖 开发文档

- [设计指导文档](./docs/FinCode最终版设计指导文档.md)

---

## 📜 许可证

MIT License

---

> **开发团队** | 2026
