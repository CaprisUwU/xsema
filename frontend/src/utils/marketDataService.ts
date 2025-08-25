/**
 * Market Data Service
 * Fetches real market data from XSEMA backend API
 */

export interface CollectionData {
  name: string;
  slug: string;
  contract_address: string;
  floor_price: number | null;
  floor_price_currency: string;
  volume_24h: number | null;
  volume_7d: number | null;
  total_volume: number | null;
  total_supply: number | null;
  owners_count: number | null;
  verified: boolean;
  image_url: string | null;
}

export interface MarketOverview {
  collections: CollectionData[];
  total_volume_24h: number;
  active_collections: number;
  market_status: string;
  last_updated: string;
}

export interface ActivityItem {
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

class MarketDataService {
  private baseUrl: string;

  constructor() {
    // Use the current hostname and port for the API
    this.baseUrl = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;
  }

  /**
   * Fetch real market overview data
   */
  async getMarketOverview(): Promise<MarketOverview | null> {
    try {
      const response = await fetch(`${this.baseUrl}/market/real-data`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success' && data.data) {
        return data.data;
      } else if (data.status === 'warning' && data.data) {
        // Return the data even if it's mock data
        return data.data;
      } else {
        console.warn('Market data response:', data);
        return null;
      }
    } catch (error) {
      console.error('Error fetching market overview:', error);
      return null;
    }
  }

  /**
   * Fetch marketplace status
   */
  async getMarketplaceStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/marketplace/status`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching marketplace status:', error);
      return null;
    }
  }

  /**
   * Fetch live market activity
   */
  async getLiveActivity(limit: number = 10): Promise<ActivityItem[]> {
    try {
      // For now, we'll simulate live activity based on market data
      // In the future, this could be a WebSocket connection or real-time API
      const marketData = await this.getMarketOverview();
      
      if (!marketData || !marketData.collections) {
        return [];
      }

      // Generate activity items based on real collection data
      const activities: ActivityItem[] = [];
      
      marketData.collections.forEach((collection, index) => {
        if (collection.floor_price) {
          activities.push({
            id: `activity_${index}`,
            type: 'floor_price_update',
            collection: collection.slug,
            collection_name: collection.name,
            contract_address: collection.contract_address,
            price: collection.floor_price,
            currency: collection.floor_price_currency,
            timestamp: new Date().toISOString(),
            source: 'opensea'
          });
        }
      });

      return activities.slice(0, limit);
    } catch (error) {
      console.error('Error fetching live activity:', error);
      return [];
    }
  }

  /**
   * Check if we have real data available
   */
  async hasRealData(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/market/real-data`);
      
      if (!response.ok) {
        return false;
      }
      
      const data = await response.json();
      return data.status === 'success' && data.data_source === 'opensea';
    } catch (error) {
      return false;
    }
  }

  /**
   * Get data source information
   */
  async getDataSourceInfo(): Promise<{ hasRealData: boolean; source: string; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/market/real-data`);
      
      if (!response.ok) {
        return {
          hasRealData: false,
          source: 'unknown',
          message: 'Failed to connect to API'
        };
      }
      
      const data = await response.json();
      
      return {
        hasRealData: data.status === 'success' && data.data_source === 'opensea',
        source: data.data_source || 'mock',
        message: data.message || 'Unknown status'
      };
    } catch (error) {
      return {
        hasRealData: false,
        source: 'error',
        message: 'Connection error'
      };
    }
  }
}

// Export singleton instance
export const marketDataService = new MarketDataService();
export default marketDataService;
