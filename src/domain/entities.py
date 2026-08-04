"""
src/domain/entities.py
Entidades del dominio para QuantBet
Versión: 0.3.3 (Completa)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class MarketType(Enum):
    """Tipos de mercado soportados"""
    # Fútbol
    ODDS_1X2 = "1X2"
    OVER_UNDER = "Over/Under"
    ASIAN_HANDICAP = "Asian Handicap"
    DOUBLE_CHANCE = "Double Chance"
    
    # Tenis
    TENNIS_WINNER = "Tennis Winner"
    TENNIS_SET_HANDICAP = "Tennis Set Handicap"
    TENNIS_TOTAL_GAMES = "Tennis Total Games"
    
    # Baloncesto
    BASKETBALL_MONEYLINE = "Basketball Moneyline"
    BASKETBALL_SPREAD = "Point Spread"
    BASKETBALL_TOTAL = "Total Points"
    BASKETBALL_QUARTER = "Quarter Winner"
    
    # Aliases para compatibilidad
    MERCADO_1X2 = ODDS_1X2  # Para código antiguo


@dataclass
class Snapshot:
    """Snapshot inmutable de odds en un momento dado"""
    event_id: str
    event_name: str
    market_type: str
    bookmaker: str
    odds_data: Dict[str, float]
    timestamp: datetime
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "market_type": self.market_type,
            "bookmaker": self.bookmaker,
            "odds_data": self.odds_data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source
        }


@dataclass
class Opportunity:
    """Oportunidad de arbitraje detectada"""
    event_id: str
    market_type: str
    profit_percent: float       # ← Nombre correcto
    odds: Dict[str, float]
    stakes: Dict[str, float]
    source: str
    timestamp: datetime
    # Atributo opcional para compatibilidad con scorer
    arbitrage_percent: float = None
    
    def __post_init__(self):
        # Si no se proporciona arbitrage_percent, usar profit_percent
        if self.arbitrage_percent is None:
            self.arbitrage_percent = self.profit_percent
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "market_type": self.market_type,
            "profit_percent": self.profit_percent,
            "odds": self.odds,
            "stakes": self.stakes,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ScoredOpportunity:
    """Oportunidad con puntuación y razonamiento"""
    opportunity: Opportunity
    score: float
    risk_level: str  # "bajo", "medio", "alto"
    reasoning: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity": self.opportunity.to_dict(),
            "score": self.score,
            "risk_level": self.risk_level,
            "reasoning": self.reasoning
        }


@dataclass
class ValueBet:
    """Apuesta con valor detectada"""
    event_id: str
    market_type: str
    selection: str
    odds: float
    implied_prob: float
    fair_prob: float
    value: float
    edge_percent: float
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "market_type": self.market_type,
            "selection": self.selection,
            "odds": self.odds,
            "implied_prob": self.implied_prob,
            "fair_prob": self.fair_prob,
            "value": self.value,
            "edge_percent": self.edge_percent,
            "score": self.score
        }


@dataclass
class DutchingResult:
    """Resultado del cálculo de Dutching"""
    event_id: str
    market_type: str
    odds: List[float]
    stakes: List[float]
    total_stake: float
    guaranteed_return: float
    profit_margin: float
    score: float = 50.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "market_type": self.market_type,
            "odds": self.odds,
            "stakes": self.stakes,
            "total_stake": self.total_stake,
            "guaranteed_return": self.guaranteed_return,
            "profit_margin": self.profit_margin,
            "score": self.score
        }


@dataclass
class Decision:
    """Decisión tomada por el sistema (auditable)"""
    event_id: str
    strategy: str
    opportunity_data: Dict[str, Any]
    decision_data: Dict[str, Any]
    opportunity_score: float
    timestamp: datetime
    executed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "strategy": self.strategy,
            "opportunity_data": self.opportunity_data,
            "decision_data": self.decision_data,
            "opportunity_score": self.opportunity_score,
            "timestamp": self.timestamp.isoformat(),
            "executed": self.executed
        }