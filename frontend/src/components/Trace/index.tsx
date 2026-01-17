import { Timeline, Card, Tag } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, SyncOutlined } from '@ant-design/icons'

interface TraceStep {
    title: string
    description: string
    status: 'success' | 'error' | 'processing'
}

interface TraceViewerProps {
    ruleId?: string
    steps?: TraceStep[]
}

const defaultSteps: TraceStep[] = [
    { title: '文档解析', description: '成功提取资产负债表数据', status: 'success' },
    { title: 'AI 推理', description: '完成财务指标分析', status: 'success' },
    { title: '规则校验', description: '发现勾稽不平衡问题', status: 'error' },
    { title: '纠偏反馈', description: '已注入校验反馈', status: 'success' },
    { title: '二次推理', description: '重新分析财务数据', status: 'success' },
    { title: '规则通过', description: '所有规则校验通过', status: 'success' },
]

const statusIcons = {
    success: <CheckCircleOutlined style={{ color: '#52C41A' }} />,
    error: <CloseCircleOutlined style={{ color: '#FF4D4F' }} />,
    processing: <SyncOutlined spin style={{ color: '#1890FF' }} />,
}

function TraceViewer({ ruleId = 'R001', steps = defaultSteps }: TraceViewerProps) {
    return (
        <div>
            <h2 style={{ marginBottom: 16 }}>
                推理轨迹追溯 <Tag color="blue">{ruleId}</Tag>
            </h2>

            <Card>
                <Timeline
                    items={steps.map((step) => ({
                        dot: statusIcons[step.status],
                        children: (
                            <div>
                                <strong>{step.title}</strong>
                                <p style={{ color: '#8c8c8c', margin: 0 }}>{step.description}</p>
                            </div>
                        ),
                    }))}
                />
            </Card>
        </div>
    )
}

export default TraceViewer
