/**
 * Live Activity Feed Component
 * 
 * Provides real-time market activity across NFT collections:
 * - Live sales and transactions
 * - Price movements and trends
 * - Market intelligence and insights
 * - Competitive advantage over other platforms
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Clock, 
  Eye,
  Filter,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface ActivityItem {
  id: string;
  type: 'sale' | 'bid' | 'listing' | 'transfer' | 'floor_price_update';
  collection: string;
  collection_name: string;
  contract_address: string;
  price: number | null;
  currency: string;
  timestamp: string;
  source: string;
}

interface CollectionActivity {
  collection: string;
  collection_name: string;
  floor_price: number;
  floor_change_24h: number;
  volume_24h: number;
  sales_count_24h: number;
  recent_activities: ActivityItem[];
}

const LiveActivityFeed: React.FC = () => {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [collections, setCollections] = useState<CollectionActivity[]>([]);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [isLive, setIsLive] = useState(true);
  const [loading, setLoading] = useState(false);

  // Fetch real data from our market data service
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Import the market data service dynamically to avoid circular dependencies
        const { default: marketDataService } = await import('../../utils/marketDataService');
        
        // Fetch live activity
        const liveActivities = await marketDataService.getLiveActivity(10);
        setActivities(liveActivities);
        
        // For now, we'll use the activities to create collection summaries
        // In the future, this could be enhanced with real collection data
        if (liveActivities.length > 0) {
          const collectionMap = new Map<string, CollectionActivity>();
          
          liveActivities.forEach(activity => {
            if (!collectionMap.has(activity.collection)) {
              collectionMap.set(activity.collection, {
                collection: activity.collection,
                collection_name: activity.collection_name,
                floor_price: activity.price || 0,
                floor_change_24h: 0, // Would need historical data for this
                volume_24h: 0, // Would need volume data for this
                sales_count_24h: 1,
                recent_activities: [activity]
              });
            } else {
              const existing = collectionMap.get(activity.collection)!;
              existing.recent_activities.push(activity);
              existing.sales_count_24h += 1;
            }
          });
          
          setCollections(Array.from(collectionMap.values()));
        }
      } catch (error) {
        console.error('Error fetching live activity:', error);
        // Fall back to mock data if real data fails
        setActivities([]);
        setCollections([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'sale':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'bid':
        return <TrendingUp className="w-4 h-4 text-blue-500" />;
      case 'listing':
        return <Eye className="w-4 h-4 text-yellow-500" />;
      case 'transfer':
        return <Activity className="w-4 h-4 text-purple-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriceChangeColor = (change?: number) => {
    if (!change) return 'text-gray-500';
    return change > 0 ? 'text-green-500' : 'text-red-500';
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatTime = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return time.toLocaleDateString();
  };

  const filteredActivities = activeFilter === 'all' 
    ? activities 
    : activities.filter(activity => activity.type === activeFilter);

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
      {/* Header */}
      <div className="p-6 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Live Market Activity
            </h2>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500' : 'bg-gray-400'}`} />
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {isLive ? 'Live' : 'Paused'}
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsLive(!isLive)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                isLive 
                  ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400' 
                  : 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
              }`}
            >
              {isLive ? 'Pause' : 'Resume'}
            </button>
            <button
              onClick={() => setLoading(true)}
              className="p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-500" />
            <span className="text-sm text-slate-600 dark:text-slate-400">Filter:</span>
          </div>
          {['all', 'sale', 'bid', 'listing', 'transfer'].map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activeFilter === filter
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="p-6">
        <div className="space-y-4">
          <AnimatePresence>
            {filteredActivities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-center space-x-4 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-600"
              >
                {/* Activity Icon */}
                <div className="flex-shrink-0">
                  {getActivityIcon(activity.type)}
                </div>

                {/* Activity Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h4 className="text-sm font-medium text-slate-900 dark:text-white">
                          {activity.collection_name}
                        </h4>
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                          {activity.contract_address.slice(0, 8)}...
                        </p>
                      </div>
                      <div className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 rounded text-xs font-medium text-blue-700 dark:text-blue-400">
                        {activity.type}
                      </div>
                    </div>
                                          <div className="text-right">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-slate-900 dark:text-white">
                            {activity.price ? `${activity.price} ${activity.currency}` : 'N/A'}
                          </span>
                          <span className="text-xs text-slate-600 dark:text-slate-400">
                            {activity.price ? `(£${(activity.price * 2000).toFixed(2)})` : ''}
                          </span>
                        </div>
                      </div>
                  </div>

                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-4 text-xs text-slate-600 dark:text-slate-400">
                      <span>Collection: {activity.collection}</span>
                      <span>Source: {activity.source}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-slate-500">
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(activity.timestamp)}</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Collection Summary */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Collection Activity Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((collection) => (
              <div
                key={collection.collection}
                className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-600"
              >
                <h4 className="font-medium text-slate-900 dark:text-white mb-2">
                  {collection.collection_name}
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-600 dark:text-slate-400">Floor Price:</span>
                    <span className="font-medium">{collection.floor_price} ETH</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600 dark:text-slate-400">24h Change:</span>
                    <span className={`font-medium ${getPriceChangeColor(collection.floor_change_24h)}`}>
                      {collection.floor_change_24h > 0 ? '+' : ''}{collection.floor_change_24h}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600 dark:text-slate-400">24h Volume:</span>
                    <span className="font-medium">{collection.volume_24h} ETH</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600 dark:text-slate-400">24h Sales:</span>
                    <span className="font-medium">{collection.sales_count_24h}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveActivityFeed;
