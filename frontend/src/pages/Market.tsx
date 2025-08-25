import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Bell, RefreshCw, Database, Wifi, AlertCircle } from 'lucide-react';
import LiveActivityFeed from '../components/market/LiveActivityFeed';
import marketDataService, { MarketOverview, CollectionData } from '../utils/marketDataService';

const Market: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [marketData, setMarketData] = useState<MarketOverview | null>(null);
  const [dataSource, setDataSource] = useState<{ hasRealData: boolean; source: string; message: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString('en-GB', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  // Fetch market data on component mount
  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get data source info first
      const sourceInfo = await marketDataService.getDataSourceInfo();
      setDataSource(sourceInfo);
      
      // Fetch market overview
      const data = await marketDataService.getMarketOverview();
      if (data) {
        setMarketData(data);
      } else {
        setError('Failed to fetch market data');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchMarketData();
    setIsRefreshing(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">
          Market Data
        </h1>
        
        {/* Data Source Indicator */}
        {dataSource && (
          <div className="mb-6 p-4 rounded-lg border-2 border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {dataSource.hasRealData ? (
                  <Database className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-yellow-500" />
                )}
                <div>
                  <p className="font-medium">
                    Data Source: {dataSource.hasRealData ? 'Live OpenSea Data' : 'Mock Data'}
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    {dataSource.message}
                  </p>
                </div>
              </div>
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center space-x-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        )}

        {/* Market Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">24h Volume</h3>
            {loading ? (
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
            ) : (
              <p className="text-2xl font-bold text-blue-600">
                {marketData ? formatCurrency(marketData.total_volume_24h || 0) : '£0.00'}
              </p>
            )}
          </div>
          
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Active Collections</h3>
            {loading ? (
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
            ) : (
              <p className="text-2xl font-bold text-green-600">
                {marketData ? marketData.active_collections : 0}
              </p>
            )}
          </div>
          
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Market Status</h3>
            {loading ? (
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
            ) : (
              <p className="text-2xl font-bold text-green-600">
                {marketData ? marketData.market_status : 'Unknown'}
              </p>
            )}
          </div>
        </div>

        {/* Live Activity Feed - Competitive Advantage */}
        <div className="mb-8">
          <LiveActivityFeed />
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Floor Prices</h2>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg">
              <Bell className="w-4 h-4 inline mr-2" />
              Set Alert
            </button>
          </div>
          
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex justify-between items-center p-4 border rounded-lg">
                  <div className="space-y-2">
                    <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-32 animate-pulse"></div>
                    <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-20 animate-pulse"></div>
                  </div>
                  <div className="space-y-2 text-right">
                    <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-20 animate-pulse"></div>
                    <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-16 animate-pulse"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : marketData && marketData.collections.length > 0 ? (
            <div className="space-y-4">
              {marketData.collections.map((collection, index) => (
                <div key={index} className="flex justify-between items-center p-4 border rounded-lg">
                  <div>
                    <h3 className="font-medium">{collection.name}</h3>
                    <p className="text-sm text-slate-500">Ethereum</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">
                      {collection.floor_price ? formatCurrency(collection.floor_price) : 'No floor price'}
                    </p>
                    <p className="text-sm text-slate-500">
                      {collection.volume_24h ? `${formatCurrency(collection.volume_24h)} vol` : 'No volume data'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              {error ? (
                <div>
                  <AlertCircle className="w-8 h-8 mx-auto mb-2 text-red-500" />
                  <p>Error loading market data: {error}</p>
                </div>
              ) : (
                <div>
                  <Database className="w-8 h-8 mx-auto mb-2 text-slate-400" />
                  <p>No market data available</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Market;
