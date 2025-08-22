"""
Enterprise authentication service with database integration.

This module provides:
- User management with database persistence
- Session management
- Organization and department management
- Portfolio and transaction tracking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
import logging

from .models import (
    User, Organization, Department, UserSession, 
    Portfolio, PortfolioAsset, Transaction, SecurityAlert, AuditLog
)
from .database import get_db_session, get_db
from ..enterprise_auth import UserRole, AuthProvider, MFAStatus

logger = logging.getLogger(__name__)

class EnterpriseService:
    """Enterprise authentication and management service."""
    
    def __init__(self):
        self.secret_key = "your-secret-key-here"  # Should come from environment
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        password: Optional[str] = None,
        role: UserRole = UserRole.USER,
        auth_provider: AuthProvider = AuthProvider.LOCAL,
        organization_id: Optional[str] = None,
        department_id: Optional[str] = None
    ) -> User:
        """Create a new enterprise user."""
        with get_db_session() as db:
            # Check if user already exists
            if db.query(User).filter(User.username == username).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            if db.query(User).filter(User.email == email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                password_hash=password_hash,
                role=role.value,
                auth_provider=auth_provider.value,
                organization_id=organization_id,
                department_id=department_id,
                permissions=self._get_default_permissions(role)
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Log the action
            self._log_audit(db, user.id, "user_created", "user", user.id)
            
            logger.info(f"Created user: {username}")
            
            # Return user with ID for external use
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "auth_provider": user.auth_provider
            }
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        with get_db_session() as db:
            user = db.query(User).filter(User.username == username).first()
            
            if not user or not user.is_active:
                return None
            
            if not user.password_hash:
                return None
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Log the action
            self._log_audit(db, user.id, "user_login", "user", user.id)
            
            return user
    
    def create_session(self, user_id: str, ip_address: str = None, user_agent: str = None) -> dict:
        """Create a new user session."""
        with get_db_session() as db:
            # Generate tokens
            access_token = self._create_access_token(user_id)
            refresh_token = self._create_refresh_token(user_id)
            
            # Create session
            session = UserSession(
                user_id=user_id,
                session_token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            logger.info(f"Created session for user: {user_id}")
            
            # Return session data for external use
            return {
                "id": session.id,
                "session_token": session.session_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at,
                "user_id": session.user_id
            }
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate a session token and return the user."""
        with get_db_session() as db:
            session = db.query(UserSession).filter(
                UserSession.session_token == session_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                return None
            
            user = db.query(User).filter(User.id == session.user_id).first()
            if not user or not user.is_active:
                return None
            
            return user
    
    def refresh_session(self, refresh_token: str) -> Optional[UserSession]:
        """Refresh a session using a refresh token."""
        with get_db_session() as db:
            session = db.query(UserSession).filter(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            ).first()
            
            if not session:
                return None
            
            # Generate new tokens
            new_access_token = self._create_access_token(session.user_id)
            new_refresh_token = self._create_refresh_token(session.user_id)
            
            # Update session
            session.session_token = new_access_token
            session.refresh_token = new_refresh_token
            session.expires_at = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            logger.info(f"Refreshed session for user: {session.user_id}")
            return session
    
    def revoke_session(self, session_token: str) -> bool:
        """Revoke a user session."""
        with get_db_session() as db:
            session = db.query(UserSession).filter(
                UserSession.session_token == session_token
            ).first()
            
            if not session:
                return False
            
            session.is_active = False
            db.commit()
            
            # Log the action
            self._log_audit(db, session.user_id, "session_revoked", "session", session.id)
            
            logger.info(f"Revoked session: {session.id}")
            return True
    
    def create_portfolio(
        self,
        user_id: str,
        name: str,
        description: str = None,
        currency: str = "GBP"
    ) -> Portfolio:
        """Create a new portfolio for a user."""
        with get_db_session() as db:
            portfolio = Portfolio(
                user_id=user_id,
                name=name,
                description=description,
                currency=currency
            )
            
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            
            # Log the action
            self._log_audit(db, user_id, "portfolio_created", "portfolio", portfolio.id)
            
            logger.info(f"Created portfolio: {name} for user: {user_id}")
            return portfolio
    
    def get_user_portfolios(self, user_id: str) -> List[Portfolio]:
        """Get all portfolios for a user."""
        with get_db_session() as db:
            return db.query(Portfolio).filter(
                Portfolio.user_id == user_id,
                Portfolio.is_active == True
            ).all()
    
    def create_security_alert(
        self,
        user_id: str,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        alert_data: Dict[str, Any] = None
    ) -> SecurityAlert:
        """Create a new security alert."""
        with get_db_session() as db:
            alert = SecurityAlert(
                user_id=user_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                alert_data=alert_data or {}
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Created security alert: {title} for user: {user_id}")
            return alert
    
    def _create_access_token(self, user_id: str) -> str:
        """Create an access token."""
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token."""
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _get_default_permissions(self, role: UserRole) -> List[str]:
        """Get default permissions for a role."""
        permissions = {
            UserRole.VIEWER: ["read_portfolio", "read_market_data"],
            UserRole.USER: ["read_portfolio", "write_portfolio", "read_market_data"],
            UserRole.ANALYST: ["read_portfolio", "write_portfolio", "read_market_data", "read_reports", "write_reports"],
            UserRole.MANAGER: ["read_portfolio", "write_portfolio", "read_market_data", "read_reports", "write_reports", "manage_users"],
            UserRole.ADMIN: ["read_portfolio", "write_portfolio", "read_market_data", "read_reports", "write_reports", "manage_users", "admin_settings"],
            UserRole.SUPER_ADMIN: ["*"]  # All permissions
        }
        return permissions.get(role, [])
    
    def _log_audit(self, db: Session, user_id: str, action: str, resource_type: str, resource_id: str):
        """Log an audit event."""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

# Global service instance
enterprise_service = EnterpriseService()
