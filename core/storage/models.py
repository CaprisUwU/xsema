"""
Database models for XSEMA enterprise authentication and portfolio management.

This module defines SQLAlchemy models for:
- Users and authentication
- Organizations and departments
- Portfolios and transactions
- Security alerts and monitoring
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_id():
    """Generate a unique identifier."""
    return str(uuid.uuid4())

class Organization(Base):
    """Organization model for enterprise customers."""
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    industry = Column(String(100))
    size = Column(String(50))  # small, medium, large, enterprise
    subscription_tier = Column(String(50), default="basic")  # basic, pro, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    departments = relationship("Department", back_populates="organization")

class Department(Base):
    """Department model within organizations."""
    __tablename__ = "departments"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(255), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    manager_id = Column(String(36), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="departments")
    users = relationship("User", back_populates="department", foreign_keys="User.department_id")

class User(Base):
    """Enterprise user model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255))  # For local auth
    role = Column(String(50), default="user")  # viewer, user, analyst, manager, admin, super_admin
    auth_provider = Column(String(50), default="local")  # local, saml, oauth, ldap
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))  # TOTP secret
    is_active = Column(Boolean, default=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"))
    department_id = Column(String(36), ForeignKey("departments.id"))
    manager_id = Column(String(36), ForeignKey("users.id"))
    permissions = Column(JSON, default=list)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])
    manager = relationship("User", remote_side=[id], foreign_keys=[manager_id])
    portfolios = relationship("Portfolio", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

class UserSession(Base):
    """User session management."""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255))
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class Portfolio(Base):
    """User portfolio model."""
    __tablename__ = "portfolios"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    total_value = Column(Float, default=0.0)
    currency = Column(String(10), default="GBP")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    assets = relationship("PortfolioAsset", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")

class PortfolioAsset(Base):
    """Portfolio asset model."""
    __tablename__ = "portfolio_assets"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id"), nullable=False)
    asset_type = Column(String(50), nullable=False)  # nft, crypto, token
    asset_id = Column(String(255), nullable=False)  # Contract address + token ID
    quantity = Column(Float, default=1.0)
    purchase_price = Column(Float)
    current_value = Column(Float)
    purchase_date = Column(DateTime)
    last_updated = Column(DateTime, default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")

class Transaction(Base):
    """Portfolio transaction model."""
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # buy, sell, transfer
    asset_id = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    blockchain_tx_hash = Column(String(255))
    status = Column(String(50), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")

class SecurityAlert(Base):
    """Security alert model."""
    __tablename__ = "security_alerts"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # high_leverage, suspicious_activity, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")  # active, resolved, dismissed
    alert_data = Column(JSON)  # Additional alert data
    created_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")

class AuditLog(Base):
    """Audit logging for compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    user_id = Column(String(36), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")
