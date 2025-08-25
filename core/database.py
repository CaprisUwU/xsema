"""
Database configuration and connection management for XSEMA.

This module handles PostgreSQL and Redis connections, connection pooling,
and provides database utilities for the application.
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

# Database drivers
try:
    import asyncpg
    import redis.asyncio as redis
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import MetaData
except ImportError:
    asyncpg = None
    redis = None
    create_async_engine = None
    AsyncSession = None
    async_sessionmaker = None
    declarative_base = None
    MetaData = None

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    "postgresql": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "xsema"),
        "user": os.getenv("POSTGRES_USER", "xsema_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "xsema_password"),
        "pool_size": int(os.getenv("POSTGRES_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("POSTGRES_MAX_OVERFLOW", "20")),
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "database": int(os.getenv("REDIS_DB", "0")),
        "password": os.getenv("REDIS_PASSWORD"),
        "ssl": os.getenv("REDIS_SSL", "false").lower() == "true",
    }
}

# SQLAlchemy setup
Base = declarative_base() if declarative_base else None
metadata = MetaData() if MetaData else None

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.postgres_engine = None
        self.redis_client = None
        self.session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections."""
        if self._initialized:
            return
        
        try:
            # Initialize PostgreSQL
            await self._init_postgresql()
            
            # Initialize Redis
            await self._init_redis()
            
            self._initialized = True
            logger.info("✅ Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database connections: {e}")
            raise
    
    async def _init_postgresql(self):
        """Initialize PostgreSQL connection."""
        if not create_async_engine:
            logger.warning("⚠️ SQLAlchemy not available, skipping PostgreSQL")
            return
        
        try:
            # Build connection string
            db_config = DATABASE_CONFIG["postgresql"]
            connection_string = (
                f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            
            # Create async engine
            self.postgres_engine = create_async_engine(
                connection_string,
                pool_size=db_config["pool_size"],
                max_overflow=db_config["max_overflow"],
                echo=os.getenv("SQL_ECHO", "false").lower() == "true",
                future=True
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                self.postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("✅ PostgreSQL connection initialized")
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL initialization failed: {e}")
            raise
    
    async def _init_redis(self):
        """Initialize Redis connection."""
        if not redis:
            logger.warning("⚠️ Redis not available, skipping Redis")
            return
        
        try:
            db_config = DATABASE_CONFIG["redis"]
            
            # Create Redis connection pool
            self.redis_client = redis.Redis(
                host=db_config["host"],
                port=db_config["port"],
                db=db_config["database"],
                password=db_config["password"],
                ssl=db_config["ssl"],
                decode_responses=True,
                max_connections=20
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis connection initialized")
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            raise
    
    @asynccontextmanager
    async def get_session(self):
        """Get a database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def get_redis(self):
        """Get Redis client."""
        if not self.redis_client:
            raise RuntimeError("Redis not initialized")
        return self.redis_client
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health status."""
        health_status = {
            "postgresql": {"status": "unknown", "error": None},
            "redis": {"status": "unknown", "error": None}
        }
        
        # Check PostgreSQL
        if self.postgres_engine:
            try:
                async with self.get_session() as session:
                    await session.execute("SELECT 1")
                health_status["postgresql"]["status"] = "healthy"
            except Exception as e:
                health_status["postgresql"]["status"] = "unhealthy"
                health_status["postgresql"]["error"] = str(e)
        
        # Check Redis
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health_status["redis"]["status"] = "healthy"
            except Exception as e:
                health_status["redis"]["status"] = "unhealthy"
                health_status["redis"]["error"] = str(e)
        
        return health_status
    
    async def close(self):
        """Close database connections."""
        try:
            if self.postgres_engine:
                await self.postgres_engine.dispose()
                logger.info("✅ PostgreSQL connections closed")
            
            if self.redis_client:
                await self.redis_client.close()
                logger.info("✅ Redis connections closed")
                
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")
        finally:
            self._initialized = False

# Global database manager instance
db_manager = DatabaseManager()

# Database dependency for FastAPI
async def get_db():
    """Dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session

async def get_redis():
    """Dependency to get Redis client."""
    return await db_manager.get_redis()
