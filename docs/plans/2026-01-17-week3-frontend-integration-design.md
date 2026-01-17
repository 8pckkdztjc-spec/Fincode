# Week 3: Frontend Integration Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create detailed implementation plan after this design is approved.

## Design Decisions

基于项目状态和用户需求确认以下设计：

### 1. 页面结构：单页面应用

使用 `react-router-dom` 管理不同视图：
- Dashboard（默认首页）
- Trace（审计轨迹查看）
- Chat（智能问答）

### 2. 文件上传：Ant Design Upload.Dragger

- 使用 Ant Design 的 `Upload` 组件库
- 支持拖拽上传
- 支持点击选择文件
- 显示上传进度

### 3. 数据刷新：自动轮询机制

- 审计启动后启动定时器
- 每 2 秒查询一次结果
- 完成后停止轮询

### 4. Dashboard 布局：居中 Modal 弹窗

- 上传功能使用 Modal 形式
- 点击"上传报表"弹出 Modal
- 保持 Dashboard 简洁

### 5. 状态管理：React 本地 State

- 使用 React Hooks (useState, useEffect)
- 管理上传状态、审计状态
- 避免引入 Redux 等复杂状态管理

---

## Component Architecture

### UploadModal Component

```typescript
interface UploadModalProps {
    visible: boolean
    onUploadSuccess: (documentId: string) => void
    onCancel: () => void
}

state:
    - file: File | null
    - uploading: boolean
    - progress: number
    - error: string | null
```

### Dashboard Component Enhancements

```typescript
state:
    - uploadingDocument: boolean
    - currentAuditId: string | null
    - auditStatus: 'idle' | 'processing' | 'completed' | 'failed'
    - auditResult: AuditResult | null
    - pollingInterval: NodeJS.Timeout | null
```

### Trace Component

- 使用 `Timeline` 组件展示推理链
- 添加展开/折叠功能
- 显示神经/符号引擎交互历史

### Chat Component Enhancements

- 添加 auditId 参数，支持上下文相关问答
- 显示用户问题和 AI 回复
- 添加加载状态显示

---

## Data Flow

```
用户操作
    ↓
UploadModal (选择文件)
    ↓
POST /api/audit/upload
    ↓
获取 document_id
    ↓
POST /api/audit/start
    ↓
轮询开始 (每 2 秒)
    ↓
GET /api/audit/result/{audit_id}
    ↓
更新 Dashboard (风险评分、违规列表、推理链)
```

---

## Technical Details

### Ant Design Upload.Dragger

```typescript
import { Upload } from 'antd'

<Upload.Dragger
    name="file"
    accept=".pdf,.xlsx"
    beforeUpload={handleBeforeUpload}
    customRequest={handleUpload}
>
    <p className="ant-upload-drag-icon">
        <InboxOutlined />
    </p>
    <p className="ant-upload-text">点击或拖拽文件上传</p>
</Upload.Dragger>
```

### Auto Polling Implementation

```typescript
useEffect(() => {
    if (auditStatus === 'processing' && !pollingInterval) {
        startPolling()
    }

    return () => {
        stopPolling()
    }
}, [auditStatus, currentAuditId])

const startPolling = () => {
    const interval = setInterval(() => {
        getAuditResult(currentAuditId)
    }, 2000)

    setPollingInterval(interval)
}

const stopPolling = () => {
    if (pollingInterval) {
        clearInterval(pollingInterval)
        setPollingInterval(null)
    }
}
```

### Status Types

```typescript
type AuditStatus = 'idle' | 'parsing' | 'analyzing' | 'validating' | 'completed' | 'failed'

interface AuditResult {
    audit_id: string
    document_id: string
    status: AuditStatus
    risk_score: number
    violations: Array<{
        rule_id: string
        severity: 'CRITICAL' | 'WARNING' | 'INFO'
        description: string
    }>
    reasoning_chain: string[]
    retry_count: number
}
```

---

## Files to Modify/Create

### Modify
- `frontend/src/App.tsx` - 添加 Router 和状态管理
- `frontend/src/components/Dashboard/index.tsx` - 集成上传 Modal 和轮询
- `frontend/src/components/Trace/index.tsx` - 连接真实数据
- `frontend/src/components/Chat/index.tsx` - 添加 auditId 支持

### Create
- `frontend/src/components/UploadModal/index.tsx` - 新建上传 Modal 组件

---

## User Experience Considerations

1. **上传反馈**
   - 显示上传进度
   - 成功后关闭 Modal
   - 自动跳转到审计结果

2. **审计进度**
   - 显示"解析中..."、"分析中..."、"验证中..."
   - 实时更新进度状态

3. **错误处理**
   - 友好错误提示
   - 提供重试按钮

4. **响应式设计**
   - 移动端适配
   - 使用 Ant Design 响应式栅格

---

## Next Steps

1. ✅ 确认设计（当前步骤）
2. 创建详细实现计划（writing-plans）
3. 设置 Git worktree
4. 逐步实现各个组件
5. 集成测试
6. 推送到 GitHub

---

**请确认此设计是否满足您的需求？**
- 单页面应用结构 ✓
- Ant Design Upload ✓
- 自动轮询机制 ✓
- Modal 弹窗上传 ✓
- React 本地 State ✓
