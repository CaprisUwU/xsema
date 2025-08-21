# Wallet Clustering - Frontend Implementation Guide

## User-Facing Features

### 1. Wallet Profile Badges
- **Risk Indicators**
  - 🟢 "Trusted Collector" (Low risk, established history)
  - 🟡 "New User" (Neutral, limited history)
  - 🔴 "High Risk" (Suspicious patterns detected)

- **Cluster Indicators**
  - "Part of a group of X wallets"
  - "Controls X% of collection" (for whale clusters)
  - "Recently active in coordinated trading"

### 2. Collection Page Enhancements
- **Cluster Distribution**
  - Pie chart showing top wallet clusters
  - Time-series of cluster activity
  - Concentration risk indicators

- **Holder Analysis**
  - Top holders with cluster affiliations
  - Cluster-based filtering
  - Historical cluster movements

## Technical Implementation

### Required API Endpoints
```typescript
// Get wallet cluster info
GET /api/v1/wallets/{address}/cluster

// Get collection cluster analysis
GET /api/v1/collections/{contract}/clusters

// Batch cluster analysis
POST /api/v1/wallets/batch/cluster
```

### React Components

#### 1. WalletClusterBadge
```typescript
interface WalletClusterBadgeProps {
  address: string;
  size?: 'sm' | 'md' | 'lg';
  showTooltip?: boolean;
}

function WalletClusterBadge({ address, size = 'md', showTooltip = true }: WalletClusterBadgeProps) {
  const { data, loading } = useWalletCluster(address);
  
  if (loading) return <LoadingSpinner size={size} />;
  if (!data) return null;

  return (
    <Tooltip content={<ClusterTooltipContent {...data} />} disabled={!showTooltip}>
      <div className={`cluster-badge ${size} risk-${data.riskLevel}`}>
        {data.riskLevel === 'high' ? '⚠️' : '👥'} {data.clusterSize > 1 ? `Group of ${data.clusterSize}` : 'Individual'}
      </div>
    </Tooltip>
  );
}
```

#### 2. ClusterNetworkGraph
```typescript
function ClusterNetworkGraph({ clusterId, maxNodes = 50 }) {
  const { nodes, edges, loading } = useClusterGraph(clusterId, { maxNodes });
  
  return (
    <div className="cluster-graph">
      <ForceGraph2D
        graphData={{ nodes, links: edges }}
        nodeLabel="id"
        nodeColor={node => getNodeColor(node.riskScore)}
        linkDirectionalParticles={2}
      />
    </div>
  );
}
```

### Data Visualization

#### 1. Cluster Distribution Chart
```javascript
// Using Chart.js example
const clusterDistribution = {
  labels: ['Whales (10+ NFTs)', 'Collectors (3-9 NFTs)', 'Retail (1-2 NFTs)'],
  datasets: [{
    data: [15, 25, 60],
    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
  }]
};
```

#### 2. Activity Timeline
```typescript
interface ActivityEvent {
  timestamp: number;
  type: 'MINT' | 'SALE' | 'TRANSFER';
  from: string;
  to: string;
  price?: number;
  nftId: string;
}

function ActivityTimeline({ events }: { events: ActivityEvent[] }) {
  return (
    <div className="activity-timeline">
      {events.map((event, i) => (
        <div key={i} className="timeline-event">
          <div className="event-icon">{getEventIcon(event.type)}</div>
          <div className="event-details">
            <div className="event-title">{formatEventTitle(event)}</div>
            <div className="event-time">{formatTimestamp(event.timestamp)}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## User Experience Flows

### 1. Wallet Investigation Flow
1. User views an NFT listing
2. Clicks on seller's address
3. Sees wallet profile with cluster info
4. Explands cluster visualization
5. Reviews associated wallets and activities

### 2. Collection Analysis Flow
1. User views collection page
2. Checks "Holder Distribution" section
3. Identifies major wallet clusters
4. Analyzes cluster behavior patterns
5. Makes informed trading decisions

## Performance Considerations

1. **Data Loading**
   - Use pagination for large clusters
   - Implement virtual scrolling for activity feeds
   - Cache cluster analysis results

2. **Visualization**
   - Limit initial node count in graphs
   - Use WebGL for large network visualizations
   - Implement progressive loading

3. **Real-time Updates**
   - Use WebSockets for live cluster updates
   - Implement optimistic UI updates
   - Batch frequent updates

## Security & Privacy

1. **Data Protection**
   - Never expose full wallet addresses
   - Hash sensitive identifiers
   - Rate limit sensitive queries

2. **User Controls**
   - Allow users to opt-out of tracking
   - Provide data correction mechanisms
   - Clear disclosure of data sources

## Future Enhancements

1. **Predictive Analytics**
   - Price movement predictions based on cluster activity
   - Wash trading probability scores
   - Smart money tracking

2. **Social Features**
   - Cluster-based social graphs
   - Influencer identification
   - Community reputation systems

3. **Advanced Filtering**
   - Custom cluster definitions
   - Behavior pattern matching
   - Historical trend analysis
