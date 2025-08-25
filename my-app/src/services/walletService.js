import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Fetch wallet clustering data for a specific wallet address
 * @param {string} walletAddress - The wallet address to analyze
 * @returns {Promise<Object>} The clustering data
 */
export const getWalletClusterData = async (walletAddress) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/wallets/${walletAddress}/cluster`);
    return response.data;
  } catch (error) {
    console.error('Error fetching wallet cluster data:', error);
    throw error;
  }
};

/**
 * Start batch processing for multiple wallet addresses
 * @param {string[]} walletAddresses - Array of wallet addresses to analyze
 * @returns {Promise<Object>} Job information including WebSocket URL
 */
export const startBatchClusterAnalysis = async (walletAddresses) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/wallets/batch/cluster`, {
      wallet_addresses: walletAddresses
    });
    return response.data;
  } catch (error) {
    console.error('Error starting batch analysis:', error);
    throw error;
  }
};

/**
 * Subscribe to WebSocket updates for a batch job
 * @param {string} jobId - The job ID to subscribe to
 * @param {function} onMessage - Callback for incoming messages
 * @param {function} onError - Callback for errors
 * @returns {WebSocket} The WebSocket connection
 */
export const subscribeToBatchUpdates = (jobId, onMessage, onError) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsBaseUrl = process.env.REACT_APP_WS_URL || 
                   `${wsProtocol}//${window.location.host}/ws`;
  
  const wsUrl = `${wsBaseUrl}/batch/${jobId}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log(`WebSocket connected for job ${jobId}`);
  };

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      onMessage(message);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
  };

  return ws;
};

export default {
  getWalletClusterData,
  startBatchClusterAnalysis,
  subscribeToBatchUpdates
};
