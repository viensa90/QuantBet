"""
Pruebas unitarias para el Motor de Arbitraje.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime, timezone
from src.domain.entities import (
    Bookmaker, BookmakerType, Sport, SportType, Competition,
    Event, EventStatus, Participant, Market, Outcome, Snapshot
)
from src.core.arbitrage import ArbitrageEngine

# --- Fixtures para crear entidades de prueba ---

@pytest.fixture
def bookmaker_a():
    return Bookmaker(id="bk_a", name="Bookmaker A", type=BookmakerType.SIMULATED)

@pytest.fixture
def bookmaker_b():
    return Bookmaker(id="bk_b", name="Bookmaker B", type=BookmakerType.SIMULATED)

@pytest.fixture
def sample_market():
    return Market(id="mkt_001", event_id="evt_001", type="1X2")

@pytest.fixture
def snapshot_arbitrage(bookmaker_a, bookmaker_b, sample_market):
    """Crea dos snapshots que juntos forman un arbitraje claro."""
    now = datetime.now(timezone.utc)
    snap1 = Snapshot(
        bookmaker=bookmaker_a,
        market=sample_market,
        timestamp_utc=now,
        odds={"1": 2.10, "X": 3.50, "2": 3.00}
    )
    snap2 = Snapshot(
        bookmaker=bookmaker_b,
        market=sample_market,
        timestamp_utc=now,
        odds={"1": 2.00, "X": 3.30, "2": 4.50}  # Mejor cuota en "2"
    )
    return [snap1, snap2]

@pytest.fixture
def snapshot_no_arbitrage(bookmaker_a, bookmaker_b, sample_market):
    """Crea dos snapshots que NO forman arbitraje (overround > 1)."""
    now = datetime.now(timezone.utc)
    snap1 = Snapshot(
        bookmaker=bookmaker_a,
        market=sample_market,
        timestamp_utc=now,
        odds={"1": 1.90, "X": 3.20, "2": 3.80}
    )
    snap2 = Snapshot(
        bookmaker=bookmaker_b,
        market=sample_market,
        timestamp_utc=now,
        odds={"1": 1.85, "X": 3.10, "2": 3.70}
    )
    return [snap1, snap2]

# --- Tests ---

def test_arbitrage_detected(snapshot_arbitrage):
    """Debe detectar arbitraje cuando el overround < 1."""
    engine = ArbitrageEngine(max_overround=0.999)
    result = engine.analyze(snapshot_arbitrage)
    
    assert result is not None, "Debería detectar arbitraje"
    assert result['roi_percent'] > 0, "ROI debería ser positivo"
    assert result['overround'] < 1.0, "Overround debería ser menor a 1"
    assert len(result['stake_distribution']) == 3, "Debería haber distribución para 3 outcomes"

def test_no_arbitrage(snapshot_no_arbitrage):
    """NO debe detectar arbitraje cuando el overround >= 1."""
    engine = ArbitrageEngine(max_overround=0.999)
    result = engine.analyze(snapshot_no_arbitrage)
    
    assert result is None, "No debería detectar arbitraje"

def test_empty_snapshots():
    """Debe manejar lista vacía sin errores."""
    engine = ArbitrageEngine()
    result = engine.analyze([])
    assert result is None

def test_single_snapshot(snapshot_arbitrage):
    """Con un solo snapshot no puede haber arbitraje."""
    engine = ArbitrageEngine()
    result = engine.analyze([snapshot_arbitrage[0]])
    assert result is None, "Un solo snapshot no puede generar arbitraje"

def test_snapshot_validation():
    """No debe permitir cuotas negativas."""
    from src.domain.entities import Bookmaker, BookmakerType, Market, Snapshot
    from datetime import datetime, timezone
    
    with pytest.raises(ValueError):
        Snapshot(
            bookmaker=Bookmaker(id="x", name="X", type=BookmakerType.SIMULATED),
            market=Market(id="y", event_id="z", type="1X2"),
            timestamp_utc=datetime.now(timezone.utc),
            odds={"1": -1.0}  # Cuota inválida
        )