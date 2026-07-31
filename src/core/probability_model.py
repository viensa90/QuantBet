"""
Modelo de probabilidades para eventos deportivos.
Calcula probabilidades justas basadas en datos históricos y estadísticos.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import math
import json

from src.domain.entities import MarketType, Snapshot
from src.logger import get_logger

logger = get_logger(__name__)


class ProbabilityModel(ABC):
    """Base para modelos de probabilidad."""
    
    @abstractmethod
    def calculate_probabilities(self, event_id: str, market_type: MarketType, 
                               metadata: Optional[Dict] = None) -> Dict[str, float]:
        """
        Calcula probabilidades justas para un evento.
        
        Args:
            event_id: ID del evento
            market_type: Tipo de mercado
            metadata: Datos adicionales (líneas, handicaps, etc.)
            
        Returns:
            Diccionario {resultado: probabilidad}
        """
        pass


class HistoricalModel(ProbabilityModel):
    """Modelo basado en datos históricos."""
    
    def __init__(self, historical_data: Optional[Dict] = None):
        """
        Inicializa el modelo con datos históricos.
        
        Args:
            historical_data: Diccionario con datos históricos por equipo
        """
        self.historical_data = historical_data or self._load_default_data()
        logger.info("HistoricalModel inicializado con %d equipos", 
                   len(self.historical_data.get('teams', {})))
    
    def _load_default_data(self) -> Dict:
        """Carga datos históricos por defecto."""
        return {
            'teams': {
                'Real Madrid': {
                    'home_win_rate': 0.70,
                    'draw_rate': 0.20,
                    'away_win_rate': 0.10,
                    'goals_scored_avg': 2.10,
                    'goals_conceded_avg': 0.90,
                    'strength': 0.85
                },
                'Barcelona': {
                    'home_win_rate': 0.65,
                    'draw_rate': 0.25,
                    'away_win_rate': 0.10,
                    'goals_scored_avg': 2.00,
                    'goals_conceded_avg': 1.00,
                    'strength': 0.80
                },
                'Atletico Madrid': {
                    'home_win_rate': 0.60,
                    'draw_rate': 0.30,
                    'away_win_rate': 0.10,
                    'goals_scored_avg': 1.50,
                    'goals_conceded_avg': 0.70,
                    'strength': 0.75
                },
                'Sevilla': {
                    'home_win_rate': 0.55,
                    'draw_rate': 0.25,
                    'away_win_rate': 0.20,
                    'goals_scored_avg': 1.70,
                    'goals_conceded_avg': 1.10,
                    'strength': 0.65
                },
            },
            'league_averages': {
                'home_win_rate': 0.45,
                'draw_rate': 0.28,
                'away_win_rate': 0.27,
                'goals_per_game': 2.50
            }
        }
    
    def get_team_stats(self, team_name: str) -> Dict:
        """Obtiene estadísticas de un equipo."""
        return self.historical_data['teams'].get(team_name, {
            'home_win_rate': 0.40,
            'draw_rate': 0.30,
            'away_win_rate': 0.30,
            'goals_scored_avg': 1.20,
            'goals_conceded_avg': 1.20,
            'strength': 0.50
        })
    
    def calculate_1x2_probabilities(self, home_team: str, away_team: str) -> Dict[str, float]:
        """
        Calcula probabilidades para mercado 1X2.
        """
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Factor de localía
        home_advantage = 1.15
        
        # Probabilidad base
        base_home_win = home_stats['home_win_rate']
        base_draw = (home_stats['draw_rate'] + away_stats['draw_rate']) / 2
        base_away_win = away_stats['away_win_rate']
        
        # Ajustar por fortaleza relativa
        strength_factor = home_stats['strength'] / (home_stats['strength'] + away_stats['strength'])
        
        # Calcular probabilidades
        home_prob = base_home_win * home_advantage * (0.5 + 0.5 * strength_factor)
        away_prob = base_away_win * (1.5 - strength_factor)
        draw_prob = base_draw * (1 - abs(strength_factor - 0.5) * 0.3)
        
        # Normalizar
        total = home_prob + draw_prob + away_prob
        if total > 0:
            return {
                'Local': home_prob / total,
                'Empate': draw_prob / total,
                'Visitante': away_prob / total
            }
        else:
            return {'Local': 0.33, 'Empate': 0.33, 'Visitante': 0.34}
    
    def calculate_over_under_probabilities(self, home_team: str, away_team: str, 
                                           line: float = 2.5) -> Dict[str, float]:
        """
        Calcula probabilidades para mercado Over/Under usando modelo Poisson.
        """
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Goles esperados
        home_goals = home_stats['goals_scored_avg'] * (home_stats['strength'] + 0.2)
        away_goals = away_stats['goals_scored_avg'] * (away_stats['strength'] + 0.1)
        
        total_goals = home_goals + away_goals
        
        # Probabilidad de Over usando Poisson
        # Simplificación: distribución normal aproximada
        if total_goals > 0:
            # Probabilidad de que los goles totales superen la línea
            # Usando aproximación normal
            variance = total_goals * 0.8  # Varianza aproximada
            std_dev = math.sqrt(variance)
            
            if std_dev > 0:
                z_score = (line - total_goals) / std_dev
                # Usando aproximación de CDF normal
                over_prob = 1 - self._normal_cdf(z_score)
            else:
                over_prob = 0.5 if total_goals > line else 0.3
        else:
            over_prob = 0.5
        
        # Limitar a rangos razonables
        over_prob = max(0.2, min(0.8, over_prob))
        
        return {
            'Over': over_prob,
            'Under': 1 - over_prob
        }
    
    def _normal_cdf(self, x: float) -> float:
        """Aproximación de la CDF de la distribución normal estándar."""
        # Algoritmo de Abramowitz & Stegun
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        sign = 1 if x >= 0 else -1
        x = abs(x)
        
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x / 2.0)
        
        return 1.0 - y if sign == 1 else y
    
    def calculate_probabilities(self, event_id: str, market_type: MarketType,
                               metadata: Optional[Dict] = None) -> Dict[str, float]:
        """
        Calcula probabilidades según el tipo de mercado.
        """
        if metadata is None:
            metadata = {}
        
        logger.debug("Calculando probabilidades para evento %s, mercado %s", 
                    event_id, market_type.value)
        
        if market_type == MarketType.MERCADO_1X2:
            home_team = metadata.get('home_team', 'Local')
            away_team = metadata.get('away_team', 'Visitante')
            return self.calculate_1x2_probabilities(home_team, away_team)
            
        elif market_type == MarketType.OVER_UNDER:
            home_team = metadata.get('home_team', 'Local')
            away_team = metadata.get('away_team', 'Visitante')
            line = metadata.get('line', 2.5)
            return self.calculate_over_under_probabilities(home_team, away_team, line)
            
        elif market_type == MarketType.ASIAN_HANDICAP:
            # Simplificación: usar 1X2 como base
            home_team = metadata.get('home_team', 'Local')
            away_team = metadata.get('away_team', 'Visitante')
            probs = self.calculate_1x2_probabilities(home_team, away_team)
            # Para Asian Handicap, convertimos probabilidades
            handicap = metadata.get('handicap', 0.0)
            if handicap > 0:
                # Local con handicap positivo
                return {
                    'Local': probs['Local'] + 0.5 * probs['Empate'],
                    'Visitante': probs['Visitante'] + 0.5 * probs['Empate']
                }
            else:
                return {
                    'Local': probs['Local'] + 0.5 * probs['Empate'],
                    'Visitante': probs['Visitante'] + 0.5 * probs['Empate']
                }
            
        elif market_type == MarketType.DOUBLE_CHANCE:
            probs = self.calculate_1x2_probabilities(
                metadata.get('home_team', 'Local'),
                metadata.get('away_team', 'Visitante')
            )
            return {
                '1X': probs['Local'] + probs['Empate'],
                'X2': probs['Empate'] + probs['Visitante'],
                '12': probs['Local'] + probs['Visitante']
            }
        else:
            logger.warning("Mercado %s no soportado para probabilidades", market_type.value)
            return {}


class EloModel(ProbabilityModel):
    """Modelo basado en rating Elo."""
    
    def __init__(self, elo_ratings: Optional[Dict[str, float]] = None):
        """
        Inicializa el modelo con ratings Elo.
        
        Args:
            elo_ratings: Diccionario {equipo: rating}
        """
        self.elo_ratings = elo_ratings or self._load_default_ratings()
        self.k_factor = 32
        self.home_advantage = 50
        logger.info("EloModel inicializado con %d equipos", len(self.elo_ratings))
    
    def _load_default_ratings(self) -> Dict[str, float]:
        """Carga ratings Elo por defecto."""
        return {
            'Real Madrid': 2100,
            'Barcelona': 2050,
            'Atletico Madrid': 1950,
            'Sevilla': 1850,
            'Valencia': 1800,
            'Villarreal': 1780,
            'Athletic Club': 1750,
            'Real Sociedad': 1730,
            'Betis': 1700,
            'Getafe': 1680,
        }
    
    def calculate_probabilities(self, event_id: str, market_type: MarketType,
                               metadata: Optional[Dict] = None) -> Dict[str, float]:
        """
        Calcula probabilidades usando Elo.
        """
        if metadata is None:
            metadata = {}
        
        if market_type == MarketType.MERCADO_1X2:
            home_team = metadata.get('home_team', 'Local')
            away_team = metadata.get('away_team', 'Visitante')
            
            home_rating = self.elo_ratings.get(home_team, 1500)
            away_rating = self.elo_ratings.get(away_team, 1500)
            
            # Probabilidad de victoria local
            diff = home_rating - away_rating + self.home_advantage
            home_win_prob = 1.0 / (1.0 + 10 ** (-diff / 400.0))
            
            # Probabilidad de empate (simplificado)
            draw_prob = 0.28 * (1 - abs(home_win_prob - 0.5) * 2)
            draw_prob = max(0.15, min(0.40, draw_prob))
            
            # Probabilidad de victoria visitante
            away_win_prob = 1 - home_win_prob - draw_prob
            away_win_prob = max(0.10, min(0.50, away_win_prob))
            
            # Ajustar para que sume 1
            total = home_win_prob + draw_prob + away_win_prob
            return {
                'Local': home_win_prob / total,
                'Empate': draw_prob / total,
                'Visitante': away_win_prob / total
            }
        else:
            # Para otros mercados, usar modelo histórico como fallback
            return HistoricalModel().calculate_probabilities(event_id, market_type, metadata)


class ProbabilityModelFactory:
    """Fábrica de modelos de probabilidad."""
    
    @staticmethod
    def create(model_type: str, config: Optional[Dict] = None) -> ProbabilityModel:
        """
        Crea un modelo de probabilidad.
        
        Args:
            model_type: 'historical' o 'elo'
            config: Configuración del modelo
            
        Returns:
            ProbabilityModel
        """
        if model_type == 'historical':
            return HistoricalModel()
        elif model_type == 'elo':
            elo_data = config.get('elo_ratings') if config else None
            return EloModel(elo_data)
        else:
            raise ValueError(f"Modelo no soportado: {model_type}")