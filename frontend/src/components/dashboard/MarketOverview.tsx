import React from 'react';
import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react';

interface MarketTrend {
  collection: string;
  floorPrice: number;
  change24h: number;
  volume24h: number;
  holders: number;
  trend: 'up' | 'down' | 'stable';
}

const MarketOverview: React.FC = () => {
  const mockTrends: MarketTrend[] = [
    {
      collection: 'Bored Ape Yacht Club',
      floorPrice: 15.5,
      change24h: 2.1,
      volume24h: 124.7,
      holders: 6250,
      trend: 'up'
    },
    {
      collection: 'CryptoPunks',
      floorPrice: 45.2,
      change24h: -1.8,
      volume24h: 89.3,
      holders: 3300,
      trend: 'down'
    },
    {
      collection: 'Doodles',
      floorPrice: 8.75,
      change24h: 0.5,
      volume24h: 67.2,
      holders: 8900,
      trend: 'stable'
    }
  ];

  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString('en-GB', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  const getTrendColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const totalVolume = mockTrends.reduce((sum, trend) => sum + trend.volume24h, 0);
  const totalHolders = mockTrends.reduce((sum, trend) => sum + trend.holders, 0);

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          Market Overview
        </h3>
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-slate-400" />
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Live Data
          </span>
        </div>
      </div>

      {/* Market Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Total Volume</p>
          <p className="text-xl font-bold text-blue-600">
            {formatCurrency(totalVolume)}
          </p>
        </div>
        <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Total Holders</p>
          <p className="text-xl font-bold text-green-600">
            {totalHolders.toLocaleString('en-GB')}
          </p>
        </div>
        <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Collections</p>
          <p className="text-xl font-bold text-purple-600">
            {mockTrends.length}
          </p>
        </div>
      </div>

      {/* Collection Trends */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300">
          Top Collections
        </h4>
        {mockTrends.map((trend, index) => (
          <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {trend.collection.charAt(0)}
                </span>
              </div>
              <div>
                <h5 className="font-medium text-slate-900 dark:text-white">
                  {trend.collection}
                </h5>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {trend.holders.toLocaleString('en-GB')} holders
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2 mb-1">
                {getTrendIcon(trend.trend)}
                <span className="font-bold text-slate-900 dark:text-white">
                  {formatCurrency(trend.floorPrice)}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`text-sm ${getTrendColor(trend.change24h)}`}>
                  {formatPercentage(trend.change24h)}
                </span>
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {formatCurrency(trend.volume24h)} vol
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Market Status */}
      <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Market Status: Active
            </span>
          </div>
          <span className="text-xs text-slate-500 dark:text-slate-500">
            Updated: {new Date().toLocaleTimeString('en-GB', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
        </div>
      </div>
    </div>
  );
};

export default MarketOverview;
