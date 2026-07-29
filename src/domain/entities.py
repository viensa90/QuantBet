"""
QuantBet - Entidades del Dominio (QB-002)
Implementación de los contratos definidos en el Modelo de Dominio Conceptual.
Principio: Estas clases son independientes de cualquier fuente de datos o lógica de negocio.
Versión 1.1 - Corrección de orden de campos en dataclasses.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid

# --- Enums de Soporte ---

class SportType(Enum):
    FOOTBALL = "football"
    TENNIS = "tennis"
    BASKETBALL = "basketball"

class EventStatus(Enum):
    PENDING = "PENDING"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"

class BookmakerType(Enum):
    TRADITIONAL_BOOKMAKER = "TRADITIONAL_BOOKMAKER"
    PREDICTION_MARKET = "PREDICTION_MARKET"
    SIMULATED = "SIMULATED"

# --- Entidades Principales ---

@dataclass(frozen=True)
class Bookmaker:
    """Casa de apuestas o fuente de datos (QB-002, 3.1.1)"""
    id: str
    name: str
    type: BookmakerType

@dataclass(frozen=True)
class Sport:
    """Deporte al que pertenece una competición (QB-002, 3.1.2)"""
    id: str
    name: str
    type: SportType

@dataclass(frozen=True)
class Competition:
    """Liga o torneo (QB-002, 3.1.2)"""
    id: str
    name: str
    sport: Sport

@dataclass(frozen=True)
class Participant:
    """Un equipo o jugador en un evento."""
    name: str
    type: str  # 'home' o 'away'

@dataclass(frozen=True)
class Event:
    """Un partido o encuentro (QB-002, 3.1.4)"""
    id: str
    competition: Competition
    start_time_utc: datetime
    participants: List[Participant]
    status: EventStatus = EventStatus.PENDING  # Valor por defecto va al final

@dataclass(frozen=True)
class Market:
    """Un tipo de apuesta dentro de un evento (QB-002, 3.1.5)"""
    id: str
    event_id: str
    type: str  # '1X2', 'OVER_UNDER_2.5', etc.
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Outcome:
    """Una posible selección en un mercado (QB-002, 3.1.6)"""
    id: str
    market_id: str
    name: str  # '1', 'X', 'Over 2.5'

@dataclass(frozen=True)
class Snapshot:
    """
    La entidad central. Fotografía inmutable de las cuotas en un instante.
    (QB-002, 3.2) - El activo más valioso del proyecto.
    """
    bookmaker: Bookmaker
    market: Market
    timestamp_utc: datetime
    odds: Dict[str, float]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Reglas de integridad inmutables."""
        # Validación: Las cuotas deben ser positivas
        for outcome_name, odds_value in self.odds.items():
            if odds_value <= 0:
                raise ValueError(f"Cuota inválida para '{outcome_name}': {odds_value}. Debe ser > 0.")

@dataclass(frozen=True)
class Decision:
    """
    Recomendación estructurada, objetiva y auditable.
    (QB-004, 3.4) - La salida del Motor de Estrategias.
    """
    strategy: str
    opportunity_score: float  # 0-100
    snapshot_ids: List[str]
    recommended_stake_total: float
    expected_roi: float
    details: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_seconds: int = 0
    
    def __post_init__(self):
        """Validaciones de integridad."""
        if self.opportunity_score < 0 or self.opportunity_score > 100:
            raise ValueError(f"Opportunity Score debe estar entre 0 y 100. Valor: {self.opportunity_score}")
        if self.recommended_stake_total <= 0:
            raise ValueError(f"Stake recomendado debe ser positivo. Valor: {self.recommended_stake_total}")