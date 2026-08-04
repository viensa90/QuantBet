"""
QuantBet - Motor de Estrategias y Puntuación
Versión: 0.3.3 (Corregido)
"""

from .arbitrage import ArbitrageEngine
from .scorer import OpportunityScorer
from .value_betting import ValueBetDetector
from .dutching import DutchingCalculator
from .bankroll import BankrollManager
from .market_handlers import MarketHandler, HandlerFactory
from .probability_model import ProbabilityModel, HistoricalModel, EloModel
from .poisson_model import PoissonModel

__all__ = [
    'ArbitrageEngine',
    'OpportunityScorer',
    'ValueBetDetector',
    'DutchingCalculator',
    'BankrollManager',
    'MarketHandler',
    'HandlerFactory',
    'ProbabilityModel',
    'HistoricalModel',
    'EloModel',
    'PoissonModel'
]