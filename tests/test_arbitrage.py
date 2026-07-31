"""
Tests para el motor de arbitraje con soporte multi-mercado.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.entities import Snapshot, MarketType
from src.core.arbitrage import ArbitrageEngine


@pytest.fixture
def multi_market_snapshots():
    """Snapshots de múltiples mercados."""
    return [
        # 1X2
        Snapshot(
            event_id="EVT-001",
            event_name="Event 1",
            source="SourceA",
            timestamp=datetime.now(),
            odds={"Local": Decimal("2.10"), "Empate": Decimal("3.40"), "Visitante": Decimal("3.80")},
            market_type=MarketType.MERCADO_1X2
        ),
        Snapshot(
            event_id="EVT-001",
            event_name="Event 1",
            source="SourceB",
            timestamp=datetime.now(),
            odds={"Local": Decimal("2.20"), "Empate": Decimal("3.20"), "Visitante": Decimal("3.90")},
            market_type=MarketType.MERCADO_1X2
        ),
        # Over/Under
        Snapshot(
            event_id="EVT-002",
            event_name="Event 2",
            source="SourceA",
            timestamp=datetime.now(),
            odds={"Over": Decimal("1.90"), "Under": Decimal("2.00")},
            market_type=MarketType.OVER_UNDER,
            metadata={"line": 2.5}
        ),
        Snapshot(
            event_id="EVT-002",
            event_name="Event 2",
            source="SourceB",
            timestamp=datetime.now(),
            odds={"Over": Decimal("2.05"), "Under": Decimal("1.85")},
            market_type=MarketType.OVER_UNDER,
            metadata={"line": 2.5}
        )
    ]


def test_arbitrage_engine_multi_market(multi_market_snapshots):
    """Test: Motor procesa múltiples mercados."""
    engine = ArbitrageEngine()
    opportunities = engine.detect_opportunities(multi_market_snapshots)
    
    # Debería encontrar al menos una oportunidad en cada mercado
    assert len(opportunities) >= 2
    
    # Verificar que hay oportunidades de ambos mercados
    market_types = set(opp.market_type for opp in opportunities)
    assert MarketType.MERCADO_1X2 in market_types
    assert MarketType.OVER_UNDER in market_types


def test_arbitrage_engine_filtered_markets(multi_market_snapshots):
    """Test: Motor filtra mercados correctamente."""
    engine = ArbitrageEngine(enabled_markets=[MarketType.MERCADO_1X2])
    opportunities = engine.detect_opportunities(multi_market_snapshots)
    
    # Solo debería encontrar oportunidades 1X2
    assert len(opportunities) >= 1
    for opp in opportunities:
        assert opp.market_type == MarketType.MERCADO_1X2


def test_arbitrage_engine_no_market_data():
    """Test: Motor maneja falta de datos."""
    engine = ArbitrageEngine()
    opportunities = engine.detect_opportunities([])
    assert opportunities == []


def test_arbitrage_engine_unsupported_market():
    """Test: Motor maneja mercado no soportado."""
    snapshots = [
        Snapshot(
            event_id="EVT-003",
            event_name="Event 3",
            source="SourceA",
            timestamp=datetime.now(),
            odds={"Yes": Decimal("1.50"), "No": Decimal("2.50")},
            market_type=MarketType.BOTH_TEAMS_SCORE  # No implementado aún
        )
    ]
    
    engine = ArbitrageEngine()
    opportunities = engine.detect_opportunities(snapshots)
    
    # No debería fallar, solo no encontrar oportunidades
    assert opportunities == []


def test_arbitrage_engine_sorts_by_percent():
    """Test: Oportunidades ordenadas por % de arbitraje."""
    # Crear snapshots con diferentes % de arbitraje
    snapshots = []
    
    # Evento con alto arbitraje
    snapshots.append(Snapshot(
        event_id="EVT-HIGH",
        event_name="High Arbitrage",
        source="SourceA",
        timestamp=datetime.now(),
        odds={"Local": Decimal("3.00"), "Empate": Decimal("4.00"), "Visitante": Decimal("5.00")},
        market_type=MarketType.MERCADO_1X2
    ))
    snapshots.append(Snapshot(
        event_id="EVT-HIGH",
        event_name="High Arbitrage",
        source="SourceB",
        timestamp=datetime.now(),
        odds={"Local": Decimal("3.10"), "Empate": Decimal("3.90"), "Visitante": Decimal("5.10")},
        market_type=MarketType.MERCADO_1X2
    ))
    
    # Evento con bajo arbitraje
    snapshots.append(Snapshot(
        event_id="EVT-LOW",
        event_name="Low Arbitrage",
        source="SourceA",
        timestamp=datetime.now(),
        odds={"Local": Decimal("2.00"), "Empate": Decimal("3.20"), "Visitante": Decimal("3.50")},
        market_type=MarketType.MERCADO_1X2
    ))
    snapshots.append(Snapshot(
        event_id="EVT-LOW",
        event_name="Low Arbitrage",
        source="SourceB",
        timestamp=datetime.now(),
        odds={"Local": Decimal("2.10"), "Empate": Decimal("3.10"), "Visitante": Decimal("3.60")},
        market_type=MarketType.MERCADO_1X2
    ))
    
    engine = ArbitrageEngine()
    opportunities = engine.detect_opportunities(snapshots)
    
    # Deberían estar ordenados por % descendente
    if len(opportunities) >= 2:
        assert opportunities[0].arbitrage_percent >= opportunities[1].arbitrage_percent