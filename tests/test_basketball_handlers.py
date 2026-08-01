"""
tests/test_basketball_handlers.py
Pruebas para handlers de Baloncesto
Versión: 0.3.1
"""

import pytest
from datetime import datetime

from src.domain.entities import Snapshot
from src.core.market_handlers import (
    BasketballMoneyline,
    BasketballSpread,
    BasketballTotalPoints,
    BasketballQuarterWinner,
    MarketHandlerFactory
)

class TestBasketballHandlers:
    """Pruebas para los handlers de Baloncesto"""
    
    def test_basketball_moneyline_handler(self):
        """Verifica handler de Moneyline de Baloncesto"""
        snapshot = Snapshot(
            event_id="bball_001",
            event_name="Lakers vs Celtics",
            market_type="Basketball Moneyline",
            bookmaker="Bet365",
            odds_data={"Lakers": 1.80, "Celtics": 2.10},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = BasketballMoneyline()
        assert handler.get_market_type() == "Basketball Moneyline"
        
        opportunities = handler.find_opportunities(snapshot)
        # Con overround > 1, no debería haber oportunidades
        assert len(opportunities) == 0
    
    def test_basketball_moneyline_arbitrage(self):
        """Verifica arbitraje en Moneyline de Baloncesto"""
        snapshot = Snapshot(
            event_id="bball_001",
            event_name="Lakers vs Celtics",
            market_type="Basketball Moneyline",
            bookmaker="Test",
            odds_data={"Lakers": 2.10, "Celtics": 2.10},  # Overround < 1
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = BasketballMoneyline()
        opportunities = handler.find_opportunities(snapshot)
        
        assert len(opportunities) == 1
        assert opportunities[0].profit_percent > 0
        assert len(opportunities[0].stakes) == 2
    
    def test_basketball_spread_handler(self):
        """Verifica handler de Spread de Baloncesto"""
        snapshot = Snapshot(
            event_id="bball_001",
            event_name="Lakers vs Celtics",
            market_type="Basketball Spread",
            bookmaker="Bet365",
            odds_data={"Lakers -5.5": 1.90, "Celtics +5.5": 1.95},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = BasketballSpread()
        assert handler.get_market_type() == "Basketball Spread"
        
        opportunities = handler.find_opportunities(snapshot)
        assert len(opportunities) == 0  # Overround > 1
    
    def test_basketball_total_points_handler(self):
        """Verifica handler de Total Points de Baloncesto"""
        snapshot = Snapshot(
            event_id="bball_001",
            event_name="Lakers vs Celtics",
            market_type="Basketball Total Points",
            bookmaker="Bet365",
            odds_data={"Over 210.5": 1.85, "Under 210.5": 2.00},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = BasketballTotalPoints()
        assert handler.get_market_type() == "Basketball Total Points"
        
        opportunities = handler.find_opportunities(snapshot)
        assert len(opportunities) == 0
    
    def test_basketball_quarter_winner_handler(self):
        """Verifica handler de Ganador del Cuarto de Baloncesto"""
        snapshot = Snapshot(
            event_id="bball_001",
            event_name="Lakers vs Celtics",
            market_type="Basketball Quarter Winner",
            bookmaker="Bet365",
            odds_data={"Lakers": 1.95, "Celtics": 2.05, "Draw": 15.00},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = BasketballQuarterWinner()
        assert handler.get_market_type() == "Basketball Quarter Winner"
        
        opportunities = handler.find_opportunities(snapshot)
        assert len(opportunities) == 0
    
    def test_market_handler_factory(self):
        """Verifica que la fábrica registra los handlers de Baloncesto"""
        supported = MarketHandlerFactory.get_supported_markets()
        
        assert "Basketball Moneyline" in supported
        assert "Basketball Spread" in supported
        assert "Basketball Total Points" in supported
        assert "Basketball Quarter Winner" in supported
        
        handler = MarketHandlerFactory.get_handler("Basketball Moneyline")
        assert handler is not None
        assert isinstance(handler, BasketballMoneyline)
    
    def test_basketball_fair_odds(self):
        """Verifica cálculo de fair odds para Baloncesto"""
        snapshot = Snapshot(
            event_id="bball_001",
            event_name="Lakers vs Celtics",
            market_type="Basketball Moneyline",
            bookmaker="Test",
            odds_data={"Lakers": 1.80, "Celtics": 2.10},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = BasketballMoneyline()
        fair_odds = handler.calculate_fair_odds(snapshot)
        
        assert fair_odds is not None
        assert len(fair_odds) == 2
        # Los fair odds deben ser mayores que los odds del bookmaker
        assert fair_odds["Lakers"] > 1.80
        assert fair_odds["Celtics"] > 2.10