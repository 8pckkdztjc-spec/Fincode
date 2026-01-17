/**
 * API 服务模块
 * 封装后端 API 调用
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

interface UploadResponse {
    document_id: string
    filename: string
    status: string
}

interface AuditResult {
    audit_id: string
    status: string
    risk_score: number | null
    violations: Array<{
        rule_id: string
        severity: string
        description: string
    }>
    reasoning_chain: string[]
}

interface QAResponse {
    answer: string
    sources: Array<{ title: string; url: string }>
    confidence: number
}

/**
 * 上传财务报表
 */
export async function uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/audit/upload`, {
        method: 'POST',
        body: formData,
    })

    if (!response.ok) {
        throw new Error('上传失败')
    }

    return response.json()
}

/**
 * 启动审计
 */
export async function startAudit(documentId: string): Promise<AuditResult> {
    const response = await fetch(`${API_BASE_URL}/audit/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: documentId }),
    })

    if (!response.ok) {
        throw new Error('启动审计失败')
    }

    return response.json()
}

/**
 * 获取审计结果
 */
export async function getAuditResult(auditId: string): Promise<AuditResult> {
    const response = await fetch(`${API_BASE_URL}/audit/result/${auditId}`)

    if (!response.ok) {
        throw new Error('获取审计结果失败')
    }

    return response.json()
}

/**
 * 智能问答
 */
export async function askQuestion(question: string, auditId?: string): Promise<QAResponse> {
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
