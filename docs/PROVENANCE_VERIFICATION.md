# NFT Provenance Verification

## Overview
The provenance verification system tracks and analyzes the complete ownership history of NFTs to detect suspicious activities, verify authenticity, and provide transparency. It helps identify potential risks such as wash trading, rapid ownership changes, and association with blacklisted addresses.

## Key Features

### 1. Ownership History Tracking
- Complete chain of custody for each NFT
- Timestamped transfer history
- Transaction details including gas prices and values

### 2. Risk Detection
- **Wash Trading Detection**: Identifies circular trading patterns
- **Rapid Ownership Changes**: Flags NFTs that change hands too quickly
- **Blacklist Checking**: Verifies against known malicious addresses
- **Address Symmetry Analysis**: Detects potentially generated or suspicious addresses

### 3. Verification & Scoring
- Comprehensive risk scoring (0-100)
- Detailed risk factor breakdown
- Verification status (verified/suspicious)

## API Endpoints

### 1. Get NFT Details with Provenance
```http
GET /api/v1/nfts/{contract_address}/{token_id}?include_provenance=true
```

**Parameters:**
- `contract_address` (string, required): The NFT contract address
- `token_id` (string, required): The token ID
- `include_provenance` (boolean, optional): Whether to include provenance verification (default: true)

**Response:**
```json
{
  "contract_address": "0x...",
  "token_id": "123",
  "metadata": { ... },
  "owner": "0x...",
  "security_analysis": { ... },
  "provenance": {
    "token_id": "123",
    "contract_address": "0x...",
    "current_owner": "0x...",
    "creator": "0x...",
    "total_transfers": 5,
    "risk_score": 15,
    "risk_factors": [
      {
        "type": "wash_trading",
        "severity": "high",
        "description": "Potential wash trading detected"
      }
    ],
    "entropy_analysis": { ... },
    "symmetry_analysis": { ... },
    "verification_status": "verified",
    "last_verified": "2025-07-25T00:00:00Z"
  },
  "last_updated": "2025-07-25T00:00:00Z"
}
```

### 2. Get Detailed Provenance
```http
GET /api/v1/nfts/{contract_address}/{token_id}/provenance?include_timeline=true
```

**Parameters:**
- `contract_address` (string, required): The NFT contract address
- `token_id` (string, required): The token ID
- `include_timeline` (boolean, optional): Whether to include ownership timeline (default: true)

**Response:**
```json
{
  "contract_address": "0x...",
  "token_id": "123",
  "verification": { ... },
  "ownership_timeline": [
    {
      "owner": "0x...",
      "start_time": "2023-01-01T00:00:00Z",
      "end_time": "2023-02-01T00:00:00Z",
      "duration_seconds": 2678400,
      "transfer_in": null,
      "transfer_out": "0x..."
    }
  ],
  "last_verified": "2025-07-25T00:00:00Z"
}
```

### 3. Get NFT Transfer History
```http
GET /api/v1/nfts/{contract_address}/{token_id}/history?limit=100
```

**Parameters:**
- `contract_address` (string, required): The NFT contract address
- `token_id` (string, required): The token ID
- `limit` (number, optional): Number of transactions to return (1-1000, default: 100)

**Response:**
```json
{
  "contract_address": "0x...",
  "token_id": "123",
  "transactions": [
    {
      "tx_hash": "0x...",
      "from": "0x...",
      "to": "0x...",
      "timestamp": "2023-01-01T00:00:00Z",
      "value": 1.5,
      "gas_price": 0.0000001,
      "gas_used": 21000,
      "block_number": 12345678,
      "log_index": 0
    }
  ],
  "total": 1,
  "limit": 100
}
```

## Risk Factors

### Wash Trading
- **Detection**: Identifies circular trading patterns where the same wallets trade the NFT back and forth
- **Risk Level**: High
- **Mitigation**: Consider additional verification for NFTs with wash trading history

### Rapid Ownership Changes
- **Detection**: Flags NFTs that change hands too quickly (multiple transfers within a short timeframe)
- **Risk Level**: Medium
- **Mitigation**: Investigate the reasons for rapid transfers

### Blacklisted Addresses
- **Detection**: Checks if any previous owners are on known blacklists
- **Risk Level**: Critical
- **Mitigation**: Exercise extreme caution when interacting with NFTs that have been associated with blacklisted addresses

### Address Symmetry
- **Detection**: Analyzes address patterns that might indicate generated or suspicious addresses
- **Risk Level**: Low to Medium
- **Mitigation**: Consider additional verification for NFTs with suspicious address patterns

## Implementation Notes

### Caching
- Provenance verification results are cached to improve performance
- Cache size is limited to 1000 entries using FIFO eviction
- The cache key is `{contract_address}_{token_id}` (case-insensitive)

### Performance Considerations
- Historical data retrieval can be resource-intensive for NFTs with many transfers
- The system implements pagination for transfer history (default 100 items per page)
- Consider using the `include_provenance` parameter to skip verification when not needed

### Integration
To integrate with the provenance verification system:

1. Use the `/nfts/{contract}/{id}` endpoint with `include_provenance=true`
2. Check the `risk_score` and `risk_factors` in the response
3. For detailed analysis, use the `/nfts/{contract}/{id}/provenance` endpoint
4. Monitor the `verification_status` field for overall verification status

## Example Use Cases

### Verifying NFT Authenticity
```python
import requests

def verify_nft_authenticity(contract_address: str, token_id: str) -> bool:
    """Check if an NFT has a clean provenance."""
    response = requests.get(
        f"https://api.your-service.com/v1/nfts/{contract_address}/{token_id}",
        params={"include_provenance": True}
    )
    data = response.json()
    
    if "provenance" not in data:
        return False
        
    return data["provenance"].get("verification_status") == "verified"
```

### Detecting Suspicious Activity
```python
def detect_suspicious_activity(contract_address: str, token_id: str) -> list:
    """Detect any suspicious activity in an NFT's history."""
    response = requests.get(
        f"https://api.your-service.com/v1/nfts/{contract_address}/{token_id}/provenance"
    )
    data = response.json()
    
    if "verification" not in data or "risk_factors" not in data["verification"]:
        return []
        
    return [
        factor for factor in data["verification"]["risk_factors"] 
        if factor["severity"] in ["high", "critical"]
    ]
```

## Troubleshooting

### Common Issues

#### Missing Provenance Data
- **Cause**: The NFT may not have any recorded transfers yet
- **Solution**: Check if the contract and token ID are correct

#### High Risk Score
- **Cause**: The NFT may have been involved in suspicious activities
- **Solution**: Review the `risk_factors` array for specific issues

#### Slow Response
- **Cause**: The NFT may have a long transaction history
- **Solution**: Use pagination and limit parameters when available

## Support
For additional help, please contact support@your-service.com or visit our [documentation](https://docs.your-service.com).
