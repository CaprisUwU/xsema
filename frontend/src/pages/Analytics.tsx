import React, { useState } from 'react';
import { BarChart3, TrendingUp, TrendingDown, PieChart, Activity, Brain, Shield, FileText, AlertCircle } from 'lucide-react';
import AdvancedAnalytics from '../components/analytics/AdvancedAnalytics';

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [activeSection, setActiveSection] = useState('overview');

  const portfolioInsights = {
    totalReturn: 23.5,
    bestPerformer: 'Bored Ape Yacht Club',
    worstPerformer: 'CryptoPunks',
    diversificationScore: 78,
    riskAdjustedReturn: 18.2
  };

  const chainDistribution = [
    { chain: 'Ethereum', percentage: 65, value: 65.5 },
    { chain: 'Polygon', percentage: 25, value: 25.2 },
    { chain: 'BSC', percentage: 10, value: 9.8 }
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

  const sections = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'advanced', name: 'Advanced Analytics', icon: Brain },
    { id: 'risk', name: 'Risk Management', icon: Shield },
    { id: 'tax', name: 'Tax Planning', icon: FileText }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">
          Analytics & Insights
        </h1>

        {/* Section Navigation */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Analytics Dashboard</h2>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
              aria-label="Select time range"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
          </div>
          
          <nav className="flex space-x-8 border-b border-slate-200 dark:border-slate-700">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeSection === section.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{section.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Section Content */}
        {activeSection === 'overview' && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
                <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Total Return</h3>
                <p className="text-3xl font-bold text-green-600">
                  {formatPercentage(portfolioInsights.totalReturn)}
                </p>
              </div>

              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
                <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Diversification</h3>
                <p className="text-3xl font-bold text-blue-600">
                  {portfolioInsights.diversificationScore}/100
                </p>
              </div>

              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
                <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Activity className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Risk-Adjusted</h3>
                <p className="text-3xl font-bold text-purple-600">
                  {formatPercentage(portfolioInsights.riskAdjustedReturn)}
                </p>
              </div>

              <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
                <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <PieChart className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Holdings</h3>
                <p className="text-3xl font-bold text-yellow-600">3</p>
              </div>
            </div>

            {/* Portfolio Performance */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Best & Worst Performers */}
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">Performance Leaders</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div>
                      <p className="font-medium">Best Performer</p>
                      <p className="text-sm text-slate-600">{portfolioInsights.bestPerformer}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-600">+29.17%</p>
                      <p className="text-sm text-slate-500">+£7.00</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <div>
                      <p className="font-medium">Worst Performer</p>
                      <p className="text-sm text-slate-600">{portfolioInsights.worstPerformer}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-red-600">-9.60%</p>
                      <p className="text-sm text-slate-500">-£4.80</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Chain Distribution */}
              <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">Chain Distribution</h3>
                <div className="space-y-4">
                  {chainDistribution.map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full mr-3" style={{
                          backgroundColor: index === 0 ? '#3B82F6' : index === 1 ? '#10B981' : '#F59E0B'
                        }}></div>
                        <span className="font-medium">{item.chain}</span>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{item.percentage}%</p>
                        <p className="text-sm text-slate-500">{formatCurrency(item.value)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4">Portfolio Recommendations</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border-l-4 border-blue-500 pl-4">
                  <h3 className="font-semibold text-blue-600 mb-2">Rebalancing Opportunity</h3>
                  <p className="text-sm text-slate-600 mb-2">
                    Consider reducing Ethereum exposure from 65% to 50% to improve diversification
                  </p>
                  <p className="text-xs text-slate-500">
                    Expected impact: +2.3% to diversification score
                  </p>
                </div>
                <div className="border-l-4 border-green-500 pl-4">
                  <h3 className="font-semibold text-green-600 mb-2">Tax Optimization</h3>
                  <p className="text-sm text-slate-600 mb-2">
                    Harvest tax losses on CryptoPunks position to offset gains
                  </p>
                  <p className="text-xs text-slate-500">
                    Potential tax savings: £1.20
                  </p>
                </div>
                <div className="border-l-4 border-purple-500 pl-4">
                  <h3 className="font-semibold text-purple-600 mb-2">Risk Management</h3>
                  <p className="text-sm text-slate-600 mb-2">
                    Consider adding stablecoin allocation for liquidity and risk reduction
                  </p>
                  <p className="text-xs text-slate-500">
                    Recommended: 10-15% of portfolio
                  </p>
                </div>
                <div className="border-l-4 border-yellow-500 pl-4">
                  <h3 className="font-semibold text-yellow-600 mb-2">Market Timing</h3>
                  <p className="text-sm text-slate-600 mb-2">
                    DCA strategy recommended for new purchases given current volatility
                  </p>
                  <p className="text-xs text-slate-500">
                    Consider 25% increments over 4 weeks
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Advanced Analytics Section */}
        {activeSection === 'advanced' && (
          <AdvancedAnalytics />
        )}

        {/* Risk Management Section */}
        {activeSection === 'risk' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
              Risk Management & Assessment
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">Portfolio Risk Profile</h3>
                <div className="space-y-4">
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <span className="font-semibold text-red-800 dark:text-red-200">High Risk Areas</span>
                    </div>
                    <ul className="text-sm text-red-700 dark:text-red-300 space-y-2">
                      <li>• Concentration risk: 65% in single collection</li>
                      <li>• Liquidity risk: Limited market depth</li>
                      <li>• Volatility: 12.3% portfolio volatility</li>
                    </ul>
                  </div>
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Shield className="w-5 h-5 text-yellow-600" />
                      <span className="font-semibold text-yellow-800 dark:text-yellow-200">Risk Mitigation</span>
                    </div>
                    <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-2">
                      <li>• Diversify across collections</li>
                      <li>• Add stablecoin allocation</li>
                      <li>• Implement stop-loss orders</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4">Stress Test Results</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">Market Crash Scenario</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">
                      Portfolio impact: -25% to -35%
                    </p>
                    <p className="text-xs text-blue-600 dark:text-blue-400">
                      Recovery time: 6-12 months
                    </p>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">Liquidity Crisis</h4>
                    <p className="text-sm text-purple-700 dark:text-purple-300 mb-2">
                      Portfolio impact: -15% to -20%
                    </p>
                    <p className="text-xs text-purple-600 dark:text-purple-400">
                      Recovery time: 3-6 months
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tax Planning Section */}
        {activeSection === 'tax' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
              Tax Planning & Compliance
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">Tax Year 2024-25 Summary</h3>
                <div className="space-y-4">
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 p-4 rounded-lg">
                    <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">Capital Gains</h4>
                    <div className="space-y-2 text-sm text-green-700 dark:text-green-300">
                      <div className="flex justify-between">
                        <span>Total Gains:</span>
                        <span className="font-semibold">£5,000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Annual Exemption Used:</span>
                        <span className="font-semibold">£3,000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Taxable Amount:</span>
                        <span className="font-semibold">£2,000</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">Tax Optimization</h4>
                    <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                      <li>• Harvest tax losses on underperforming assets</li>
                      <li>• Use remaining £0 annual exemption</li>
                      <li>• Consider timing of gains/losses</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4">HMRC Compliance</h3>
                <div className="space-y-4">
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <FileText className="w-5 h-5 text-yellow-600" />
                      <span className="font-semibold text-yellow-800 dark:text-yellow-200">Reporting Requirements</span>
                    </div>
                    <div className="text-sm text-yellow-700 dark:text-yellow-300 space-y-2">
                      <p>• Self Assessment deadline: 31 January 2026</p>
                      <p>• Digital records must be maintained</p>
                      <p>• All transactions must be documented</p>
                    </div>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">Tax Rates</h4>
                    <div className="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                      <p>• Basic rate: 10% on capital gains</p>
                      <p>• Higher rate: 20% on capital gains</p>
                      <p>• Annual exemption: £3,000 (2024-25)</p>
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

export default Analytics;
