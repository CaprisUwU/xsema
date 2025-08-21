/**
 * Enterprise Dashboard Component
 * 
 * Foundation for Phase 3 enterprise features:
 * - SSO and authentication status
 * - Enterprise reporting capabilities
 * - API marketplace integration
 * - Performance monitoring
 * - Compliance and security status
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Users, 
  BarChart3, 
  Zap, 
  Globe, 
  Lock,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  Database,
  Cloud,
  Key,
  FileText,
  Settings,
  Activity
} from 'lucide-react';

interface EnterpriseStatus {
  sso_enabled: boolean;
  ldap_connected: boolean;
  mfa_required: boolean;
  compliance_status: 'compliant' | 'pending' | 'non_compliant';
  performance_score: number;
  uptime_percentage: number;
  active_users: number;
  api_calls_24h: number;
}

interface ComplianceItem {
  id: string;
  name: string;
  status: 'compliant' | 'pending' | 'non_compliant';
  last_checked: string;
  next_review: string;
  description: string;
}

interface PerformanceMetric {
  name: string;
  value: number;
  target: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
}

const EnterpriseDashboard: React.FC = () => {
  const [enterpriseStatus, setEnterpriseStatus] = useState<EnterpriseStatus | null>(null);
  const [complianceItems, setComplianceItems] = useState<ComplianceItem[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetric[]>([]);
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data for demonstration
  useEffect(() => {
    setEnterpriseStatus({
      sso_enabled: true,
      ldap_connected: true,
      mfa_required: true,
      compliance_status: 'compliant',
      performance_score: 98.5,
      uptime_percentage: 99.97,
      active_users: 1250,
      api_calls_24h: 2500000
    });

    setComplianceItems([
      {
        id: '1',
        name: 'GDPR Compliance',
        status: 'compliant',
        last_checked: '2025-01-15T10:30:00Z',
        next_review: '2025-04-15T10:30:00Z',
        description: 'Data protection and privacy compliance'
      },
      {
        id: '2',
        name: 'SOC 2 Type II',
        status: 'compliant',
        last_checked: '2025-01-10T14:20:00Z',
        next_review: '2025-07-10T14:20:00Z',
        description: 'Security, availability, and confidentiality controls'
      },
      {
        id: '3',
        name: 'ISO 27001',
        status: 'pending',
        last_checked: '2025-01-05T09:15:00Z',
        next_review: '2025-03-05T09:15:00Z',
        description: 'Information security management system'
      },
      {
        id: '4',
        name: 'MiFID II Compliance',
        status: 'non_compliant',
        last_checked: '2024-12-20T16:45:00Z',
        next_review: '2025-02-20T16:45:00Z',
        description: 'Financial services regulation compliance'
      }
    ]);

    setPerformanceMetrics([
      {
        name: 'API Response Time',
        value: 145,
        target: 200,
        unit: 'ms',
        trend: 'stable'
      },
      {
        name: 'Database Query Time',
        value: 25,
        target: 50,
        unit: 'ms',
        trend: 'up'
      },
      {
        name: 'Cache Hit Rate',
        value: 94.2,
        target: 90,
        unit: '%',
        trend: 'up'
      },
      {
        name: 'Error Rate',
        value: 0.12,
        target: 0.5,
        unit: '%',
        trend: 'down'
      }
    ]);
  }, []);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'security', name: 'Security & Compliance', icon: Shield },
    { id: 'performance', name: 'Performance', icon: Zap },
    { id: 'users', name: 'User Management', icon: Users },
    { id: 'integrations', name: 'Integrations', icon: Globe },
    { id: 'settings', name: 'Settings', icon: Settings }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'non_compliant':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
        return <CheckCircle className="w-4 h-4" />;
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'non_compliant':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down':
        return <TrendingUp className="w-4 h-4 text-red-600 transform rotate-180" />;
      default:
        return <TrendingUp className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatNumber = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (!enterpriseStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white dark:bg-slate-800 rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Enterprise Dashboard
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Comprehensive enterprise features and compliance monitoring
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
      {activeTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Enterprise Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* SSO Status */}
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                  <Key className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${enterpriseStatus.sso_enabled ? 'text-green-600 bg-green-100 dark:bg-green-900/20' : 'text-red-600 bg-red-100 dark:bg-red-900/20'}`}>
                  {enterpriseStatus.sso_enabled ? 'Active' : 'Inactive'}
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">SSO Enabled</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {enterpriseStatus.sso_enabled ? 'Single sign-on is active' : 'Single sign-on is disabled'}
              </p>
            </div>

            {/* LDAP Status */}
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${enterpriseStatus.ldap_connected ? 'text-green-600 bg-green-100 dark:bg-green-900/20' : 'text-red-600 bg-red-100 dark:bg-red-900/20'}`}>
                  {enterpriseStatus.ldap_connected ? 'Connected' : 'Disconnected'}
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">LDAP Connected</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {enterpriseStatus.ldap_connected ? 'Active Directory connected' : 'Active Directory disconnected'}
              </p>
            </div>

            {/* Performance Score */}
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {enterpriseStatus.performance_score}%
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Performance Score</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Overall system performance rating
              </p>
            </div>

            {/* Uptime */}
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                  {enterpriseStatus.uptime_percentage}%
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">System Uptime</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Current system availability
              </p>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Active Users */}
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Active Users</h3>
              <div className="flex items-center justify-between">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {formatNumber(enterpriseStatus.active_users)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Currently online
                </div>
              </div>
            </div>

            {/* API Usage */}
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">API Usage (24h)</h3>
              <div className="flex items-center justify-between">
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {formatNumber(enterpriseStatus.api_calls_24h)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  API calls today
                </div>
              </div>
            </div>
          </div>

          {/* Compliance Overview */}
          <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {complianceItems.map((item) => (
                <div key={item.id} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-slate-600 rounded-lg">
                  {getStatusIcon(item.status)}
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{item.name}</div>
                    <div className={`text-xs px-2 py-1 rounded-full inline-block ${getStatusColor(item.status)}`}>
                      {item.status.replace('_', ' ')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Security & Compliance Tab */}
      {activeTab === 'security' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Security Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">SSO Enabled</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">MFA Required</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">LDAP Connected</span>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance Details</h3>
              <div className="space-y-4">
                {complianceItems.map((item) => (
                  <div key={item.id} className="border border-gray-200 dark:border-slate-600 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">{item.name}</h4>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(item.status)}`}>
                        {item.status.replace('_', ' ')}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{item.description}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>Last checked: {formatDate(item.last_checked)}</span>
                      <span>Next review: {formatDate(item.next_review)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Performance Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {performanceMetrics.map((metric, index) => (
                  <div key={index} className="border border-gray-200 dark:border-slate-600 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">{metric.name}</h4>
                      {getTrendIcon(metric.trend)}
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {metric.value}{metric.unit}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        Target: {metric.target}{metric.unit}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* User Management Tab */}
      {activeTab === 'users' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">User Management</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <Users className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {formatNumber(enterpriseStatus.active_users)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Users</div>
              </div>
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <Shield className="w-8 h-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {enterpriseStatus.mfa_required ? '100%' : '0%'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">MFA Enabled</div>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <Key className="w-8 h-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {enterpriseStatus.sso_enabled ? 'SSO' : 'Local'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Authentication</div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Integrations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border border-gray-200 dark:border-slate-600 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <Database className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-gray-900 dark:text-white">LDAP/Active Directory</span>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium inline-block ${enterpriseStatus.ldap_connected ? 'text-green-600 bg-green-100 dark:bg-green-900/20' : 'text-red-600 bg-red-100 dark:bg-red-900/20'}`}>
                  {enterpriseStatus.ldap_connected ? 'Connected' : 'Disconnected'}
                </div>
              </div>
              <div className="border border-gray-200 dark:border-slate-600 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-2">
                  <Cloud className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-gray-900 dark:text-white">SSO Providers</span>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium inline-block ${enterpriseStatus.sso_enabled ? 'text-green-600 bg-green-100 dark:bg-green-900/20' : 'text-red-600 bg-red-100 dark:bg-red-900/20'}`}>
                  {enterpriseStatus.sso_enabled ? 'Active' : 'Inactive'}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Enterprise Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-600 rounded-lg">
                <span className="text-gray-700 dark:text-gray-300">Enable SSO</span>
                <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                  <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1"></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-600 rounded-lg">
                <span className="text-gray-700 dark:text-gray-300">Require MFA</span>
                <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                  <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1"></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-600 rounded-lg">
                <span className="text-gray-700 dark:text-gray-300">LDAP Sync</span>
                <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                  <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1"></div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default EnterpriseDashboard;
