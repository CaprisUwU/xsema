import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Badge, Tooltip, Popover, List, Typography, Alert, Space, Spin, Button } from 'antd';
import { InfoCircleOutlined, TeamOutlined, WarningOutlined, ReloadOutlined } from '@ant-design/icons';
import { useWalletCluster } from '../contexts/WalletClusterContext';

const { Text } = Typography;

/**
 * Displays wallet clustering information in a compact badge format
 */
const WalletClusterBadge = ({ 
  walletAddress, 
  autoFetch = true,
  showDetails = true,
  size = 'default',
  onClusterData,
  ...props
}) => {
  const [visible, setVisible] = useState(false);
  const { 
    getClusterData, 
    fetchWalletCluster, 
    isLoading 
  } = useWalletCluster();
  
  // Get cluster data from context
  const clusterData = getClusterData(walletAddress);
  const loading = isLoading(walletAddress);
  
  // Process cluster data for display
  const clusterInfo = clusterData ? {
    clusterSize: clusterData.cluster_members?.length || 0,
    riskScore: clusterData.risk_score || 0,
    members: clusterData.cluster_members || []
  } : {
    clusterSize: 0,
    riskScore: 0,
    members: []
  };

  // Fetch cluster data if autoFetch is enabled
  useEffect(() => {
    if (autoFetch && walletAddress && !clusterData) {
      fetchWalletCluster(walletAddress)
        .then(data => {
          if (onClusterData && data) {
            onClusterData(data);
          }
        })
        .catch(console.error);
    }
  }, [walletAddress, autoFetch, clusterData, fetchWalletCluster, onClusterData]);

  // Determine badge status based on risk score
  const getRiskLevel = (score) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.4) return 'warning';
    return 'success';
  };

  // Format risk score for display
  const formatRiskScore = (score) => {
    return (score * 100).toFixed(0) + '%';
  };

  // Get business-friendly security level description
  const getSecurityLevel = (score) => {
    if (score >= 0.7) return 'High Risk';
    if (score >= 0.4) return 'Moderate Risk';
    return 'Low Risk';
  };

  // Handle popover visibility and manual refresh
  const handleRefresh = useCallback(() => {
    fetchWalletCluster(walletAddress)
      .then(data => {
        if (onClusterData && data) {
          onClusterData(data);
        }
        message.success('Wallet cluster data refreshed');
      })
      .catch(error => {
        console.error('Error refreshing wallet cluster data:', error);
        message.error('Failed to refresh wallet cluster data');
      });
  }, [walletAddress, fetchWalletCluster, onClusterData]);

  // Loading state
  if (loading) {
    return (
      <Badge 
        count={
          <Spin size="small" />
        }
        className="wallet-cluster-badge"
      >
        <TeamOutlined style={{ marginRight: 4 }} />
        <span>Analyzing wallet...</span>
      </Badge>
    );
  }

  // No cluster data available
  if (!clusterData) {
    return (
      <Button 
        type="link" 
        size={size} 
        icon={<ReloadOutlined />} 
        onClick={handleRefresh}
        loading={loading}
      >
        Check for wallet groups
      </Button>
    );
  }
  
  // No clusters found
  if (clusterInfo.clusterSize === 0) {
    return (
      <Tooltip title="No related wallets found">
        <Badge 
          className="wallet-cluster-badge"
          status="success"
          text={
            <Space size={4}>
              <TeamOutlined style={{ fontSize: size === 'small' ? '12px' : '14px' }} />
              <Text style={{ fontSize: size === 'small' ? '12px' : '14px' }}>
                No groups
              </Text>
            </Space>
          }
        />
      </Tooltip>
    );
  }

  // Badge content
  const badgeContent = (
    <Space size={4}>
      <TeamOutlined style={{ fontSize: size === 'small' ? '12px' : '14px' }} />
      <Text style={{ fontSize: size === 'small' ? '12px' : '14px' }}>
        Group: {clusterInfo.clusterSize} {clusterInfo.clusterSize === 1 ? 'address' : 'addresses'}
      </Text>
      {clusterInfo.riskScore > 0.4 && (
        <Tooltip title={`Security Rating: ${getSecurityLevel(clusterInfo.riskScore)}`}>
          <WarningOutlined style={{ color: getRiskLevel(clusterInfo.riskScore) === 'error' ? '#ff4d4f' : '#faad14' }} />
        </Tooltip>
      )}
    </Space>
  );

  // If details are disabled, just show the badge
  if (!showDetails) {
    return (
      <Badge 
        className="wallet-cluster-badge"
        status={getRiskLevel(clusterInfo.riskScore)}
        text={badgeContent}
      />
    );
  }

  // Handle popover visibility change
  const handleVisibleChange = (newVisible) => {
    setVisible(newVisible);
    
    // Refresh data when popover is opened
    if (newVisible) {
      fetchWalletCluster(walletAddress).catch(console.error);
    }
  };

  // Popover content with cluster details
  const popoverContent = (
    <div style={{ maxWidth: 300 }}>
      <div style={{ marginBottom: 12 }}>
        <Text strong>Wallet Group Analysis</Text>
      </div>
      
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <div>
          <Text type="secondary">Group Size:</Text>
          <Text style={{ float: 'right' }}>{clusterInfo.clusterSize} addresses</Text>
        </div>
        
        {clusterInfo.riskScore > 0 && (
          <div>
            <Text type="secondary">Security Rating:</Text>
            <Text 
              style={{ 
                float: 'right',
                color: getRiskLevel(clusterInfo.riskScore) === 'error' ? '#ff4d4f' : 
                       getRiskLevel(clusterInfo.riskScore) === 'warning' ? '#faad14' : '#52c41a'
              }}
            >
              {getSecurityLevel(clusterInfo.riskScore)}
            </Text>
          </div>
        )}
        
        {clusterInfo.members.length > 0 && (
          <div>
            <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Group Members:</Text>
            <List
              size="small"
              dataSource={clusterInfo.members}
              renderItem={member => (
                <List.Item>
                  <Text code style={{ fontSize: '12px' }}>
                    {member === walletAddress ? `${member} (current)` : member}
                  </Text>
                </List.Item>
              )}
              style={{ maxHeight: 200, overflowY: 'auto' }}
            />
          </div>
        )}
        
        <Alert 
          type="info" 
          showIcon 
          icon={<InfoCircleOutlined />} 
          message="Wallet grouping helps identify related addresses that may be controlled by the same entity for security analysis."
          style={{ marginTop: 16 }}
        />
      </Space>
    </div>
  );

  // Main badge component
  const badge = (
    <Badge 
      className="wallet-cluster-badge"
      status={getRiskLevel(clusterInfo.riskScore)}
      text={badgeContent}
    />
  );

  // Wrap in Popover if details are enabled
  if (showDetails) {
    return (
      <Popover
        content={popoverContent}
        title={
          <Space>
            <TeamOutlined />
            <span>Wallet Group Details</span>
            <Button 
              type="text" 
              size="small" 
              icon={<ReloadOutlined />} 
              onClick={handleRefresh}
              loading={loading}
            />
          </Space>
        }
        trigger="hover"
        visible={visible}
        onVisibleChange={handleVisibleChange}
        overlayStyle={{ maxWidth: 400 }}
        {...props}
      >
        {badge}
      </Popover>
    );
  }
  
  // Return just the badge if details are disabled
  return badge;
};

WalletClusterBadge.propTypes = {
  /** The wallet address being analyzed */
  walletAddress: PropTypes.string.isRequired,
  
  /** Automatically fetch cluster data when component mounts */
  autoFetch: PropTypes.bool,
  
  /** Show detailed popover on hover */
  showDetails: PropTypes.bool,
  
  /** Size of the badge */
  size: PropTypes.oneOf(['small', 'default', 'large']),
  
  /** Callback when cluster data is loaded/refreshed */
  onClusterData: PropTypes.func
};

WalletClusterBadge.defaultProps = {
  autoFetch: true,
  showDetails: true,
  size: 'default',
  onClusterData: undefined
};

export default WalletClusterBadge;
