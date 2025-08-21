import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Calendar, Filter } from 'lucide-react';

interface ChartDataPoint {
  date: string;
  value: number;
  change: number;
  volume: number;
}

const PortfolioChart: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('value');

  // Mock data with UK formatting
  const mockData: ChartDataPoint[] = [
    { date: '05/08/2025', value: 98.5, change: 2.1, volume: 45.2 },
    { date: '06/08/2025', value: 101.2, change: 2.7, volume: 52.8 },
    { date: '07/08/2025', value: 99.8, change: -1.4, volume: 38.9 },
    { date: '08/08/2025', value: 103.5, change: 3.7, volume: 67.3 },
    { date: '09/08/2025', value: 107.2, change: 3.6, volume: 73.1 },
    { date: '10/08/2025', value: 105.8, change: -1.3, volume: 58.4 },
    { date: '11/08/2025', value: 110.5, change: 4.4, volume: 82.7 }
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

  const getChangeColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const maxValue = Math.max(...mockData.map(d => d.value));
  const minValue = Math.min(...mockData.map(d => d.value));

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            Portfolio Performance
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Track your portfolio value over time
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white text-sm"
            aria-label="Select metric"
          >
            <option value="value">Portfolio Value</option>
            <option value="change">Daily Change</option>
            <option value="volume">Trading Volume</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white text-sm"
            aria-label="Select time range"
          >
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="90d">90 Days</option>
            <option value="1y">1 Year</option>
          </select>
        </div>
      </div>

      {/* Chart Visualization */}
      <div className="mb-6">
        <div className="h-64 flex items-end justify-between space-x-2">
          {mockData.map((point, index) => {
            const height = selectedMetric === 'value' 
              ? ((point.value - minValue) / (maxValue - minValue)) * 100
              : selectedMetric === 'change'
              ? Math.abs(point.change) * 10
              : (point.volume / 100) * 100;

            return (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div className="relative group">
                  <div 
                    className={`w-full rounded-t transition-all duration-200 ${
                      selectedMetric === 'value' 
                        ? 'bg-gradient-to-t from-blue-500 to-blue-600'
                        : selectedMetric === 'change'
                        ? point.change >= 0 
                          ? 'bg-gradient-to-t from-green-500 to-green-600'
                          : 'bg-gradient-to-t from-red-500 to-red-600'
                        : 'bg-gradient-to-t from-purple-500 to-purple-600'
                    }`}
                    style={{ height: `${Math.max(height, 4)}%` }}
                  />
                  <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-slate-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
                    {selectedMetric === 'value' && formatCurrency(point.value)}
                    {selectedMetric === 'change' && formatPercentage(point.change)}
                    {selectedMetric === 'volume' && formatCurrency(point.volume)}
                  </div>
                </div>
                <span className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                  {point.date.split('/').slice(0, 2).join('/')}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Current Value</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">
            {formatCurrency(mockData[mockData.length - 1].value)}
          </p>
        </div>
        <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Total Change</p>
          <p className={`text-xl font-bold ${getChangeColor(mockData[mockData.length - 1].value - mockData[0].value)}`}>
            {formatPercentage(((mockData[mockData.length - 1].value - mockData[0].value) / mockData[0].value) * 100)}
          </p>
        </div>
        <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Best Day</p>
          <p className="text-xl font-bold text-green-600">
            {formatPercentage(Math.max(...mockData.map(d => d.change)))}
          </p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
        <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
          Recent Activity
        </h4>
        <div className="space-y-2">
          {mockData.slice(-3).reverse().map((point, index) => (
            <div key={index} className="flex items-center justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400">
                {point.date}
              </span>
              <div className="flex items-center space-x-2">
                <span className={getChangeColor(point.change)}>
                  {formatPercentage(point.change)}
                </span>
                {point.change >= 0 ? (
                  <TrendingUp className="w-3 h-3 text-green-600" />
                ) : (
                  <TrendingDown className="w-3 h-3 text-red-600" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PortfolioChart;
