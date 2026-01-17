import { useState, useEffect, useRef } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Progress, Button, message, Space } from 'antd'
import { UploadOutlined, SyncOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import UploadModal from '../UploadModal'
import { startAudit, getAuditResult } from '../../services/api'
import type { AuditResult } from '../../services/api'

interface RiskItem {
    key: string
    ruleId: string
    description: string
    severity: string
}

const severityConfig: Record<string, { color: string; text: string }> = {
    CRITICAL: { color: '#FF4D4F', text: '严重' },
    WARNING: { color: '#FAAD14', text: '警告' },
    INFO: { color: '#52C41A', text: '提示' },
}

const columns: ColumnsType<RiskItem> = [
    {
        title: '规则编号',
        dataIndex: 'ruleId',
        key: 'ruleId',
    },
    {
        title: '描述',
        dataIndex: 'description',
        key: 'description',
    },
    {
        title: '等级',
        dataIndex: 'severity',
        key: 'severity',
        render: (severity: string) => {
            const config = severityConfig[severity] || severityConfig.INFO
            return (
                <Tag color={config.color}>
                    {config.text}
                </Tag>
            )
        },
    },
    {
        title: '操作',
        key: 'action',
        render: () => <a>查看详情</a>,
    },
]

const initialData: RiskItem[] = []

function Dashboard() {
    const [uploadModalVisible, setUploadModalVisible] = useState(false)
    const [auditData, setAuditData] = useState<AuditResult | null>(null)
    const [polling, setPolling] = useState(false)
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current)
            }
        }
    }, [])

    useEffect(() => {
        if (polling && auditData?.audit_id) {
            timerRef.current = setInterval(async () => {
                try {
                    const result = await getAuditResult(auditData.audit_id)
                    setAuditData(result)

                    if (result.status === 'COMPLETED' || result.status === 'FAILED') {
                        setPolling(false)
                        if (timerRef.current) clearInterval(timerRef.current)
                        if (result.status === 'COMPLETED') {
                            message.success('审计完成')
                        } else {
                            message.error('审计失败')
                        }
                    }
                } catch (error) {
                    console.error('Polling error:', error)
                }
            }, 2000)
        } else {
            if (timerRef.current) {
                clearInterval(timerRef.current)
            }
        }
    }, [polling, auditData?.audit_id])

    const handleUploadSuccess = async (documentId: string) => {
        try {
            message.loading({ content: '正在启动审计...', key: 'startAudit' })
            const result = await startAudit(documentId)
            setAuditData(result)
            setPolling(true)
            message.success({ content: '审计已启动，正在分析...', key: 'startAudit' })
        } catch (error) {
            message.error({ content: '启动审计失败', key: 'startAudit' })
        }
    }

    const tableData = auditData?.violations?.map((v, index) => ({
        key: String(index),
        ruleId: v.rule_id,
        description: v.description,
        severity: v.severity,
    })) || initialData

    const riskScore = auditData?.risk_score || 0
    const violationCount = auditData?.violations?.length || 0
    const criticalCount = auditData?.violations?.filter(v => v.severity === 'CRITICAL').length || 0
    const warningCount = auditData?.violations?.filter(v => v.severity === 'WARNING').length || 0
    const infoCount = auditData?.violations?.filter(v => v.severity === 'INFO').length || 0
    
    const passRate = 100 - riskScore

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h2 style={{ margin: 0 }}>风险概览</h2>
                <Space>
                    {polling && <Tag icon={<SyncOutlined spin />} color="processing">正在分析</Tag>}
                    <Button 
                        type="primary" 
                        icon={<UploadOutlined />} 
                        onClick={() => setUploadModalVisible(true)}
                        disabled={polling}
                    >
                        上传报表
                    </Button>
                </Space>
            </div>

            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="综合风险分"
                            value={riskScore}
                            valueStyle={{ color: riskScore > 60 ? '#FF4D4F' : '#FAAD14', fontSize: 36 }}
                            suffix="/ 100"
                        />
                        <Progress 
                            percent={riskScore} 
                            status="active" 
                            strokeColor={riskScore > 60 ? '#FF4D4F' : '#FAAD14'} 
                            showInfo={false} 
                        />
                        <div style={{ color: '#8c8c8c', marginTop: 8 }}>
                            {riskScore > 60 ? '高风险' : riskScore > 30 ? '中等风险' : '低风险'}
                        </div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="检出问题数"
                            value={violationCount}
                            valueStyle={{ color: '#FF4D4F' }}
                        />
                        <div style={{ marginTop: 16, color: '#8c8c8c' }}>
                            严重 {criticalCount} / 警告 {warningCount} / 提示 {infoCount}
                        </div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="合规通过率"
                            value={passRate}
                            precision={1}
                            valueStyle={{ color: '#52C41A' }}
                            suffix="%"
                        />
                        <Progress percent={passRate} status="success" showInfo={false} />
                    </Card>
                </Col>
            </Row>

            <Card title="风险明细">
                <Table 
                    columns={columns} 
                    dataSource={tableData} 
                    pagination={false} 
                    locale={{ emptyText: '暂无数据，请上传报表进行审计' }}
                />
            </Card>

            <UploadModal
                open={uploadModalVisible}
                onClose={() => setUploadModalVisible(false)}
                onSuccess={handleUploadSuccess}
            />
        </div>
    )
}

export default Dashboard
