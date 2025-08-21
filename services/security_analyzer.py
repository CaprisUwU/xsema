"""
Enhanced Security Analysis with SimHash and Behavioral Patterns

This module provides advanced security analysis for smart contracts and wallets,
using simhash for similarity detection and pattern analysis for identifying
suspicious activities including wash trading and mint anomalies.
"""
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from web3 import Web3

# Import our simhash implementation
from utils.simhash import SimHasher, simhash, simhash_distance, similarity
from utils.bitwise import analyze_bytecode_patterns
from utils.address_symmetry import check_address_symmetry

# Import our new security features
from core.security.wash_trading import WashTradingDetector
from core.security.mint_anomaly import MintAnomalyDetector

# Type aliases
Address = str
ContractAddress = str
TransactionHash = str

@dataclass
class SecurityScore:
    """Comprehensive security assessment for a contract or wallet."""
    address: str
    score: float  # 0-100, higher is better
    risk_factors: List[Dict[str, Any]]
    confidence: float  # 0-1, confidence in the assessment
    timestamp: str

class SecurityAnalyzer:
    """Advanced security analysis for blockchain entities."""
    
    def __init__(self, w3: Optional[Any] = None):
        """Initialize the security analyzer.
        
        Args:
            w3: Optional Web3 instance for direct blockchain access
        """
        self.w3 = w3
        self.simhasher = SimHasher()
        self.known_malicious_hashes = set()  # In production, load from a database
        self.behavioral_profiles = {}  # Cache for behavioral profiles
        
        # Initialize security detectors
        self.wash_trading_detector = WashTradingDetector()
        self.mint_anomaly_detector = MintAnomalyDetector()
        
        # Known phishing patterns (simplified for example)
        self.phishing_indicators = [
            "airdrop", "claim", "reward", "verification", "walletconnect",
            "connectwallet", "migrate", "upgrade", "approve"
        ]
    
    async def analyze_contract(self, contract_address: str) -> Dict[str, Any]:
        """Perform comprehensive security analysis of a smart contract.
        
        Args:
            contract_address: The contract address to analyze
            
        Returns:
            dict: Security analysis results including wash trading and mint analysis
        """
        if not Web3.is_address(contract_address):
            raise ValueError(f"Invalid contract address: {contract_address}")
            
        contract_address = Web3.to_checksum_address(contract_address)
        
        # Get contract code and metadata
        try:
            code = self.w3.eth.get_code(contract_address).hex()
            if code == '0x':
                return {
                    "address": contract_address,
                    "error": "No code at this address",
                    "is_contract": False
                }
                
            # 1. Bytecode analysis
            bytecode_analysis = analyze_bytecode_patterns(code)
            
            # 2. Generate simhash of the bytecode
            code_simhash = self.simhasher.simhash(code)
            
            # 3. Check against known malicious contracts
            is_similar_to_malicious = await self._check_malicious_similarity(code_simhash)
            
            # 4. Check for common vulnerabilities
            vulnerabilities = self._detect_common_vulnerabilities(code)
            
            # 5. Check for suspicious functions
            suspicious_functions = self._find_suspicious_functions(code)
            
            # 6. Run wash trading analysis (async)
            wash_trading_analysis = await self._analyze_wash_trading(contract_address)
            
            # 7. Run mint anomaly detection (async)
            mint_analysis = await self._analyze_mint_anomalies(contract_address)
            
            # 8. Calculate overall risk score (0-100, higher is better)
            risk_score = self._calculate_risk_score(
                bytecode_analysis,
                is_similar_to_malicious,
                vulnerabilities,
                suspicious_functions,
                wash_trading_analysis.get('score', 0) / 100 if wash_trading_analysis else 0,
                mint_analysis.get('score', 0) / 100 if mint_analysis else 0
            )
            
            return {
                "address": contract_address,
                "is_contract": True,
                "code_fingerprint": hex(code_simhash),  # Business-friendly term
                "is_similar_to_malicious": is_similar_to_malicious,
                "bytecode_analysis": bytecode_analysis,
                "vulnerabilities": vulnerabilities,
                "suspicious_functions": suspicious_functions,
                "security_score": risk_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "address": contract_address,
                "error": str(e),
                "is_contract": None
            }
    
    async def analyze_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Analyze wallet behavior and security.
        
        Args:
            wallet_address: The wallet address to analyze
            
        Returns:
            dict: Wallet security analysis
        """
        if not Web3.is_address(wallet_address):
            raise ValueError(f"Invalid wallet address: {wallet_address}")
            
        wallet_address = Web3.to_checksum_address(wallet_address)
        
        try:
            # 1. Check if it's a contract
            code = self.w3.eth.get_code(wallet_address).hex()
            is_contract = code != '0x'
            
            # 2. Get transaction history (simplified)
            # In production, you'd fetch actual transactions
            tx_count = self.w3.eth.get_transaction_count(wallet_address)
            
            # 3. Analyze wallet patterns
            patterns = {
                "new_wallet": tx_count < 5,
                "high_frequency": tx_count > 1000,  # Arbitrary threshold
                "address_symmetry": check_address_symmetry(wallet_address)
            }
            
            # 4. Generate behavior profile
            behavior_profile = await self._generate_behavior_profile(wallet_address)
            
            # 5. Check for phishing indicators
            phishing_indicators = self._check_phishing_indicators(behavior_profile)
            
            # 6. Calculate risk score
            risk_score = self._calculate_wallet_risk_score(
                patterns, 
                behavior_profile,
                phishing_indicators
            )
            
            return {
                "address": wallet_address,
                "is_contract": is_contract,
                "transaction_count": tx_count,
                "patterns": patterns,
                "behavior_profile": behavior_profile,
                "phishing_indicators": phishing_indicators,
                "security_score": risk_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "address": wallet_address,
                "error": str(e)
            }
    
    async def _generate_behavior_profile(self, address: str) -> Dict[str, Any]:
        """Generate a behavior profile for an address."""
        # In production, this would analyze transaction history, interactions, etc.
        # For now, return a simplified version
        return {
            "first_seen": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "total_transactions": self.w3.eth.get_transaction_count(address),
            "contracts_interacted_with": [],  # Would be populated in production
            "common_interaction_patterns": []  # Would be populated in production
        }
    
    def _check_phishing_indicators(self, behavior_profile: Dict[str, Any]) -> List[str]:
        """Check for indicators of phishing or malicious behavior."""
        indicators = []
        
        # Check transaction patterns
        if behavior_profile.get("total_transactions", 0) == 0:
            indicators.append("new_wallet_with_no_history")
            
        # Check for common phishing patterns in transaction data
        # This is simplified - in production, you'd analyze actual transaction data
        
        return indicators
    
    async def _check_malicious_similarity(self, code_simhash: int) -> bool:
        """Check if code is similar to known malicious contracts."""
        # In production, this would query a database of known malicious hashes
        # For now, just check against an empty set
        return code_simhash in self.known_malicious_hashes
    
    def _detect_common_vulnerabilities(self, code: str) -> List[str]:
        """Detect common smart contract vulnerabilities."""
        vulnerabilities = []
        
        # This is simplified - in production, use tools like Slither or Mythril
        if "DELEGATECALL" in code.upper():
            vulnerabilities.append("delegatecall_usage")
            
        if "SELFDESTRUCT" in code.upper():
            vulnerabilities.append("selfdestruct_usage")
            
        return vulnerabilities
    
    def _find_suspicious_functions(self, code: str) -> List[str]:
        """Find potentially suspicious functions in contract code."""
        suspicious = []
        
        # This is simplified - in production, use proper parsing
        if "transferFrom" in code and "onlyOwner" not in code:
            suspicious.append("unrestricted_transfer_from")
            
        if "approve" in code and "onlyOwner" not in code:
            suspicious.append("unrestricted_approve")
            
        return suspicious
    
    async def _analyze_wash_trading(self, contract_address: str) -> Dict[str, Any]:
        """Analyze a collection for wash trading patterns.
        
        Args:
            contract_address: The NFT contract address to analyze
            
        Returns:
            dict: Wash trading analysis results
        """
        try:
            # Run wash trading analysis
            analysis = await asyncio.get_event_loop().run_in_executor(
                None,
                self.wash_trading_detector.analyze_collection,
                contract_address
            )
            
            # Add timestamp and normalize data
            analysis['timestamp'] = datetime.utcnow().isoformat()
            return analysis
            
        except Exception as e:
            return {
                "error": f"Error analyzing wash trading: {str(e)}",
                "score": 0,
                "confidence": 0,
                "suspicious_trades": []
            }
            
    async def _analyze_mint_anomalies(self, contract_address: str) -> Dict[str, Any]:
        """Analyze a collection for minting anomalies.
        
        Args:
            contract_address: The NFT contract address to analyze
            
        Returns:
            dict: Mint anomaly analysis results
        """
        try:
            # Run mint anomaly detection
            analysis = await asyncio.get_event_loop().run_in_executor(
                None,
                self.mint_anomaly_detector.analyze_collection_mints,
                contract_address
            )
            
            # Add timestamp and normalize data
            analysis['timestamp'] = datetime.utcnow().isoformat()
            return analysis
            
        except Exception as e:
            return {
                "error": f"Error analyzing mint anomalies: {str(e)}",
                "score": 0,
                "confidence": 0,
                "anomalies": []
            }
            
    def _calculate_risk_score(
        self,
        bytecode_analysis: Dict[str, Any],
        is_similar_to_malicious: bool,
        vulnerabilities: List[str],
        suspicious_functions: List[str],
        wash_trading_risk: float = 0.0,
        mint_anomaly_risk: float = 0.0
    ) -> float:
        """Calculate an overall security score (0-100, higher is better).
        
        Args:
            bytecode_analysis: Results from bytecode pattern analysis
            is_similar_to_malicious: Whether the contract is similar to known malicious contracts
            vulnerabilities: List of detected vulnerabilities
            suspicious_functions: List of potentially dangerous functions
            wash_trading_risk: Normalized wash trading risk score (0-1)
            mint_anomaly_risk: Normalized mint anomaly risk score (0-1)
            
        Returns:
            float: Security score from 0-100, where higher is better
        """
        # Start with a perfect score
        score = 100.0
        
        # Penalize for similarity to known malicious contracts
        if is_similar_to_malicious:
            score -= 75.0
            
        # Deduct points for vulnerabilities and suspicious patterns
        score -= len(vulnerabilities) * 10  # Deduction per vulnerability
        score -= len(suspicious_functions) * 3  # Deduction per suspicious function
        
        if is_similar_to_malicious:
            score -= 25  # Deduction for similarity to known malicious contracts
            
        # Deduct for wash trading risk (weighted 20% of total score)
        wash_trading_deduction = wash_trading_risk * 20
        score -= wash_trading_deduction
        
        # Deduct for mint anomaly risk (weighted 15% of total score)
        mint_anomaly_deduction = mint_anomaly_risk * 15
        score -= mint_anomaly_deduction
        
        # Ensure score stays within bounds
        return max(0, min(100, score))
    
    def _calculate_wallet_risk_score(
        self,
        patterns: Dict[str, Any],
        behavior_profile: Dict[str, Any],
        phishing_indicators: List[str]
    ) -> float:
        """Calculate a wallet risk score (0-100, higher is better)."""
        # Start with a neutral score
        score = 50.0
        
        # New wallets are slightly riskier
        if patterns.get("new_wallet", False):
            score -= 10.0
            
        # High frequency of transactions could indicate automation
        if patterns.get("high_frequency", False):
            score -= 5.0
            
        # Symmetrical addresses are sometimes used in phishing
        if patterns.get("address_symmetry", {}).get("is_symmetrical", False):
            score -= 5.0
            
        # Penalize for phishing indicators
        score -= len(phishing_indicators) * 10.0
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))

# Global instance
security_analyzer = SecurityAnalyzer()
