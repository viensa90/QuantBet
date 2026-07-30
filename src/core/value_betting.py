"""
Detector de Value Bets.
Identifica apuestas con valor esperado positivo basado en cuotas implícitas y probabilidades estimadas.
"""

from typing import List, Dict, Tuple
from src.domain.entities import Snapshot


class ValueBetDetector:
    """
    Detecta value bets comparando cuotas de bookmakers con probabilidades justas estimadas.
    """
    
    def __init__(self, margin: float = 0.05):
        """
        Args:
            margin: Margen mínimo de valor para considerar una apuesta (ej: 0.05 = 5% de valor)
        """
        self.margin = margin
    
    def detect(self, event_id: str, snapshots: List[Snapshot], 
               fair_probabilities: Dict[str, float]) -> List[Dict]:
        """
        Encuentra value bets en un evento.
        
        Args:
            event_id: ID del evento
            snapshots: Lista de snapshots de cuotas
            fair_probabilities: Probabilidades justas estimadas por selección (clave: "Local", "Empate", etc.)
        
        Returns:
            Lista de value bets encontradas (diccionarios con info)
        """
        value_bets = []
        
        # Agrupar snapshots por selección
        selections = self._group_by_selection(snapshots)
        
        for selection, fair_prob in fair_probabilities.items():
            if selection not in selections:
                continue
            
            # Buscar la mejor cuota disponible para esta selección
            best_snapshot = max(selections[selection], key=lambda s: s.odds)
            implied_prob = 1.0 / best_snapshot.odds
            
            # Si la cuota implica una probabilidad menor que la justa, hay valor
            if fair_prob > implied_prob + self.margin:
                value = (fair_prob - implied_prob) / implied_prob * 100  # % de valor
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
        """Agrupa snapshots por selección."""
        groups = {}
        for s in snapshots:
            if s.selection not in groups:
                groups[s.selection] = []
            groups[s.selection].append(s)
        return groups