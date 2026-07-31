"""
Tests para handlers de mercado.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.entities import Snapshot, MarketType, Opportunity
from src.core.market_handlers import (
    MarketHandler1X2,
    MarketHandlerOverUnder,
    MarketHandlerAsianHandicap,
    MarketHandlerDoubleChance,
    MarketHandlerFactory
)


@pytest.fixture
def snapshots_1x2():
    return [
        Snapshot(
            event_id="EVT-001",
            event_name="Test Event",
            source="BookmakerA",
            timestamp=datetime.now(),
            odds={"Local": Decimal("2.10"), "Empate": Decimal("3.40"), "Visitante": Decimal("3.80")},
            market_type=MarketType.MERCADO_1X2
        ),
        Snapshot(
            event_id="EVT-001",
            event_name="Test Event",
            source="BookmakerB",
            timestamp=datetime.now(),
            odds={"Local": Decimal("2.20"), "Empate": Decimal("3.20"), "Visitante": Decimal("3.90")},
            market_type=MarketType.MERCADO_1X2
        )
    ]


@pytest.fixture
def snapshots_over_under():
    return [
        Snapshot(
            event_id="EVT-002",
            event_name="Test Event 2",
            source="BookmakerA",
            timestamp=datetime.now(),
            odds={"Over": Decimal("1.90"), "Under": Decimal("2.00")},
            market_type=MarketType.OVER_UNDER,
            metadata={"line": 2.5}
        ),
        Snapshot(
            event_id="EVT-002",
            event_name="Test Event 2",
            source="BookmakerB",
            timestamp=datetime.now(),
            odds={"Over": Decimal("2.05"), "Under": Decimal("1.85")},
            market_type=MarketType.OVER_UNDER,
            metadata={"line": 2.5}
        )
    ]


def test_handler_1x2_detect(snapshots_1x2):
    """Test: Handler 1X2 detecta oportunidades correctamente."""
    handler = MarketHandler1X2()
    opportunities = handler.detect_opportunities(snapshots_1x2)
    
    assert len(opportunities) == 1
    opp = opportunities[0]
    assert opp.event_id == "EVT-001"
    assert opp.market_type == MarketType.MERCADO_1X2
    assert opp.arbitrage_percent > 0
    assert opp.odds_used["Local"] == Decimal("2.20")
    assert opp.odds_used["Visitante"] == Decimal("3.90")


def test_handler_over_under_detect(snapshots_over_under):
    """Test: Handler Over/Under detecta oportunidades correctamente."""
    handler = MarketHandlerOverUnder()
    opportunities = handler.detect_opportunities(snapshots_over_under)
    
    assert len(opportunities) == 1
    opp = opportunities[0]
    assert opp.event_id == "EVT-002"
    assert opp.market_type == MarketType.OVER_UNDER
    assert opp.arbitrage_percent > 0
    assert opp.metadata["line"] == 2.5


def test_handler_asian_handicap():
    """Test: Handler Asian Handicap funciona correctamente."""
    snapshots = [
        Snapshot(
            event_id="EVT-003",
            event_name="Test Event 3",
            source="BookmakerA",
            timestamp=datetime.now(),
            odds={"Local": Decimal("1.80"), "Visitante": Decimal("2.10")},
            market_type=MarketType.ASIAN_HANDICAP,
            metadata={"handicap": -0.5}
        ),
        Snapshot(
            event_id="EVT-003",
            event_name="Test Event 3",
            source="BookmakerB",
            timestamp=datetime.now(),
            odds={"Local": Decimal("1.85"), "Visitante": Decimal("2.05")},
            market_type=MarketType.ASIAN_HANDICAP,
            metadata={"handicap": -0.5}
        )
    ]
    
    handler = MarketHandlerAsianHandicap()
    opportunities = handler.detect_opportunities(snapshots)
    
    assert len(opportunities) >= 1


def test_handler_double_chance():
    """Test: Handler Double Chance funciona correctamente."""
    snapshots = [
        Snapshot(
            event_id="EVT-004",
            event_name="Test Event 4",
            source="BookmakerA",
            timestamp=datetime.now(),
            odds={"1X": Decimal("1.20"), "X2": Decimal("1.80"), "12": Decimal("1.40")},
            market_type=MarketType.DOUBLE_CHANCE
        ),
        Snapshot(
            event_id="EVT-004",
            event_name="Test Event 4",
            source="BookmakerB",
            timestamp=datetime.now(),
            odds={"1X": Decimal("1.25"), "X2": Decimal("1.75"), "12": Decimal("1.45")},
            market_type=MarketType.DOUBLE_CHANCE
        )
    ]
    
    handler = MarketHandlerDoubleChance()
    opportunities = handler.detect_opportunities(snapshots)
    
    assert len(opportunities) >= 1


def test_market_handler_factory():
    """Test: Fábrica de handlers retorna handlers correctos."""
    handler_1x2 = MarketHandlerFactory.get_handler(MarketType.MERCADO_1X2)
    assert isinstance(handler_1x2, MarketHandler1X2)
    
    handler_ou = MarketHandlerFactory.get_handler(MarketType.OVER_UNDER)
    assert isinstance(handler_ou, MarketHandlerOverUnder)
    
    markets = MarketHandlerFactory.get_supported_markets()
    assert MarketType.MERCADO_1X2 in markets
    assert MarketType.OVER_UNDER in markets
    assert MarketType.ASIAN_HANDICAP in markets
    assert MarketType.DOUBLE_CHANCE in markets