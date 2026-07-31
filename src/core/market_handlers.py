"""
Handlers específicos para cada tipo de mercado.
Cada handler sabe cómo extraer oportunidades de su mercado.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Dict, Optional, Tuple, Any
from itertools import combinations

from src.domain.entities import Snapshot, Opportunity, MarketType


class MarketHandler(ABC):
    """Base para handlers de mercado."""
    
    @abstractmethod
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        """Detecta oportunidades de arbitraje en este mercado."""
        pass
    
    @abstractmethod
    def get_required_outcomes(self) -> List[str]:
        """Retorna los resultados requeridos para este mercado."""
        pass


class MarketHandler1X2(MarketHandler):
    """Handler para mercado 1X2."""
    
    def get_required_outcomes(self) -> List[str]:
        return ["Local", "Empate", "Visitante"]
    
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        opportunities = []
        
        # Agrupar por evento
        events = {}
        for s in snapshots:
            if s.market_type != MarketType.MERCADO_1X2:
                continue
            if s.event_id not in events:
                events[s.event_id] = []
            events[s.event_id].append(s)
        
        # Para cada evento, buscar mejores cuotas por resultado
        for event_id, event_snapshots in events.items():
            best_odds = {}
            sources_used = {}
            
            for outcome in self.get_required_outcomes():
                best_odds[outcome] = Decimal('0')
                sources_used[outcome] = None
                
                for snapshot in event_snapshots:
                    if outcome in snapshot.odds:
                        odds = snapshot.odds[outcome]
                        if odds > best_odds[outcome]:
                            best_odds[outcome] = odds
                            sources_used[outcome] = snapshot.source
            
            # Verificar que tenemos todos los outcomes
            if all(odds > 0 for odds in best_odds.values()):
                # Calcular arbitraje
                total_inv = sum(Decimal(1) / odds for odds in best_odds.values())
                arbitrage_percent = float((Decimal(1) / total_inv - 1) * 100)
                
                if arbitrage_percent > 0:
                    stakes = {outcome: Decimal(1) / odds for outcome, odds in best_odds.items()}
                    total_stake = sum(stakes.values())
                    
                    opportunity = Opportunity(
                        event_id=event_id,
                        event_name=event_snapshots[0].event_name if event_snapshots else event_id,
                        source="MULTI_SOURCE",
                        market_type=MarketType.MERCADO_1X2,
                        arbitrage_percent=arbitrage_percent,
                        total_stake=total_stake,
                        stakes=stakes,
                        odds_used=best_odds,
                        timestamp=event_snapshots[0].timestamp
                    )
                    opportunities.append(opportunity)
        
        return opportunities


class MarketHandlerOverUnder(MarketHandler):
    """Handler para mercado Over/Under."""
    
    def get_required_outcomes(self) -> List[str]:
        return ["Over", "Under"]
    
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        opportunities = []
        
        # Agrupar por evento y línea
        events_lines = {}
        for s in snapshots:
            if s.market_type != MarketType.OVER_UNDER:
                continue
            
            line = s.metadata.get('line', 2.5)  # Línea por defecto 2.5
            key = (s.event_id, line)
            
            if key not in events_lines:
                events_lines[key] = []
            events_lines[key].append(s)
        
        # Para cada evento-línea, buscar mejores cuotas
        for (event_id, line), event_snapshots in events_lines.items():
            best_odds = {}
            sources_used = {}
            
            for outcome in self.get_required_outcomes():
                best_odds[outcome] = Decimal('0')
                sources_used[outcome] = None
                
                for snapshot in event_snapshots:
                    if outcome in snapshot.odds:
                        odds = snapshot.odds[outcome]
                        if odds > best_odds[outcome]:
                            best_odds[outcome] = odds
                            sources_used[outcome] = snapshot.source
            
            if all(odds > 0 for odds in best_odds.values()):
                total_inv = sum(Decimal(1) / odds for odds in best_odds.values())
                arbitrage_percent = float((Decimal(1) / total_inv - 1) * 100)
                
                if arbitrage_percent > 0:
                    stakes = {outcome: Decimal(1) / odds for outcome, odds in best_odds.items()}
                    total_stake = sum(stakes.values())
                    
                    opportunity = Opportunity(
                        event_id=event_id,
                        event_name=event_snapshots[0].event_name if event_snapshots else event_id,
                        source="MULTI_SOURCE",
                        market_type=MarketType.OVER_UNDER,
                        arbitrage_percent=arbitrage_percent,
                        total_stake=total_stake,
                        stakes=stakes,
                        odds_used=best_odds,
                        timestamp=event_snapshots[0].timestamp,
                        metadata={"line": line}
                    )
                    opportunities.append(opportunity)
        
        return opportunities


class MarketHandlerAsianHandicap(MarketHandler):
    """Handler para mercado Asian Handicap."""
    
    def get_required_outcomes(self) -> List[str]:
        return ["Local", "Visitante"]
    
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        opportunities = []
        
        # Agrupar por evento y línea de handicap
        events_lines = {}
        for s in snapshots:
            if s.market_type != MarketType.ASIAN_HANDICAP:
                continue
            
            line = s.metadata.get('handicap', 0.0)  # Handicap por defecto 0
            key = (s.event_id, line)
            
            if key not in events_lines:
                events_lines[key] = []
            events_lines[key].append(s)
        
        # Para cada evento-línea, buscar mejores cuotas
        for (event_id, handicap), event_snapshots in events_lines.items():
            best_odds = {}
            sources_used = {}
            
            for outcome in self.get_required_outcomes():
                best_odds[outcome] = Decimal('0')
                sources_used[outcome] = None
                
                for snapshot in event_snapshots:
                    if outcome in snapshot.odds:
                        odds = snapshot.odds[outcome]
                        if odds > best_odds[outcome]:
                            best_odds[outcome] = odds
                            sources_used[outcome] = snapshot.source
            
            if all(odds > 0 for odds in best_odds.values()):
                total_inv = sum(Decimal(1) / odds for odds in best_odds.values())
                arbitrage_percent = float((Decimal(1) / total_inv - 1) * 100)
                
                if arbitrage_percent > 0:
                    stakes = {outcome: Decimal(1) / odds for outcome, odds in best_odds.items()}
                    total_stake = sum(stakes.values())
                    
                    opportunity = Opportunity(
                        event_id=event_id,
                        event_name=event_snapshots[0].event_name if event_snapshots else event_id,
                        source="MULTI_SOURCE",
                        market_type=MarketType.ASIAN_HANDICAP,
                        arbitrage_percent=arbitrage_percent,
                        total_stake=total_stake,
                        stakes=stakes,
                        odds_used=best_odds,
                        timestamp=event_snapshots[0].timestamp,
                        metadata={"handicap": handicap}
                    )
                    opportunities.append(opportunity)
        
        return opportunities


class MarketHandlerDoubleChance(MarketHandler):
    """Handler para mercado Doble Oportunidad."""
    
    def get_required_outcomes(self) -> List[str]:
        return ["1X", "X2", "12"]  # Local o Empate, Empate o Visitante, Local o Visitante
    
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        opportunities = []
        
        # Agrupar por evento
        events = {}
        for s in snapshots:
            if s.market_type != MarketType.DOUBLE_CHANCE:
                continue
            if s.event_id not in events:
                events[s.event_id] = []
            events[s.event_id].append(s)
        
        for event_id, event_snapshots in events.items():
            best_odds = {}
            sources_used = {}
            
            for outcome in self.get_required_outcomes():
                best_odds[outcome] = Decimal('0')
                sources_used[outcome] = None
                
                for snapshot in event_snapshots:
                    if outcome in snapshot.odds:
                        odds = snapshot.odds[outcome]
                        if odds > best_odds[outcome]:
                            best_odds[outcome] = odds
                            sources_used[outcome] = snapshot.source
            
            if all(odds > 0 for odds in best_odds.values()):
                total_inv = sum(Decimal(1) / odds for odds in best_odds.values())
                arbitrage_percent = float((Decimal(1) / total_inv - 1) * 100)
                
                if arbitrage_percent > 0:
                    stakes = {outcome: Decimal(1) / odds for outcome, odds in best_odds.items()}
                    total_stake = sum(stakes.values())
                    
                    opportunity = Opportunity(
                        event_id=event_id,
                        event_name=event_snapshots[0].event_name if event_snapshots else event_id,
                        source="MULTI_SOURCE",
                        market_type=MarketType.DOUBLE_CHANCE,
                        arbitrage_percent=arbitrage_percent,
                        total_stake=total_stake,
                        stakes=stakes,
                        odds_used=best_odds,
                        timestamp=event_snapshots[0].timestamp
                    )
                    opportunities.append(opportunity)
        
        return opportunities


class MarketHandlerFactory:
    """Fábrica de handlers de mercado."""
    
    _handlers = {
        MarketType.MERCADO_1X2: MarketHandler1X2,
        MarketType.OVER_UNDER: MarketHandlerOverUnder,
        MarketType.ASIAN_HANDICAP: MarketHandlerAsianHandicap,
        MarketType.DOUBLE_CHANCE: MarketHandlerDoubleChance,
    }
    
    @classmethod
    def get_handler(cls, market_type: MarketType) -> MarketHandler:
        """Retorna el handler para el tipo de mercado."""
        handler_class = cls._handlers.get(market_type)
        if not handler_class:
            raise ValueError(f"No hay handler para {market_type}")
        return handler_class()
    
    @classmethod
    def get_supported_markets(cls) -> List[MarketType]:
        """Retorna lista de mercados soportados."""
        return list(cls._handlers.keys())