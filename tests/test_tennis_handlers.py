"""
tests/test_tennis_handlers.py
Pruebas para handlers de Tenis
Versión: 0.3.1
"""

import pytest
from datetime import datetime

from src.domain.entities import Snapshot
from src.core.market_handlers import (
    TennisMatchWinner,
    TennisSetHandicap,
    TennisTotalGames,
    MarketHandlerFactory
)

class TestTennisHandlers:
    """Pruebas para los handlers de Tenis"""
    
    def test_tennis_winner_handler(self):
        """Verifica handler de Winner de Tenis"""
        snapshot = Snapshot(
            event_id="tennis_001",
            event_name="Nadal vs Djokovic",
            market_type="Tennis Winner",
            bookmaker="Bet365",
            odds_data={"Nadal": 1.85, "Djokovic": 2.10},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = TennisMatchWinner()
        assert handler.get_market_type() == "Tennis Winner"
        
        opportunities = handler.find_opportunities(snapshot)
        # Con overround > 1, no debería haber oportunidades
        assert len(opportunities) == 0
    
    def test_tennis_winner_arbitrage(self):
        """Verifica arbitraje en Winner de Tenis"""
        snapshot = Snapshot(
            event_id="tennis_001",
            event_name="Nadal vs Djokovic",
            market_type="Tennis Winner",
            bookmaker="Test",
            odds_data={"Nadal": 2.10, "Djokovic": 2.10},  # Overround < 1
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = TennisMatchWinner()
        opportunities = handler.find_opportunities(snapshot)
        
        assert len(opportunities) == 1
        assert opportunities[0].profit_percent > 0
        assert len(opportunities[0].stakes) == 2
    
    def test_tennis_set_handicap_handler(self):
        """Verifica handler de Set Handicap"""
        snapshot = Snapshot(
            event_id="tennis_001",
            event_name="Nadal vs Djokovic",
            market_type="Tennis Set Handicap",
            bookmaker="Bet365",
            odds_data={"Nadal -1.5": 2.20, "Djokovic +1.5": 1.75},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = TennisSetHandicap()
        assert handler.get_market_type() == "Tennis Set Handicap"
        
        opportunities = handler.find_opportunities(snapshot)
        assert len(opportunities) == 0  # Overround > 1
    
    def test_tennis_total_games_handler(self):
        """Verifica handler de Total Games"""
        snapshot = Snapshot(
            event_id="tennis_001",
            event_name="Nadal vs Djokovic",
            market_type="Tennis Total Games",
            bookmaker="Bet365",
            odds_data={"Over 22.5": 1.90, "Under 22.5": 1.95},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = TennisTotalGames()
        assert handler.get_market_type() == "Tennis Total Games"
        
        opportunities = handler.find_opportunities(snapshot)
        assert len(opportunities) == 0
    
    def test_market_handler_factory(self):
        """Verifica que la fábrica registra los handlers de Tenis"""
        supported = MarketHandlerFactory.get_supported_markets()
        
        assert "Tennis Winner" in supported
        assert "Tennis Set Handicap" in supported
        assert "Tennis Total Games" in supported
        
        handler = MarketHandlerFactory.get_handler("Tennis Winner")
        assert handler is not None
        assert isinstance(handler, TennisMatchWinner)
    
    def test_tennis_fair_odds(self):
        """Verifica cálculo de fair odds para Tenis"""
        snapshot = Snapshot(
            event_id="tennis_001",
            event_name="Nadal vs Djokovic",
            market_type="Tennis Winner",
            bookmaker="Test",
            odds_data={"Nadal": 1.85, "Djokovic": 2.10},
            timestamp=datetime.now(),
            source="test"
        )
        
        handler = TennisMatchWinner()
        fair_odds = handler.calculate_fair_odds(snapshot)
        
        assert fair_odds is not None
        assert len(fair_odds) == 2
        # Los fair odds deben ser mayores que los odds del bookmaker
        assert fair_odds["Nadal"] > 1.85
        assert fair_odds["Djokovic"] > 2.10