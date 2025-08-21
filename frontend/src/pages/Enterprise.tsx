/**
 * Enterprise Page
 * 
 * Comprehensive enterprise features showcase:
 * - Enterprise dashboard integration
 * - SSO and authentication features
 * - Advanced reporting capabilities
 * - API marketplace preview
 * - Performance optimization features
 * - Market expansion roadmap
 */

import React, { useState } from 'react';
import { 
  Building2, 
  Shield, 
  BarChart3, 
  Zap, 
  Globe, 
  Users,
  Lock,
  Database,
  Cloud,
  Key,
  FileText,
  Settings,
  CheckCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  Activity,
  Rocket,
  Target,
  Award
} from 'lucide-react';
import EnterpriseDashboard from '../components/enterprise/EnterpriseDashboard';

const Enterprise: React.FC = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const enterpriseFeatures = [
    {
      id: 'sso',
      name: 'Single Sign-On (SSO)',
      description: 'Enterprise SSO with SAML 2.0, OAuth 2.0, and OpenID Connect',
      status: 'ready',
      icon: Key,
      benefits: ['Centralized authentication', 'Seamless user experience', 'Enhanced security']
    },
    {
      id: 'ldap',
      name: 'LDAP/Active Directory',
      description: 'Enterprise directory integration with automatic user provisioning',
      status: 'ready',
      icon: Database,
      benefits: ['User synchronization', 'Group management', 'Role-based access control']
    },
    {
      id: 'mfa',
      name: 'Multi-Factor Authentication',
      description: 'TOTP, SMS, and hardware key support for enhanced security',
      status: 'ready',
      icon: Shield,
      benefits: ['Enhanced security', 'Compliance ready', 'Flexible options']
    },
    {
      id: 'reporting',
      name: 'Advanced Reporting',
      description: 'Custom report builder with compliance and business intelligence tools',
      status: 'development',
      icon: BarChart3,
      benefits: ['Custom dashboards', 'Compliance reporting', 'Business intelligence']
    },
    {
      id: 'api',
      name: 'API Marketplace',
      description: 'Third-party integrations and developer platform',
      status: 'planning',
      icon: Globe,
      benefits: ['Third-party integrations', 'Developer SDKs', 'Plugin system']
    },
    {
      id: 'performance',
      name: 'Performance Optimization',
      description: 'Database optimization, caching, and scalability enhancements',
      status: 'planning',
      icon: Zap,
      benefits: ['Improved performance', 'Auto-scaling', 'Real-time monitoring']
    }
  ];

  const complianceFrameworks = [
    {
      name: 'GDPR',
      status: 'compliant',
      description: 'Data protection and privacy compliance',
      last_audit: '2025-01-15',
      next_audit: '2025-04-15'
    },
    {
      name: 'SOC 2 Type II',
      status: 'compliant',
      description: 'Security, availability, and confidentiality controls',
      last_audit: '2025-01-10',
      next_audit: '2025-07-10'
    },
    {
      name: 'ISO 27001',
      status: 'pending',
      description: 'Information security management system',
      last_audit: '2025-01-05',
      next_audit: '2025-03-05'
    },
    {
      name: 'MiFID II',
      status: 'non_compliant',
      description: 'Financial services regulation compliance',
      last_audit: '2024-12-20',
      next_audit: '2025-02-20'
    }
  ];

  const performanceMetrics = [
    { name: 'API Response Time', current: 145, target: 200, unit: 'ms', trend: 'stable' },
    { name: 'Database Query Time', current: 25, target: 50, unit: 'ms', trend: 'up' },
    { name: 'Cache Hit Rate', current: 94.2, target: 90, unit: '%', trend: 'up' },
    { name: 'Error Rate', current: 0.12, target: 0.5, unit: '%', trend: 'down' },
    { name: 'System Uptime', current: 99.97, target: 99.9, unit: '%', trend: 'up' }
  ];

  const sections = [
    { id: 'overview', name: 'Overview', icon: Building2 },
    { id: 'features', name: 'Enterprise Features', icon: Shield },
    { id: 'compliance', name: 'Compliance', icon: CheckCircle },
    { id: 'performance', name: 'Performance', icon: Zap },
    { id: 'roadmap', name: 'Roadmap', icon: Rocket },
    { id: 'dashboard', name: 'Enterprise Dashboard', icon: BarChart3 }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'development':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'planning':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4" />;
      case 'development':
        return <Clock className="w-4 h-4" />;
      case 'planning':
        return <Target className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getComplianceStatusColor = (status: string) => {
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

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
            Enterprise Features
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            Professional-grade NFT portfolio management for enterprise organizations
          </p>
        </div>

        {/* Section Navigation */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 mb-8">
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
          <div className="space-y-8">
            {/* Enterprise Value Proposition */}
            <div className="bg-white dark:bg-slate-800 rounded-xl p-8">
              <div className="text-center mb-8">
                <Building2 className="w-16 h-16 text-blue-600 dark:text-blue-400 mx-auto mb-4" />
                <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                  Enterprise-Grade NFT Portfolio Management
                </h2>
                <p className="text-lg text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
                  XSEMA Enterprise provides institutional-grade tools for managing NFT portfolios at scale, 
                  with enterprise security, compliance, and integration capabilities.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="text-center">
                  <Shield className="w-12 h-12 text-green-600 dark:text-green-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Enterprise Security</h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    SSO, LDAP integration, MFA, and comprehensive security controls
                  </p>
                </div>
                <div className="text-center">
                  <CheckCircle className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Compliance Ready</h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    GDPR, SOC 2, ISO 27001, and regulatory compliance built-in
                  </p>
                </div>
                <div className="text-center">
                  <Zap className="w-12 h-12 text-purple-600 dark:text-purple-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">High Performance</h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    Optimized for scale with real-time monitoring and auto-scaling
                  </p>
                </div>
              </div>
            </div>

            {/* Key Benefits */}
            <div className="bg-white dark:bg-slate-800 rounded-xl p-8">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Key Benefits</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-start space-x-3">
                  <Award className="w-6 h-6 text-blue-600 dark:text-blue-400 mt-1" />
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white mb-1">Professional Portfolio Management</h3>
                    <p className="text-slate-600 dark:text-slate-400">
                      Advanced P&L tracking, risk assessment, and ML-powered insights
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Users className="w-6 h-6 text-green-600 dark:text-green-400 mt-1" />
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white mb-1">Team Collaboration</h3>
                    <p className="text-slate-600 dark:text-slate-400">
                      Multi-user access with role-based permissions and audit trails
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Globe className="w-6 h-6 text-purple-600 dark:text-purple-400 mt-1" />
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white mb-1">Enterprise Integrations</h3>
                    <p className="text-slate-600 dark:text-slate-400">
                      Connect with existing enterprise systems and workflows
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <BarChart3 className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mt-1" />
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white mb-1">Advanced Reporting</h3>
                    <p className="text-slate-600 dark:text-slate-400">
                      Custom reports, compliance tools, and business intelligence
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enterprise Features Section */}
        {activeSection === 'features' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Enterprise Features</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {enterpriseFeatures.map((feature) => {
                  const Icon = feature.icon;
                  return (
                    <div key={feature.id} className="border border-slate-200 dark:border-slate-700 rounded-lg p-6">
                      <div className="flex items-start space-x-4">
                        <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                          <Icon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{feature.name}</h3>
                            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(feature.status)}`}>
                              {feature.status}
                            </div>
                          </div>
                          <p className="text-slate-600 dark:text-slate-400 mb-3">{feature.description}</p>
                          <ul className="space-y-1">
                            {feature.benefits.map((benefit, index) => (
                              <li key={index} className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                                <CheckCircle className="w-4 h-4 text-green-600" />
                                <span>{benefit}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Compliance Section */}
        {activeSection === 'compliance' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Compliance & Security</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {complianceFrameworks.map((framework, index) => (
                  <div key={index} className="border border-slate-200 dark:border-slate-700 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{framework.name}</h3>
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${getComplianceStatusColor(framework.status)}`}>
                        {framework.status.replace('_', ' ')}
                      </div>
                    </div>
                    <p className="text-slate-600 dark:text-slate-400 mb-3">{framework.description}</p>
                    <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                      <span>Last audit: {framework.last_audit}</span>
                      <span>Next audit: {framework.next_audit}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Performance Section */}
        {activeSection === 'performance' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Performance Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {performanceMetrics.map((metric, index) => (
                  <div key={index} className="border border-slate-200 dark:border-slate-700 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium text-slate-900 dark:text-white">{metric.name}</h3>
                      {getTrendIcon(metric.trend)}
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {metric.current}{metric.unit}
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">
                        Target: {metric.target}{metric.unit}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Roadmap Section */}
        {activeSection === 'roadmap' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Development Roadmap</h2>
              <div className="space-y-6">
                <div className="border-l-4 border-blue-500 pl-6">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Phase 3A: Enterprise Integration (Weeks 1-6)</h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-3">
                    SSO, LDAP integration, advanced user management, and compliance framework
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                    <Clock className="w-4 h-4" />
                    <span>In Progress</span>
                  </div>
                </div>
                <div className="border-l-4 border-yellow-500 pl-6">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Phase 3B: Advanced Reporting (Weeks 7-12)</h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-3">
                    Custom report builder, compliance tools, and business intelligence features
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                    <Target className="w-4 h-4" />
                    <span>Planning</span>
                  </div>
                </div>
                <div className="border-l-4 border-purple-500 pl-6">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Phase 3C: API Marketplace (Weeks 13-18)</h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-3">
                    Third-party integrations, developer platform, and plugin system
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                    <Target className="w-4 h-4" />
                    <span>Planning</span>
                  </div>
                </div>
                <div className="border-l-4 border-green-500 pl-6">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Phase 3D: Performance Optimization (Weeks 19-24)</h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-3">
                    Database optimization, caching improvements, and scalability enhancements
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                    <Target className="w-4 h-4" />
                    <span>Planning</span>
                  </div>
                </div>
                <div className="border-l-4 border-indigo-500 pl-6">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Phase 3E: Market Expansion (Weeks 25-30)</h3>
                  <p className="text-slate-600 dark:text-slate-400 mb-3">
                    Additional blockchain networks, geographic expansion, and multi-currency support
                  </p>
                  <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                    <Target className="w-4 h-4" />
                    <span>Planning</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enterprise Dashboard Section */}
        {activeSection === 'dashboard' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Enterprise Dashboard</h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6">
                Comprehensive enterprise monitoring and management dashboard
              </p>
              <EnterpriseDashboard />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Enterprise;
