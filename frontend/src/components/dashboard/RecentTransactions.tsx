import React from 'react';
import { ArrowUpRight, ArrowDownLeft } from 'lucide-react';

interface Transaction {
  id: string;
  type: 'buy' | 'sell';
  asset: string;
  amount: number;
  price: number;
  total: number;
  timestamp: string;
  status: 'completed' | 'pending';
}

const RecentTransactions: React.FC = () => {
  const mockTransactions: Transaction[] = [
    {
      id: '1',
      type: 'buy',
      asset: 'Bored Ape Yacht Club #1234',
      amount: 1,
      price: 15.5,
      total: 15.5,
      timestamp: '11/08/2025 14:30',
      status: 'completed'
    },
    {
      id: '2',
      type: 'sell',
      asset: 'CryptoPunk #5678',
      amount: 1,
      price: 45.2,
      total: 45.2,
      timestamp: '10/08/2025 16:45',
      status: 'completed'
    }
  ];

  const formatCurrency = (value: number) => {
    return `£${value.toLocaleString('en-GB', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  const getTypeColor = (type: string) => {
    return type === 'buy' 
      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
  };

  const getTypeIcon = (type: string) => {
    return type === 'buy' 
      ? <ArrowDownLeft className="w-4 h-4" />
      : <ArrowUpRight className="w-4 h-4" />;
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Recent Transactions
      </h3>
      
      <div className="space-y-4">
        {mockTransactions.map((tx) => (
          <div key={tx.id} className="border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
                  {getTypeIcon(tx.type)}
                </div>
                <div>
                  <p className="font-medium">{tx.asset}</p>
                  <p className="text-sm text-slate-500">{tx.timestamp}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold">{formatCurrency(tx.total)}</p>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(tx.type)}`}>
                  {tx.type.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentTransactions;
