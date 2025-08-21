"""
Production-ready logging configuration for XSEMA

This module provides a comprehensive logging system with:
- Structured logging (JSON format for production)
- Log rotation and file management
- Different log levels for different environments
- Performance monitoring
- Security event logging
"""

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

# Log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

class StructuredFormatter(logging.Formatter):
    """JSON-structured log formatter for production environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class HumanReadableFormatter(logging.Formatter):
    """Human-readable log formatter for development environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = f"[{record.levelname:8}]"
        logger = f"[{record.name:20}]"
        message = record.getMessage()
        
        # Add module and line info
        location = f"({record.module}:{record.lineno})"
        
        return f"{timestamp} {level} {logger} {location} {message}"

class XSEMALogger:
    """Main logging class for XSEMA application."""
    
    def __init__(self, name: str = "xsema"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup log handlers based on environment."""
        
        if ENVIRONMENT == "production":
            self._setup_production_handlers()
        else:
            self._setup_development_handlers()
    
    def _setup_production_handlers(self):
        """Setup production logging with JSON format and rotation."""
        
        # Console handler (structured)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
        
        # Error file handler (rotating)
        error_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "xsema_error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        # Info file handler (rotating)
        info_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "xsema_info.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(info_handler)
        
        # Security events handler
        security_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "xsema_security.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(security_handler)
        
        # Performance metrics handler
        perf_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "xsema_performance.log",
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=5
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(perf_handler)
    
    def _setup_development_handlers(self):
        """Setup development logging with human-readable format."""
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(HumanReadableFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(LOG_DIR / "xsema_dev.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(HumanReadableFormatter())
        self.logger.addHandler(file_handler)
    
    def log_with_context(self, level: str, message: str, **extra_fields):
        """Log message with additional context fields."""
        record = self.logger.makeRecord(
            self.name, getattr(logging, level.upper()), 
            "", 0, message, (), None
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log security-related events."""
        self.log_with_context(
            severity,
            f"Security event: {event_type}",
            event_type=event_type,
            security_details=details,
            severity=severity
        )
    
    def log_performance_metric(self, operation: str, duration_ms: float, **metadata):
        """Log performance metrics."""
        self.log_with_context(
            "INFO",
            f"Performance: {operation} took {duration_ms:.2f}ms",
            operation=operation,
            duration_ms=duration_ms,
            performance_metadata=metadata
        )
    
    def log_api_request(self, method: str, path: str, status_code: int, duration_ms: float, **metadata):
        """Log API request details."""
        level = "INFO" if status_code < 400 else "WARNING"
        self.log_with_context(
            level,
            f"API {method} {path} - {status_code} ({duration_ms:.2f}ms)",
            api_method=method,
            api_path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            api_metadata=metadata
        )
    
    def log_blockchain_event(self, chain: str, event_type: str, details: Dict[str, Any]):
        """Log blockchain-related events."""
        self.log_with_context(
            "INFO",
            f"Blockchain {chain}: {event_type}",
            blockchain_chain=chain,
            blockchain_event=event_type,
            blockchain_details=details
        )

# Global logger instance
xsema_logger = XSEMALogger()

# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"xsema.{name}")

def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "INFO"):
    """Log security event using global logger."""
    xsema_logger.log_security_event(event_type, details, severity)

def log_performance_metric(operation: str, duration_ms: float, **metadata):
    """Log performance metric using global logger."""
    xsema_logger.log_performance_metric(operation, duration_ms, **metadata)

def log_api_request(method: str, path: str, status_code: int, duration_ms: float, **metadata):
    """Log API request using global logger."""
    xsema_logger.log_api_request(method, path, status_code, duration_ms, **metadata)

def log_blockchain_event(chain: str, event_type: str, details: Dict[str, Any]):
    """Log blockchain event using global logger."""
    xsema_logger.log_blockchain_event(chain, event_type, details)

# Middleware for FastAPI
class LoggingMiddleware:
    """FastAPI middleware for request logging."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = datetime.utcnow()
            
            # Log request start
            xsema_logger.log_with_context(
                "INFO",
                f"Request started: {scope['method']} {scope['path']}",
                request_method=scope['method'],
                request_path=scope['path'],
                client_ip=scope.get('client', ('unknown', 0))[0]
            )
            
            # Process request
            await self.app(scope, receive, send)
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log request completion
            xsema_logger.log_with_context(
                "INFO",
                f"Request completed: {scope['method']} {scope['path']} ({duration:.2f}ms)",
                request_method=scope['method'],
                request_path=scope['path'],
                duration_ms=duration
            )
        else:
            await self.app(scope, receive, send)

# Log cleanup utility
def cleanup_old_logs(max_days: int = 30):
    """Clean up log files older than specified days."""
    import time
    current_time = time.time()
    cutoff_time = current_time - (max_days * 24 * 60 * 60)
    
    for log_file in LOG_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"Cleaned up old log file: {log_file}")
            except Exception as e:
                print(f"Failed to clean up {log_file}: {e}")

# Initialize logging
if __name__ == "__main__":
    # Test logging
    logger = get_logger("test")
    logger.info("Logging system initialized successfully")
    
    # Test structured logging
    xsema_logger.log_security_event("login_attempt", {"user_id": "123", "ip": "192.168.1.1"})
    xsema_logger.log_performance_metric("database_query", 45.2, table="users", rows=100)
    xsema_logger.log_blockchain_event("ethereum", "block_mined", {"block_number": 12345678})
