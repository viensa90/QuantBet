"""
QuantBet - Motor de Arbitraje (QB-004, Estrategia 1)
Detecta oportunidades de arbitraje (surebets) entre dos o más Snapshots.
Principio: No conoce el origen de los datos. Solo opera sobre objetos Snapshot normalizados.
"""
from typing import List, Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    """
    Analiza un conjunto de Snapshots para detectar arbitraje.
    Una oportunidad de arbitraje existe cuando el overround (suma de probabilidades implícitas)
    es menor a 1.0, garantizando ganancia independientemente del resultado.
    """
    
    def __init__(self, max_overround: float = 0.999):
        """
        Args:
            max_overround: Overround máximo para considerar arbitraje.
                          1.0 = equilibrio, <1.0 = arbitraje.
        """
        self.max_overround = max_overround
    
    def analyze(self, snapshots: List['Snapshot']) -> Optional[Dict]:
        """
        Busca la mejor combinación de cuotas para cada outcome del mercado.
        
        Args:
            snapshots: Lista de Snapshots del mismo mercado (mismo Market.type y parámetros),
                       pero potencialmente de diferentes bookmakers.
        
        Returns:
            Diccionario con la información del arbitraje si existe:
            {
                'best_odds': {outcome_name: (bookmaker_id, snapshot_id, odds)},
                'overround': float,
                'roi_percent': float,
                'stake_distribution': {outcome_name: porcentaje}
            }
            None si no hay arbitraje.
        """
        if not snapshots:
            logger.warning("analyze() llamado con lista vacía de snapshots.")
            return None
        
        # Verificar que todos los snapshots sean del mismo mercado
        market_id = snapshots[0].market.id
        market_type = snapshots[0].market.type
        
        # Obtener todos los outcomes únicos del mercado
        all_outcomes = set()
        for snap in snapshots:
            if snap.market.id != market_id:
                logger.warning(f"Snapshot {snap.id} es de un mercado diferente. Se ignora.")
                continue
            all_outcomes.update(snap.odds.keys())
        
        if len(all_outcomes) < 2:
            logger.warning(f"Mercado {market_id} tiene menos de 2 outcomes. No se puede calcular arbitraje.")
            return None
        
        # Encontrar la mejor cuota para cada outcome
        best_odds = {}
        for outcome in all_outcomes:
            best = None
            for snap in snapshots:
                if outcome in snap.odds:
                    odds = snap.odds[outcome]
                    if best is None or odds > best[2]:
                        best = (snap.bookmaker.id, snap.id, odds)
            if best:
                best_odds[outcome] = best
        
        # Calcular overround (suma de probabilidades implícitas)
        overround = sum(1.0 / odds[2] for odds in best_odds.values())
        
        logger.debug(f"Mercado {market_id}: overround={overround:.4f}, max_overround={self.max_overround}")
        
        if overround >= self.max_overround:
            return None  # No hay arbitraje
        
        # Calcular ROI
        roi_percent = (1.0 - overround) * 100.0 / overround
        
        # Calcular distribución óptima de stakes (normalizada a 100 unidades)
        total_stake = 100.0
        stake_distribution = {}
        for outcome, (bookmaker_id, snapshot_id, odds) in best_odds.items():
            # Fórmula: Stake_i = Total / (Odds_i * Sum(1/Odds_j))
            stake = total_stake / (odds * overround)
            stake_distribution[outcome] = {
                'bookmaker_id': bookmaker_id,
                'snapshot_id': snapshot_id,
                'odds': odds,
                'stake_percentage': round(stake, 2)
            }
        
        return {
            'best_odds': best_odds,
            'overround': round(overround, 6),
            'roi_percent': round(roi_percent, 4),
            'stake_distribution': stake_distribution
        }