"""
Tests para BankrollManager.
"""

import pytest
from datetime import datetime
from src.core.bankroll import BankrollManager
from src.domain.entities import Opportunity


class TestBankrollManager:
    """Tests para el gestor de bankroll."""
    
    @pytest.fixture
    def bankroll(self):
        """Fixture: Bankroll con $1000 y 10% exposición."""
        return BankrollManager(total_bankroll=1000.0, max_exposure=0.10)
    
    @pytest.fixture
    def opportunity(self):
        """Fixture: Oportunidad de 3 outcomes."""
        return Opportunity(
            opportunity_id="OPP-001",
            event_id="EVT-001",
            market="1X2",
            outcomes={
                "Local": ("Bet365", 2.10),
                "Empate": ("WilliamHill", 3.50),
                "Visitante": ("Betfair", 4.50)
            },
            overround=0.98,
            roi=2.04,
            timestamp=datetime.now()
        )
    
    def test_available_bankroll_initial(self, bankroll):
        """Test 1: Bankroll disponible inicial es el total."""
        assert bankroll.available == 1000.0
    
    def test_validate_sufficient_funds(self, bankroll, opportunity):
        """Test 2: Validación con fondos suficientes."""
        valid, message, stakes = bankroll.validate(opportunity)
        assert valid is True
        assert "Inversión requerida" in message
        assert len(stakes) == 3
        # Verificar que los stakes están calculados
        for selection, stake_info in stakes.items():
            assert "bookmaker" in stake_info
            assert "odds" in stake_info
            assert "stake" in stake_info
            assert stake_info["stake"] == 100.0  # 1000 * 0.10
    
    def test_validate_insufficient_funds(self, opportunity):
        """Test 3: Rechazo cuando fondos insuficientes."""
        bankroll = BankrollManager(total_bankroll=10.0, max_exposure=0.10)
        valid, message, stakes = bankroll.validate(opportunity)
        assert valid is False
        assert "Fondos insuficientes" in message
        assert stakes == {}
    
    def test_reserve_funds_success(self, bankroll):
        """Test 4: Reserva de fondos exitosa."""
        assert bankroll.reserve_funds(300.0) is True
        assert bankroll.reserved == 300.0
        assert bankroll.available == 700.0
    
    def test_reserve_funds_exceeds_available(self, bankroll):
        """Test 5: No permite reservar más de lo disponible."""
        assert bankroll.reserve_funds(1200.0) is False
        assert bankroll.reserved == 0.0
        assert bankroll.available == 1000.0
    
    def test_release_funds(self, bankroll):
        """Test 6: Liberación de fondos."""
        bankroll.reserve_funds(500.0)
        bankroll.release_funds(200.0)
        assert bankroll.reserved == 300.0
        assert bankroll.available == 700.0
    
    def test_release_funds_not_below_zero(self, bankroll):
        """Test 7: No permite reservas negativas."""
        bankroll.reserve_funds(100.0)
        bankroll.release_funds(200.0)
        assert bankroll.reserved == 0.0