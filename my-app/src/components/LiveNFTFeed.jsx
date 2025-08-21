import { useEffect, useState, useRef } from 'react';
import { formatDistanceToNow } from 'date-fns';
import './LiveNFTFeed.css';

const LiveNFTFeed = () => {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [subscriptions] = useState(['nft_transfer']);
  const ws = useRef(null);
  const clientId = useRef(`client-${Math.random().toString(36).substr(2, 9)}`);

  // Format Ethereum address for display
  const formatAddress = (address) => {
    if (!address) return 'Unknown';
    return `${address.substring(0, 6)}...${address.substring(38)}`;
  };

  // Format price with 4 decimal places
  const formatPrice = (price) => {
    if (!price) return 'N/A';
    const num = parseFloat(price);
    return num.toFixed(4);
  };

  // Format timestamp to relative time
  const formatTime = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp * 1000), { addSuffix: true });
    } catch (e) {
      return '';
    }
  };

  // Connect to WebSocket
  const connectWebSocket = () => {
    try {
      // Use wss:// for production, ws:// for local development
      const wsUrl = process.env.NODE_ENV === 'production' 
        ? `wss://your-api-url/ws`
        : `ws://localhost:8000/ws`;
      
      ws.current = new WebSocket(wsUrl);
      
      // Set a timeout for the connection
      const connectionTimeout = setTimeout(() => {
        if (ws.current && ws.current.readyState === WebSocket.CONNECTING) {
          console.error('WebSocket connection timeout');
          ws.current.close();
          setError('Connection timeout. Retrying...');
          setTimeout(connectWebSocket, 3000);
        }
      }, 5000);
      
      ws.current.onopen = () => {
        clearTimeout(connectionTimeout);
        console.log('WebSocket Connected');
        setIsConnected(true);
        setError(null);
        setIsLoading(false);
        
        // Subscribe to channels with client ID
        const subscribeMessage = {
          type: 'subscribe',
          channels: subscriptions,
          clientId: clientId.current
        };
        
        ws.current.send(JSON.stringify(subscribeMessage));
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types
          switch (data.type) {
            case 'nft_transfer':
              setEvents(prev => [{
                ...data.data,
                id: `${data.data.transactionHash}-${data.data.logIndex || Date.now()}`
              }, ...prev].slice(0, 100)); // Keep last 100 events
              break;
            case 'error':
              setError(data.message);
              break;
            default:
              console.log('Unhandled message type:', data.type);
          }
        } catch (e) {
          console.error('Error processing message:', e);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket Disconnected');
        setIsConnected(false);
        // Attempt to reconnect after a delay
        setTimeout(connectWebSocket, 5000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setError('Connection error. Attempting to reconnect...');
        setIsConnected(false);
      };

    } catch (error) {
      console.error('WebSocket Connection Error:', error);
      setError('Failed to connect to server. Retrying...');
      setIsConnected(false);
      // Attempt to reconnect after a delay
      setTimeout(connectWebSocket, 5000);
    }
  };

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();

    // Clean up on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  return (
    <div className="live-nft-feed">
      <div className="feed-header">
        <h2>Live NFT Transfers</h2>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Live' : 'Disconnected'}
        </div>
      </div>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Connecting to live feed...</p>
        </div>
      ) : (
        <div className="events-container">
          {events.length === 0 ? (
            <div className="no-events">
              <p>Waiting for NFT transfers...</p>
            </div>
          ) : (
            events.map((event) => (
              <div key={event.id} className="event-item">
                <div className="event-header">
                  <span className="event-type">NFT Transfer</span>
                  <span className="event-time">{formatTime(event.timestamp)}</span>
                </div>
                <div className="event-details">
                  <div className="detail-row">
                    <span className="detail-label">Token ID:</span>
                    <span className="detail-value">#{event.tokenId}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">From:</span>
                    <span className="address" title={event.from}>
                      {formatAddress(event.from)}
                    </span>
                    <span className="transfer-arrow">→</span>
                    <span className="detail-label">To:</span>
                    <span className="address" title={event.to}>
                      {formatAddress(event.to)}
                    </span>
                  </div>
                  {event.price && event.price !== '0' && (
                    <div className="detail-row">
                      <span className="detail-label">Price:</span>
                      <span className="price">{formatPrice(event.price)} ETH</span>
                    </div>
                  )}
                </div>
                <div className="event-footer">
                  <a 
                    href={`https://etherscan.io/tx/${event.transactionHash}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="tx-link"
                  >
                    View on Etherscan
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default LiveNFTFeed;
