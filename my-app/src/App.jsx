import { useState } from 'react';
import { Badges } from "./Badges";
import LiveNFTFeed from "./components/LiveNFTFeed";
import TraitAnalyzer from "./components/TraitAnalyzer";
import WalletBadgeExample from "./components/WalletBadgeExample";
import FloorPriceTracker from "./components/FloorPriceTracker";
import WalletClusterExample from "./examples/WalletClusterExample";
import { WalletClusterProvider } from "./contexts/WalletClusterContext";
import { Tabs } from 'antd';
import "./App.css";

const { TabPane } = Tabs;

function App() {
  const [activeTab, setActiveTab] = useState('live');
  
  // Flags to control which badges are shown
  const flags = {
    showRarePattern: true,    // Previously 'symbolic'
    showUniqueTraits: true,   // Previously 'structural'
    showPerfectBalance: true, // Previously 'golden'
    showPremiumScore: true,   // Previously 'hybrid'
    showCaution: false,       // Previously 'clone'
    showVerified: true        // Previously 'unique'
  };

  return (
    <WalletClusterProvider>
      <div className="app-container">
        <header className="app-header">
          <h1>NFT Analytics Dashboard</h1>
          <Tabs 
            activeKey={activeTab} 
            onChange={setActiveTab}
            className="main-tabs"
            centered
          >
            <TabPane tab="Live Feed" key="live" />
            <TabPane tab="Analytics" key="analytics" />
            <TabPane tab="Floor Prices" key="floor-prices" />
            <TabPane tab="Wallet Clustering" key="clustering" />
          </Tabs>
        </header>
        
        <main className="main-content">
          {activeTab === 'live' ? (
            <LiveNFTFeed />
          ) : activeTab === 'analytics' ? (
            <div className="analytics-container">
              <Tabs defaultActiveKey="badges" className="analytics-tabs">
                <TabPane tab="Badges" key="badges">
                  <h2>NFT/Contract Analytics Badges</h2>
                  <Badges flags={flags} />
                  
                  <div style={{ marginTop: '40px' }}>
                    <h3>Wallet Badge Example</h3>
                    <WalletBadgeExample />
                  </div>
                </TabPane>
                <TabPane tab="Trait Analysis" key="traits">
                  <h2>NFT Trait Analysis</h2>
                  <TraitAnalyzer />
                </TabPane>
              </Tabs>
            </div>
          ) : activeTab === 'floor-prices' ? (
            <FloorPriceTracker />
          ) : (
            <div className="clustering-container">
              <h2>Wallet Clustering Demo</h2>
              <WalletClusterExample />
            </div>
          )}
        </main>
      
        <footer className="app-footer">
          <p> {new Date().getFullYear()} NFT Analytics Dashboard</p>
          <p>© {new Date().getFullYear()} NFT Analytics Dashboard</p>
        </footer>
      </div>
    </WalletClusterProvider>
  );
}



export default App;
