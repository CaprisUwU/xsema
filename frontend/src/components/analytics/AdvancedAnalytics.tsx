/**
 * Advanced Analytics Component
 * 
 * Integrates all Phase 2 advanced features:
 * - P&L calculations and performance metrics
 * - Risk assessment and stress testing
 * - ML-powered recommendations
 * - Tax reporting and compliance
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Shield, 
  Brain, 
  FileText, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react';

interface PnLData {
  total_cost_basis: number;
  current_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  roi_percentage: number;
  annualized_roi?: number;
  performance_metrics?: {
    sharpe_ratio?: number;
    sortino_ratio?: number;
    max_drawdown?: number;
    volatility?: number;
    beta?: number;
  };
}

interface RiskAssessment {
  overall_risk: string;
  overall_score: number;
  risk_factors: Array<{
    category: string;
    description: string;
    risk_score: number;
    impact: string;
    mitigation: string;
  }>;
  recommendations: string[];
}

interface MLRecommendation {
  type: string;
  asset_name: string;
  confidence: string;
  confidence_score: number;
  reasoning: string;
  expected_return: number;
  risk_level: string;
  time_horizon: string;
}

interface TaxReport {
  tax_year: string;
  total_proceeds: number;
  total_cost_basis: number;
  total_gains: number;
  total_losses: number;
  net_gains: number;
  annual_exemption_used: number;
  annual_exemption_remaining: number;
  taxable_gains: number;
  estimated_tax: number;
}

const AdvancedAnalytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState('pnl');
  const [pnlData, setPnlData] = useState<PnLData | null>(null);
  const [riskData, setRiskData] = useState<RiskAssessment | null>(null);
  const [recommendations, setRecommendations] = useState<MLRecommendation[]>([]);
  const [taxData, setTaxData] = useState<TaxReport | null>(null);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration - in production this would come from API
  useEffect(() => {
    setPnlData({
      total_cost_basis: 50000,
      current_value: 75000,
      unrealized_pnl: 25000,
      realized_pnl: 5000,
      total_pnl: 30000,
      roi_percentage: 60,
      annualized_roi: 45.25,
      performance_metrics: {
        sharpe_ratio: 1.85,
        sortino_ratio: 2.12,
        max_drawdown: 8.50,
        volatility: 12.30,
        beta: 1.20
      }
    });

    setRiskData({
      overall_risk: 'medium',
      overall_score: 45.2,
      risk_factors: [
        {
          category: 'concentration',
          description: 'High concentration in single collection',
          risk_score: 75.0,
          impact: 'Significant portfolio volatility',
          mitigation: 'Diversify across multiple collections'
        },
        {
          category: 'liquidity',
          description: 'Limited market liquidity for some assets',
          risk_score: 60.0,
          impact: 'Difficulty selling at fair prices',
          mitigation: 'Maintain adequate cash reserves'
        }
      ],
      recommendations: [
        'Reduce exposure to single collection by 30%',
        'Add assets from different blockchain platforms',
        'Implement stop-loss orders for high-risk positions'
      ]
    });

    setRecommendations([
      {
        type: 'buy',
        asset_name: 'Cool Cats #123',
        confidence: 'high',
        confidence_score: 0.85,
        reasoning: 'Asset appears undervalued based on fundamentals',
        expected_return: 0.18,
        risk_level: 'medium',
        time_horizon: '3-6 months'
      },
      {
        type: 'sell',
        asset_name: 'Overvalued Asset',
        confidence: 'medium',
        confidence_score: 0.70,
        reasoning: 'Asset trading above fair value',
        expected_return: -0.10,
        risk_level: 'high',
        time_horizon: '1-3 months'
      }
    ]);

    setTaxData({
      tax_year: '2024-25',
      total_proceeds: 25000,
      total_cost_basis: 20000,
      total_gains: 5000,
      total_losses: 1000,
      net_gains: 4000,
      annual_exemption_used: 3000,
      annual_exemption_remaining: 0,
      taxable_gains: 1000,
      estimated_tax: 200
    });
  }, []);

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'very_high': return 'text-green-600 bg-green-100';
      case 'high': return 'text-blue-600 bg-blue-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const tabs = [
    { id: 'pnl', name: 'P&L Analysis', icon: TrendingUp },
    { id: 'risk', name: 'Risk Assessment', icon: Shield },
    { id: 'ml', name: 'ML Recommendations', icon: Brain },
    { id: 'tax', name: 'Tax Reporting', icon: FileText }
  ];

  return (
    <div className="p-6 bg-white dark:bg-slate-800 rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Advanced Analytics Dashboard
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Comprehensive portfolio analysis powered by Phase 2 advanced features
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {/* P&L Analysis Tab */}
        {activeTab === 'pnl' && pnlData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Total Cost Basis</div>
                <div className="text-2xl font-bold">£{pnlData.total_cost_basis.toLocaleString()}</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Current Value</div>
                <div className="text-2xl font-bold">£{pnlData.current_value.toLocaleString()}</div>
              </div>
              <div className={`p-4 rounded-lg text-white ${
                pnlData.total_pnl >= 0 
                  ? 'bg-gradient-to-r from-green-500 to-green-600' 
                  : 'bg-gradient-to-r from-red-500 to-red-600'
              }`}>
                <div className="text-sm opacity-90">Total P&L</div>
                <div className="text-2xl font-bold">£{pnlData.total_pnl.toLocaleString()}</div>
                <div className="text-sm opacity-90">{pnlData.roi_percentage.toFixed(2)}% ROI</div>
              </div>
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-4 rounded-lg text-white">
                <div className="text-sm opacity-90">Annualized ROI</div>
                <div className="text-2xl font-bold">
                  {pnlData.annualized_roi ? `${pnlData.annualized_roi.toFixed(2)}%` : 'N/A'}
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            {pnlData.performance_metrics && (
              <div className="bg-gray-50 dark:bg-slate-700 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Performance Metrics
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {pnlData.performance_metrics.sharpe_ratio?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Sharpe Ratio</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {pnlData.performance_metrics.sortino_ratio?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Sortino Ratio</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {pnlData.performance_metrics.max_drawdown?.toFixed(2) || 'N/A'}%
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Max Drawdown</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">
                      {pnlData.performance_metrics.volatility?.toFixed(2) || 'N/A'}%
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Volatility</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {pnlData.performance_metrics.beta?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Beta</div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Risk Assessment Tab */}
        {activeTab === 'risk' && riskData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overall Risk Score */}
            <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 rounded-lg text-white">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm opacity-90">Overall Risk Level</div>
                  <div className="text-3xl font-bold capitalize">{riskData.overall_risk}</div>
                  <div className="text-sm opacity-90">Risk Score: {riskData.overall_score.toFixed(1)}</div>
                </div>
                <div className="text-right">
                  <div className="text-6xl opacity-20">
                    {riskData.overall_risk === 'low' && <CheckCircle />}
                    {riskData.overall_risk === 'medium' && <AlertTriangle />}
                    {riskData.overall_risk === 'high' && <XCircle />}
                    {riskData.overall_risk === 'critical' && <XCircle />}
                  </div>
                </div>
              </div>
            </div>

            {/* Risk Factors */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Risk Factors
              </h3>
              {riskData.risk_factors.map((factor, index) => (
                <div key={index} className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(factor.category)}`}>
                          {factor.category}
                        </span>
                        <span className="text-sm font-medium text-red-800 dark:text-red-200">
                          Risk Score: {factor.risk_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="text-sm text-red-700 dark:text-red-300 mb-2">
                        {factor.description}
                      </div>
                      <div className="text-xs text-red-600 dark:text-red-400">
                        <strong>Impact:</strong> {factor.impact}
                      </div>
                      <div className="text-xs text-red-600 dark:text-red-400">
                        <strong>Mitigation:</strong> {factor.mitigation}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recommendations */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
                Risk Mitigation Recommendations
              </h3>
              <ul className="space-y-2">
                {riskData.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm text-blue-800 dark:text-blue-200">
                    <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}

        {/* ML Recommendations Tab */}
        {activeTab === 'ml' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="bg-gradient-to-r from-purple-500 to-indigo-500 p-6 rounded-lg text-white">
              <div className="flex items-center space-x-3">
                <Brain className="w-8 h-8" />
                <div>
                  <div className="text-lg font-semibold">AI-Powered Portfolio Insights</div>
                  <div className="text-sm opacity-90">
                    Machine learning recommendations based on market analysis and portfolio performance
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.map((rec, index) => (
                <div key={index} className={`border rounded-lg p-4 ${
                  rec.type === 'buy' 
                    ? 'border-green-200 bg-green-50 dark:bg-green-900/20' 
                    : 'border-red-200 bg-red-50 dark:bg-red-900/20'
                }`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      rec.type === 'buy' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {rec.type.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(rec.confidence)}`}>
                      {rec.confidence.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div className="mb-3">
                    <div className="font-semibold text-gray-900 dark:text-white">{rec.asset_name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{rec.reasoning}</div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500 dark:text-gray-400">Expected Return</div>
                      <div className={`font-semibold ${
                        rec.expected_return >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {(rec.expected_return * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500 dark:text-gray-400">Risk Level</div>
                      <div className="font-semibold capitalize">{rec.risk_level}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 dark:text-gray-400">Time Horizon</div>
                      <div className="font-semibold">{rec.time_horizon}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 dark:text-gray-400">Confidence</div>
                      <div className="font-semibold">{(rec.confidence_score * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Tax Reporting Tab */}
        {activeTab === 'tax' && taxData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 rounded-lg text-white">
              <div className="flex items-center space-x-3">
                <FileText className="w-8 h-8" />
                <div>
                  <div className="text-lg font-semibold">Tax Year {taxData.tax_year}</div>
                  <div className="text-sm opacity-90">
                    HMRC-compliant tax reporting and capital gains analysis
                  </div>
                </div>
              </div>
            </div>

            {/* Tax Summary Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-slate-700 p-4 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Proceeds</div>
                <div className="text-xl font-bold text-gray-900 dark:text-white">
                  £{taxData.total_proceeds.toLocaleString()}
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-slate-700 p-4 rounded-lg">
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Cost Basis</div>
                <div className="text-xl font-bold text-gray-900 dark:text-white">
                  £{taxData.total_cost_basis.toLocaleString()}
                </div>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                <div className="text-sm text-green-600 dark:text-green-400">Total Gains</div>
                <div className="text-xl font-bold text-green-700 dark:text-green-300">
                  £{taxData.total_gains.toLocaleString()}
                </div>
              </div>
              <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                <div className="text-sm text-red-600 dark:text-red-400">Total Losses</div>
                <div className="text-xl font-bold text-red-700 dark:text-red-300">
                  £{taxData.total_losses.toLocaleString()}
                </div>
              </div>
            </div>

            {/* Tax Calculation Details */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4">
                Tax Calculation Summary
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-blue-800 dark:text-blue-200">Net Capital Gains:</span>
                    <span className="font-semibold text-blue-900 dark:text-blue-100">
                      £{taxData.net_gains.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-800 dark:text-blue-200">Annual Exemption Used:</span>
                    <span className="font-semibold text-blue-900 dark:text-blue-100">
                      £{taxData.annual_exemption_used.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-800 dark:text-blue-200">Annual Exemption Remaining:</span>
                    <span className="font-semibold text-blue-900 dark:text-blue-100">
                      £{taxData.annual_exemption_remaining.toLocaleString()}
                    </span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-blue-800 dark:text-blue-200">Taxable Gains:</span>
                    <span className="font-semibold text-blue-900 dark:text-blue-100">
                      £{taxData.taxable_gains.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-800 dark:text-blue-200">Estimated Tax:</span>
                    <span className="font-semibold text-blue-900 dark:text-blue-100">
                      £{taxData.estimated_tax.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-800 dark:text-blue-200">Effective Tax Rate:</span>
                    <span className="font-semibold text-blue-900 dark:text-blue-100">
                      {taxData.taxable_gains > 0 ? ((taxData.estimated_tax / taxData.taxable_gains) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* HMRC Compliance Notice */}
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-4 rounded-lg">
              <div className="flex items-start space-x-3">
                <Info className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-yellow-800 dark:text-yellow-200">
                  <strong>HMRC Compliance:</strong> This report is generated in accordance with UK tax regulations. 
                  The annual exemption for {taxData.tax_year} is £3,000. Please ensure all information is accurate 
                  before submitting to HMRC.
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default AdvancedAnalytics;
