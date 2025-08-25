"""
Advanced security features for XSEMA.

This module provides comprehensive security features including rate limiting,
input validation, threat detection, and security monitoring.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import defaultdict, deque
import re

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event structure."""
    event_type: str
    severity: str  # low, medium, high, critical
    source_ip: str
    user_id: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
    threat_score: float

class RateLimiter:
    """Advanced rate limiting with sliding window and burst protection."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, datetime] = {}
        self.block_duration = timedelta(minutes=15)
    
    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed."""
        now = datetime.now()
        
        # Check if IP is blocked
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                return False
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self.requests[identifier] and self.requests[identifier][0] < cutoff:
            self.requests[identifier].popleft()
        
        # Check rate limit
        if len(self.requests[identifier]) >= self.max_requests:
            # Block the IP
            self.blocked_ips[identifier] = now + self.block_duration
            logger.warning(f"Rate limit exceeded for {identifier}, blocked for {self.block_duration}")
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """Get rate limiting statistics for an identifier."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < cutoff:
            self.requests[identifier].popleft()
        
        return {
            "current_requests": len(self.requests[identifier]),
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "is_blocked": identifier in self.blocked_ips,
            "block_until": self.blocked_ips.get(identifier)
        }

class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(--|/\*|\*/|xp_|sp_)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+['\"].*['\"]\s*=\s*['\"].*['\"])"
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        # Path traversal patterns
        self.path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c"
        ]
        
        # Compile patterns
        self.sql_regex = re.compile("|".join(self.sql_patterns), re.IGNORECASE)
        self.xss_regex = re.compile("|".join(self.xss_patterns), re.IGNORECASE)
        self.path_regex = re.compile("|".join(self.path_patterns), re.IGNORECASE)
    
    def validate_string(self, value: str, max_length: int = 1000) -> Dict[str, Any]:
        """Validate and sanitize a string input."""
        if not isinstance(value, str):
            return {"valid": False, "error": "Value must be a string"}
        
        if len(value) > max_length:
            return {"valid": False, "error": f"String too long (max {max_length} characters)"}
        
        # Check for SQL injection
        if self.sql_regex.search(value):
            return {"valid": False, "error": "Potential SQL injection detected"}
        
        # Check for XSS
        if self.xss_regex.search(value):
            return {"valid": False, "error": "Potential XSS attack detected"}
        
        # Check for path traversal
        if self.path_regex.search(value):
            return {"valid": False, "error": "Potential path traversal attack detected"}
        
        # Sanitize the string
        sanitized = self._sanitize_string(value)
        
        return {
            "valid": True,
            "sanitized": sanitized,
            "original_length": len(value),
            "sanitized_length": len(sanitized)
        }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate email address."""
        if not isinstance(email, str):
            return {"valid": False, "error": "Email must be a string"}
        
        # Basic email pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return {"valid": False, "error": "Invalid email format"}
        
        # Check length
        if len(email) > 254:  # RFC 5321 limit
            return {"valid": False, "error": "Email too long"}
        
        return {"valid": True, "email": email.lower()}
    
    def validate_wallet_address(self, address: str) -> Dict[str, Any]:
        """Validate Ethereum wallet address."""
        if not isinstance(address, str):
            return {"valid": False, "error": "Address must be a string"}
        
        # Ethereum address pattern
        if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
            return {"valid": False, "error": "Invalid Ethereum address format"}
        
        return {"valid": True, "address": address}
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string by removing dangerous characters."""
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters (except newline and tab)
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # HTML encode special characters
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        
        return value

class ThreatDetector:
    """Advanced threat detection and scoring."""
    
    def __init__(self):
        self.suspicious_patterns = {
            "sql_injection": 0.8,
            "xss_attack": 0.7,
            "path_traversal": 0.6,
            "rate_limit_exceeded": 0.5,
            "unusual_activity": 0.4,
            "suspicious_ip": 0.3
        }
        
        self.ip_reputation: Dict[str, Dict[str, Any]] = {}
        self.user_behavior: Dict[str, Dict[str, Any]] = {}
    
    def analyze_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request for potential threats."""
        threat_score = 0.0
        threats = []
        
        # Analyze IP address
        source_ip = request_data.get("source_ip", "")
        ip_analysis = self._analyze_ip(source_ip)
        threat_score += ip_analysis["score"]
        if ip_analysis["threats"]:
            threats.extend(ip_analysis["threats"])
        
        # Analyze user behavior
        user_id = request_data.get("user_id")
        if user_id:
            behavior_analysis = self._analyze_user_behavior(user_id, request_data)
            threat_score += behavior_analysis["score"]
            if behavior_analysis["threats"]:
                threats.extend(behavior_analysis["threats"])
        
        # Analyze request patterns
        pattern_analysis = self._analyze_request_patterns(request_data)
        threat_score += pattern_analysis["score"]
        if pattern_analysis["threats"]:
            threats.extend(pattern_analysis["threats"])
        
        # Determine severity
        severity = self._calculate_severity(threat_score)
        
        return {
            "threat_score": min(threat_score, 1.0),  # Cap at 1.0
            "severity": severity,
            "threats": threats,
            "recommendations": self._get_recommendations(threat_score, threats)
        }
    
    def _analyze_ip(self, ip: str) -> Dict[str, Any]:
        """Analyze IP address for threats."""
        score = 0.0
        threats = []
        
        if not ip:
            return {"score": score, "threats": threats}
        
        # Check IP reputation
        if ip in self.ip_reputation:
            reputation = self.ip_reputation[ip]
            if reputation.get("blocked", False):
                score += 0.8
                threats.append("IP previously blocked")
            
            if reputation.get("suspicious_requests", 0) > 100:
                score += 0.4
                threats.append("High number of suspicious requests")
        
        # Check for suspicious IP patterns
        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
            score += 0.2
            threats.append("Private IP address")
        
        return {"score": score, "threats": threats}
    
    def _analyze_user_behavior(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user behavior for anomalies."""
        score = 0.0
        threats = []
        
        if user_id not in self.user_behavior:
            self.user_behavior[user_id] = {
                "request_count": 0,
                "last_request": None,
                "suspicious_actions": 0,
                "failed_auth": 0
            }
        
        behavior = self.user_behavior[user_id]
        behavior["request_count"] += 1
        
        # Check for rapid requests
        now = datetime.now()
        if behavior["last_request"]:
            time_diff = (now - behavior["last_request"]).total_seconds()
            if time_diff < 1 and behavior["request_count"] > 10:
                score += 0.3
                threats.append("Rapid request pattern")
        
        behavior["last_request"] = now
        
        # Check for suspicious actions
        if request_data.get("action") in ["login", "password_reset"]:
            if behavior["failed_auth"] > 5:
                score += 0.5
                threats.append("Multiple failed authentication attempts")
        
        return {"score": score, "threats": threats}
    
    def _analyze_request_patterns(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request patterns for threats."""
        score = 0.0
        threats = []
        
        # Check for unusual user agents
        user_agent = request_data.get("user_agent", "")
        if user_agent:
            suspicious_agents = ["bot", "crawler", "scraper", "curl", "wget"]
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                score += 0.2
                threats.append("Suspicious user agent")
        
        # Check for unusual request methods
        method = request_data.get("method", "")
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            score += 0.3
            threats.append("Unusual HTTP method")
        
        return {"score": score, "threats": threats}
    
    def _calculate_severity(self, threat_score: float) -> str:
        """Calculate threat severity level."""
        if threat_score >= 0.8:
            return "critical"
        elif threat_score >= 0.6:
            return "high"
        elif threat_score >= 0.4:
            return "medium"
        elif threat_score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    def _get_recommendations(self, threat_score: float, threats: List[str]) -> List[str]:
        """Get security recommendations based on threats."""
        recommendations = []
        
        if threat_score >= 0.8:
            recommendations.append("Immediately block IP address")
            recommendations.append("Review user account for compromise")
            recommendations.append("Enable enhanced monitoring")
        
        if threat_score >= 0.6:
            recommendations.append("Implement additional rate limiting")
            recommendations.append("Enable CAPTCHA for authentication")
            recommendations.append("Review access logs")
        
        if "SQL injection" in threats:
            recommendations.append("Implement input validation")
            recommendations.append("Use parameterized queries")
        
        if "XSS attack" in threats:
            recommendations.append("Implement output encoding")
            recommendations.append("Enable Content Security Policy")
        
        return recommendations

class SecurityMonitor:
    """Comprehensive security monitoring and alerting."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.input_validator = InputValidator()
        self.threat_detector = ThreatDetector()
        self.security_events: List[SecurityEvent] = []
        self.alert_callbacks: List[Callable] = []
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze a request for security threats."""
        # Rate limiting check
        identifier = request_data.get("source_ip", "unknown")
        rate_limit_allowed = await self.rate_limiter.is_allowed(identifier)
        
        if not rate_limit_allowed:
            await self._log_security_event(
                "rate_limit_exceeded",
                "high",
                identifier,
                request_data.get("user_id"),
                {"identifier": identifier},
                0.8
            )
            return {
                "allowed": False,
                "reason": "Rate limit exceeded",
                "retry_after": 900  # 15 minutes
            }
        
        # Input validation
        validation_results = {}
        for key, value in request_data.items():
            if isinstance(value, str):
                validation_results[key] = self.input_validator.validate_string(value)
        
        # Check for validation failures
        validation_failures = [
            key for key, result in validation_results.items()
            if not result["valid"]
        ]
        
        if validation_failures:
            await self._log_security_event(
                "input_validation_failed",
                "high",
                identifier,
                request_data.get("user_id"),
                {"failures": validation_failures, "results": validation_results},
                0.7
            )
            return {
                "allowed": False,
                "reason": "Input validation failed",
                "failures": validation_failures
            }
        
        # Threat detection
        threat_analysis = self.threat_detector.analyze_request(request_data)
        
        if threat_analysis["threat_score"] > 0.6:
            await self._log_security_event(
                "high_threat_detected",
                "critical",
                identifier,
                request_data.get("user_id"),
                threat_analysis,
                threat_analysis["threat_score"]
            )
        
        # Log all security events
        if threat_analysis["threats"]:
            await self._log_security_event(
                "threat_detected",
                threat_analysis["severity"],
                identifier,
                request_data.get("user_id"),
                threat_analysis,
                threat_analysis["threat_score"]
            )
        
        return {
            "allowed": True,
            "threat_score": threat_analysis["threat_score"],
            "severity": threat_analysis["severity"],
            "recommendations": threat_analysis["recommendations"]
        }
    
    async def _log_security_event(self, event_type: str, severity: str, source_ip: str,
                                 user_id: Optional[str], details: Dict[str, Any], threat_score: float):
        """Log a security event."""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            details=details,
            timestamp=datetime.now(),
            threat_score=threat_score
        )
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # Trigger alerts for high-severity events
        if severity in ["high", "critical"]:
            await self._trigger_alert(event)
        
        logger.warning(f"Security event: {event_type} - {severity} - IP: {source_ip} - Score: {threat_score}")
    
    async def _trigger_alert(self, event: SecurityEvent):
        """Trigger security alerts."""
        for callback in self.alert_callbacks:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        recent_events = [e for e in self.security_events if e.timestamp > last_hour]
        daily_events = [e for e in self.security_events if e.timestamp > last_day]
        
        return {
            "total_events": len(self.security_events),
            "events_last_hour": len(recent_events),
            "events_last_day": len(daily_events),
            "high_severity_events": len([e for e in daily_events if e.severity in ["high", "critical"]]),
            "blocked_ips": len(self.rate_limiter.blocked_ips),
            "active_threats": len([e for e in recent_events if e.threat_score > 0.5])
        }

# Global security monitor instance
security_monitor = SecurityMonitor()
