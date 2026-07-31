"""
Motor de arbitraje con soporte multi-mercado.
"""

from typing import List, Dict, Optional
from decimal import Decimal

from src.domain.entities import Snapshot, Opportunity, MarketType
from src.core.market_handlers import MarketHandlerFactory
from src.logger import get_logger

logger = get_logger(__name__)


class ArbitrageEngine:
    """Motor de detección de arbitraje multi-mercado."""
    
    def __init__(self, enabled_markets: Optional[List[MarketType]] = None):
        """
        Inicializa el motor.
        
        Args:
            enabled_markets: Lista de mercados a procesar. None = todos.
        """
        self.enabled_markets = enabled_markets or MarketHandlerFactory.get_supported_markets()
        logger.info("Motor de arbitraje inicializado con mercados: %s", 
                   [m.value for m in self.enabled_markets])
    
    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        """
        Detecta oportunidades de arbitraje en todos los mercados.
        
        Args:
            snapshots: Lista de snapshots a procesar
            
        Returns:
            Lista de oportunidades detectadas
        """
        all_opportunities = []
        
        # Procesar cada mercado habilitado
        for market_type in self.enabled_markets:
            try:
                handler = MarketHandlerFactory.get_handler(market_type)
                market_snapshots = [s for s in snapshots if s.market_type == market_type]
                
                if not market_snapshots:
                    logger.debug("No hay snapshots para mercado %s", market_type.value)
                    continue
                
                opportunities = handler.detect_opportunities(market_snapshots)
                all_opportunities.extend(opportunities)
                
                if opportunities:
                    logger.info("Mercado %s: %d oportunidades detectadas", 
                               market_type.value, len(opportunities))
                    
            except Exception as e:
                logger.error("Error procesando mercado %s: %s", market_type.value, str(e))
        
        # Ordenar por porcentaje de arbitraje (mayor primero)
        all_opportunities.sort(key=lambda x: x.arbitrage_percent, reverse=True)
        
        logger.info("Total oportunidades detectadas: %d", len(all_opportunities))
        return all_opportunities