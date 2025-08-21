"""
Debt & Leverage Tracking Service

This service provides comprehensive debt tracking including:
- Debt position monitoring
- Leverage ratio calculations
- Risk alerts and warnings
- Collateral management
"""
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum

from portfolio.models.portfolio import Portfolio
from portfolio.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DebtPosition:
    """Detailed debt position information"""
    portfolio_id: str
    total_debt: Decimal
    total_collateral: Decimal
    available_collateral: Decimal
    leverage_ratio: Decimal
    risk_level: RiskLevel
    interest_rate: Decimal
    monthly_payment: Decimal
    next_payment_date: datetime
    loan_terms: Dict[str, Any]
    last_updated: datetime

@dataclass
class LeverageMetrics:
    """Comprehensive leverage metrics"""
    portfolio_id: str
    current_leverage: Decimal
    max_safe_leverage: Decimal
    leverage_utilization: Decimal
    margin_requirement: Decimal
    available_margin: Decimal
    risk_score: int
    recommendations: List[str]

@dataclass
class RiskAlert:
    """Risk alert for debt positions"""
    alert_id: str
    portfolio_id: str
    alert_type: str
    severity: RiskLevel
    message: str
    recommendation: str
    created_at: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime]

@dataclass
class CollateralAsset:
    """Collateral asset information"""
    asset_id: str
    asset_name: str
    current_value: Decimal
    collateral_value: Decimal
    haircut_percentage: Decimal
    liquidation_price: Decimal
    last_valuation: datetime

