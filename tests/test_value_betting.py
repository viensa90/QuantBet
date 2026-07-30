"""
Tests para ValueBetDetector.
"""

import pytest
from datetime import datetime
from src.domain.entities import Snapshot
from src.core.value_betting import ValueBetDetector


class TestValueBetDetector:
    
    @pytest.fixture
    def detector(self):
        return ValueBetDetector(margin=0.05)
    
    @pytest.fixture
    def snapshots(self):
        return [
            Snapshot("S001", "EVT-001", "1X2", "Local", 2.50, "Bet365", datetime.now()),
            Snapshot("S002", "EVT-001", "1X2", "Empate", 3.00, "WilliamHill", datetime.now()),
            Snapshot("S003", "EVT-001", "1X2", "Visitante", 2.80, "Betfair", datetime.now()),
        ]
    
    def test_detect_value_bet(self, detector, snapshots):
        """Detecta value bet cuando la probabilidad justa es mayor que la implícita."""
        fair_probs = {"Local": 0.45, "Empate": 0.30, "Visitante": 0.25}
        value_bets = detector.detect("EVT-001", snapshots, fair_probs)
        # Local: cuota 2.50 -> prob implícita 0.40, justa 0.45 -> hay valor
        assert len(value_bets) > 0
        local_bet = next((b for b in value_bets if b["selection"] == "Local"), None)
        assert local_bet is not None
        assert local_bet["value_percentage"] > 0
    
    def test_no_value_bet(self, detector, snapshots):
        """No detecta value bet si no hay diferencia suficiente."""
        fair_probs = {"Local": 0.35, "Empate": 0.33, "Visitante": 0.32}
        value_bets = detector.detect("EVT-001", snapshots, fair_probs)
        assert len(value_bets) == 0
    
    def test_missing_selection(self, detector, snapshots):
        """Maneja selecciones no presentes en los snapshots."""
        fair_probs = {"Local": 0.45, "EquipoD": 0.55}
        value_bets = detector.detect("EVT-001", snapshots, fair_probs)
        assert len(value_bets) == 1  # Solo Local