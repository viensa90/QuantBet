"""
Entidades de dominio de QuantBet.
Snapshots, Oportunidades, Decisiones con soporte multi-mercado.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Optional, List, Any


class MarketType(Enum):
    """Tipos de mercado soportados."""
    MERCADO_1X2 = "1X2"
    OVER_UNDER = "OVER_UNDER"
    ASIAN_HANDICAP = "ASIAN_HANDICAP"
    DOUBLE_CHANCE = "DOUBLE_CHANCE"
    BOTH_TEAMS_SCORE = "BOTH_TEAMS_SCORE"


@dataclass
class Snapshot:
    """Snapshot inmutable de cuotas en un momento dado."""
    event_id: str
    event_name: str
    source: str
    timestamp: datetime
    odds: Dict[str, Decimal]  # Ej: {"Local": 2.10, "Empate": 3.40, "Visitante": 3.80}
    market_type: MarketType = MarketType.MERCADO_1X2
    metadata: Dict[str, Any] = field(default_factory=dict)  # Línea de handicap, total de goles, etc.


@dataclass
class Opportunity:
    """Oportunidad de arbitraje detectada."""
    event_id: str
    event_name: str
    source: str
    market_type: MarketType
    arbitrage_percent: float  # Ej: 3.76
    total_stake: Decimal
    stakes: Dict[str, Decimal]  # Apuestas por mercado/resultado
    odds_used: Dict[str, Decimal]  # Cuotas utilizadas
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)  # Handicap, línea, etc.


@dataclass
class ScoredOpportunity:
    """Oportunidad con puntuación."""
    opportunity: Opportunity
    score: float  # 0-100
    risk_level: str  # "bajo", "medio", "alto"
    reasoning: List[str] = field(default_factory=list)


@dataclass
class ValueBet:
    """Value bet detectado."""
    event_id: str
    event_name: str
    source: str
    market_type: MarketType
    outcome: str  # "Local", "Empate", "Visitante", "Over", "Under", etc.
    fair_probability: float  # Probabilidad justa estimada
    actual_odds: Decimal  # Cuota actual
    value_percent: float  # Valor positivo = buena oportunidad
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DutchingOpportunity:
    """Oportunidad de dutching."""
    event_id: str
    event_name: str
    market_type: MarketType
    coverage_percent: float  # % de cobertura de todos los resultados
    total_stake: Decimal
    stakes: Dict[str, Decimal]  # Apuestas por resultado
    expected_profit: Decimal
    outcomes: List[str]  # Resultados cubiertos
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """Decisión registrada en BD (auditable)."""
    event_id: str
    source: str
    strategy: str  # "ARBITRAGE", "VALUE_BET", "DUTCHING"
    accepted: bool
    score: Optional[float]
    stake: Optional[Decimal]
    metadata: Dict[str, Any]
    timestamp: datetime