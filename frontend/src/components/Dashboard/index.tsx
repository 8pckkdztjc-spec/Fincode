import { Card, Row, Col, Statistic, Table, Tag, Progress } from 'antd'
import type { ColumnsType } from 'antd/es/table'

interface RiskItem {
    key: string
    ruleId: string
    description: string
    severity: 'CRITICAL' | 'WARNING' | 'INFO'
}

const severityConfig = {
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
        render: (severity: keyof typeof severityConfig) => (
            <Tag color={severityConfig[severity].color}>
                {severityConfig[severity].text}
            </Tag>
        ),
    },
    {
        title: '操作',
        key: 'action',
        render: () => <a>查看详情</a>,
    },
]

// 示例数据
const mockData: RiskItem[] = [
    { key: '1', ruleId: 'R001', description: '资产负债表勾稽不平衡', severity: 'CRITICAL' },
    { key: '2', ruleId: 'R012', description: '应收账款周转异常', severity: 'WARNING' },
    { key: '3', ruleId: 'R005', description: '存货计价方法合规', severity: 'INFO' },
]

function Dashboard() {
    return (
        <div>
            <h2 style={{ marginBottom: 24 }}>风险概览</h2>

            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="综合风险分"
                            value={72}
                            valueStyle={{ color: '#FAAD14', fontSize: 36 }}
                            suffix="/ 100"
                        />
                        <Progress percent={72} status="active" strokeColor="#FAAD14" showInfo={false} />
                        <div style={{ color: '#FAAD14', marginTop: 8 }}>中等风险</div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="检出问题数"
                            value={3}
                            valueStyle={{ color: '#FF4D4F' }}
                        />
                        <div style={{ marginTop: 16, color: '#8c8c8c' }}>
                            严重 1 / 警告 1 / 提示 1
                        </div>
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic
                            title="合规通过率"
                            value={85.7}
                            precision={1}
                            valueStyle={{ color: '#52C41A' }}
                            suffix="%"
                        />
                        <Progress percent={85.7} status="success" showInfo={false} />
                    </Card>
                </Col>
            </Row>

            <Card title="风险明细">
                <Table columns={columns} dataSource={mockData} pagination={false} />
            </Card>
        </div>
    )
}

export default Dashboard
