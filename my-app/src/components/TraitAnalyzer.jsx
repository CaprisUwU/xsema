import React, { useState, useCallback } from 'react';
import useTraitAnalysis from '../hooks/useTraitAnalysis';

/**
 * Component for analyzing NFT traits
 */
const TraitAnalyzer = () => {
  const [collectionSlug, setCollectionSlug] = useState('');
  const [tokenId, setTokenId] = useState('');
  const [traitData, setTraitData] = useState('');
  const [apiKey, setApiKey] = useState('');
  
  const {
    isLoading,
    error,
    analysis,
    progress,
    analyzeToken,
    analyzeCollection,
    getCollectionStats,
    reset
  } = useTraitAnalysis({ apiKey: apiKey || undefined });

  // Handle token analysis
  const handleTokenAnalysis = useCallback(async () => {
    if (!tokenId || !traitData) return;
    
    try {
      const tokenData = {
        token_id: tokenId,
        traits: JSON.parse(traitData)
      };
      
      // This is a simplified example - in a real app, you'd fetch this from your backend
      const collectionData = {
        traitCounts: {
          // Example trait counts - in a real app, fetch this from your backend
          background: { blue: 10, red: 20, green: 70 },
          body: { robot: 5, human: 45, alien: 50 },
          eyes: { laser: 10, normal: 90 },
          accessory: { sword: 5, shield: 15, none: 80 }
        },
        totalTokens: 100
      };
      
      await analyzeToken(tokenData, collectionData);
    } catch (err) {
      console.error('Failed to analyze token:', err);
    }
  }, [tokenId, traitData, analyzeToken]);

  // Handle collection analysis
  const handleCollectionAnalysis = useCallback(async () => {
    if (!collectionSlug) return;
    
    try {
      await analyzeCollection(collectionSlug, { limit: 100 });
    } catch (err) {
      console.error('Failed to analyze collection:', err);
    }
  }, [collectionSlug, analyzeCollection]);

  // Handle collection stats
  const handleGetStats = useCallback(async () => {
    if (!collectionSlug) return;
    
    try {
      const stats = await getCollectionStats(collectionSlug);
      console.log('Collection stats:', stats);
      alert(`Fetched stats for ${collectionSlug}. Check console for details.`);
    } catch (err) {
      console.error('Failed to get collection stats:', err);
    }
  }, [collectionSlug, getCollectionStats]);

  return (
    <div className="trait-analyzer">
      <h2>NFT Trait Analyzer</h2>
      
      <div className="api-key-section">
        <label>
          API Key (optional):
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key"
          />
        </label>
      </div>

      <div className="analysis-section">
        <h3>Analyze Token</h3>
        <div>
          <label>
            Token ID:
            <input
              type="text"
              value={tokenId}
              onChange={(e) => setTokenId(e.target.value)}
              placeholder="e.g., 123"
            />
          </label>
        </div>
        <div>
          <label>
            Trait Data (JSON):
            <textarea
              value={traitData}
              onChange={(e) => setTraitData(e.target.value)}
              placeholder='{"background": "blue", "body": "robot"}'
              rows={4}
            />
          </label>
        </div>
        <button 
          onClick={handleTokenAnalysis}
          disabled={isLoading || !tokenId || !traitData}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Token'}
        </button>
      </div>

      <div className="collection-section">
        <h3>Collection Analysis</h3>
        <div>
          <label>
            Collection Slug:
            <input
              type="text"
              value={collectionSlug}
              onChange={(e) => setCollectionSlug(e.target.value)}
              placeholder="e.g., boredapeyachtclub"
            />
          </label>
        </div>
        <div className="button-group">
          <button 
            onClick={handleGetStats}
            disabled={isLoading || !collectionSlug}
          >
            Get Collection Stats
          </button>
          <button 
            onClick={handleCollectionAnalysis}
            disabled={isLoading || !collectionSlug}
          >
            {isLoading ? `Analyzing... ${progress}%` : 'Analyze Collection'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          <h4>Error</h4>
          <p>{error}</p>
        </div>
      )}

      {analysis && (
        <div className="results">
          <h3>Analysis Results</h3>
          <pre>{JSON.stringify(analysis, null, 2)}</pre>
          <button onClick={reset}>Clear Results</button>
        </div>
      )}

      <style jsx>{`
        .trait-analyzer {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }
        .analysis-section, .collection-section {
          margin: 20px 0;
          padding: 15px;
          border: 1px solid #ddd;
          border-radius: 5px;
        }
        label {
          display: block;
          margin: 10px 0;
        }
        input[type="text"],
        input[type="password"],
        textarea {
          width: 100%;
          padding: 8px;
          margin-top: 5px;
          border: 1px solid #ccc;
          border-radius: 4px;
        }
        textarea {
          font-family: monospace;
        }
        button {
          background-color: #4CAF50;
          color: white;
          padding: 10px 15px;
          margin: 5px 5px 5px 0;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }
        .error {
          color: #d32f2f;
          background-color: #ffebee;
          padding: 10px;
          border-radius: 4px;
          margin: 10px 0;
        }
        .results {
          margin-top: 20px;
          padding: 15px;
          background-color: #f5f5f5;
          border-radius: 4px;
          overflow-x: auto;
        }
        pre {
          white-space: pre-wrap;
          word-wrap: break-word;
        }
        .button-group {
          display: flex;
          gap: 10px;
          margin-top: 10px;
        }
      `}</style>
    </div>
  );
};

export default TraitAnalyzer;
