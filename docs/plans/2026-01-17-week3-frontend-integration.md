# Week 3: Frontend Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完成前端界面与后端 API 的完整对接，实现文件上传、自动轮询审计结果、风险仪表盘数据联动、思维链可视化和智能问答功能。

**Architecture:**
- 使用 React Router 实现单页面应用（Dashboard 默认首页）
- Ant Design Upload.Dragger 实现文件上传
- React 本地 Hooks 管理状态（useState, useEffect）
- 自动轮询机制获取审计结果
- Modal 弹窗集成上传功能到 Dashboard

**Tech Stack:**
- React 18 + TypeScript
- Ant Design 5.15（Upload.Dragger 组件）
- react-router-dom 6.x（路由管理）
- Axios 1.6（HTTP 请求）

---

## Task 1: App Router Setup

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: Write failing test**

```bash
# Since App.tsx is a simple routing setup, we'll verify it works first
# Run: cd frontend && npm run dev
# Expected: Dev server starts, no errors
```

**Step 2: Run test to verify**

Run: `cd frontend && npm run dev` (手动验证路由配置）

**Step 3: Implement React Router**

```typescript
// frontend/src/App.tsx

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Trace from './components/Trace'
import Chat from './components/Chat'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trace/:auditId" element={<Trace />} />
        <Route path="/chat/:auditId" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

**Step 4: Run test to verify it passes**

Run: `cd frontend && npm run dev`

Expected: 应用正常启动，可以访问不同路由

**Step 5: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): add React Router for navigation"
```

---

## Task 2: Upload Modal Component

**Files:**
- Create: `frontend/src/components/UploadModal/index.tsx`

**Step 1: Write component skeleton**

```typescript
// frontend/src/components/UploadModal/index.tsx

import { useState } from 'react'
import { Modal, Upload, message, Progress, Alert } from 'antd'
import type { UploadFile } from 'antd/es/upload'

function UploadModal({ visible, onUploadSuccess, onCancel }: {
  visible: boolean
  onUploadSuccess: (documentId: string) => void
  onCancel: () => void
}) {
  const [file, setFile] = useState<UploadFile | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleUpload = async (options: any) => {
    if (!options.file) return

    setUploading(true)
    setProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', options.file)

      const onProgress = (event: { loaded: number, total: number }) => {
        if (event.total) {
          setProgress(Math.round((event.loaded / event.total) * 100))
        }
      }

      const response = await fetch('/api/v1/audit/upload', {
        method: 'POST',
        body: formData,
        onProgress,
      })

      if (response.ok) {
        const result = await response.json()
        message.success('上传成功')
        setProgress(100)
        onUploadSuccess(result.document_id)
        handleCancel()
      } else {
        message.error('上传失败')
      }
    } catch (error) {
      message.error('上传出错：' + (error as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handleCancel = () => {
    setFile(null)
    setProgress(0)
    setUploading(false)
    onCancel?.()
  }

  return (
    <Modal
      title="上传财务报表"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <div style={{ padding: 24 }}>
        <Upload.Dragger
          name="file"
          accept=".pdf,.xlsx"
          beforeUpload={(file) => {
            setFile(file)
          }}
          customRequest={handleUpload}
          disabled={uploading}
        >
          <p className="ant-upload-hint">
            <InboxOutlined style={{ fontSize: 48, color: '#1890FF' }} />
          </p>
          <p className="ant-upload-text">
            {uploading ? `上传中... ${progress}%` : '点击或拖拽文件上传'}
          </p>
        </Upload.Dragger>

        {progress > 0 && progress < 100 && (
          <Progress percent={progress} status="active" />
        )}

        {progress === 100 && (
          <Alert
            message="上传成功，正在解析文档..."
            type="success"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </div>
    </Modal>
  )
}

export default UploadModal
```

**Step 2: Run application to verify**

Run: `cd frontend && npm run dev` (手动验证组件)

Expected: 上传 Modal 可以正常显示和交互

**Step 3: Commit**

```bash
git add frontend/src/components/UploadModal/index.tsx
git commit -m "feat(frontend): add Upload Modal component with drag-drop support"
```

---

## Task 3: Dashboard Component with Upload Integration

**Files:**
- Modify: `frontend/src/components/Dashboard/index.tsx`

**Step 1: Write failing test (manual verification)**

No automated test for this task - we'll verify by running the app manually.

**Step 2: Implement state management**

```typescript
// Add to existing Dashboard component

import { useState, useEffect, useRef } from 'react'
import { Card, Button, Space, Spin, Tag } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import { uploadDocument, startAudit, getAuditResult } from '../../services/api'
import type { AuditResult } from '../../services/api'

function Dashboard() {
  // State for upload modal
  const [uploadModalVisible, setUploadModalVisible] = useState(false)
  const [currentAuditId, setCurrentAuditId] = useState<string | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Upload success handler
  const handleUploadSuccess = (documentId: string) => {
    setCurrentAuditId(documentId)
    startPolling(documentId)
  }

  // Auto-polling implementation
  const startPolling = (auditId: string) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
    }

    // Poll every 2 seconds
    pollingIntervalRef.current = setInterval(async () => {
      const result = await getAuditResult(auditId)

      if (result.status === 'completed') {
        stopPolling()
        setAuditData(result)
      } else if (result.status === 'failed') {
        stopPolling()
        // Handle error
      }
      // Continue polling for 'processing' status
    }, 2000)
  }

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [])
```

**Step 3: Replace mock data with real API calls**

```typescript
// In Dashboard component, replace the mock data section

const [auditData, setAuditData] = useState<AuditResult | null>(null)

// Replace the mockData variable with real state
// Remove mockData array and use auditData from API

// In the return JSX, replace mockData.map() with:
{auditData && (
  <Card title="风险明细">
    <Table columns={columns} dataSource={auditData.violations || []} pagination={false} />
  </Card>
)}
```

**Step 4: Add trigger for Upload Modal**

```typescript
// Add to Dashboard component

return (
  <div>
    <Space direction="vertical" style={{ width: '100%', padding: 24 }} size="large">
      <Card
        title="上传财务报表"
        style={{ textAlign: 'center', minHeight: 200 }}
      >
        <InboxOutlined style={{ fontSize: 64, color: '#1890FF', marginBottom: 16 }} />
        <Button
          type="primary"
          size="large"
          onClick={() => setUploadModalVisible(true)}
        >
          上传报表
        </Button>
      </Card>

      {/* Risk overview section (keep existing) */}
      {auditData && <RiskOverview riskScore={auditData.risk_score} />}
      {auditData && <RiskDetail violations={auditData.violations} />}
      {auditData && <ReasoningChain steps={auditData.reasoning_chain} />}
    </Space>

    <UploadModal
      visible={uploadModalVisible}
      onUploadSuccess={handleUploadSuccess}
      onCancel={() => setUploadModalVisible(false)}
    />
  </div>
)
```

**Step 5: Run application to verify**

Run: `cd frontend && npm run dev` (手动验证）

Expected: 点击上传按钮，打开 Modal，选择文件，上传后自动跳转到审计结果

**Step 6: Commit**

```bash
git add frontend/src/components/Dashboard/index.tsx
git commit -m "feat(frontend): integrate Upload Modal and auto-polling in Dashboard"
```

---

## Task 4: API Service Enhancement (Polling Support)

**Files:**
- Modify: `frontend/src/services/api.ts`

**Step 1: Write failing test**

No test - API service methods are straightforward.

**Step 2: Add polling support helper**

```typescript
// Add to api.ts

export const startPolling = async (auditId: string, onResult: (result: AuditResult) => void) => {
  const maxAttempts = 150 // 5 minutes at 2s intervals
  let attempts = 0

  while (attempts < maxAttempts) {
    const result = await getAuditResult(auditId)
    attempts++

    if (result.status === 'completed' || result.status === 'failed') {
      onResult(result)
      return
    }

    // Wait 2 seconds before next poll
    await new Promise(resolve => setTimeout(resolve, 2000))
  }

  throw new Error('Polling timeout')
}
```

**Step 3: Run application to verify**

Run: `cd frontend && npm run dev` (手动验证)

Expected: 轮询机制正常工作

**Step 4: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat(frontend): add polling support to API service"
```

---

## Task 5: Trace Component Integration

**Files:**
- Modify: `frontend/src/components/Trace/index.tsx`

**Step 1: Write failing test (manual)**

Verify component works after data integration.

**Step 2: Connect to real audit data**

```typescript
// Add props to Trace component

interface TraceProps {
  auditId: string
}

function Trace({ auditId }: TraceProps) {
  // Fetch audit result when auditId changes
  useEffect(() => {
    if (auditId) {
      getAuditResult(auditId).then(setAuditData)
    }
  }, [auditId])

  // Remove mock data
  // Replace with: const [auditData, setAuditData] = useState<AuditResult | null>(null)
```

**Step 3: Enhance visualization**

```typescript
// Add interactive features to Timeline

const [expandedSteps, setExpandedSteps] = useState<number[]>([])

const toggleStep = (index: number) => {
  if (expandedSteps.includes(index)) {
    setExpandedSteps(expandedSteps.filter(i => i !== index))
  } else {
    setExpandedSteps([...expandedSteps, index])
  }
}

// In Timeline component, add onClick to each item:
<Timeline.Item
  dot={item.dot}
  onClick={() => toggleStep(index)}
  style={{ cursor: 'pointer' }}
>
  {item.content}
</Timeline.Item>
```

**Step 4: Run application to verify**

Run: `cd frontend && npm run dev` (手动验证)

Expected: 点击风险项目可以跳转到 Trace 页面，查看详细推理链

**Step 5: Commit**

```bash
git add frontend/src/components/Trace/index.tsx
git commit -m "feat(frontend): connect Trace component to real audit data"
```

---

## Task 6: Chat Component Integration

**Files:**
- Modify: `frontend/src/components/Chat/index.tsx`

**Step 1: Write failing test (manual)**

Verify component works with audit context.

**Step 2: Add audit context to API calls**

```typescript
// Modify askQuestion function to support audit context

export const askQuestion = async (
  question: string,
  auditId?: string
): Promise<QAResponse> => {
  const response = await fetch(`${API_BASE_URL}/qa/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, audit_id: auditId }),
  })

  if (!response.ok) {
    throw new Error('问答请求失败')
  }

  return response.json()
}
```

**Step 3: Update Chat component to use auditId**

```typescript
// In Chat component, update the askQuestion call

interface ChatProps {
  auditId?: string
}

function Chat({ auditId }: ChatProps) {
  // In the handleSend function, pass auditId
  const handleSend = async () => {
    if (!inputValue.trim()) return

    setLoading(true)

    const result = await askQuestion(inputValue, auditId)

    // Add user message
    setMessages((prev) => [...prev, userMessage])

    // Add AI response
    setTimeout(() => {
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: result.answer || '抱歉，我无法回答这个问题'
      }])
      setLoading(false)
      setInputValue('')
    }, 1000)
  }
}
```

**Step 4: Run application to verify**

Run: `cd frontend && npm run dev` (手动验证)

Expected: 问答功能与审计结果关联

**Step 5: Commit**

```bash
git add frontend/src/components/Chat/index.tsx
git commit -m "feat(frontend): connect Chat component to audit context"
```

---

## Task 7: Integration Testing

**Files:**
- None (manual testing)

**Step 1: Manual end-to-end testing**

Test the complete user flow:
1. 打开 Dashboard (`/`)
2. 点击"上传报表"按钮
3. 选择测试文件并上传
4. 观察上传进度
5. 等待自动轮询获取审计结果
6. 查看风险仪表盘更新
7. 点击风险项目，跳转到 Trace 页面查看推理链
8. 在 Chat 页面询问审计相关问题

**Step 2: Verify responsive design**

- 测试移动端适配
- 验证 Modal 在不同屏幕尺寸下的表现
- 检查 Dashboard 布局的响应性

**Step 3: Verify auto-polling**

- 确认审计完成后停止轮询
- 验证网络错误时的降级处理
- 测试手动刷新按钮功能

**Step 4: Run linter**

Run: `cd frontend && npm run lint`

Expected: 无 lint 错误

**Step 5: Commit**

```bash
git commit -m "chore(frontend): integration testing complete"
```

---

## Task 8: Final Polish and Deployment

**Files:**
- Modify: `frontend/package.json`, `frontend/src/main.tsx` (if needed)

**Step 1: Add VITE_API_BASE_URL to .env**

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**Step 2: Update main.tsx to set base URL**

```typescript
// frontend/src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// Update api.ts to use the environment variable
// Or hardcode the base URL for development

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

**Step 3: Build and verify**

Run: `cd frontend && npm run build`

Expected: 构建成功，无错误

**Step 4: Run dev server to verify**

Run: `cd frontend && npm run dev`

Expected: 前端应用正常启动，可以与后端通信

**Step 5: Commit**

```bash
git add frontend/package.json frontend/src/main.tsx frontend/.env
git commit -m "chore(frontend): add environment configuration and final polish"
```

---

## Verification Checklist

Before claiming Week 3 is complete:

- [ ] App Router 配置完成（/、/trace、/chat 路由）
- [ ] Upload Modal 组件创建并正常工作
- [ ] Dashboard 集成上传功能和轮询机制
- [ ] API 服务层增强（轮询支持）
- [ ] Trace 组件对接真实审计数据
- [ ] Chat 组件支持审计上下文
- [ ] 端到端测试通过（完整用户流程）
- [ ] 响应式设计验证
- [ ] Lint 通过（`npm run lint`）
- [ ] 所有提交已推送

---

## Summary

This plan implements complete Week 3 frontend integration:

1. **Router Setup**: React Router with route configuration
2. **Upload Modal**: Ant Design Upload.Dragger with progress tracking
3. **Dashboard Integration**: Upload trigger + auto-polling + audit result display
4. **API Enhancement**: Polling mechanism for long-running audit tasks
5. **Trace Component**: Real data connection + interactive features
6. **Chat Component**: Audit context support
7. **Integration Testing**: End-to-end user flow verification
8. **Final Polish**: Environment configuration, build verification

Total estimated time: 3-4 hours
