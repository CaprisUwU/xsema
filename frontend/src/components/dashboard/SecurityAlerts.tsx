import React from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface SecurityAlert {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  title: string;
  description: string;
  timestamp: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  resolved: boolean;
}

const SecurityAlerts: React.FC = () => {
  const mockAlerts: SecurityAlert[] = [
    {
      id: '1',
      type: 'warning',
      title: 'High Leverage Detected',
      description: 'Portfolio leverage ratio exceeds recommended threshold',
      timestamp: '11/08/2025 14:30',
      priority: 'medium',
      resolved: false
    },
    {
      id: '2',
      type: 'error',
      title: 'Suspicious Wallet Activity',
      description: 'Unusual transaction patterns detected in connected wallet',
      timestamp: '10/08/2025 16:45',
      priority: 'high',
      resolved: false
    },
    {
      id: '3',
      type: 'success',
      title: 'Security Scan Complete',
      description: 'All security checks passed successfully',
      timestamp: '09/08/2025 12:15',
      priority: 'low',
      resolved: true
    }
  ];

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'info':
        return <Shield className="w-5 h-5 text-blue-600" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      default:
        return <Shield className="w-5 h-5 text-slate-600" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'high':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300';
    }
  };

  const activeAlerts = mockAlerts.filter(alert => !alert.resolved);
  const resolvedAlerts = mockAlerts.filter(alert => alert.resolved);

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          Security Alerts
        </h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-500 dark:text-slate-400">
            {activeAlerts.length} active
          </span>
        </div>
      </div>

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="space-y-3 mb-6">
          {activeAlerts.map((alert) => (
            <div key={alert.id} className="border-l-4 border-yellow-500 pl-4 py-3 bg-yellow-50 dark:bg-yellow-900/10 rounded-r-lg">
              <div className="flex items-start space-x-3">
                {getAlertIcon(alert.type)}
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-medium text-slate-900 dark:text-white">
                      {alert.title}
                    </h4>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(alert.priority)}`}>
                      {alert.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                    {alert.description}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-500">
                    {alert.timestamp}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Resolved Alerts */}
      {resolvedAlerts.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
            Resolved Alerts
          </h4>
          <div className="space-y-2">
            {resolvedAlerts.map((alert) => (
              <div key={alert.id} className="flex items-center space-x-3 text-sm text-slate-500 dark:text-slate-400">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="flex-1">{alert.title}</span>
                <span className="text-xs">{alert.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {mockAlerts.length === 0 && (
        <div className="text-center py-8">
          <Shield className="w-12 h-12 text-green-600 mx-auto mb-3" />
          <p className="text-slate-500 dark:text-slate-400">No security alerts at this time.</p>
        </div>
      )}
    </div>
  );
};

export default SecurityAlerts;
