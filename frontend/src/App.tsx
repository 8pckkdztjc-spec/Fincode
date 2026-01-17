import { Layout, Menu, theme } from 'antd'
import {
    DashboardOutlined,
    FileTextOutlined,
    AuditOutlined,
    MessageOutlined,
    SettingOutlined,
} from '@ant-design/icons'
import Dashboard from './components/Dashboard'

const { Header, Sider, Content } = Layout

function App() {
    const {
        token: { colorBgContainer },
    } = theme.useToken()

    const menuItems = [
        { key: '1', icon: <DashboardOutlined />, label: '首页' },
        { key: '2', icon: <FileTextOutlined />, label: '报表' },
        { key: '3', icon: <AuditOutlined />, label: '审计' },
        { key: '4', icon: <MessageOutlined />, label: '问答' },
        { key: '5', icon: <SettingOutlined />, label: '设置' },
    ]

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
                        defaultSelectedKeys={['1']}
                        style={{ height: '100%', borderRight: 0 }}
                        items={menuItems}
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
                        <Dashboard />
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    )
}

export default App
