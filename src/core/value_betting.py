"""
Detector de Value Bets.
Identifica apuestas con valor esperado positivo comparando cuotas implícitas con probabilidades justas estimadas.
"""

from typing import List, Dict
from src.domain.entities import Snapshot


class ValueBetDetector:
    """Detecta value bets basado en un margen mínimo de valor."""

    def __init__(self, margin: float = 0.05):
        """
        Args:
            margin: Margen de valor mínimo (ej. 0.05 = 5% de valor)
        """
        self.margin = margin

    def detect(self, event_id: str, snapshots: List[Snapshot],
               fair_probabilities: Dict[str, float]) -> List[Dict]:
        """
        Encuentra value bets en un evento.

        Args:
            event_id: ID del evento
            snapshots: Lista de snapshots de cuotas
            fair_probabilities: Probabilidades justas estimadas por selección

        Returns:
            Lista de value bets encontradas
        """
        value_bets = []
        selections = self._group_by_selection(snapshots)

        for selection, fair_prob in fair_probabilities.items():
            if selection not in selections:
                continue

            best_snapshot = max(selections[selection], key=lambda s: s.odds)
            implied_prob = 1.0 / best_snapshot.odds

            if fair_prob > implied_prob + self.margin:
                value = (fair_prob - implied_prob) / implied_prob * 100
                value_bets.append({
                    "event_id": event_id,
                    "selection": selection,
                    "bookmaker": best_snapshot.bookmaker,
                    "odds": best_snapshot.odds,
                    "fair_probability": fair_prob,
                    "implied_probability": implied_prob,
                    "value_percentage": round(value, 2),
                    "snapshot_id": best_snapshot.snapshot_id
                })

        return value_bets

    def _group_by_selection(self, snapshots: List[Snapshot]) -> Dict[str, List[Snapshot]]:
        groups = {}
        for s in snapshots:
            groups.setdefault(s.selection, []).append(s)
        return groups