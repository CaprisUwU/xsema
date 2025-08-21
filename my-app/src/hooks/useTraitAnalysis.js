import { useState, useCallback, useEffect, useRef } from 'react';
import traitService from '../services/traitService';

/**
 * Custom hook for handling trait analysis
 * @param {Object} options - Options for the hook
 * @param {string} [options.apiKey] - Optional API key for authenticated requests
 * @returns {Object} Analysis state and methods
 */
export const useTraitAnalysis = ({ apiKey } = {}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [progress, setProgress] = useState(0);
  const wsRef = useRef(null);

  // Clean up WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  /**
   * Analyze a single token's traits
   * @param {Object} tokenData - The token data to analyze
   * @param {Object} collectionData - The collection's trait distribution
   * @param {Object} options - Additional options
   */
  const analyzeToken = useCallback(async (tokenData, collectionData, options = {}) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await traitService.analyzeTokenTraits(
        tokenData,
        collectionData,
        { ...options, apiKey }
      );
      setAnalysis(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to analyze token');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [apiKey]);

  /**
   * Get trait statistics for a collection
   * @param {string} collectionSlug - The collection's unique identifier
   * @returns {Promise<Object>} Collection statistics
   */
  const getCollectionStats = useCallback(async (collectionSlug) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const stats = await traitService.getCollectionTraitStats(collectionSlug, { apiKey });
      return stats;
    } catch (err) {
      setError(err.message || 'Failed to fetch collection stats');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [apiKey]);

  /**
   * Analyze an entire collection's traits
   * @param {string} collectionSlug - The collection's unique identifier
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Analysis results
   */
  const analyzeCollection = useCallback(async (collectionSlug, options = {}) => {
    setIsLoading(true);
    setError(null);
    setProgress(0);
    
    try {
      // Start the batch analysis
      const result = await traitService.analyzeCollectionTraits(
        collectionSlug,
        { ...options, apiKey }
      );

      // If the analysis is queued and provides a job ID, set up WebSocket
      if (result.jobId) {
        return new Promise((resolve, reject) => {
          // Close any existing WebSocket connection
          if (wsRef.current) {
            wsRef.current.close();
          }

          // Set up new WebSocket connection
          wsRef.current = traitService.subscribeToTraitAnalysis(
            result.jobId,
            (message) => {
              if (message.type === 'progress') {
                setProgress(message.data.progress);
              } else if (message.type === 'result') {
                setAnalysis(message.data);
                resolve(message.data);
              }
            },
            (error) => {
              setError(error.message || 'WebSocket error');
              reject(error);
            }
          );
        });
      }

      // If the analysis is complete immediately, return the result
      setAnalysis(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to analyze collection');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [apiKey]);

  return {
    // State
    isLoading,
    error,
    analysis,
    progress,
    
    // Methods
    analyzeToken,
    analyzeCollection,
    getCollectionStats,
    
    // Reset
    reset: useCallback(() => {
      setAnalysis(null);
      setError(null);
      setProgress(0);
    }, [])
  };
};

export default useTraitAnalysis;