class DebtTracker:
    """Advanced debt tracking and leverage monitoring service"""
    
    def __init__(self, portfolio_service: PortfolioService):
        self.portfolio_service = portfolio_service
        self.logger = logging.getLogger(__name__)
        
        # Risk thresholds
        self.LEVERAGE_THRESHOLDS = {
            RiskLevel.LOW: Decimal('1.5'),
            RiskLevel.MEDIUM: Decimal('2.5'),
            RiskLevel.HIGH: Decimal('4.0'),
            RiskLevel.CRITICAL: Decimal('6.0')
        }
        
        self.MARGIN_REQUIREMENTS = {
            RiskLevel.LOW: Decimal('0.25'),      # 25% margin required
            RiskLevel.MEDIUM: Decimal('0.40'),   # 40% margin required
            RiskLevel.HIGH: Decimal('0.60'),     # 60% margin required
            RiskLevel.CRITICAL: Decimal('0.80')  # 80% margin required
        }
    
    async def track_debt_position(self, portfolio_id: str, user_id: str) -> Optional[DebtPosition]:
        """Track comprehensive debt position for a portfolio"""
        try:
            # Get portfolio
            portfolio = await self.portfolio_service.get_portfolio(portfolio_id, user_id)
            if not portfolio:
                self.logger.warning(f"Portfolio {portfolio_id} not found for user {user_id}")
                return None
            
            # Get debt and collateral data
            debt_data = await self._get_debt_data(portfolio_id)
            collateral_data = await self._get_collateral_data(portfolio_id)
            
            if not debt_data and not collateral_data:
                # No debt position
                return await self._create_no_debt_position(portfolio_id)
            
            # Calculate metrics
            total_debt = debt_data.get('total_debt', Decimal('0'))
            total_collateral = collateral_data.get('total_collateral', Decimal('0'))
            available_collateral = collateral_data.get('available_collateral', Decimal('0'))
            
            # Calculate leverage ratio
            leverage_ratio = (total_debt / total_collateral) if total_collateral > 0 else Decimal('0')
            
            # Determine risk level
            risk_level = self._calculate_risk_level(leverage_ratio)
            
            # Get loan terms
            loan_terms = debt_data.get('loan_terms', {})
            interest_rate = loan_terms.get('interest_rate', Decimal('0'))
            monthly_payment = loan_terms.get('monthly_payment', Decimal('0'))
            next_payment_date = loan_terms.get('next_payment_date', datetime.now(timezone.utc))
            
            debt_position = DebtPosition(
                portfolio_id=portfolio_id,
                total_debt=total_debt,
                total_collateral=total_collateral,
                available_collateral=available_collateral,
                leverage_ratio=leverage_ratio,
                risk_level=risk_level,
                interest_rate=interest_rate,
                monthly_payment=monthly_payment,
                next_payment_date=next_payment_date,
                loan_terms=loan_terms,
                last_updated=datetime.now(timezone.utc)
            )
            
            self.logger.info(f"Debt position tracked for portfolio {portfolio_id}: {leverage_ratio} leverage")
            return debt_position
            
        except Exception as e:
            self.logger.error(f"Error tracking debt position for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def calculate_leverage_metrics(self, portfolio_id: str, user_id: str) -> Optional[LeverageMetrics]:
        """Calculate comprehensive leverage metrics"""
        try:
            # Get debt position
            debt_position = await self.track_debt_position(portfolio_id, user_id)
            if not debt_position:
                return None
            
            # Calculate leverage metrics
            current_leverage = debt_position.leverage_ratio
            max_safe_leverage = self.LEVERAGE_THRESHOLDS[RiskLevel.MEDIUM]  # Use medium as safe threshold
            
            leverage_utilization = (current_leverage / max_safe_leverage * 100) if max_safe_leverage > 0 else Decimal('0')
            
            # Calculate margin requirements
            margin_requirement = self.MARGIN_REQUIREMENTS[debt_position.risk_level]
            available_margin = debt_position.available_collateral / debt_position.total_debt if debt_position.total_debt > 0 else Decimal('0')
            
            # Calculate risk score (0-100)
            risk_score = self._calculate_risk_score(current_leverage, leverage_utilization, available_margin)
            
            # Generate recommendations
            recommendations = self._generate_leverage_recommendations(current_leverage, leverage_utilization, available_margin)
            
            leverage_metrics = LeverageMetrics(
                portfolio_id=portfolio_id,
                current_leverage=current_leverage,
                max_safe_leverage=max_safe_leverage,
                leverage_utilization=leverage_utilization,
                margin_requirement=margin_requirement,
                available_margin=available_margin,
                risk_score=risk_score,
                recommendations=recommendations
            )
            
            return leverage_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating leverage metrics for portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def get_risk_alerts(self, portfolio_id: str, user_id: str) -> List[RiskAlert]:
        """Get risk alerts for a portfolio"""
        try:
            alerts = []
            
            # Get debt position
            debt_position = await self.track_debt_position(portfolio_id, user_id)
            if not debt_position:
                return alerts
            
            # Check leverage alerts
            if debt_position.leverage_ratio > self.LEVERAGE_THRESHOLDS[RiskLevel.HIGH]:
                alerts.append(RiskAlert(
                    alert_id=f"leverage_high_{portfolio_id}",
                    portfolio_id=portfolio_id,
                    alert_type="HIGH_LEVERAGE",
                    severity=RiskLevel.HIGH,
                    message=f"Portfolio leverage is {debt_position.leverage_ratio:.2f}x, exceeding safe threshold",
                    recommendation="Consider reducing debt or adding collateral to lower risk",
                    created_at=datetime.now(timezone.utc),
                    acknowledged=False,
                    acknowledged_at=None
                ))
            
            # Check margin alerts
            margin_ratio = debt_position.available_collateral / debt_position.total_debt if debt_position.total_debt > 0 else Decimal('0')
            required_margin = self.MARGIN_REQUIREMENTS[debt_position.risk_level]
            
            if margin_ratio < required_margin:
                alerts.append(RiskAlert(
                    alert_id=f"margin_low_{portfolio_id}",
                    portfolio_id=portfolio_id,
                    alert_type="LOW_MARGIN",
                    severity=RiskLevel.CRITICAL,
                    message=f"Available margin ({margin_ratio:.1%}) below required ({required_margin:.1%})",
                    recommendation="Add collateral immediately to avoid liquidation risk",
                    created_at=datetime.now(timezone.utc),
                    acknowledged=False,
                    acknowledged_at=None
                ))
            
            # Check payment alerts
            days_until_payment = (debt_position.next_payment_date - datetime.now(timezone.utc)).days
            if days_until_payment <= 7:
                alerts.append(RiskAlert(
                    alert_id=f"payment_due_{portfolio_id}",
                    portfolio_id=portfolio_id,
                    alert_type="PAYMENT_DUE",
                    severity=RiskLevel.MEDIUM if days_until_payment > 3 else RiskLevel.HIGH,
                    message=f"Monthly payment of £{debt_position.monthly_payment} due in {days_until_payment} days",
                    recommendation="Ensure sufficient funds are available for payment",
                    created_at=datetime.now(timezone.utc),
                    acknowledged=False,
                    acknowledged_at=None
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting risk alerts for portfolio {portfolio_id}: {str(e)}")
            return []
    
    async def get_collateral_assets(self, portfolio_id: str, user_id: str) -> List[CollateralAsset]:
        """Get collateral assets for a portfolio"""
        try:
            # This would typically fetch from a collateral management service
            # For now, return mock data
            return [
                CollateralAsset(
                    asset_id="collateral_1",
                    asset_name="Bored Ape #1234",
                    current_value=Decimal('75.0'),
                    collateral_value=Decimal('60.0'),  # 80% of current value
                    haircut_percentage=Decimal('0.20'),  # 20% haircut
                    liquidation_price=Decimal('45.0'),  # 60% of current value
                    last_valuation=datetime.now(timezone.utc)
                ),
                CollateralAsset(
                    asset_id="collateral_2",
                    asset_name="CryptoPunk #5678",
                    current_value=Decimal('30.0'),
                    collateral_value=Decimal('24.0'),  # 80% of current value
                    haircut_percentage=Decimal('0.20'),  # 20% haircut
                    liquidation_price=Decimal('18.0'),  # 60% of current value
                    last_valuation=datetime.now(timezone.utc)
                )
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting collateral assets for portfolio {portfolio_id}: {str(e)}")
            return []
    
    async def calculate_debt_to_income_ratio(self, portfolio_id: str, user_id: str) -> Optional[Decimal]:
        """Calculate debt-to-income ratio"""
        try:
            # Get debt position
            debt_position = await self.track_debt_position(portfolio_id, user_id)
            if not debt_position:
                return None
            
            # Get income data (this would typically fetch from user profile)
            monthly_income = await self._get_monthly_income(user_id)
            if not monthly_income:
                return None
            
            # Calculate DTI ratio
            dti_ratio = (debt_position.monthly_payment / monthly_income) if monthly_income > 0 else Decimal('0')
            
            return dti_ratio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Error calculating DTI ratio for portfolio {portfolio_id}: {str(e)}")
            return None
    
    # Private helper methods
    
    async def _get_debt_data(self, portfolio_id: str) -> Dict[str, Any]:
        """Get debt data for a portfolio"""
        # This would typically fetch from a debt management service
        # For now, return mock data
        return {
            'total_debt': Decimal('50.0'),
            'loan_terms': {
                'interest_rate': Decimal('0.08'),  # 8% APR
                'monthly_payment': Decimal('4.0'),
                'next_payment_date': datetime.now(timezone.utc) + timedelta(days=15),
                'loan_type': 'NFT-backed',
                'term_length': 12,  # months
                'origination_fee': Decimal('0.02')  # 2%
            }
        }
    
    async def _get_collateral_data(self, portfolio_id: str) -> Dict[str, Any]:
        """Get collateral data for a portfolio"""
        # This would typically fetch from a collateral management service
        # For now, return mock data
        return {
            'total_collateral': Decimal('105.0'),
            'available_collateral': Decimal('55.0'),  # Total - debt
            'collateral_ratio': Decimal('2.1'),  # 105/50
            'liquidation_threshold': Decimal('1.5')
        }
    
    def _calculate_risk_level(self, leverage_ratio: Decimal) -> RiskLevel:
        """Calculate risk level based on leverage ratio"""
        if leverage_ratio <= self.LEVERAGE_THRESHOLDS[RiskLevel.LOW]:
            return RiskLevel.LOW
        elif leverage_ratio <= self.LEVERAGE_THRESHOLDS[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        elif leverage_ratio <= self.LEVERAGE_THRESHOLDS[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _calculate_risk_score(self, leverage: Decimal, utilization: Decimal, margin: Decimal) -> int:
        """Calculate risk score (0-100)"""
        try:
            # Leverage component (0-40 points)
            leverage_score = min(40, int(leverage * 10))
            
            # Utilization component (0-30 points)
            utilization_score = min(30, int(utilization / 3.33))
            
            # Margin component (0-30 points)
            margin_score = max(0, 30 - int(margin * 30))
            
            total_score = leverage_score + utilization_score + margin_score
            return min(100, total_score)
            
        except Exception:
            return 50  # Default score
    
    def _generate_leverage_recommendations(self, leverage: Decimal, utilization: Decimal, margin: Decimal) -> List[str]:
        """Generate leverage recommendations"""
        recommendations = []
        
        if leverage > self.LEVERAGE_THRESHOLDS[RiskLevel.HIGH]:
            recommendations.append("Consider reducing debt to lower leverage risk")
            recommendations.append("Add additional collateral to improve margin position")
        
        elif leverage > self.LEVERAGE_THRESHOLDS[RiskLevel.MEDIUM]:
            recommendations.append("Monitor leverage closely and consider debt reduction")
            recommendations.append("Ensure adequate collateral coverage")
        
        if utilization > 80:
            recommendations.append("Leverage utilization is high - consider reducing exposure")
        
        if margin < 0.3:
            recommendations.append("Margin position is tight - add collateral if possible")
        
        if not recommendations:
            recommendations.append("Current leverage position is within safe parameters")
        
        return recommendations
    
    async def _get_monthly_income(self, user_id: str) -> Optional[Decimal]:
        """Get monthly income for a user"""
        # This would typically fetch from user profile or financial data
        # For now, return mock data
        return Decimal('5000.0')  # £5,000 per month
    
    async def _create_no_debt_position(self, portfolio_id: str) -> DebtPosition:
        """Create debt position for portfolios with no debt"""
        return DebtPosition(
            portfolio_id=portfolio_id,
            total_debt=Decimal('0'),
            total_collateral=Decimal('0'),
            available_collateral=Decimal('0'),
            leverage_ratio=Decimal('0'),
            risk_level=RiskLevel.LOW,
            interest_rate=Decimal('0'),
            monthly_payment=Decimal('0'),
            next_payment_date=datetime.now(timezone.utc),
            loan_terms={},
            last_updated=datetime.now(timezone.utc)
        )
