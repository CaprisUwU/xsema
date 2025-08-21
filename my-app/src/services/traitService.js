import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1';

/**
 * Analyze a single token's traits
 * @param {Object} tokenData - The token data to analyze
 * @param {Object} collectionData - The collection's trait distribution
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Analysis results
 */
export const analyzeTokenTraits = async (tokenData, collectionData, options = {}) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/traits/analyze/token`,
      {
        token_data: tokenData,
        collection_trait_counts: collectionData.traitCounts,
        total_tokens: collectionData.totalTokens,
        weights: options.weights
      },
      {
        headers: {
          'Content-Type': 'application/json',
          ...(options.apiKey && { 'X-API-Key': options.apiKey })
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error analyzing token traits:', error);
    throw error;
  }
};

/**
 * Get trait statistics for a collection
 * @param {string} collectionSlug - The collection's unique identifier
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Collection statistics
 */
export const getCollectionTraitStats = async (collectionSlug, options = {}) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/traits/stats/${encodeURIComponent(collectionSlug)}`,
      {
        headers: {
          ...(options.apiKey && { 'X-API-Key': options.apiKey })
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching collection trait stats:', error);
    throw error;
  }
};

/**
 * Analyze an entire collection's traits
 * @param {string} collectionSlug - The collection's unique identifier
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Analysis results
 */
export const analyzeCollectionTraits = async (collectionSlug, options = {}) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/traits/analyze/collection/${encodeURIComponent(collectionSlug)}`,
      {
        params: {
          limit: options.limit || 100
        },
        headers: {
          ...(options.apiKey && { 'X-API-Key': options.apiKey })
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error analyzing collection traits:', error);
    throw error;
  }
};

/**
 * Subscribe to WebSocket for real-time trait analysis updates
 * @param {string} jobId - The analysis job ID
 * @param {function} onMessage - Callback for incoming messages
 * @param {function} onError - Callback for errors
 * @returns {WebSocket} The WebSocket connection
 */
export const subscribeToTraitAnalysis = (jobId, onMessage, onError) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsBaseUrl = process.env.REACT_APP_WS_URL || 
                   `${wsProtocol}//${window.location.host}/ws`;
  
  const wsUrl = `${wsBaseUrl}/traits/analysis/${jobId}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log(`Connected to trait analysis WebSocket for job ${jobId}`);
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };

  ws.onclose = (event) => {
    if (event.wasClean) {
      console.log(`WebSocket connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
      console.error('WebSocket connection died');
      // Attempt to reconnect after a delay
      setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...');
        return subscribeToTraitAnalysis(jobId, onMessage, onError);
      }, 5000);
    }
  };

  return ws;
};

const traitService = {
  analyzeTokenTraits,
  getCollectionTraitStats,
  analyzeCollectionTraits,
  subscribeToTraitAnalysis
};

export default traitService;
