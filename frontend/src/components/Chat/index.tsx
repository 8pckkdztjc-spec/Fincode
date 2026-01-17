import { useState } from 'react'
import { Card, Input, Button, List, Avatar, Spin } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
}

function ChatPanel() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: '您好！我是 FinCode 智能助手，可以帮您解答财务审计相关问题。请问有什么可以帮您？',
        },
    ])
    const [inputValue, setInputValue] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSend = async () => {
        if (!inputValue.trim()) return

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
        }

        setMessages((prev) => [...prev, userMessage])
        setInputValue('')
        setLoading(true)

        // TODO: 调用后端 API
        setTimeout(() => {
            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: '这是一个示例回复。完整功能将接入 DeepSeek R1 进行智能问答。',
            }
            setMessages((prev) => [...prev, assistantMessage])
            setLoading(false)
        }, 1000)
    }

    return (
        <Card title="智能问答" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflowY: 'auto', marginBottom: 16 }}>
                <List
                    itemLayout="horizontal"
                    dataSource={messages}
                    renderItem={(item) => (
                        <List.Item style={{ borderBottom: 'none', padding: '8px 0' }}>
                            <List.Item.Meta
                                avatar={
                                    <Avatar
                                        icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                                        style={{ backgroundColor: item.role === 'user' ? '#1890FF' : '#52C41A' }}
                                    />
                                }
                                title={item.role === 'user' ? '您' : 'FinCode'}
                                description={item.content}
                            />
                        </List.Item>
                    )}
                />
                {loading && (
                    <div style={{ textAlign: 'center', padding: 16 }}>
                        <Spin tip="思考中..." />
                    </div>
                )}
            </div>

            <Input.Group compact style={{ display: 'flex' }}>
                <Input
                    placeholder="请输入您的问题..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onPressEnter={handleSend}
                    style={{ flex: 1 }}
                />
                <Button type="primary" icon={<SendOutlined />} onClick={handleSend}>
                    发送
                </Button>
            </Input.Group>
        </Card>
    )
}

export default ChatPanel
