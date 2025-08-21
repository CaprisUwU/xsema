# Wallet Clustering System

## Overview
The Wallet Clustering System groups related Ethereum wallets based on their on-chain behavior, interaction patterns, and transaction characteristics. This helps identify coordinated activities, detect potential Sybil attacks, and uncover relationships between different addresses that might not be immediately obvious.

## Key Features

### 1. Behavior-Based Clustering
- **Transaction Patterns**: Analyzes transaction frequency, timing, and patterns
- **Interaction Analysis**: Tracks smart contracts and tokens interacted with
- **Gas Behavior**: Examines gas price patterns and usage
- **Activity Vectors**: Creates numerical representations of wallet behavior

### 2. Advanced Similarity Detection
- **Simhash Fingerprinting**: Efficiently compares wallet behaviors using simhash
- **Hybrid Similarity**: Combines multiple similarity metrics for accurate clustering
- **Activity Correlation**: Identifies wallets with synchronized activities

### 3. Security Analysis
- **Risk Scoring**: Calculates risk scores for wallet clusters
- **Anomaly Detection**: Flags unusual behavior patterns
- **Sybil Attack Detection**: Identifies potential Sybil attacks

## Core Components

### 1. Wallet Class
Represents a wallet with its properties and behaviors:
- Basic info (address, transaction count)
- Activity patterns (active days, timestamps)
- Interaction data (contracts, tokens)
- Behavioral fingerprints

### Example: Creating a Wallet Profile
```python
from core.security.wallet_clustering import Wallet

# Create a new wallet
wallet = Wallet("0x123...")

# Update with transaction data
wallet.update_from_transaction({
    'from': '0x123...',
    'to': '0x456...',
    'value': '1000000000000000000',  # 1 ETH
    'gas_price': '2000000000',
    'timestamp': 1627228800,
    'contract_address': '0x789...',
    'token_id': '1',
    'to_is_contract': True
})

# Finalize the wallet profile
wallet.finalize()
```

### 2. WalletCluster Class
Manages a group of related wallets:
- Maintains cluster centroid
- Handles wallet additions
- Calculates cluster-level metrics

### 3. WalletClustering Class
Main class that performs the clustering:
- Builds wallet profiles from transaction data
- Performs hierarchical clustering
- Merges similar clusters
- Analyzes clusters for security concerns

## API Endpoints

### 1. Analyze Wallet Cluster
```http
GET /api/v1/wallets/{wallet_address}/cluster
```

**Parameters:**
- `wallet_address` (string, required): The wallet address to analyze
- `depth` (integer, optional): Degrees of separation to analyze (default: 2)
- `include_risk` (boolean, optional): Include risk analysis (default: true)

### 2. Batch Process Wallet Clusters
```http
POST /api/v1/wallets/batch/cluster
```

**Request Body:**
```json
{
  "wallet_addresses": ["0x123...", "0x456..."],
  "depth": "medium",
  "include_risk": true
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "total_addresses": 2,
  "valid_addresses": ["0x123...", "0x456..."],
  "invalid_addresses": [],
  "created_at": 1627228800,
  "status_url": "/api/v1/wallets/batch/status/550e8400-e29b-41d4-a716-446655440000",
  "websocket_url": "/ws/wallets/batch/550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Get Batch Job Status
```http
GET /api/v1/wallets/batch/status/{job_id}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 50,
  "total": 2,
  "created_at": 1627228800,
  "started_at": 1627228801,
  "completed_at": null,
  "results": {
    "clusters": [
      {
        "wallet_address": "0x123...",
        "cluster_members": ["0x123...", "0x789..."],
        "cluster_size": 2
      }
    ],
    "failed_addresses": []
  }
}
```

## Best Practices & Performance Considerations

### 1. Batch Processing
- **Optimal Batch Size**: Process 50-100 wallets per batch for best performance
- **Rate Limiting**: Implement client-side rate limiting (1 request per second)
- **Error Handling**: Always check for failed addresses in the response

### 2. Real-time Monitoring
- **WebSocket Timeout**: Implement a 30-second ping/pong mechanism
- **Reconnection Logic**: Automatically reconnect with exponential backoff
- **Message Queuing**: Use message queues for high-volume processing

### 3. Performance Optimization
- **Caching**: Cache results for 1 hour (default TTL)
- **Parallel Processing**: Use WebSocket for real-time updates during long-running jobs
- **Data Sampling**: For large datasets, consider sampling before full analysis

### 4. Security Considerations
- **Input Validation**: Always validate wallet addresses
- **API Keys**: Secure your API keys and use HTTPS
- **Data Privacy**: Be mindful of PII and sensitive data in wallet transactions

### 5. Monitoring and Alerts
- **Track Metrics**: Monitor job success/failure rates
- **Set Alerts**: For high-risk clusters or processing errors
- **Logging**: Enable detailed logging for debugging

## Code Examples

### 1. Python: Batch Process Wallets
```python
import requests
import json
import asyncio
import websockets

