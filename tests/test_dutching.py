"""
Tests para DutchingCalculator.
"""

import pytest
from src.core.dutching import DutchingCalculator


class TestDutchingCalculator:
    
    @pytest.fixture
    def calculator(self):
        return DutchingCalculator()
    
    def test_dutching_two_outcomes(self, calculator):
        """Cálculo correcto para dos selecciones."""
        selections = [("Local", 2.00), ("Visitante", 3.00)]
        result = calculator.calculate(selections, total_stake=100.0)
        
        assert "stakes" in result
        assert len(result["stakes"]) == 2
        # Verificar que la suma de stakes es aproximadamente total_stake
        total = sum(result["stakes"].values())
        assert abs(total - 100.0) < 0.1
        # Ganancia positiva si es surebet implícito
        assert result["profit"] >= 0
    
    def test_dutching_profit_calculation(self, calculator):
        """Ganancia calculada correctamente."""
        selections = [("A", 2.00), ("B", 2.00)]
        result = calculator.calculate(selections, total_stake=100.0)
        # Cada stake debería ser 50, ganancia = 100/(1/2+1/2) - 100 = 100/1 - 100 = 0
        assert result["profit"] == 0.0
        assert result["profit_percentage"] == 0.0
    
    def test_dutching_three_outcomes(self, calculator):
        """Cálculo con tres outcomes."""
        selections = [("Local", 2.50), ("Empate", 3.20), ("Visitante", 2.80)]
        result = calculator.calculate(selections, total_stake=200.0)
        assert len(result["stakes"]) == 3
        total = sum(result["stakes"].values())
        assert abs(total - 200.0) < 0.2
    
    def test_empty_selections(self, calculator):
        """Retorno seguro para lista vacía."""
        result = calculator.calculate([], 100.0)
        assert result["stakes"] == {}
        assert result["total_stake"] == 0.0
        assert result["profit"] == 0.0