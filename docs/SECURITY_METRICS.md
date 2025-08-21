# Security Metrics Guide

This guide explains the security metrics used in our NFT analytics platform to help you understand and interpret the security scores for NFT collections and contracts.

## Table of Contents

1. [Overview](#overview)
2. [Wash Trading Detection](#wash-trading-detection)
3. [Mint Anomaly Detection](#mint-anomaly-detection)
4. [Security Score](#security-score)
5. [FAQ](#faq)

## Overview

Our platform provides several security metrics to help you assess the legitimacy and risk profile of NFT collections. These metrics analyze on-chain data to detect potential market manipulation and suspicious activities.

## Wash Trading Detection

Wash trading occurs when a trader buys and sells the same asset to create misleading market activity. Our system detects several patterns:

### Key Indicators

- **Circular Trades**: The same asset is traded between a small group of wallets in a short period
- **Rapid Buy/Sell**: The same wallet buys and sells the same NFT quickly
- **Volume Spikes**: Unusual trading volume that doesn't match typical market behavior

### Interpretation

| Score Range | Risk Level | Description |
|-------------|------------|-------------|
| 0-30       | Low        | Normal trading activity detected |
| 31-70      | Medium     | Some suspicious patterns detected |
| 71-100     | High       | Strong evidence of wash trading |

## Mint Anomaly Detection

Mint anomalies can indicate bot activity or other manipulative behaviors during the initial distribution of NFTs.

### Key Indicators

- **Burst Minting**: An unusually high number of mints in a short time period
- **Sequential Minting**: Sequential token IDs being minted by the same wallet
- **Gas Price Spikes**: Unusually high gas prices paid for mints

### Interpretation

| Score Range | Risk Level | Description |
|-------------|------------|-------------|
| 0-30       | Low        | Normal minting patterns |
| 31-70      | Medium     | Some unusual patterns detected |
| 71-100     | High       | Strong evidence of mint manipulation |

## Security Score

The overall security score is a weighted combination of various security metrics, providing a quick assessment of a collection's security health.

### Components

- **Wash Trading Risk** (40% weight)
- **Mint Anomaly Risk** (30% weight)
- **Smart Contract Security** (20% weight)
- **Wallet Concentration** (10% weight)

### Interpretation

| Score Range | Rating | Description |
|-------------|--------|-------------|
| 90-100     | Excellent | Very low risk, highly secure |
| 70-89      | Good    | Low risk, standard security measures |
| 50-69      | Fair    | Moderate risk, exercise caution |
| 30-49      | Poor    | High risk, significant concerns |
| 0-29       | Critical | Very high risk, extreme caution advised |

## FAQ

### How often are these metrics updated?
Metrics are updated in real-time as new transactions are processed on the blockchain.

### Can these metrics guarantee a collection is safe?
No security system is perfect. These metrics are tools to help assess risk, but they cannot provide absolute guarantees.

### Why might a legitimate collection have high risk scores?
New collections often show patterns that resemble suspicious activity. Always consider the context and do additional research.

### How can I use these metrics in my investment decisions?
Use these metrics as one of several factors in your decision-making process, along with community sentiment, project fundamentals, and market conditions.

### Where can I see these metrics in the platform?
Security metrics are displayed on collection pages and can be accessed via our API for programmatic use.

## API Reference

### Get Wash Trading Analysis
```
GET /api/v1/analyze/wash-trading/{collection_address}
```

### Get Mint Anomaly Analysis
```
GET /api/v1/analyze/mint-anomalies/{collection_address}
```

### Get Full Security Analysis
```
GET /api/v1/analyze/contract/{contract_address}
```

## Support

For questions about these metrics or to report potential issues, please contact our support team at security@nftanalytics.com
