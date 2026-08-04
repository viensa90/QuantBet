"""
Puntuador de oportunidades con soporte multi-mercado.
Versión: 0.3.3 (Corregido)
"""

from typing import List, Dict, Any
from decimal import Decimal

from src.domain.entities import Opportunity, ScoredOpportunity, MarketType
from src.logger import get_logger

logger = get_logger(__name__)


class OpportunityScorer:
    """Puntuador de oportunidades 0-100."""
    
    def __init__(self):
        self.weights = {
            'profit_percent': 0.50,
            'liquidity': 0.25,
            'market_complexity': 0.25
        }
        logger.info("OpportunityScorer inicializado con pesos: %s", self.weights)
    
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
        
        # 1. Factor: % de beneficio (usar profit_percent o arbitrage_percent)
        profit = getattr(opportunity, 'profit_percent', 0.0)
        if profit == 0 and hasattr(opportunity, 'arbitrage_percent'):
            profit = opportunity.arbitrage_percent
        
        profit_score = min(profit / 10.0, 1.0) * 100
        weighted_profit = profit_score * self.weights['profit_percent']
        score += weighted_profit
        reasoning.append(f"Beneficio {profit:.2f}% -> {profit_score:.1f}pts (peso {self.weights['profit_percent']*100:.0f}%)")
        
        # 2. Factor: liquidez (simulado por ahora)
        liquidity_score = 50.0  # Default
        weighted_liq = liquidity_score * self.weights['liquidity']
        score += weighted_liq
        reasoning.append(f"Liquidez simulada -> {liquidity_score:.1f}pts (peso {self.weights['liquidity']*100:.0f}%)")
        
        # 3. Factor: complejidad del mercado
        market_type = opportunity.market_type
        if isinstance(market_type, MarketType):
            market_key = market_type.value
        else:
            market_key = str(market_type)
        
        complexity_scores = {
            "1X2": 80.0,
            "Double Chance": 70.0,
            "Over/Under": 60.0,
            "Asian Handicap": 40.0,
            "Tennis Winner": 75.0,
            "Tennis Set Handicap": 45.0,
            "Tennis Total Games": 55.0,
            "Basketball Moneyline": 80.0,
            "Point Spread": 50.0,
            "Total Points": 60.0,
            "Quarter Winner": 65.0,
        }
        complexity_score = complexity_scores.get(market_key, 50.0)
        weighted_complexity = complexity_score * self.weights['market_complexity']
        score += weighted_complexity
        reasoning.append(f"Complejidad {market_key} -> {complexity_score:.1f}pts (peso {self.weights['market_complexity']*100:.0f}%)")
        
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
            threshold: Umbral mínimo de % de beneficio
            
        Returns:
            Lista de oportunidades puntuadas
        """
        scored = []
        
        for opp in opportunities:
            # Obtener el beneficio correcto
            profit = getattr(opp, 'profit_percent', 0.0)
            if profit == 0 and hasattr(opp, 'arbitrage_percent'):
                profit = opp.arbitrage_percent
            
            # Filtrar por umbral
            if profit >= threshold:
                scored.append(self.score_opportunity(opp))
            else:
                logger.debug("Oportunidad descartada por umbral: %.2f%% < %.2f%%", 
                           profit, threshold)
        
        # Ordenar por puntuación
        scored.sort(key=lambda x: x.score, reverse=True)
        
        logger.info("Oportunidades puntuadas: %d (de %d totales)", 
                   len(scored), len(opportunities))
        return scored