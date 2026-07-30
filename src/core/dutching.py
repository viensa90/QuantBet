"""
Calculador de Dutching.
Permite cubrir múltiples resultados de un evento con stakes ajustados para garantizar ganancia si alguno acierta.
"""

from typing import Dict, List, Tuple


class DutchingCalculator:
    """
    Calcula stakes para dutching (cobertura de múltiples selecciones).
    """
    
    def calculate(self, selections: List[Tuple[str, float]], total_stake: float) -> Dict:
        """
        Calcula stakes para dutching.
        
        Args:
            selections: Lista de tuplas (nombre_seleccion, cuota)
            total_stake: Cantidad total a apostar
        
        Returns:
            Diccionario con stakes individuales y ganancia potencial
        """
        if not selections:
            return {"stakes": {}, "total_stake": 0.0, "profit": 0.0, "profit_percentage": 0.0}
        
        # Suma de inversos de cuotas
        sum_inverse = sum(1.0 / odds for _, odds in selections)
        
        stakes = {}
        for name, odds in selections:
            # Proporción según fórmula de dutching: stake_i = (total_stake / sum_inverse) * (1 / odds)
            individual_stake = (total_stake / sum_inverse) * (1.0 / odds)
            stakes[name] = round(individual_stake, 2)
        
        # Ganancia si gana cualquiera
        profit = total_stake / sum_inverse - total_stake
        profit_percentage = (profit / total_stake) * 100 if total_stake > 0 else 0.0
        
        return {
            "stakes": stakes,
            "total_stake": total_stake,
            "profit": round(profit, 2),
            "profit_percentage": round(profit_percentage, 2)
        }