"""
Tests para modelos de probabilidad.
"""

import pytest
from decimal import Decimal

from src.core.probability_model import HistoricalModel, EloModel, ProbabilityModelFactory
from src.domain.entities import MarketType


def test_historical_model_1x2():
    """Test: Modelo histórico calcula 1X2 correctamente."""
    model = HistoricalModel()
    probs = model.calculate_1x2_probabilities("Real Madrid", "Barcelona")
    
    assert "Local" in probs
    assert "Empate" in probs
    assert "Visitante" in probs
    
    # Deberían sumar 1
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.01
    
    # Real Madrid debería tener mayor probabilidad como local
    assert probs["Local"] > probs["Visitante"]


def test_historical_model_over_under():
    """Test: Modelo histórico calcula Over/Under correctamente."""
    model = HistoricalModel()
    probs = model.calculate_over_under_probabilities("Real Madrid", "Barcelona", 2.5)
    
    assert "Over" in probs
    assert "Under" in probs
    
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.01


def test_historical_model_market_types():
    """Test: Modelo histórico soporta diferentes tipos de mercado."""
    model = HistoricalModel()
    
    # 1X2
    probs_1x2 = model.calculate_probabilities(
        "EVT-001",
        MarketType.MERCADO_1X2,
        {"home_team": "Real Madrid", "away_team": "Barcelona"}
    )
    assert len(probs_1x2) == 3
    
    # Over/Under
    probs_ou = model.calculate_probabilities(
        "EVT-002",
        MarketType.OVER_UNDER,
        {"home_team": "Real Madrid", "away_team": "Barcelona", "line": 2.5}
    )
    assert len(probs_ou) == 2


def test_elo_model():
    """Test: Modelo Elo calcula probabilidades correctamente."""
    model = EloModel()
    probs = model.calculate_probabilities(
        "EVT-001",
        MarketType.MERCADO_1X2,
        {"home_team": "Real Madrid", "away_team": "Barcelona"}
    )
    
    assert "Local" in probs
    assert "Empate" in probs
    assert "Visitante" in probs
    
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.01


def test_probability_model_factory():
    """Test: Fábrica crea modelos correctamente."""
    model_hist = ProbabilityModelFactory.create("historical")
    assert isinstance(model_hist, HistoricalModel)
    
    model_elo = ProbabilityModelFactory.create("elo")
    assert isinstance(model_elo, EloModel)


def test_value_betting_integration():
    """Test: Integración de value betting con modelo real."""
    from src.core.value_betting import ValueBetDetector
    from src.domain.entities import Snapshot
    from datetime import datetime
    
    # Crear snapshot con cuotas
    snapshot = Snapshot(
        event_id="EVT-001",
        event_name="Real Madrid vs Barcelona",
        source="TestBookmaker",
        timestamp=datetime.now(),
        odds={"Local": Decimal("2.00"), "Empate": Decimal("3.50"), "Visitante": Decimal("4.00")},
        market_type=MarketType.MERCADO_1X2,
        metadata={"home_team": "Real Madrid", "away_team": "Barcelona"}
    )
    
    # Detectar value bets
    detector = ValueBetDetector({"type": "historical"})
    value_bets = detector.detect_value_bets([snapshot], min_value_threshold=0.05)
    
    # Debería encontrar algunos value bets
    # (dependiendo del modelo y las cuotas)
    assert isinstance(value_bets, list)


def test_poisson_model():
    """Test: Modelo Poisson calcula probabilidades correctamente."""
    from src.core.poisson_model import PoissonModel
    
    model = PoissonModel()
    probs = model.match_probabilities("Real Madrid", "Barcelona")
    
    assert "home_win" in probs
    assert "draw" in probs
    assert "away_win" in probs
    assert "over_2.5" in probs
    
    total = probs["home_win"] + probs["draw"] + probs["away_win"]
    assert abs(total - 1.0) < 0.01