# Start batch job
response = requests.post(
    "http://your-api-url/api/v1/wallets/batch/cluster",
    json={
        "wallet_addresses": ["0x123...", "0x456..."],
        "depth": "medium",
        "include_risk": True
    }
)
job_data = response.json()
print(f"Started batch job: {job_data['job_id']}")

# Monitor progress via WebSocket
async def monitor_progress(job_id):
    uri = f"ws://your-api-url/ws/wallets/batch/{job_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "progress":
                    print(f"Progress: {data['progress']}% ({data['processed']}/{data['total']})")
                elif data["type"] == "completed":
                    print("Batch processing completed!")
                    print(f"Results: {json.dumps(data['results'], indent=2)}")
                    break
                elif data["type"] == "error":
                    print(f"Error: {data['error']}")
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed")
                break

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(monitor_progress(job_data["job_id"]))
```

### 2. JavaScript: Batch Process Wallets
```javascript
const axios = require('axios');
const WebSocket = require('ws');

// Start batch job
async function startBatchJob() {
  try {
    const response = await axios.post('http://your-api-url/api/v1/wallets/batch/cluster', {
      wallet_addresses: ['0x123...', '0x456...'],
      depth: 'medium',
      include_risk: true
    });
    
    const jobData = response.data;
    console.log(`Started batch job: ${jobData.job_id}`);
    monitorProgress(jobData.job_id);
  } catch (error) {
    console.error('Error starting batch job:', error.message);
  }
}

