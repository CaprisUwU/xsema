import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Shield, 
  BarChart3, 
  Eye, 
  AlertTriangle,
  PoundSterling,
  Calendar
} from 'lucide-react';
import { format } from 'date-fns';
import { enGB } from 'date-fns/locale';

// Components
import StatCard from '../components/dashboard/StatCard';
import PortfolioChart from '../components/dashboard/PortfolioChart';
import RecentTransactions from '../components/dashboard/RecentTransactions';
import SecurityAlerts from '../components/dashboard/SecurityAlerts';
import MarketOverview from '../components/dashboard/MarketOverview';

// Types
interface DashboardStats {
  totalValue: number;
  totalChange: number;
  changePercentage: number;
  securityScore: number;
  riskLevel: string;
  activeAlerts: number;
  transactions24h: number;
}

const Dashboard: React.FC = () => {
  // Mock data - in real app this would come from API
  const stats: DashboardStats = {
    totalValue: 125000.50,
    totalChange: 3250.75,
    changePercentage: 2.67,
    securityScore: 87,
    riskLevel: 'Low',
    activeAlerts: 2,
    transactions24h: 15
  };

  // UK date formatting
  const currentDate = format(new Date(), 'EEEE, d MMMM yyyy', { locale: enGB });
  const currentTime = format(new Date(), 'HH:mm', { locale: enGB });

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Welcome back to XSEMA
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            {currentDate} at {currentTime}
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
            Refresh Data
          </button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6"
      >
        <StatCard
          title="Portfolio Value"
          value={`£${stats.totalValue.toLocaleString('en-GB', { 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 2 
          })}`}
          change={stats.totalChange}
          changePercentage={stats.changePercentage}
          icon={TrendingUp}
          trend={stats.totalChange >= 0 ? 'up' : 'down'}
          className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20"
        />
        
        <StatCard
          title="Security Score"
          value={`${stats.securityScore}/100`}
          change={stats.securityScore - 85}
          changePercentage={((stats.securityScore - 85) / 85) * 100}
          icon={Shield}
          trend="up"
          className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20"
        />
        
        <StatCard
          title="Risk Level"
          value={stats.riskLevel}
          change={0}
          changePercentage={0}
          icon={AlertTriangle}
          trend="neutral"
          className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20"
        />
        
        <StatCard
          title="24h Transactions"
          value={stats.transactions24h.toString()}
          change={3}
          changePercentage={25}
          icon={BarChart3}
          trend="up"
          className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20"
        />
      </motion.div>

      {/* Portfolio Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.15 }}
        className="mb-6"
      >
        <PortfolioChart />
      </motion.div>

      {/* Main Content Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Portfolio Chart */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Portfolio Performance
              </h2>
              <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                <Calendar className="w-4 h-4" />
                <span>Last 30 days</span>
              </div>
            </div>
            <PortfolioChart />
          </div>
        </div>

        {/* Security Alerts */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Security Alerts
              </h2>
              <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-red-900 dark:text-red-300">
                {stats.activeAlerts} Active
              </span>
            </div>
            <SecurityAlerts />
          </div>
        </div>
      </motion.div>

      {/* Bottom Row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Recent Transactions */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
              Recent Transactions
            </h2>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors">
              View All
            </button>
          </div>
          <RecentTransactions />
        </div>

        {/* Market Overview */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
              Market Overview
            </h2>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium transition-colors">
              View Details
            </button>
          </div>
          <MarketOverview />
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
      >
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-6">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex flex-col items-center p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all group">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-200 dark:group-hover:bg-blue-800/50 transition-colors">
              <Eye className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              View Portfolio
            </span>
          </button>

          <button className="flex flex-col items-center p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-green-300 dark:hover:border-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 transition-all group">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-green-200 dark:group-hover:bg-green-800/50 transition-colors">
              <Shield className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Security Scan
            </span>
          </button>

          <button className="flex flex-col items-center p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-purple-300 dark:hover:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all group">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-purple-200 dark:group-hover:bg-purple-800/50 transition-colors">
              <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Analytics
            </span>
          </button>

          <button className="flex flex-col items-center p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-orange-300 dark:hover:border-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-all group">
            <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-orange-200 dark:group-hover:bg-orange-800/50 transition-colors">
              <TrendingUp className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Market Data
            </span>
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
