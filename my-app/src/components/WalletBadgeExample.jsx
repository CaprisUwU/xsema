import React, { useState } from 'react';
import { Card, Button, Input, Space, Divider, Typography } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import WalletClusterBadge from './WalletClusterBadge';

const { Title, Text, Paragraph } = Typography;

// Mock data for the example
const MOCK_GROUP_DATA = {
  wallet_address: "0x1234...abcd",
  group_members: [
    "0x1234...abcd",
    "0x5678...ef01",
    "0x9abc...2345"
  ],
  security_rating: 0.75
};

const WalletBadgeExample = () => {
  const [walletAddress, setWalletAddress] = useState("0x1234...abcd");
  const [showBadge, setShowBadge] = useState(true);
  const [loading, setLoading] = useState(false);
  
  // Simulate loading data
  const refreshData = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  return (
    <Card 
      title={
        <Space>
          <span>Wallet Group Badge</span>
          <Text type="secondary" style={{ fontSize: 14, fontWeight: 'normal' }}>
            <InfoCircleOutlined /> Hover over the badge to see group details
          </Text>
        </Space>
      }
      style={{ maxWidth: 800, margin: '20px auto' }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <Title level={5}>Example Usage:</Title>
          <div style={{ 
            padding: '16px', 
            backgroundColor: '#f5f5f5', 
            borderRadius: '8px',
            margin: '12px 0'
          }}>
            <Text>Wallet Address: {walletAddress}</Text>
            {showBadge && (
              <div style={{ marginTop: '8px' }}>
                <WalletClusterBadge 
                  walletAddress={walletAddress}
                  clusterData={MOCK_GROUP_DATA}
                  loading={loading}
                  showDetails={true}
                />
              </div>
            )}
          </div>
        </div>

        <Divider orientation="left">Interactive Demo</Divider>
        
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div>
            <Text strong>Wallet Address:</Text>
            <Input 
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              placeholder="Enter wallet address"
              style={{ marginTop: '8px' }}
            />
          </div>
          
          <Space>
            <Button 
              type="primary" 
              onClick={refreshData}
              loading={loading}
            >
              Refresh Data
            </Button>
            <Button 
              onClick={() => setShowBadge(!showBadge)}
            >
              {showBadge ? 'Hide Badge' : 'Show Badge'}
            </Button>
          </Space>
        </Space>

        <Divider orientation="left">Code Example</Divider>
        
        <pre style={{ 
          backgroundColor: '#f6f8fa', 
          padding: '16px', 
          borderRadius: '6px',
          overflowX: 'auto'
        }}>
          <code>
{`import WalletClusterBadge from './components/WalletClusterBadge';

// In your component:
<WalletClusterBadge
  walletAddress="0x1234...abcd"
  clusterData={{
    wallet_address: "0x1234...abcd",
    group_members: [
      "0x1234...abcd",
      "0x5678...ef01",
      "0x9abc...2345"
    ],
    security_rating: 0.75
  }}
  loading={false}
  showDetails={true}
/>`}
          </code>
        </pre>

        <div>
          <Title level={5}>Props:</Title>
          <ul>
            <li><Text strong>walletAddress</Text> (string, required) - The wallet address to display</li>
            <li><Text strong>clusterData</Text> (object) - Group information including members and security rating</li>
            <li><Text strong>loading</Text> (boolean) - Shows a loading spinner when true</li>
            <li><Text strong>showDetails</Text> (boolean) - Enables/disables the hover details popover</li>
            <li><Text strong>size</Text> (string) - Size of the badge ('small' or 'default')</li>
          </ul>
        </div>
      </Space>
    </Card>
  );
};

export default WalletBadgeExample;
