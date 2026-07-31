"""
Modelo Poisson para predicción de goles y probabilidades.
"""

import math
from typing import Dict, Tuple, List, Optional
from decimal import Decimal

from src.core.probability_model import HistoricalModel
from src.logger import get_logger

logger = get_logger(__name__)


class PoissonModel:
    """
    Modelo Poisson para predicción de resultados en fútbol.
    Calcula probabilidades de resultados exactos y mercados derivados.
    """
    
    def __init__(self, historical_model: Optional[HistoricalModel] = None):
        """
        Inicializa el modelo Poisson.
        
        Args:
            historical_model: Modelo histórico para estadísticas de equipos
        """
        self.historical_model = historical_model or HistoricalModel()
        logger.info("PoissonModel inicializado")
    
    def calculate_expected_goals(self, home_team: str, away_team: str) -> Tuple[float, float]:
        """
        Calcula goles esperados para cada equipo.
        
        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            
        Returns:
            Tuple(home_goals_expected, away_goals_expected)
        """
        home_stats = self.historical_model.get_team_stats(home_team)
        away_stats = self.historical_model.get_team_stats(away_team)
        
        # Goles esperados con ajustes
        home_goals = home_stats['goals_scored_avg'] * 1.1  # Factor localía
        away_goals = away_stats['goals_scored_avg'] * 0.9  # Factor visitante
        
        # Ajuste por defensa
        home_goals *= (1 + (1 - home_stats['goals_conceded_avg'] / 1.5) * 0.2)
        away_goals *= (1 + (1 - away_stats['goals_conceded_avg'] / 1.5) * 0.2)
        
        return home_goals, away_goals
    
    def poisson_probability(self, goals: int, expected: float) -> float:
        """
        Calcula probabilidad Poisson para un número de goles.
        
        Args:
            goals: Número de goles
            expected: Goles esperados
            
        Returns:
            Probabilidad (0-1)
        """
        if expected <= 0:
            return 0.0
        
        # f(x; λ) = (e^(-λ) * λ^x) / x!
        # Usando log para evitar overflow
        log_prob = -expected + goals * math.log(expected) - math.lgamma(goals + 1)
        return math.exp(log_prob)
    
    def match_probabilities(self, home_team: str, away_team: str, 
                           max_goals: int = 5) -> Dict[str, float]:
        """
        Calcula probabilidades de resultados exactos y agregados.
        
        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            max_goals: Número máximo de goles a considerar
            
        Returns:
            Diccionario con probabilidades
        """
        home_exp, away_exp = self.calculate_expected_goals(home_team, away_team)
        
        # Matriz de probabilidades
        probs = {}
        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                prob = self.poisson_probability(h, home_exp) * self.poisson_probability(a, away_exp)
                probs[f"{h}-{a}"] = prob
        
        # Probabilidades agregadas
        home_win = sum(probs[f"{h}-{a}"] for h in range(max_goals + 1) 
                      for a in range(max_goals + 1) if h > a)
        draw = sum(probs[f"{h}-{h}"] for h in range(max_goals + 1))
        away_win = sum(probs[f"{h}-{a}"] for h in range(max_goals + 1) 
                      for a in range(max_goals + 1) if a > h)
        
        # Over/Under
        over_25 = sum(probs[f"{h}-{a}"] for h in range(max_goals + 1) 
                     for a in range(max_goals + 1) if h + a > 2.5)
        over_35 = sum(probs[f"{h}-{a}"] for h in range(max_goals + 1) 
                     for a in range(max_goals + 1) if h + a > 3.5)
        over_45 = sum(probs[f"{h}-{a}"] for h in range(max_goals + 1) 
                     for a in range(max_goals + 1) if h + a > 4.5)
        
        # Ambos equipos marcan
        btts = sum(probs[f"{h}-{a}"] for h in range(1, max_goals + 1) 
                  for a in range(1, max_goals + 1))
        
        return {
            'exact_scores': probs,
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win,
            'over_2.5': over_25,
            'under_2.5': 1 - over_25,
            'over_3.5': over_35,
            'under_3.5': 1 - over_35,
            'over_4.5': over_45,
            'under_4.5': 1 - over_45,
            'btts_yes': btts,
            'btts_no': 1 - btts
        }
    
    def calculate_probabilities(self, event_id: str, market_type: str,
                               metadata: Optional[Dict] = None) -> Dict[str, float]:
        """
        Calcula probabilidades para un mercado específico usando Poisson.
        
        Args:
            event_id: ID del evento
            market_type: Tipo de mercado ('1X2', 'OVER_UNDER', 'BTTS', etc.)
            metadata: Datos adicionales (equipos, líneas)
            
        Returns:
            Diccionario con probabilidades
        """
        if metadata is None:
            metadata = {}
        
        home_team = metadata.get('home_team', 'Local')
        away_team = metadata.get('away_team', 'Visitante')
        
        probs = self.match_probabilities(home_team, away_team)
        
        if market_type == '1X2':
            return {
                'Local': probs['home_win'],
                'Empate': probs['draw'],
                'Visitante': probs['away_win']
            }
        elif market_type == 'OVER_UNDER':
            line = metadata.get('line', 2.5)
            if line == 2.5:
                return {'Over': probs['over_2.5'], 'Under': probs['under_2.5']}
            elif line == 3.5:
                return {'Over': probs['over_3.5'], 'Under': probs['under_3.5']}
            elif line == 4.5:
                return {'Over': probs['over_4.5'], 'Under': probs['under_4.5']}
            else:
                return {'Over': 0.5, 'Under': 0.5}
        elif market_type == 'BTTS':
            return {'Yes': probs['btts_yes'], 'No': probs['btts_no']}
        else:
            logger.warning("Mercado %s no soportado por PoissonModel", market_type)
            return {}