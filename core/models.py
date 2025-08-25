"""
Database models for XSEMA application.

This module defines SQLAlchemy models for users, portfolios, NFTs,
and other core entities in the system.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Create Base locally to ensure it's always available
Base = declarative_base()

class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(String(20), default="user")  # user, premium, admin
    status = Column(String(20), default="active")  # active, suspended, deleted
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class APIKey(Base):
    """API key model for user authentication."""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    permissions = Column(JSON)  # Store permissions as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

class Portfolio(Base):
    """Portfolio model for user NFT collections."""
    
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    nfts = relationship("PortfolioNFT", back_populates="portfolio")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', user_id={self.user_id})>"

class NFT(Base):
    """NFT model for storing NFT metadata and data."""
    
    __tablename__ = "nfts"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String(100), nullable=False)
    contract_address = Column(String(42), nullable=False)  # Ethereum address
    chain_id = Column(Integer, default=1)  # 1 = Ethereum mainnet
    name = Column(String(255))
    description = Column(Text)
    image_url = Column(String(500))
    external_url = Column(String(500))
    attributes = Column(JSON)  # Store NFT attributes as JSON
    nft_data = Column(JSON)  # Store full NFT data as JSON
    rarity_score = Column(Float)
    floor_price = Column(Float)
    last_floor_price = Column(Float)
    volume_24h = Column(Float)
    holders_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio_nfts = relationship("PortfolioNFT", back_populates="nft")
    
    def __repr__(self):
        return f"<NFT(id={self.id}, token_id='{self.token_id}', contract='{self.contract_address}')>"

class PortfolioNFT(Base):
    """Junction table for portfolio-NFT relationships."""
    
    __tablename__ = "portfolio_nfts"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    nft_id = Column(Integer, ForeignKey("nfts.id"), nullable=False)
    quantity = Column(Integer, default=1)
    purchase_price = Column(Float)
    purchase_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="nfts")
    nft = relationship("NFT", back_populates="portfolio_nfts")
    
    def __repr__(self):
        return f"<PortfolioNFT(portfolio_id={self.portfolio_id}, nft_id={self.nft_id})>"

class Collection(Base):
    """NFT collection model."""
    
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_address = Column(String(42), unique=True, nullable=False)
    chain_id = Column(Integer, default=1)
    name = Column(String(255), nullable=False)
    symbol = Column(String(50))
    description = Column(Text)
    image_url = Column(String(500))
    banner_url = Column(String(500))
    external_url = Column(String(500))
    twitter_url = Column(String(500))
    discord_url = Column(String(500))
    website_url = Column(String(500))
    stats = Column(JSON)  # Store collection stats as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}', contract='{self.contract_address}')>"

class MarketData(Base):
    """Market data model for storing price and volume data."""
    
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    nft_id = Column(Integer, ForeignKey("nfts.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    price = Column(Float)
    volume = Column(Float)
    sales_count = Column(Integer)
    unique_buyers = Column(Integer)
    unique_sellers = Column(Integer)
    floor_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketData(id={self.id}, nft_id={self.nft_id}, timestamp={self.timestamp})>"

class Wallet(Base):
    """Wallet model for storing wallet information."""
    
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(42), unique=True, nullable=False)  # Ethereum address
    chain_id = Column(Integer, default=1)
    label = Column(String(100))
    is_verified = Column(Boolean, default=False)
    risk_score = Column(Float)
    tags = Column(JSON)  # Store wallet tags as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, address='{self.address}', chain_id={self.chain_id})>"

class AuditLog(Base):
    """Audit log model for tracking system activities."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"

# Create tables function
def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
