"""
Calculador de Dutching (cobertura de resultados).
Versión: 0.3.3 (Optimizado para Snapshots)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict

from src.domain.entities import Snapshot, Opportunity
from src.logger import get_logger

logger = get_logger(__name__)


class DutchingCalculator:
    """
    Calculador de Dutching que agrupa snapshots por evento/mercado
    y selecciona las mejores odds de cada bookmaker.
    """
    
    def __init__(self, total_stake: float = 100.0, min_profit_margin: float = 0.0):
        """
        Inicializa el calculador.
        
        Args:
            total_stake: Monto total a apostar (por defecto 100)
            min_profit_margin: Margen de beneficio mínimo (0 = cualquier oportunidad)
        """
        self.total_stake = total_stake
        self.min_profit_margin = min_profit_margin
        logger.info("DutchingCalculator inicializado con total_stake: %.2f, min_margin: %.2f%%", 
                   total_stake, min_profit_margin * 100)
    
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        """
        Detecta oportunidades de Dutching agrupando snapshots por evento y mercado.
        
        Args:
            snapshots: Lista de Snapshots inmutables
            
        Returns:
            Lista de oportunidades de Dutching
        """
        # 1. Agrupar snapshots por (event_id, market_type)
        grouped = defaultdict(list)
        for snapshot in snapshots:
            key = (snapshot.event_id, snapshot.market_type)
            grouped[key].append(snapshot)
        
        opportunities = []
        
        for (event_id, market_type), snapshots_list in grouped.items():
            # 2. Para cada grupo, seleccionar la mejor odds por resultado
            best_odds = self._get_best_odds(snapshots_list)
            
            if len(best_odds) < 2:
                logger.debug(f"Evento {event_id}: menos de 2 resultados disponibles")
                continue
            
            # 3. Validar odds
            if not self._validate_odds(best_odds):
                continue
            
            # 4. Calcular overround y margen de beneficio
            overround = sum(1.0 / odd for odd in best_odds.values())
            profit_margin = (1.0 / overround - 1.0) if overround > 0 else -1.0
            
            # 5. Filtrar por margen mínimo
            if profit_margin < self.min_profit_margin:
                logger.debug(f"Evento {event_id}: margen {profit_margin:.2f}% < mínimo {self.min_profit_margin:.2f}%")
                continue
            
            # 6. Calcular stakes para Dutching
            stakes = self._calculate_stakes(best_odds)
            
            # 7. Crear oportunidad
            opportunity = Opportunity(
                event_id=event_id,
                market_type=market_type,
                profit_percent=profit_margin * 100,
                odds=best_odds,
                stakes=stakes,
                source="DutchingCalculator",
                timestamp=snapshots_list[0].timestamp,
                arbitrage_percent=profit_margin * 100
            )
            opportunities.append(opportunity)
            
            logger.debug(f"Dutching detectado para {event_id}: {profit_margin:.2f}% beneficio")
        
        logger.info("Dutching: detectadas %d oportunidades", len(opportunities))
        return opportunities
    
    def _get_best_odds(self, snapshots: List[Snapshot]) -> Dict[str, float]:
        """
        Dado un grupo de snapshots del mismo evento/mercado,
        selecciona la mejor odds para cada resultado (la más alta).
        
        Args:
            snapshots: Lista de snapshots del mismo evento y mercado
            
        Returns:
            Diccionario {resultado: mejor_odds}
        """
        best_odds = {}
        
        for snapshot in snapshots:
            for outcome, odd in snapshot.odds_data.items():
                if outcome not in best_odds or odd > best_odds[outcome]:
                    best_odds[outcome] = odd
        
        return best_odds
    
    def _validate_odds(self, odds_data: Dict[str, float]) -> bool:
        """Valida que los odds sean mayores que 1 y no nulos."""
        if not odds_data:
            return False
        for odd in odds_data.values():
            if odd <= 1.0:
                return False
        return True
    
    def _calculate_stakes(self, odds_data: Dict[str, float]) -> Dict[str, float]:
        """
        Calcula las stakes para cubrir todos los resultados.
        
        Args:
            odds_data: Diccionario {resultado: odds}
            
        Returns:
            Diccionario {resultado: stake}
        """
        # Suma de las probabilidades implícitas
        inv_sum = sum(1.0 / odd for odd in odds_data.values())
        
        stakes = {}
        for outcome, odd in odds_data.items():
            # Fórmula de Dutching: stake = (total_stake / odd) / (suma de 1/odds)
            stakes[outcome] = (self.total_stake / odd) / inv_sum
        
        return stakes
    
    def calculate_dutching(self, selections: List[Dict]) -> Dict[str, Any]:
        """
        Método original para compatibilidad (calcula sobre selecciones).
        
        Args:
            selections: Lista de diccionarios con 'odds' y 'label'
            
        Returns:
            Diccionario con stakes y retorno garantizado
        """
        if not selections:
            return {"error": "No hay selecciones"}
        
        odds_list = [s['odds'] for s in selections]
        inv_sum = sum(1.0 / odd for odd in odds_list)
        
        stakes = {}
        for sel in selections:
            stakes[sel.get('label', 'unknown')] = (self.total_stake / sel['odds']) / inv_sum
        
        guaranteed_return = self.total_stake / inv_sum
        
        return {
            "stakes": stakes,
            "total_stake": self.total_stake,
            "guaranteed_return": guaranteed_return,
            "profit": guaranteed_return - self.total_stake,
            "profit_margin": (guaranteed_return - self.total_stake) / self.total_stake * 100
        }