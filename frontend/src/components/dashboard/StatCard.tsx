import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../../utils/cn';

interface StatCardProps {
  title: string;
  value: string;
  change: number;
  changePercentage: number;
  icon: LucideIcon;
  trend: 'up' | 'down' | 'neutral';
  className?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changePercentage,
  icon: Icon,
  trend,
  className
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Minus className="w-4 h-4 text-slate-400" />;
    }
  };

  const getChangeColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-slate-600';
    }
  };

  return (
    <div className={cn(
      "bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6",
      className
    )}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            {title}
          </p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            {value}
          </p>
          <div className="flex items-center space-x-2">
            {getTrendIcon()}
            <span className={cn("text-sm font-medium", getChangeColor())}>
              {trend !== 'neutral' && (
                <>
                  {trend === 'up' ? '+' : '-'}
                  £{Math.abs(change).toLocaleString('en-GB', { 
                    minimumFractionDigits: 2, 
                    maximumFractionDigits: 2 
                  })}
                  {' '}
                  ({Math.abs(changePercentage).toFixed(2)}%)
                </>
              )}
              {trend === 'neutral' && 'No change'}
            </span>
          </div>
        </div>
        <div className="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-slate-600 dark:text-slate-400" />
        </div>
      </div>
    </div>
  );
};

export default StatCard;
