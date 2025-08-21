import React, { useState } from 'react';
import { Card, Typography, Space, Input, Button, Divider, Alert, Row, Col } from 'antd';
import { WalletClusterBadge } from '../components/WalletClusterBadge';
import { WalletClusterProvider } from '../contexts/WalletClusterContext';

const { Title, Text, Paragraph } = Typography;

const WalletClusterExample = () => {
  const [walletAddress, setWalletAddress] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [showBadge, setShowBadge] = useState(false);

  const handleAnalyze = () => {
    if (inputValue.trim()) {
      setWalletAddress(inputValue.trim());
      setShowBadge(true);
    }
  };

  const handleClusterData = (data) => {
    console.log('Cluster data received:', data);
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <Title level={2}>Wallet Cluster Badge Example</Title>
      <Paragraph>
        This example demonstrates how to use the <Text code>WalletClusterBadge</Text> component
        to display wallet clustering information and risk analysis.
      </Paragraph>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} md={12}>
          <Card title="Interactive Example" style={{ height: '100%' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Enter a wallet address to analyze:</Text>
                <Input.Search
                  placeholder="0x..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onSearch={handleAnalyze}
                  enterButton="Analyze"
                  style={{ marginTop: 8 }}
                />
              </div>

              <Divider>Result</Divider>

              {showBadge && (
                <div style={{ textAlign: 'center', padding: '16px 0' }}>
                  <WalletClusterBadge 
                    walletAddress={walletAddress}
                    onClusterData={handleClusterData}
                    style={{ margin: '0 auto' }}
                  />
                </div>
              )}

              <Alert 
                message="How it works"
                description={
                  <ul>
                    <li>Enter a wallet address and click 'Analyze'</li>
                    <li>The badge will show cluster information if available</li>
                    <li>Hover over the badge to see detailed cluster information</li>
                    <li>Click the refresh icon to update the cluster data</li>
                  </ul>
                }
                type="info"
                showIcon
              />
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="Usage Examples" style={{ height: '100%' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Basic Usage:</Text>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
                  {`<WalletClusterBadge 
  walletAddress="0x1234..." 
  autoFetch={true}
  showDetails={true}
/>`}
                </pre>
              </div>

              <div>
                <Text strong>With Callback:</Text>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
                  {`<WalletClusterBadge 
  walletAddress="0x1234..."
  onClusterData={(data) => {
    console.log('Cluster data:', data);
  }}
/>`}
                </pre>
              </div>

              <div>
                <Text strong>Custom Styling:</Text>
                <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
                  {`<WalletClusterBadge 
  walletAddress="0x1234..."
  style={{ 
    border: '1px solid #d9d9d9',
    padding: '4px 8px',
    borderRadius: 4
  }}
/>`}
                </pre>
              </div>

              <Divider>Component Props</Divider>
              
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Prop</th>
                    <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Type</th>
                    <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Default</th>
                    <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}><Text code>walletAddress</Text></td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>string</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>''</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>The wallet address to analyze</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}><Text code>autoFetch</Text></td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>boolean</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>true</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Whether to automatically fetch cluster data on mount</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}><Text code>showDetails</Text></td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>boolean</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>true</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Whether to show detailed popover on hover</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}><Text code>size</Text></td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>'small' | 'default' | 'large'</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>'default'</td>
                    <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>Size of the badge</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '8px' }}><Text code>onClusterData</Text></td>
                    <td style={{ padding: '8px' }}>function</td>
                    <td style={{ padding: '8px' }}>undefined</td>
                    <td style={{ padding: '8px' }}>Callback when cluster data is loaded/refreshed</td>
                  </tr>
                </tbody>
              </table>
            </Space>
          </Card>
        </Col>
      </Row>

      <Card title="Implementation Notes" style={{ marginTop: 24 }}>
        <Title level={4}>Setup</Title>
        <Paragraph>
          To use the WalletClusterBadge component, you need to wrap your application with the <Text code>WalletClusterProvider</Text>:
        </Paragraph>
        
        <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
{`import React from 'react';
import { WalletClusterProvider } from './contexts/WalletClusterContext';
import App from './App';

function Root() {
  return (
    <WalletClusterProvider>
      <App />
    </WalletClusterProvider>
  );
}

export default Root;`}
        </pre>

        <Title level={4} style={{ marginTop: 24 }}>API Integration</Title>
        <Paragraph>
          The component integrates with the following API endpoints:
        </Paragraph>
        <ul>
          <li><Text code>GET /api/v1/wallets/&#123;address&#125;/cluster</Text> - Get cluster data for a single wallet</li>
          <li><Text code>POST /api/v1/wallets/batch/cluster</Text> - Start batch processing for multiple wallets</li>
          <li><Text code>WS /ws/batch/&#123;job_id&#125;</Text> - WebSocket endpoint for real-time updates on batch jobs</li>
        </ul>

        <Title level={4} style={{ marginTop: 24 }}>Error Handling</Title>
        <Paragraph>
          The component handles various error cases:
        </Paragraph>
        <ul>
          <li>Network errors are caught and displayed to the user</li>
          <li>Invalid wallet addresses are validated before making API calls</li>
          <li>WebSocket reconnection is handled automatically</li>
        </ul>
      </Card>
    </div>
  );
};

// Wrap with provider for the example
const WalletClusterExampleWrapper = () => (
  <WalletClusterProvider>
    <WalletClusterExample />
  </WalletClusterProvider>
);

export default WalletClusterExampleWrapper;
