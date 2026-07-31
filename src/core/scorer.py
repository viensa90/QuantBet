"""
Puntuador de oportunidades con soporte multi-mercado.
"""

from typing import List, Dict, Any
from decimal import Decimal

from src.domain.entities import Opportunity, ScoredOpportunity, MarketType
from src.logger import get_logger

logger = get_logger(__name__)


class Scorer:
    """Puntuador de oportunidades 0-100."""
    
    def __init__(self):
        self.weights = {
            'arbitrage_percent': 0.50,
            'liquidity': 0.25,
            'market_complexity': 0.25
        }
        logger.info("Scorer inicializado con pesos: %s", self.weights)
    
    def score_opportunity(self, opportunity: Opportunity) -> ScoredOpportunity:
        """
        Calcula puntuación para una oportunidad.
        
        Args:
            opportunity: Oportunidad a puntuar
            
        Returns:
            ScoredOpportunity con puntuación y razonamiento
        """
        reasoning = []
        score = 0.0
        
        # 1. Factor: % de arbitraje
        arb_score = min(opportunity.arbitrage_percent / 10.0, 1.0) * 100
        weighted_arb = arb_score * self.weights['arbitrage_percent']
        score += weighted_arb
        reasoning.append(f"Arbitraje {opportunity.arbitrage_percent:.2f}% -> {arb_score:.1f}pts (peso {self.weights['arbitrage_percent']*100:.0f}%)")
        
        # 2. Factor: liquidez (simulado por ahora)
        liquidity_score = 50.0  # Default
        weighted_liq = liquidity_score * self.weights['liquidity']
        score += weighted_liq
        reasoning.append(f"Liquidez simulada -> {liquidity_score:.1f}pts (peso {self.weights['liquidity']*100:.0f}%)")
        
        # 3. Factor: complejidad del mercado
        complexity_scores = {
            MarketType.MERCADO_1X2: 80.0,      # Fácil
            MarketType.DOUBLE_CHANCE: 70.0,    # Medio-fácil
            MarketType.OVER_UNDER: 60.0,       # Medio
            MarketType.ASIAN_HANDICAP: 40.0,   # Complejo
        }
        complexity_score = complexity_scores.get(opportunity.market_type, 50.0)
        weighted_complexity = complexity_score * self.weights['market_complexity']
        score += weighted_complexity
        reasoning.append(f"Complejidad {opportunity.market_type.value} -> {complexity_score:.1f}pts (peso {self.weights['market_complexity']*100:.0f}%)")
        
        # Normalizar a 0-100
        final_score = min(score, 100.0)
        
        # Determinar nivel de riesgo
        if final_score >= 70:
            risk_level = "bajo"
        elif final_score >= 50:
            risk_level = "medio"
        else:
            risk_level = "alto"
        
        return ScoredOpportunity(
            opportunity=opportunity,
            score=final_score,
            risk_level=risk_level,
            reasoning=reasoning
        )
    
    def score_opportunities(self, opportunities: List[Opportunity], 
                           threshold: float = 2.0) -> List[ScoredOpportunity]:
        """
        Puntúa múltiples oportunidades y filtra por umbral.
        
        Args:
            opportunities: Lista de oportunidades
            threshold: Umbral mínimo de % de arbitraje
            
        Returns:
            Lista de oportunidades puntuadas
        """
        scored = []
        
        for opp in opportunities:
            # Filtrar por umbral
            if opp.arbitrage_percent >= threshold:
                scored.append(self.score_opportunity(opp))
            else:
                logger.debug("Oportunidad descartada por umbral: %.2f%% < %.2f%%", 
                           opp.arbitrage_percent, threshold)
        
        # Ordenar por puntuación
        scored.sort(key=lambda x: x.score, reverse=True)
        
        logger.info("Oportunidades puntuadas: %d (de %d totales)", 
                   len(scored), len(opportunities))
        return scored