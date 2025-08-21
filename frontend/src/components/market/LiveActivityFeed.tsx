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
  type: 'sale' | 'bid' | 'listing' | 'transfer';
  collection: string;
  token_id: string;
  token_name: string;
  price: number;
  price_usd: number;
  currency: string;
  from_address: string;
  to_address: string;
  transaction_hash: string;
  timestamp: string;
  marketplace: string;
  rarity_score?: number;
  price_change?: number;
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

  // Mock data for demonstration - in production this would come from WebSocket/API
  useEffect(() => {
    const mockActivities: ActivityItem[] = [
      {
        id: '1',
        type: 'sale',
        collection: '0x1234...',
        token_id: '1234',
        token_name: 'Bored Ape #1234',
        price: 25.5,
        price_usd: 51000,
        currency: 'ETH',
        from_address: '0xabcd...',
        to_address: '0xefgh...',
        transaction_hash: '0x1234...',
        timestamp: new Date().toISOString(),
        marketplace: 'OpenSea',
        rarity_score: 95.2,
        price_change: 12.5
      },
      {
        id: '2',
        type: 'bid',
        collection: '0x5678...',
        token_id: '5678',
        token_name: 'Doodle #5678',
        price: 8.2,
        price_usd: 16400,
        currency: 'ETH',
        from_address: '0xijkl...',
        to_address: '0xmnop...',
        transaction_hash: '0x5678...',
        timestamp: new Date(Date.now() - 30000).toISOString(),
        marketplace: 'Blur',
        rarity_score: 87.3,
        price_change: -2.1
      },
      {
        id: '3',
        type: 'listing',
        collection: '0x9abc...',
        token_id: '9abc',
        token_name: 'Azuki #9abc',
        price: 12.8,
        price_usd: 25600,
        currency: 'ETH',
        from_address: '0xqrst...',
        to_address: '',
        transaction_hash: '0x9abc...',
        timestamp: new Date(Date.now() - 60000).toISOString(),
        marketplace: 'OpenSea',
        rarity_score: 92.1,
        price_change: 0
      }
    ];

    const mockCollections: CollectionActivity[] = [
      {
        collection: '0x1234...',
        collection_name: 'Bored Ape Yacht Club',
        floor_price: 25.5,
        floor_change_24h: 12.5,
        volume_24h: 1250.5,
        sales_count_24h: 45,
        recent_activities: mockActivities.filter(a => a.collection === '0x1234...')
      },
      {
        collection: '0x5678...',
        collection_name: 'Doodles',
        floor_price: 8.2,
        floor_change_24h: -2.1,
        volume_24h: 450.2,
        sales_count_24h: 23,
        recent_activities: mockActivities.filter(a => a.collection === '0x5678...')
      },
      {
        collection: '0x9abc...',
        collection_name: 'Azuki',
        floor_price: 12.8,
        floor_change_24h: 0,
        volume_24h: 890.7,
        sales_count_24h: 34,
        recent_activities: mockActivities.filter(a => a.collection === '0x9abc...')
      }
    ];

    setActivities(mockActivities);
    setCollections(mockCollections);
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
                          {activity.token_name}
                        </h4>
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                          {activity.collection_name || activity.collection}
                        </p>
                      </div>
                      {activity.rarity_score && (
                        <div className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 rounded text-xs font-medium text-blue-700 dark:text-blue-400">
                          Rarity: {activity.rarity_score}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-slate-900 dark:text-white">
                          {activity.price} {activity.currency}
                        </span>
                        <span className="text-xs text-slate-600 dark:text-slate-400">
                          (£{(activity.price_usd * 0.79).toFixed(2)})
                        </span>
                      </div>
                      {activity.price_change !== undefined && (
                        <span className={`text-xs font-medium ${getPriceChangeColor(activity.price_change)}`}>
                          {activity.price_change > 0 ? '+' : ''}{activity.price_change}%
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-4 text-xs text-slate-600 dark:text-slate-400">
                      <span>From: {formatAddress(activity.from_address)}</span>
                      {activity.to_address && (
                        <span>To: {formatAddress(activity.to_address)}</span>
                      )}
                      <span>{activity.marketplace}</span>
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
