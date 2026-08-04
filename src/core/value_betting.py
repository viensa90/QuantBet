"""
Detector de Value Bets con soporte para múltiples modelos de probabilidad.
"""

from typing import List, Dict, Optional, Any
from decimal import Decimal

from src.domain.entities import Snapshot, ValueBet, MarketType
from src.core.probability_model import ProbabilityModel, HistoricalModel, ProbabilityModelFactory
from src.logger import get_logger

logger = get_logger(__name__)


class ValueBetDetector:
    """Detector de value bets usando modelos de probabilidad."""
    
    def __init__(self, model_config: Optional[Dict] = None):
        """
        Inicializa el detector.
        
        Args:
            model_config: Configuración del modelo de probabilidad
        """
        self.model_config = model_config or {}
        model_type = self.model_config.get('type', 'historical')
        self.model = ProbabilityModelFactory.create(model_type, self.model_config)
        logger.info("ValueBetDetector inicializado con modelo %s", model_type)
    
    def detect_value_bets(self, snapshots: List[Snapshot], min_value_threshold: float = 0.05) -> List[ValueBet]:
        """
        Detecta value bets en los snapshots.
        
        Args:
            snapshots: Lista de snapshots a procesar
            min_value_threshold: Umbral mínimo de valor (0.05 = 5%)
            
        Returns:
            Lista de ValueBet detectados
        """
        value_bets = []
        
        for snapshot in snapshots:
            # ✅ Convertir market_type de str a MarketType
            try:
                market_type_enum = MarketType(snapshot.market_type)
            except ValueError:
                logger.warning(f"Tipo de mercado no reconocido: {snapshot.market_type}")
                continue
            
            # Calcular probabilidades justas
            fair_probs = self.model.calculate_probabilities(
                snapshot.event_id,
                market_type_enum,  # ✅ Ahora es un MarketType
                snapshot.metadata
            )
            
            if not fair_probs:
                continue
            
            # Calcular valor para cada resultado
            for outcome, odds in snapshot.odds_data.items():
                if outcome not in fair_probs:
                    continue
                
                fair_prob = fair_probs[outcome]
                actual_prob = float(1 / odds) if odds > 0 else 0
                
                # Calcular valor
                value_percent = (actual_prob - fair_prob) / fair_prob if fair_prob > 0 else 0
                
                if value_percent >= min_value_threshold:
                    value_bet = ValueBet(
                        event_id=snapshot.event_id,
                        market_type=snapshot.market_type,
                        selection=outcome,
                        odds=odds,
                        implied_prob=actual_prob,
                        fair_prob=fair_prob,
                        value=value_percent,
                        edge_percent=value_percent * 100,
                        score=value_percent * 100
                    )
                    value_bets.append(value_bet)
        
        # Ordenar por valor (mayor primero)
        value_bets.sort(key=lambda x: x.value, reverse=True)
        
        if value_bets:
            logger.info("Detectados %d value bets", len(value_bets))
            top = value_bets[0]
            logger.debug("Top value bet: %s - %s con valor %.2f%%", 
                        top.event_id, top.selection, top.value * 100)
        
        return value_bets
    
    def get_fair_probabilities(self, snapshot: Snapshot) -> Dict[str, float]:
        """
        Obtiene probabilidades justas para un snapshot.
        
        Args:
            snapshot: Snapshot a analizar
            
        Returns:
            Diccionario {resultado: probabilidad}
        """
        # ✅ Convertir market_type de str a MarketType
        try:
            market_type_enum = MarketType(snapshot.market_type)
        except ValueError:
            logger.warning(f"Tipo de mercado no reconocido: {snapshot.market_type}")
            return {}
        
        return self.model.calculate_probabilities(
            snapshot.event_id,
            market_type_enum,  # ✅ Ahora es un MarketType
            snapshot.metadata
        )