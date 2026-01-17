import { Layout, Menu, theme } from 'antd'
import {
    DashboardOutlined,
    FileTextOutlined,
    AuditOutlined,
    MessageOutlined,
    SettingOutlined,
} from '@ant-design/icons'
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import TraceViewer from './components/Trace'
import ChatPanel from './components/Chat'

const { Header, Sider, Content } = Layout

function AppLayout() {
    const {
        token: { colorBgContainer },
    } = theme.useToken()
    const navigate = useNavigate()
    const location = useLocation()

    const menuItems = [
        { key: '/', icon: <DashboardOutlined />, label: '首页' },
        { key: '/report', icon: <FileTextOutlined />, label: '报表' },
        { key: '/audit', icon: <AuditOutlined />, label: '审计' },
        { key: '/chat/new', icon: <MessageOutlined />, label: '问答' },
        { key: '/settings', icon: <SettingOutlined />, label: '设置' },
    ]

    const getSelectedKey = () => {
        const path = location.pathname
        if (path.startsWith('/chat')) return '/chat/new'
        if (path.startsWith('/trace')) return '/audit'
        return path === '/' ? '/' : path
    }

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{
                display: 'flex',
                alignItems: 'center',
                background: '#001529',
                padding: '0 24px'
            }}>
                <div style={{
                    color: '#fff',
                    fontSize: '20px',
                    fontWeight: 'bold',
                    marginRight: '48px'
                }}>
                    FinCode
                </div>
                <span style={{ color: 'rgba(255,255,255,0.65)' }}>
                    神经符号协同财务审计助手
                </span>
            </Header>
            <Layout>
                <Sider width={200} style={{ background: colorBgContainer }}>
                    <Menu
                        mode="inline"
                        selectedKeys={[getSelectedKey()]}
                        style={{ height: '100%', borderRight: 0 }}
                        items={menuItems}
                        onClick={({ key }) => navigate(key)}
                    />
                </Sider>
                <Layout style={{ padding: '24px' }}>
                    <Content
                        style={{
                            padding: 24,
                            margin: 0,
                            minHeight: 280,
                            background: colorBgContainer,
                            borderRadius: 8,
                        }}
                    >
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/trace/:auditId" element={<TraceViewer />} />
                            <Route path="/chat/:auditId" element={<ChatPanel />} />
                            <Route path="/chat/new" element={<ChatPanel />} />
                        </Routes>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    )
}

function App() {
    return (
        <BrowserRouter>
            <AppLayout />
        </BrowserRouter>
    )
}

export default App
