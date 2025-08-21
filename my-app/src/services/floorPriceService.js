import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1';

/**
 * Get floor price for a specific collection
 * @param {string} contractAddress - Collection contract address
 * @param {string} timeframe - Time period ('1h', '24h', '7d', '30d')
 * @returns {Promise<Object>} Floor price data
 */
export const getCollectionFloorPrice = async (contractAddress, timeframe = '24h') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/collections/${contractAddress}/floor-price`, {
      params: { timeframe }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching floor price:', error);
    throw error;
  }
};

/**
 * Get floor price history for a collection
 * @param {string} contractAddress - Collection contract address
 * @param {number} days - Number of days of history
 * @returns {Promise<Object>} Floor price history
 */
export const getFloorPriceHistory = async (contractAddress, days = 30) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/collections/${contractAddress}/floor-price/history`, {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching floor price history:', error);
    throw error;
  }
};

/**
 * Get trending collections by floor price changes
 * @param {string} timeframe - Time period ('1h', '24h', '7d')
 * @param {number} limit - Number of results
 * @returns {Promise<Object>} Trending collections
 */
export const getTrendingCollections = async (timeframe = '24h', limit = 20) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/collections/trending`, {
      params: { timeframe, limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching trending collections:', error);
    throw error;
  }
};

/**
 * Get market summary with floor price data
 * @param {string} timeframe - Time period
 * @returns {Promise<Object>} Market summary
 */
export const getMarketSummary = async (timeframe = '24h') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/markets/summary`, {
      params: { timeframe }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching market summary:', error);
    throw error;
  }
};

/**
 * Get paginated collections with floor prices
 * @param {number} page - Page number (1-based)
 * @param {number} limit - Items per page
 * @param {string} sortBy - Sort field ('floor_price', 'volume', 'change')
 * @param {string} order - Sort order ('asc', 'desc')
 * @returns {Promise<Object>} Paginated collections
 */
export const getCollections = async (page = 1, limit = 20, sortBy = 'floor_price', order = 'desc') => {
  try {
    const offset = (page - 1) * limit;
    const response = await axios.get(`${API_BASE_URL}/collections`, {
      params: { 
        limit, 
        offset, 
        sort_by: sortBy, 
        order 
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching collections:', error);
    throw error;
  }
};

/**
 * Real-time floor price subscription via WebSocket
 * @param {Function} onUpdate - Callback for price updates
 * @param {Array} collections - Array of collection addresses to watch
 * @returns {WebSocket} WebSocket connection
 */
export const subscribeToFloorPrices = (onUpdate, collections = []) => {
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8001/ws';
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('Connected to floor price WebSocket');
    // Subscribe to floor price updates
    ws.send(JSON.stringify({
      type: 'subscribe',
      channel: 'floor_prices',
      collections: collections
    }));
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'floor_price_update') {
        onUpdate(data.data);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('Floor price WebSocket disconnected');
  };

  return ws;
};
