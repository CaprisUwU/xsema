/**
 * Portfolio Manager Component
 * 
 * Comprehensive portfolio management with:
 * - Portfolio overview and performance
 * - Asset allocation and management
 * - Performance tracking and analytics
 * - Integration with advanced features
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  PieChart, 
  BarChart3, 
  Calendar,
  DollarSign,
  Percent,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface PortfolioAsset {
  id: string;
  name: string;
  collection: string;
  chain: string;
  quantity: number;
  cost_basis: number;
  current_value: number;
  unrealized_pnl: number;
  roi_percentage: number;
  holding_period_days: number;
  last_updated: string;
}

interface PortfolioSummary {
  total_value: number;
  total_cost_basis: number;
  total_pnl: number;
  roi_percentage: number;
  asset_count: number;
  collections_count: number;
  chains_count: number;
  performance_7d: number;
  performance_30d: number;
  performance_90d: number;
}

interface AssetAllocation {
  category: string;
  value: number;
  percentage: number;
  count: number;
}

const PortfolioManager: React.FC = () => {
  const [activeView, setActiveView] = useState('overview');
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
  const [assets, setAssets] = useState<PortfolioAsset[]>([]);
  const [assetAllocation, setAssetAllocation] = useState<AssetAllocation[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<PortfolioAsset | null>(null);

  // Mock data for demonstration
  useEffect(() => {
    setPortfolioSummary({
      total_value: 125000,
      total_cost_basis: 95000,
      total_pnl: 30000,
      roi_percentage: 31.58,
      asset_count: 24,
      collections_count: 8,
      chains_count: 3,
      performance_7d: 5.2,
      performance_30d: 12.8,
      performance_90d: 28.5
    });

    setAssets([
      {
        id: '1',
        name: 'Bored Ape #1234',
        collection: 'Bored Ape Yacht Club',
        chain: 'Ethereum',
        quantity: 1,
        cost_basis: 25000,
        current_value: 35000,
        unrealized_pnl: 10000,
        roi_percentage: 40,
        holding_period_days: 180,
        last_updated: '2025-01-15T10:30:00Z'
      },
      {
        id: '2',
        name: 'Cool Cat #5678',
        collection: 'Cool Cats',
        chain: 'Ethereum',
        quantity: 1,
        cost_basis: 8000,
        current_value: 12000,
        unrealized_pnl: 4000,
        roi_percentage: 50,
        holding_period_days: 120,
        last_updated: '2025-01-15T10:30:00Z'
      },
      {
        id: '3',
        name: 'Doodle #9012',
        collection: 'Doodles',
        chain: 'Ethereum',
        quantity: 1,
        cost_basis: 15000,
        current_value: 18000,
        unrealized_pnl: 3000,
        roi_percentage: 20,
        holding_period_days: 90,
        last_updated: '2025-01-15T10:30:00Z'
      }
    ]);

    setAssetAllocation([
      { category: 'Blue Chip NFTs', value: 65000, percentage: 52, count: 8 },
      { category: 'Mid Tier NFTs', value: 40000, percentage: 32, count: 12 },
      { category: 'Emerging NFTs', value: 20000, percentage: 16, count: 4 }
    ]);
  }, []);

  const views = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'assets', name: 'Assets', icon: PieChart },
    { id: 'allocation', name: 'Allocation', icon: PieChart },
    { id: 'performance', name: 'Performance', icon: TrendingUp }
  ];

  const getPerformanceColor = (value: number) => {
    if (value >= 0) return 'text-green-600';
    return 'text-red-600';
  };

  const getPerformanceIcon = (value: number) => {
    if (value >= 0) return <TrendingUp className="w-4 h-4" />;
    return <TrendingDown className="w-4 h-4" />;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="p-6 bg-white dark:bg-slate-800 rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Portfolio Manager
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Comprehensive portfolio management and performance tracking
        </p>
      </div>

      {/* View Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-8">
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <button
                key={view.id}
                onClick={() => setActiveView(view.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeView === view.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
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
      <div className="min-h-[500px]">
        {/* Overview Tab */}
        {activeView === 'overview' && portfolioSummary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Total Portfolio Value</div>
                <div className="text-2xl font-bold">{formatCurrency(portfolioSummary.total_value)}</div>
                <div className="text-sm opacity-90">{portfolioSummary.asset_count} Assets</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Total P&L</div>
                <div className="text-2xl font-bold">{formatCurrency(portfolioSummary.total_pnl)}</div>
                <div className="text-sm opacity-90">{portfolioSummary.roi_percentage.toFixed(2)}% ROI</div>
              </div>
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Collections</div>
                <div className="text-2xl font-bold">{portfolioSummary.collections_count}</div>
                <div className="text-sm opacity-90">Across {portfolioSummary.chains_count} Chains</div>
              </div>
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Cost Basis</div>
                <div className="text-2xl font-bold">{formatCurrency(portfolioSummary.total_cost_basis)}</div>
                <div className="text-sm opacity-90">Total Invested</div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="bg-gray-50 dark:bg-slate-700 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Performance Metrics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-white dark:bg-slate-600 rounded-lg">
                  <div className="flex items-center justify-center space-x-2 mb-2">
                    {getPerformanceIcon(portfolioSummary.performance_7d)}
                    <span className={`text-lg font-bold ${getPerformanceColor(portfolioSummary.performance_7d)}`}>
                      {portfolioSummary.performance_7d.toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">7 Day Performance</div>
                </div>
                <div className="text-center p-4 bg-white dark:bg-slate-600 rounded-lg">
                  <div className="flex items-center justify-center space-x-2 mb-2">
                    {getPerformanceIcon(portfolioSummary.performance_30d)}
                    <span className={`text-lg font-bold ${getPerformanceColor(portfolioSummary.performance_30d)}`}>
                      {portfolioSummary.performance_30d.toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">30 Day Performance</div>
                </div>
                <div className="text-center p-4 bg-white dark:bg-slate-600 rounded-lg">
                  <div className="flex items-center justify-center space-x-2 mb-2">
                    {getPerformanceIcon(portfolioSummary.performance_90d)}
                    <span className={`text-lg font-bold ${getPerformanceColor(portfolioSummary.performance_90d)}`}>
                      {portfolioSummary.performance_90d.toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">90 Day Performance</div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
                Quick Actions
              </h3>
              <div className="flex flex-wrap gap-3">
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                  <Plus className="w-4 h-4" />
                  <span>Add Asset</span>
                </button>
                <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                  <TrendingUp className="w-4 h-4" />
                  <span>View Analytics</span>
                </button>
                <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                  <BarChart3 className="w-4 h-4" />
                  <span>Generate Report</span>
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Assets Tab */}
        {activeView === 'assets' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Portfolio Assets ({assets.length})
              </h3>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
                <Plus className="w-4 h-4" />
                <span>Add Asset</span>
              </button>
            </div>

            {/* Assets Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-slate-700 rounded-lg overflow-hidden">
                <thead className="bg-gray-50 dark:bg-slate-600">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Asset
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Collection
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Chain
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Cost Basis
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Current Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      P&L
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      ROI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Holding Period
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                  {assets.map((asset) => (
                    <tr 
                      key={asset.id} 
                      className="hover:bg-gray-50 dark:hover:bg-slate-600 cursor-pointer transition-colors"
                      onClick={() => setSelectedAsset(asset)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {asset.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {asset.collection}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {asset.chain}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {formatCurrency(asset.cost_basis)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {formatCurrency(asset.current_value)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${
                          asset.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(asset.unrealized_pnl)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm font-medium ${
                          asset.roi_percentage >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {asset.roi_percentage.toFixed(2)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          {asset.holding_period_days} days
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Allocation Tab */}
        {activeView === 'allocation' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Asset Allocation
            </h3>

            {/* Allocation Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-50 dark:bg-slate-700 p-6 rounded-lg">
                <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-4">
                  Allocation by Category
                </h4>
                <div className="space-y-4">
                  {assetAllocation.map((allocation, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full ${
                          index === 0 ? 'bg-blue-500' : 
                          index === 1 ? 'bg-green-500' : 'bg-purple-500'
                        }`}></div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {allocation.category}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {formatCurrency(allocation.value)}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          {allocation.percentage.toFixed(1)}% • {allocation.count} assets
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-slate-700 p-6 rounded-lg">
                <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-4">
                  Portfolio Diversification
                </h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Collections</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {portfolioSummary?.collections_count || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Blockchain Chains</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {portfolioSummary?.chains_count || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Total Assets</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {portfolioSummary?.asset_count || 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Performance Tab */}
        {activeView === 'performance' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Performance Analytics
            </h3>

            {/* Performance Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-slate-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Best Performer</span>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">Cool Cat #5678</div>
                <div className="text-sm text-green-600">+50.0% ROI</div>
              </div>
              <div className="bg-white dark:bg-slate-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingDown className="w-5 h-5 text-red-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Worst Performer</span>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">None</div>
                <div className="text-sm text-green-600">All assets positive</div>
              </div>
              <div className="bg-white dark:bg-slate-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Longest Held</span>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">Bored Ape #1234</div>
                <div className="text-sm text-blue-600">180 days</div>
              </div>
            </div>

            {/* Performance Chart Placeholder */}
            <div className="bg-gray-50 dark:bg-slate-700 p-8 rounded-lg text-center">
              <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <div className="text-lg font-medium text-gray-600 dark:text-gray-400 mb-2">
                Performance Chart
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-500">
                Interactive performance chart will be displayed here
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-slate-800 rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto"
          >
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Asset Details
              </h3>
              <button
                onClick={() => setSelectedAsset(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Name</label>
                <div className="text-sm text-gray-900 dark:text-white">{selectedAsset.name}</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Collection</label>
                <div className="text-sm text-gray-900 dark:text-white">{selectedAsset.collection}</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Chain</label>
                <div className="text-sm text-gray-900 dark:text-white">{selectedAsset.chain}</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Cost Basis</label>
                <div className="text-sm text-gray-900 dark:text-white">{formatCurrency(selectedAsset.cost_basis)}</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Current Value</label>
                <div className="text-sm text-gray-900 dark:text-white">{formatCurrency(selectedAsset.current_value)}</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Unrealized P&L</label>
                <div className={`text-sm font-medium ${
                  selectedAsset.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(selectedAsset.unrealized_pnl)}
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">ROI</label>
                <div className={`text-sm font-medium ${
                  selectedAsset.roi_percentage >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {selectedAsset.roi_percentage.toFixed(2)}%
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Holding Period</label>
                <div className="text-sm text-gray-900 dark:text-white">{selectedAsset.holding_period_days} days</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Last Updated</label>
                <div className="text-sm text-gray-900 dark:text-white">{formatDate(selectedAsset.last_updated)}</div>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                Edit Asset
              </button>
              <button className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors">
                View History
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default PortfolioManager;