// Monitor progress via WebSocket
function monitorProgress(jobId) {
  const ws = new WebSocket(`ws://your-api-url/ws/wallets/batch/${jobId}`);
  
  ws.on('open', () => {
    console.log('Connected to WebSocket server');
  });
  
  ws.on('message', (data) => {
    const message = JSON.parse(data);
    
    switch (message.type) {
      case 'progress':
        console.log(`Progress: ${message.progress}% (${message.processed}/${message.total})`);
        break;
      case 'completed':
        console.log('Batch processing completed!');
        console.log('Results:', JSON.stringify(message.results, null, 2));
        ws.close();
        break;
      case 'error':
        console.error('Error:', message.error);
        ws.close();
        break;
    }
  });
  
  ws.on('close', () => {
    console.log('Disconnected from WebSocket server');
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
}

startBatchJob();
```

### 3. WebSocket Updates
Connect to receive real-time updates about batch processing:
```
ws://your-api-url/ws/wallets/batch/{job_id}
```

**Message Types:**
1. Progress Update:
```json
{
  "type": "progress",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 50,
  "processed": 1,
  "total": 2
}
```

2. Completion:
```json
{
  "type": "completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": {
    "clusters": [...],
    "failed_addresses": []
  }
}
```

3. Error:
```json
{
  "type": "error",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "error": "Error message"
}
```

**Response:**
```json
{
  "wallet_address": "0x...",
  "cluster_id": "abc123",
  "cluster_members": ["0x...", "0x..."],
  "cluster_size": 5,
  "risk_score": 45,
  "risk_factors": [
    {
      "type": "high_similarity",
      "severity": "medium",
      "description": "Multiple wallets with nearly identical behavior patterns"
    }
  ],
  "analysis": {
    "total_transactions": 1234,
    "unique_contracts": 12,
    "time_span_days": 30,
    "behavioral_fingerprint": "a1b2c3d4..."
  },
  "last_updated": "2025-07-25T00:00:00Z"
}
```

### 2. Get Cluster Members
```http
GET /api/v1/wallets/clusters/{cluster_id}
```

**Parameters:**
- `cluster_id` (string, required): The cluster ID to retrieve
- `limit` (integer, optional): Maximum number of members to return (default: 100, max: 1000)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response:**
```json
{
  "cluster_id": "abc123",
  "total_members": 5,
  "members": [
    {
      "address": "0x...",
      "first_seen": "2023-01-01T00:00:00Z",
      "last_active": "2025-07-25T00:00:00Z",
      "transaction_count": 123
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 5
  }
}
```

## Implementation Details

### Clustering Algorithm
1. **Profile Building**:
   - Collects transaction history for each wallet
   - Extracts behavioral features
   - Generates simhash fingerprints

2. **Initial Clustering**:
   - Groups wallets with identical or similar simhashes
   - Uses Hamming distance for similarity comparison

3. **Hierarchical Merging**:
   - Merges clusters with high similarity scores
   - Uses hybrid similarity metrics
   - Maintains minimum cluster size requirements

### Risk Analysis
- **Cluster Size**: Larger clusters may indicate potential Sybil attacks
- **Behavioral Similarity**: Near-identical behavior patterns across wallets
- **Activity Correlation**: Synchronized transaction timing
- **Address Generation Patterns**: Similar address generation techniques

## Example Use Cases

### 1. Detecting Sybil Attacks
```python
def detect_sybil_attack(cluster_analysis):
    """Detect potential Sybil attack based on cluster analysis."""
    if cluster_analysis['cluster_size'] > 10 and \
       cluster_analysis['risk_score'] > 70:
        return True
    return False
```

### 2. Finding Related Wallets
```python
async def get_related_wallets(wallet_address, depth=2):
    """Get all wallets related to the given wallet."""
    cluster_data = await get_wallet_cluster(wallet_address, depth=depth)
    return {
        'primary_wallet': wallet_address,
        'related_wallets': cluster_data['cluster_members'],
        'cluster_id': cluster_data['cluster_id']
    }
```

### 3. Risk Assessment
```python
def assess_wallet_risk(wallet_address):
    """Assess the risk level of a wallet based on its cluster."""
    cluster_data = get_wallet_cluster(wallet_address)
    risk_level = 'low'
    
    if cluster_data['risk_score'] > 70:
        risk_level = 'high'
    elif cluster_data['risk_score'] > 30:
        risk_level = 'medium'
        
    return {
        'wallet': wallet_address,
        'risk_level': risk_level,
        'risk_factors': cluster_data['risk_factors'],
        'cluster_size': cluster_data['cluster_size']
    }
```

## Performance Considerations

### Caching
- Cluster analysis results are cached
- Cache invalidation on new transactions
- Configurable TTL for cached results

### Scalability
- Batch processing for large wallet sets
- Background processing for deep analysis
- Paginated API responses

## Integration Guide

### 1. Adding to Your Project
```python
from core.security.wallet_clustering import WalletClustering

# Initialize the clustering system
clustering = WalletClustering(
    simhash_threshold=3,
    min_cluster_size=2,
    hybrid_similarity_threshold=0.7
)

# Cluster wallets
wallets = load_wallet_data()  # Your wallet data loading function
clusters = clustering.cluster_wallets(wallets)

# Analyze clusters
analysis = clustering.analyze_clusters(clusters)
```

### 2. API Integration
```javascript
// Get cluster for a wallet
async function getWalletCluster(walletAddress) {
  const response = await fetch(`/api/v1/wallets/${walletAddress}/cluster`);
  return response.json();
}

// Get cluster members
async function getClusterMembers(clusterId, limit = 100, offset = 0) {
  const response = await fetch(
    `/api/v1/wallets/clusters/${clusterId}?limit=${limit}&offset=${offset}`
  );
  return response.json();
}
```

## Troubleshooting

### Common Issues

#### Cluster Not Found
- **Cause**: The wallet may not be part of any cluster yet
- **Solution**: Ensure the wallet has sufficient transaction history

#### High Memory Usage
- **Cause**: Analyzing too many wallets at once
- **Solution**: Increase batch size or analyze in smaller chunks

#### Slow Performance
- **Cause**: Deep analysis of large wallet sets
- **Solution**: Use background processing and cache results

## Support
For additional help, contact support@your-service.com or visit our [documentation](https://docs.your-service.com).
