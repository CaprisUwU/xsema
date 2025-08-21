"""
Security Monitoring Script

This script monitors the performance and effectiveness of the security features,
including wash trading detection and mint anomaly detection. It generates reports
and alerts when potential issues are detected.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('security_monitor')

# Import our security analyzer and detectors
from services.security_analyzer import security_analyzer
from core.security.wash_trading import WashTradingDetector
from core.security.mint_anomaly import MintAnomalyDetector

# Configuration
MONITOR_INTERVAL = 3600  # Run every hour
ALERT_THRESHOLDS = {
    'wash_trading_score': 70,  # Alert if score > 70
    'mint_anomaly_score': 70,  # Alert if score > 70
    'error_rate': 0.1,  # Alert if error rate > 10%
    'processing_time': 5.0  # Alert if analysis takes > 5 seconds
}

class SecurityMonitor:
    """Monitors the performance and effectiveness of security features."""
    
    def __init__(self):
        """Initialize the security monitor."""
        self.stats = {
            'total_analyses': 0,
            'wash_trading_analyses': 0,
            'mint_anomaly_analyses': 0,
            'errors': 0,
            'alerts_triggered': 0,
            'start_time': datetime.utcnow(),
            'last_alert': None
        }
        
        # Initialize detectors with default settings
        self.wash_trading_detector = WashTradingDetector()
        self.mint_anomaly_detector = MintAnomalyDetector()
    
    async def analyze_collection(self, collection_address: str) -> Dict[str, Any]:
        """Run security analysis on a collection.
        
        Args:
            collection_address: The collection contract address
            
        Returns:
            dict: Analysis results
        """
        start_time = time.time()
        self.stats['total_analyses'] += 1
        
        try:
            # Run wash trading analysis
            wash_analysis = await self._run_with_metrics(
                self.wash_trading_detector.analyze_collection,
                collection_address,
                'wash_trading_analyses'
            )
            
            # Run mint anomaly analysis
            mint_analysis = await self._run_with_metrics(
                self.mint_anomaly_detector.analyze_collection_mints,
                collection_address,
                'mint_anomaly_analyses'
            )
            
            # Check for alerts
            await self._check_for_alerts({
                'wash_trading_score': wash_analysis.get('score', 0),
                'mint_anomaly_score': mint_analysis.get('score', 0),
                'collection': collection_address
            })
            
            return {
                'wash_trading_analysis': wash_analysis,
                'mint_anomaly_analysis': mint_analysis,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error analyzing collection {collection_address}: {str(e)}")
            raise
    
    async def _run_with_metrics(self, func, *args, metric_name: str = None, **kwargs):
        """Run a function and track metrics."""
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            processing_time = time.time() - start_time
            
            # Track metrics if a metric name is provided
            if metric_name:
                if metric_name not in self.stats:
                    self.stats[metric_name] = {
                        'count': 0,
                        'total_time': 0.0,
                        'avg_time': 0.0,
                        'last_run': datetime.utcnow().isoformat()
                    }
                
                self.stats[metric_name]['count'] += 1
                self.stats[metric_name]['total_time'] += processing_time
                self.stats[metric_name]['avg_time'] = (
                    self.stats[metric_name]['total_time'] / 
                    self.stats[metric_name]['count']
                )
                self.stats[metric_name]['last_run'] = datetime.utcnow().isoformat()
            
            # Check for slow processing
            if processing_time > ALERT_THRESHOLDS['processing_time']:
                await self.trigger_alert(
                    'slow_processing',
                    f"{func.__name__} took {processing_time:.2f} seconds to complete",
                    {'processing_time': processing_time}
                )
            
            return result
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    async def _check_for_alerts(self, metrics: Dict[str, Any]):
        """Check if any alert conditions are met."""
        alerts = []
        
        # Check wash trading score
        if metrics['wash_trading_score'] > ALERT_THRESHOLDS['wash_trading_score']:
            alerts.append({
                'type': 'high_wash_trading_risk',
                'message': f"High wash trading risk detected: {metrics['wash_trading_score']}",
                'collection': metrics['collection'],
                'score': metrics['wash_trading_score']
            })
        
        # Check mint anomaly score
        if metrics['mint_anomaly_score'] > ALERT_THRESHOLDS['mint_anomaly_score']:
            alerts.append({
                'type': 'high_mint_anomaly_risk',
                'message': f"High mint anomaly risk detected: {metrics['mint_anomaly_score']}",
                'collection': metrics['collection'],
                'score': metrics['mint_anomaly_score']
            })
        
        # Trigger alerts if any conditions are met
        for alert in alerts:
            await self.trigger_alert(alert['type'], alert['message'], alert)
    
    async def trigger_alert(self, alert_type: str, message: str, details: Dict[str, Any] = None):
        """Trigger an alert."""
        self.stats['alerts_triggered'] += 1
        self.stats['last_alert'] = datetime.utcnow().isoformat()
        
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': alert_type,
            'message': message,
            'details': details or {}
        }
        
        # Log the alert
        logger.warning(f"ALERT: {message}")
        
        # In a production environment, you would also:
        # 1. Send notifications (email, Slack, etc.)
        # 2. Store the alert in a database
        # 3. Trigger any automated responses
        
        return alert
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current monitoring statistics."""
        uptime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_human': str(timedelta(seconds=int(uptime))),
            'total_analyses': self.stats['total_analyses'],
            'wash_trading_analyses': self.stats.get('wash_trading_analyses', {}).get('count', 0),
            'mint_anomaly_analyses': self.stats.get('mint_anomaly_analyses', {}).get('count', 0),
            'errors': self.stats['errors'],
            'alerts_triggered': self.stats['alerts_triggered'],
            'last_alert': self.stats['last_alert'],
            'avg_wash_trading_time': self.stats.get('wash_trading_analyses', {}).get('avg_time', 0),
            'avg_mint_anomaly_time': self.stats.get('mint_anomaly_analyses', {}).get('avg_time', 0)
        }

async def monitor_collections(collection_addresses: List[str]):
    """Monitor a list of NFT collections."""
    monitor = SecurityMonitor()
    
    try:
        while True:
            logger.info("Starting security monitoring cycle...")
            
            for address in collection_addresses:
                try:
                    logger.info(f"Analyzing collection: {address}")
                    await monitor.analyze_collection(address)
                    
                    # Log stats periodically
                    if monitor.stats['total_analyses'] % 10 == 0:
                        stats = monitor.get_stats()
                        logger.info(f"Monitoring stats: {json.dumps(stats, indent=2)}")
                    
                except Exception as e:
                    logger.error(f"Error monitoring collection {address}: {str(e)}")
            
            # Wait for the next monitoring cycle
            logger.info(f"Monitoring cycle complete. Next cycle in {MONITOR_INTERVAL} seconds...")
            await asyncio.sleep(MONITOR_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitoring error: {str(e)}")
    finally:
        # Log final stats
        stats = monitor.get_stats()
        logger.info(f"Final monitoring stats: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    # Example collections to monitor
    COLLECTIONS_TO_MONITOR = [
        '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',  # BAYC
        '0x60E4d786628Fea6478F785A6d7e704777c86a7c6',  # MAYC
        '0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7'   # Doodles
    ]
    
    # Run the monitor
    asyncio.run(monitor_collections(COLLECTIONS_TO_MONITOR))
