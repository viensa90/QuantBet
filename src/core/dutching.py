"""
Calculador de Dutching.
Permite cubrir múltiples selecciones con stakes ajustados para garantizar ganancia si alguna acierta.
"""

from typing import List, Tuple, Dict


class DutchingCalculator:
    """Calcula stakes para dutching."""

    def calculate(self, selections: List[Tuple[str, float]], total_stake: float) -> Dict:
        """
        Args:
            selections: Lista de (nombre_selección, cuota)
            total_stake: Cantidad total a apostar

        Returns:
            Diccionario con stakes, profit, etc.
        """
        if not selections:
            return {"stakes": {}, "total_stake": 0.0, "profit": 0.0, "profit_percentage": 0.0}

        sum_inverse = sum(1.0 / odds for _, odds in selections)

        stakes = {}
        for name, odds in selections:
            individual_stake = (total_stake / sum_inverse) * (1.0 / odds)
            stakes[name] = round(individual_stake, 2)

        profit = total_stake / sum_inverse - total_stake
        profit_percentage = (profit / total_stake) * 100 if total_stake > 0 else 0.0

        return {
            "stakes": stakes,
            "total_stake": total_stake,
            "profit": round(profit, 2),
            "profit_percentage": round(profit_percentage, 2)
        }