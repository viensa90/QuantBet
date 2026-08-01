"""
src/core/market_handlers.py
Handlers específicos por mercado (Strategy Pattern)
Versión: 0.3.1 (Soporte para Tenis)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from src.domain.entities import Snapshot, Opportunity, MarketType

logger = logging.getLogger(__name__)

class BaseMarketHandler(ABC):
    """Clase base para handlers de mercado"""
    
    @abstractmethod
    def get_market_type(self) -> str:
        """Retorna el tipo de mercado"""
        pass
    
    @abstractmethod
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        """Encuentra oportunidades de arbitraje en un snapshot"""
        pass
    
    @abstractmethod
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        """Calcula odds justas para value betting"""
        pass
    
    def validate_odds(self, odds_data: Dict[str, float]) -> bool:
        """Valida que los odds sean consistentes"""
        if not odds_data:
            return False
        for odd in odds_data.values():
            if odd <= 1.0:
                return False
        return True

class Handler1X2(BaseMarketHandler):
    """Handler para mercado 1X2 (Fútbol, Tenis, etc.)"""
    
    def get_market_type(self) -> str:
        return "1X2"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        # Calcular overround
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        # Si overround < 1, hay arbitraje
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            # Calcular stakes para arbitraje
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        """Calcula odds justas (inverso de probabilidades)"""
        if not self.validate_odds(snapshot.odds_data):
            return None
        
        # Usar modelo de probabilidad (implementación externa)
        # Por ahora retorna None, será manejado por el modelo externo
        return None

class HandlerOverUnder(BaseMarketHandler):
    """Handler para mercado Over/Under"""
    
    def get_market_type(self) -> str:
        return "Over/Under"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        # Calcular overround
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        return None

class HandlerAsianHandicap(BaseMarketHandler):
    """Handler para Asian Handicap"""
    
    def get_market_type(self) -> str:
        return "Asian Handicap"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        return None

class HandlerDoubleChance(BaseMarketHandler):
    """Handler para Double Chance"""
    
    def get_market_type(self) -> str:
        return "Double Chance"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        return None

# === NUEVOS HANDLERS PARA TENIS ===

class TennisMatchWinner(BaseMarketHandler):
    """
    Handler para Winner del partido (Tenis)
    Mercado: 1X2 pero con 2 resultados (Jugador1, Jugador2)
    """
    
    def get_market_type(self) -> str:
        return "Tennis Winner"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        # Tenis tiene 2 resultados principales
        if len(snapshot.odds_data) < 2:
            return opportunities
        
        # Calcular overround
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        """Calcula odds justas para tenis (2 resultados)"""
        if not self.validate_odds(snapshot.odds_data):
            return None
        
        # Estimación simple: basado en odds implícitos
        total_implied = sum(1.0 / odd for odd in snapshot.odds_data.values())
        if total_implied <= 0:
            return None
        
        fair_odds = {}
        for outcome, odd in snapshot.odds_data.items():
            # Ajustar para eliminar margen del bookmaker
            fair_prob = (1.0 / odd) / total_implied
            fair_odds[outcome] = 1.0 / fair_prob
        
        return fair_odds

class TennisSetHandicap(BaseMarketHandler):
    """
    Handler para Handicap en Sets (Tenis)
    Mercado: Handicap en sets (ej: -1.5, +1.5)
    """
    
    def get_market_type(self) -> str:
        return "Tennis Set Handicap"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        if len(snapshot.odds_data) < 2:
            return opportunities
        
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        return None

class TennisTotalGames(BaseMarketHandler):
    """
    Handler para Total de Games (Tenis)
    Mercado: Over/Under en games (ej: Over 22.5, Under 22.5)
    """
    
    def get_market_type(self) -> str:
        return "Tennis Total Games"
    
    def find_opportunities(self, snapshot: Snapshot) -> List[Opportunity]:
        opportunities = []
        
        if not self.validate_odds(snapshot.odds_data):
            return opportunities
        
        if len(snapshot.odds_data) < 2:
            return opportunities
        
        overround = sum(1.0 / odd for odd in snapshot.odds_data.values())
        
        if overround < 1.0:
            profit_percent = (1.0 / overround - 1.0) * 100
            
            stakes = {}
            for outcome, odd in snapshot.odds_data.items():
                stakes[outcome] = 1.0 / odd / overround
            
            opportunity = Opportunity(
                event_id=snapshot.event_id,
                market_type=self.get_market_type(),
                profit_percent=profit_percent,
                odds=snapshot.odds_data,
                stakes=stakes,
                source=snapshot.source,
                timestamp=snapshot.timestamp
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def calculate_fair_odds(self, snapshot: Snapshot) -> Optional[Dict[str, float]]:
        return None

class MarketHandlerFactory:
    """Fábrica de handlers de mercado"""
    
    _handlers = {
        "1X2": Handler1X2,
        "Over/Under": HandlerOverUnder,
        "Asian Handicap": HandlerAsianHandicap,
        "Double Chance": HandlerDoubleChance,
        # Nuevos handlers para Tenis
        "Tennis Winner": TennisMatchWinner,
        "Tennis Set Handicap": TennisSetHandicap,
        "Tennis Total Games": TennisTotalGames,
    }
    
    @classmethod
    def get_handler(cls, market_type: str) -> Optional[BaseMarketHandler]:
        """Retorna el handler para un mercado específico"""
        handler_class = cls._handlers.get(market_type)
        if handler_class:
            return handler_class()
        return None
    
    @classmethod
    def get_supported_markets(cls) -> List[str]:
        """Retorna lista de mercados soportados"""
        return list(cls._handlers.keys())
    
    @classmethod
    def register_handler(cls, market_type: str, handler_class):
        """Registra un nuevo handler (extensible)"""
        cls._handlers[market_type] = handler_class
        logger.info(f"Handler registrado: {market_type}")