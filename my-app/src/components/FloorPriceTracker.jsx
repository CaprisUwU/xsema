import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Select, Button, Input, Space, Typography, Tag, Statistic, Row, Col, Spin, Alert } from 'antd';
import { SearchOutlined, ReloadOutlined, TrendingUpOutlined, TrendingDownOutlined } from '@ant-design/icons';
import { getCollections, getTrendingCollections, subscribeToFloorPrices } from '../services/floorPriceService';

const { Title, Text } = Typography;
const { Option } = Select;

const FloorPriceTracker = () => {
  const [collections, setCollections] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [timeframe, setTimeframe] = useState('24h');
  const [sortBy, setSortBy] = useState('floor_price');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalItems, setTotalItems] = useState(0);
  const [realTimeUpdates, setRealTimeUpdates] = useState(new Map());
  const [wsConnection, setWsConnection] = useState(null);
  const [error, setError] = useState(null);

  // Fetch collections data
  const fetchCollections = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getCollections(currentPage, pageSize, sortBy, sortOrder);
      setCollections(response.data || []);
      setTotalItems(response.total || 0);
    } catch (err) {
      setError('Failed to fetch collections data');
      console.error('Error fetching collections:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, sortBy, sortOrder]);

  // Fetch trending collections
  const fetchTrending = useCallback(async () => {
    try {
      const response = await getTrendingCollections(timeframe, 10);
      setTrending(response.data || []);
    } catch (err) {
      console.error('Error fetching trending collections:', err);
    }
  }, [timeframe]);

  // Setup real-time updates
  useEffect(() => {
    const collectionAddresses = collections.map(c => c.contract_address).filter(Boolean);
    
    if (collectionAddresses.length > 0) {
      const ws = subscribeToFloorPrices((update) => {
        setRealTimeUpdates(prev => new Map(prev.set(update.contract_address, update)));
      }, collectionAddresses);
      
      setWsConnection(ws);
      
      return () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    }
  }, [collections]);

  // Initial data fetch
  useEffect(() => {
    fetchCollections();
    fetchTrending();
  }, [fetchCollections, fetchTrending]);

  // Handle table changes (pagination, sorting)
  const handleTableChange = (pagination, filters, sorter) => {
    setCurrentPage(pagination.current);
    setPageSize(pagination.pageSize);
    
    if (sorter.field) {
      setSortBy(sorter.field);
      setSortOrder(sorter.order === 'ascend' ? 'asc' : 'desc');
    }
  };

  // Format price with ETH symbol
  const formatPrice = (price) => {
    if (!price || price === 0) return 'N/A';
    return `${parseFloat(price).toFixed(4)} ETH`;
  };

  // Format percentage change
  const formatChange = (change) => {
    if (!change || change === 0) return '0.00%';
    const formatted = `${change > 0 ? '+' : ''}${parseFloat(change).toFixed(2)}%`;
    return (
      <span style={{ color: change > 0 ? '#52c41a' : '#ff4d4f' }}>
        {change > 0 ? <TrendingUpOutlined /> : <TrendingDownOutlined />} {formatted}
      </span>
    );
  };

  // Get real-time price or fallback to static price
  const getDisplayPrice = (collection) => {
    const realTimeData = realTimeUpdates.get(collection.contract_address);
    return realTimeData ? realTimeData.floor_price : collection.floor_price;
  };

  // Get real-time change or fallback to static change
  const getDisplayChange = (collection) => {
    const realTimeData = realTimeUpdates.get(collection.contract_address);
    return realTimeData ? realTimeData.change_24h : collection.change_24h;
  };

  // Table columns
  const columns = [
    {
      title: 'Collection',
      dataIndex: 'name',
      key: 'name',
      filteredValue: searchText ? [searchText] : null,
      onFilter: (value, record) => 
        record.name.toLowerCase().includes(value.toLowerCase()) ||
        record.symbol?.toLowerCase().includes(value.toLowerCase()),
      render: (text, record) => (
        <Space>
          {record.image_url && (
            <img 
              src={record.image_url} 
              alt={text} 
              style={{ width: 32, height: 32, borderRadius: 4 }}
            />
          )}
          <div>
            <div style={{ fontWeight: 'bold' }}>{text}</div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.symbol} • {record.total_supply || 'N/A'} items
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Floor Price',
      dataIndex: 'floor_price',
      key: 'floor_price',
      sorter: true,
      render: (text, record) => {
        const price = getDisplayPrice(record);
        const hasRealTimeUpdate = realTimeUpdates.has(record.contract_address);
        return (
          <div>
            <Statistic
              value={formatPrice(price)}
              valueStyle={{ 
                fontSize: 16,
                color: hasRealTimeUpdate ? '#1890ff' : undefined
              }}
            />
            {hasRealTimeUpdate && (
              <Tag color="blue" style={{ fontSize: 10 }}>LIVE</Tag>
            )}
          </div>
        );
      },
    },
    {
      title: '24h Change',
      dataIndex: 'change_24h',
      key: 'change_24h',
      sorter: true,
      render: (text, record) => formatChange(getDisplayChange(record)),
    },
    {
      title: '24h Volume',
      dataIndex: 'volume_24h',
      key: 'volume_24h',
      sorter: true,
      render: (text) => formatPrice(text),
    },
    {
      title: 'Sales',
      dataIndex: 'sales_24h',
      key: 'sales_24h',
      sorter: true,
      render: (text) => text || 0,
    },
    {
      title: 'Owners',
      dataIndex: 'owners',
      key: 'owners',
      render: (text) => text || 'N/A',
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={[16, 16]}>
        {/* Header */}
        <Col span={24}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <Title level={2} style={{ margin: 0 }}>
              Floor Price Tracker
            </Title>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={() => {
                  fetchCollections();
                  fetchTrending();
                }}
                loading={loading}
              >
                Refresh
              </Button>
            </Space>
          </div>
        </Col>

        {/* Trending Collections */}
        <Col span={24}>
          <Card title="Trending Collections" size="small" style={{ marginBottom: 16 }}>
            <Row gutter={[8, 8]}>
              {trending.slice(0, 6).map((collection, index) => (
                <Col span={4} key={collection.contract_address || index}>
                  <Card size="small" style={{ textAlign: 'center' }}>
                    <Statistic
                      title={collection.name}
                      value={formatPrice(collection.floor_price)}
                      suffix={formatChange(collection.change_24h)}
                      valueStyle={{ fontSize: 12 }}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* Filters */}
        <Col span={24}>
          <Card size="small" style={{ marginBottom: 16 }}>
            <Row gutter={[16, 16]} align="middle">
              <Col span={8}>
                <Input
                  placeholder="Search collections..."
                  prefix={<SearchOutlined />}
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                />
              </Col>
              <Col span={4}>
                <Select
                  value={timeframe}
                  onChange={setTimeframe}
                  style={{ width: '100%' }}
                >
                  <Option value="1h">1 Hour</Option>
                  <Option value="24h">24 Hours</Option>
                  <Option value="7d">7 Days</Option>
                  <Option value="30d">30 Days</Option>
                </Select>
              </Col>
              <Col span={4}>
                <Select
                  value={sortBy}
                  onChange={setSortBy}
                  style={{ width: '100%' }}
                >
                  <Option value="floor_price">Floor Price</Option>
                  <Option value="change_24h">24h Change</Option>
                  <Option value="volume_24h">Volume</Option>
                  <Option value="sales_24h">Sales</Option>
                </Select>
              </Col>
              <Col span={4}>
                <Select
                  value={sortOrder}
                  onChange={setSortOrder}
                  style={{ width: '100%' }}
                >
                  <Option value="desc">High to Low</Option>
                  <Option value="asc">Low to High</Option>
                </Select>
              </Col>
              <Col span={4}>
                <Tag color={wsConnection ? 'green' : 'red'}>
                  {wsConnection ? 'Live Updates ON' : 'Live Updates OFF'}
                </Tag>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* Error Alert */}
        {error && (
          <Col span={24}>
            <Alert
              message="Error"
              description={error}
              type="error"
              closable
              onClose={() => setError(null)}
              style={{ marginBottom: 16 }}
            />
          </Col>
        )}

        {/* Collections Table */}
        <Col span={24}>
          <Card>
            <Spin spinning={loading}>
              <Table
                columns={columns}
                dataSource={collections}
                rowKey="contract_address"
                pagination={{
                  current: currentPage,
                  pageSize: pageSize,
                  total: totalItems,
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total, range) => 
                    `${range[0]}-${range[1]} of ${total} collections`,
                }}
                onChange={handleTableChange}
                size="small"
              />
            </Spin>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default FloorPriceTracker;
