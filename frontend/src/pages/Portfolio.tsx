import React, { useState } from 'react';
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  Eye, 
  EyeOff, 
  Plus,
  Filter,
  Download,
  RefreshCw,
  BarChart3,
  PieChart,
  Settings
} from 'lucide-react';
import { cn } from '../utils/cn';
import PortfolioManager from '../components/portfolio/PortfolioManager';

interface PortfolioAsset {
  id: string;
  name: string;
  symbol: string;
  balance: number;
  currentPrice: number;
  purchasePrice: number;
  change24h: number;
  changePercentage: number;
  marketValue: number;
  profitLoss: number;
  profitLossPercentage: number;
  chain: string;
  lastUpdated: string;
}

const Portfolio: React.FC = () => {
  const [isBalanceVisible, setIsBalanceVisible] = useState(true);
  const [selectedChain, setSelectedChain] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('value');
  const [activeView, setActiveView] = useState('overview');

  // Mock data with UK formatting
  const mockAssets: PortfolioAsset[] = [
    {
      id: '1',
      name: 'Bored Ape Yacht Club',
      symbol: 'BAYC',
      balance: 2,
      currentPrice: 15.5,
      purchasePrice: 12.0,
      change24h: 0.8,
      changePercentage: 5.45,
      marketValue: 31.0,
      profitLoss: 7.0,
      profitLossPercentage: 29.17,
      chain: 'Ethereum',
      lastUpdated: '11/08/2025 14:30'
    },
    {
      id: '2',
      name: 'CryptoPunks',
      symbol: 'PUNK',
      balance: 1,
      currentPrice: 45.2,
      purchasePrice: 50.0,
      change24h: -2.1,
      changePercentage: -4.44,
      marketValue: 45.2,
      profitLoss: -4.8,
      profitLossPercentage: -9.6,
      chain: 'Ethereum',
      lastUpdated: '11/08/2025 14:30'
    },
    {
      id: '3',
      name: 'Doodles',
      symbol: 'DOODLE',
      balance: 3,
      currentPrice: 8.75,
      purchasePrice: 7.5,
      change24h: 0.25,
      changePercentage: 2.94,
      marketValue: 26.25,
      profitLoss: 3.75,
      profitLossPercentage: 16.67,
      chain: 'Polygon',
      lastUpdated: '11/08/2025 14:30'
    }
  ];

  const totalValue = mockAssets.reduce((sum, asset) => sum + asset.marketValue, 0);
  const totalProfitLoss = mockAssets.reduce((sum, asset) => sum + asset.profitLoss, 0);
  const totalProfitLossPercentage = (totalProfitLoss / (totalValue - totalProfitLoss)) * 100;

  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString('en-GB', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getProfitLossColor = (value: number) => {
    if (value > 0) return 'text-green-600 dark:text-green-400';
    if (value < 0) return 'text-red-600 dark:text-red-400';
    return 'text-slate-600 dark:text-slate-400';
  };

  const getProfitLossBgColor = (value: number) => {
    if (value > 0) return 'bg-green-50 dark:bg-green-900/20';
    if (value < 0) return 'bg-red-50 dark:bg-red-900/20';
    return 'bg-slate-50 dark:bg-slate-800';
  };

  const filteredAssets = mockAssets.filter(asset => 
    selectedChain === 'all' || asset.chain === selectedChain
  );

  const sortedAssets = [...filteredAssets].sort((a, b) => {
    switch (sortBy) {
      case 'value':
        return b.marketValue - a.marketValue;
      case 'profit':
        return b.profitLoss - a.profitLoss;
      case 'change':
        return b.changePercentage - a.changePercentage;
      default:
        return 0;
    }
  });

  const views = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'manager', name: 'Portfolio Manager', icon: PieChart },
    { id: 'assets', name: 'Asset List', icon: Wallet },
    { id: 'settings', name: 'Settings', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Portfolio
              </h1>
              <p className="text-slate-600 dark:text-slate-400 mt-2">
                Track your NFT investments across multiple chains
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button className="flex items-center px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
              <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Plus className="w-4 h-4 mr-2" />
                Add Asset
              </button>
            </div>
          </div>
        </div>

        {/* View Navigation */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 mb-8">
          <nav className="flex space-x-8 border-b border-slate-200 dark:border-slate-700">
            {views.map((view) => {
              const Icon = view.icon;
              return (
                <button
                  key={view.id}
                  onClick={() => setActiveView(view.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeView === view.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{view.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* View Content */}
        {activeView === 'overview' && (
          <>
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {/* Total Value */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                      Total Portfolio Value
                    </p>
                    <div className="flex items-center space-x-2 mt-2">
                      <button
                        onClick={() => setIsBalanceVisible(!isBalanceVisible)}
                        className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                        aria-label="Toggle balance visibility"
                      >
                        {isBalanceVisible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                      </button>
                      <p className="text-2xl font-bold text-slate-900 dark:text-white">
                        {isBalanceVisible ? formatCurrency(totalValue) : '••••••'}
                      </p>
                    </div>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                    <Wallet className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                </div>
              </div>

              {/* Total Profit/Loss */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                      Total Profit/Loss
                    </p>
                    <p className={cn("text-2xl font-bold mt-2", getProfitLossColor(totalProfitLoss))}>
                      {formatCurrency(totalProfitLoss)}
                    </p>
                    <p className={cn("text-sm mt-1", getProfitLossColor(totalProfitLoss))}>
                      {formatPercentage(totalProfitLossPercentage)}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                    {totalProfitLoss > 0 ? (
                      <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
                    ) : (
                      <TrendingDown className="w-6 h-6 text-red-600 dark:text-red-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Asset Count */}
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                      Total Assets
                    </p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-white mt-2">
                      {mockAssets.length}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      Across {new Set(mockAssets.map(a => a.chain)).size} chains
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 mb-8">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <button 
                  onClick={() => setActiveView('manager')}
                  className="flex items-center justify-center p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
                >
                  <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" />
                  <span className="font-medium text-blue-800 dark:text-blue-200">Portfolio Manager</span>
                </button>
                <button className="flex items-center justify-center p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/40 transition-colors">
                  <Plus className="w-6 h-6 text-green-600 dark:text-green-400 mr-3" />
                  <span className="font-medium text-green-800 dark:text-green-200">Add Asset</span>
                </button>
                <button className="flex items-center justify-center p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-colors">
                  <Download className="w-6 h-6 text-purple-600 dark:text-purple-400 mr-3" />
                  <span className="font-medium text-purple-800 dark:text-purple-200">Export Data</span>
                </button>
                <button className="flex items-center justify-center p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/40 transition-colors">
                  <Settings className="w-6 h-6 text-yellow-600 dark:text-yellow-400 mr-3" />
                  <span className="font-medium text-yellow-800 dark:text-yellow-200">Settings</span>
                </button>
              </div>
            </div>

            {/* Recent Performance */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 mb-8">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Recent Performance
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Best & Worst Performers */}
                <div>
                  <h4 className="text-md font-semibold mb-4">Performance Leaders</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div>
                        <p className="font-medium">Best Performer</p>
                        <p className="text-sm text-slate-600">Bored Ape Yacht Club</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-green-600">+29.17%</p>
                        <p className="text-sm text-slate-500">+£7.00</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <div>
                        <p className="font-medium">Worst Performer</p>
                        <p className="text-sm text-slate-600">CryptoPunks</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-red-600">-9.60%</p>
                        <p className="text-sm text-slate-500">-£4.80</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Chain Distribution */}
                <div>
                  <h4 className="text-md font-semibold mb-4">Chain Distribution</h4>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full mr-3 bg-blue-500"></div>
                        <span className="font-medium">Ethereum</span>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">65%</p>
                        <p className="text-sm text-slate-500">£49.60</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full mr-3 bg-green-500"></div>
                        <span className="font-medium">Polygon</span>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">25%</p>
                        <p className="text-sm text-slate-500">£26.25</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Portfolio Manager View */}
        {activeView === 'manager' && (
          <PortfolioManager />
        )}

        {/* Asset List View */}
        {activeView === 'assets' && (
          <>
            {/* Filters and Controls */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 mb-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
                <div className="flex items-center space-x-4">
                  <div>
                    <label htmlFor="chain-filter" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Chain
                    </label>
                    <select
                      id="chain-filter"
                      value={selectedChain}
                      onChange={(e) => setSelectedChain(e.target.value)}
                      className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="all">All Chains</option>
                      <option value="Ethereum">Ethereum</option>
                      <option value="Polygon">Polygon</option>
                      <option value="BSC">BSC</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="sort-by" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Sort By
                    </label>
                    <select
                      id="sort-by"
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="value">Portfolio Value</option>
                      <option value="profit">Profit/Loss</option>
                      <option value="change">24h Change</option>
                    </select>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <button className="flex items-center px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                    <Filter className="w-4 h-4 mr-2" />
                    More Filters
                  </button>
                  <button className="flex items-center px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </button>
                </div>
              </div>
            </div>

            {/* Assets Table */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                  <thead className="bg-slate-50 dark:bg-slate-700/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Asset
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Balance
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Current Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Market Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        24h Change
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Profit/Loss
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Chain
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        Last Updated
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                    {sortedAssets.map((asset) => (
                      <tr key={asset.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-slate-900 dark:text-white">
                              {asset.name}
                            </div>
                            <div className="text-sm text-slate-500 dark:text-slate-400">
                              {asset.symbol}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-white">
                          {asset.balance}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-white">
                          {formatCurrency(asset.currentPrice)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-white">
                          {formatCurrency(asset.marketValue)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={cn("text-sm font-medium", getProfitLossColor(asset.change24h))}>
                            {formatCurrency(asset.change24h)}
                          </div>
                          <div className={cn("text-sm", getProfitLossColor(asset.changePercentage))}>
                            {formatPercentage(asset.changePercentage)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={cn("text-sm font-medium", getProfitLossColor(asset.profitLoss))}>
                            {formatCurrency(asset.profitLoss)}
                          </div>
                          <div className={cn("text-sm", getProfitLossColor(asset.profitLossPercentage))}>
                            {formatPercentage(asset.profitLossPercentage)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                            {asset.chain}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                          {asset.lastUpdated}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Settings View */}
        {activeView === 'settings' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
              Portfolio Settings
            </h2>
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                  Display Preferences
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-700 dark:text-slate-300">Show Portfolio Value</span>
                    <button
                      onClick={() => setIsBalanceVisible(!isBalanceVisible)}
                      className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                    >
                      {isBalanceVisible ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-700 dark:text-slate-300">Default Currency</span>
                    <span className="text-slate-900 dark:text-white font-medium">GBP (£)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-700 dark:text-slate-300">Date Format</span>
                    <span className="text-slate-900 dark:text-white font-medium">DD/MM/YYYY</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                  Notifications
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-700 dark:text-slate-300">Price Alerts</span>
                    <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                      <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1"></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-700 dark:text-slate-300">Portfolio Updates</span>
                    <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                      <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Portfolio;
