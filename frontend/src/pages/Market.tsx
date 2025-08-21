import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Bell, RefreshCw } from 'lucide-react';
import LiveActivityFeed from '../components/market/LiveActivityFeed';

const Market: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const mockData = [
    {
      name: 'Bored Ape Yacht Club',
      floorPrice: 15.5,
      change24h: 0.8,
      volume24h: 124.7,
      chain: 'Ethereum'
    },
    {
      name: 'CryptoPunks',
      floorPrice: 45.2,
      change24h: -2.1,
      volume24h: 89.3,
      chain: 'Ethereum'
    }
  ];

  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString('en-GB', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">
          Market Data
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">24h Volume</h3>
            <p className="text-2xl font-bold text-blue-600">
              {formatCurrency(214.0)}
            </p>
          </div>
          
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Active Collections</h3>
            <p className="text-2xl font-bold text-green-600">12</p>
          </div>
          
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-8">Market Status</h3>
            <p className="text-2xl font-bold text-green-600">Active</p>
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
          
          <div className="space-y-4">
            {mockData.map((item, index) => (
              <div key={index} className="flex justify-between items-center p-4 border rounded-lg">
                <div>
                  <h3 className="font-medium">{item.name}</h3>
                  <p className="text-sm text-slate-500">{item.chain}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{formatCurrency(item.floorPrice)}</p>
                  <p className={`text-sm ${item.change24h > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {item.change24h > 0 ? '+' : ''}{item.change24h.toFixed(2)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Market;
