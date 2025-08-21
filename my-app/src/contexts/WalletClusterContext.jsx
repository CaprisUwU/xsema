import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { message } from 'antd';
import * as walletService from '../services/walletService';

const WalletClusterContext = createContext();

export const WalletClusterProvider = ({ children }) => {
  const [clusters, setClusters] = useState({});
  const [loading, setLoading] = useState({});
  const [batchJobs, setBatchJobs] = useState({});
  const [wsConnections, setWsConnections] = useState({});

  // Clean up WebSocket connections on unmount
  useEffect(() => {
    return () => {
      Object.values(wsConnections).forEach(ws => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      });
    };
  }, [wsConnections]);

  // Fetch cluster data for a single wallet
  const fetchWalletCluster = useCallback(async (walletAddress) => {
    if (!walletAddress) return null;
    
    // Return cached data if available
    if (clusters[walletAddress]) {
      return clusters[walletAddress];
    }

    setLoading(prev => ({ ...prev, [walletAddress]: true }));
    
    try {
      const data = await walletService.getWalletClusterData(walletAddress);
      
      setClusters(prev => ({
        ...prev,
        [walletAddress]: data
      }));
      
      return data;
    } catch (error) {
      message.error(`Failed to load wallet cluster data: ${error.message}`);
      return null;
    } finally {
      setLoading(prev => ({ ...prev, [walletAddress]: false }));
    }
  }, [clusters]);

  // Start batch processing for multiple wallets
  const startBatchAnalysis = useCallback(async (walletAddresses) => {
    if (!walletAddresses || walletAddresses.length === 0) return null;
    
    const jobKey = walletAddresses.sort().join(',');
    
    // Return existing job if already in progress
    if (batchJobs[jobKey]) {
      return batchJobs[jobKey];
    }
    
    try {
      setBatchJobs(prev => ({
        ...prev,
        [jobKey]: { status: 'pending', progress: 0, total: walletAddresses.length }
      }));
      
      const jobInfo = await walletService.startBatchClusterAnalysis(walletAddresses);
      
      // Setup WebSocket connection for real-time updates
      const ws = walletService.subscribeToBatchUpdates(
        jobInfo.job_id,
        (message) => {
          if (message.type === 'progress') {
            setBatchJobs(prev => ({
              ...prev,
              [jobKey]: {
                ...prev[jobKey],
                status: 'processing',
                progress: message.progress,
                total: message.total
              }
            }));
          } else if (message.type === 'completed') {
            // Update clusters with results
            setClusters(prev => ({
              ...prev,
              ...Object.fromEntries(
                message.results.clusters.map(cluster => [
                  cluster.wallet_address,
                  cluster
                ])
              )
            }));
            
            // Update job status
            setBatchJobs(prev => ({
              ...prev,
              [jobKey]: {
                ...prev[jobKey],
                status: 'completed',
                progress: 100,
                results: message.results
              }
            }));
            
            // Close WebSocket connection
            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.close();
              setWsConnections(prev => {
                const updated = { ...prev };
                delete updated[jobKey];
                return updated;
              });
            }
          }
        },
        (error) => {
          console.error('WebSocket error:', error);
          message.error('Connection to update stream lost. Please refresh the page.');
        }
      );
      
      // Store WebSocket connection for cleanup
      setWsConnections(prev => ({
        ...prev,
        [jobKey]: ws
      }));
      
      return jobInfo;
      
    } catch (error) {
      message.error(`Failed to start batch analysis: ${error.message}`);
      setBatchJobs(prev => {
        const updated = { ...prev };
        delete updated[jobKey];
        return updated;
      });
      throw error;
    }
  }, [batchJobs]);

  // Get cluster data for a wallet
  const getClusterData = useCallback((walletAddress) => {
    return clusters[walletAddress] || null;
  }, [clusters]);

  // Check if a wallet is being loaded
  const isLoading = useCallback((walletAddress) => {
    return !!loading[walletAddress];
  }, [loading]);

  // Get batch job status
  const getBatchStatus = useCallback((walletAddresses) => {
    const jobKey = Array.isArray(walletAddresses) 
      ? walletAddresses.sort().join(',')
      : walletAddresses;
      
    return batchJobs[jobKey] || null;
  }, [batchJobs]);

  return (
    <WalletClusterContext.Provider
      value={{
        clusters,
        getClusterData,
        isLoading,
        fetchWalletCluster,
        startBatchAnalysis,
        getBatchStatus,
      }}
    >
      {children}
    </WalletClusterContext.Provider>
  );
};

export const useWalletCluster = () => {
  const context = useContext(WalletClusterContext);
  if (!context) {
    throw new Error('useWalletCluster must be used within a WalletClusterProvider');
  }
  return context;
};

export default WalletClusterContext;
