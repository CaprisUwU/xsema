import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react';

const Security: React.FC = () => {
  const [showDetails, setShowDetails] = useState(false);

  const securityMetrics = {
    overallScore: 95,
    riskLevel: 'Low',
    threatsDetected: 2,
    walletsAnalyzed: 15,
    suspiciousActivity: 1
  };

  const walletAnalysis = [
    {
      address: '0x1234...5678',
      riskScore: 85,
      status: 'Safe',
      threats: ['None detected'],
      lastActivity: '11/08/2025 14:30'
    },
    {
      address: '0x8765...4321',
      riskScore: 45,
      status: 'Medium Risk',
      threats: ['High gas usage', 'Multiple failed transactions'],
      lastActivity: '11/08/2025 13:45'
    }
  ];

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Safe':
        return 'bg-green-100 text-green-800';
      case 'Medium Risk':
        return 'bg-yellow-100 text-yellow-800';
      case 'High Risk':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-8">
          Security Analysis
        </h1>

        {/* Security Overview */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
            <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Security Score</h3>
            <p className="text-3xl font-bold text-green-600">{securityMetrics.overallScore}/100</p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
            <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Risk Level</h3>
            <p className="text-2xl font-bold text-blue-600">{securityMetrics.riskLevel}</p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Threats</h3>
            <p className="text-3xl font-bold text-red-600">{securityMetrics.threatsDetected}</p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
            <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Eye className="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Wallets</h3>
            <p className="text-3xl font-bold text-purple-600">{securityMetrics.walletsAnalyzed}</p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 text-center">
            <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Suspicious</h3>
            <p className="text-3xl font-bold text-yellow-600">{securityMetrics.suspiciousActivity}</p>
          </div>
        </div>

        {/* Wallet Analysis */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Wallet Analysis</h2>
            <button 
              onClick={() => setShowDetails(!showDetails)}
              className="flex items-center text-blue-600 hover:text-blue-700"
            >
              {showDetails ? <EyeOff className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
              {showDetails ? 'Hide Details' : 'Show Details'}
            </button>
          </div>

          <div className="space-y-4">
            {walletAnalysis.map((wallet, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-medium">{wallet.address}</h3>
                    <p className="text-sm text-slate-500">Last activity: {wallet.lastActivity}</p>
                  </div>
                  <div className="text-right">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(wallet.status)}`}>
                      {wallet.status}
                    </span>
                    <p className={`text-sm font-medium mt-1 ${getRiskColor(wallet.riskScore)}`}>
                      Risk Score: {wallet.riskScore}/100
                    </p>
                  </div>
                </div>

                {showDetails && (
                  <div className="mt-3 pt-3 border-t">
                    <h4 className="font-medium mb-2">Threats Detected:</h4>
                    <ul className="space-y-1">
                      {wallet.threats.map((threat, threatIndex) => (
                        <li key={threatIndex} className="flex items-center text-sm">
                          {threat === 'None detected' ? (
                            <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2" />
                          )}
                          {threat}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Security Recommendations */}
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">Security Recommendations</h2>
          <div className="space-y-3">
            <div className="flex items-start">
              <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5" />
              <div>
                <p className="font-medium">Enable 2FA on all accounts</p>
                <p className="text-sm text-slate-600">Two-factor authentication adds an extra layer of security</p>
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5" />
              <div>
                <p className="font-medium">Use hardware wallets for large holdings</p>
                <p className="text-sm text-slate-600">Cold storage provides maximum security for valuable assets</p>
              </div>
            </div>
            <div className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
              <div>
                <p className="font-medium">Review suspicious wallet activity</p>
                <p className="text-sm text-slate-600">Monitor wallet 0x8765...4321 for unusual patterns</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Security;
