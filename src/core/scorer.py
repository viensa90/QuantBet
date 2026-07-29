"""
QuantBet - Motor de Puntuación (QB-004, 3.3)
Calcula el Opportunity Score para una decisión detectada.
Principio: Pondera múltiples factores (ROI, tiempo, liquidez) para priorizar oportunidades.
"""
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OpportunityScorer:
    """
    Asigna una puntuación de 0 a 100 a una oportunidad de arbitraje.
    Combina el ROI, la frescura de los datos, el tiempo hasta el evento y la liquidez.
    """
    
    def __init__(self, weights: dict, max_freshness_age_seconds: int = 10, time_decay_start_minutes: int = 10):
        """
        Args:
            weights: Diccionario con los pesos para cada factor.
                     Ej: {'roi': 50, 'time': 30, 'liquidity': 20}
            max_freshness_age_seconds: Edad máxima del snapshot para máxima puntuación de frescura.
            time_decay_start_minutes: Minutos antes del evento en que empieza a decaer la puntuación.
        """
        self.weights = weights
        self.max_freshness_age_seconds = max_freshness_age_seconds
        self.time_decay_start_minutes = time_decay_start_minutes
        
        # Normalizar pesos
        total_weight = sum(weights.values())
        if total_weight != 100:
            logger.warning(f"Pesos suman {total_weight}. Se normalizarán a 100.")
            self.weights = {k: (v / total_weight) * 100 for k, v in weights.items()}
    
    def calculate(
        self,
        roi_percent: float,
        snapshot_ages_seconds: list,
        event_start_time_utc: Optional[datetime] = None,
        max_stake_allowed: float = 0.0,
        confidence_factor: float = 1.0
    ) -> float:
        """
        Calcula el Opportunity Score.
        
        Args:
            roi_percent: ROI de la oportunidad (ej. 5.2 para 5.2%).
            snapshot_ages_seconds: Lista con la antigüedad de cada snapshot en segundos.
            event_start_time_utc: Hora de inicio del evento (None si no se conoce).
            max_stake_allowed: Stake máximo permitido por el bankroll.
            confidence_factor: Factor de confianza en los datos (0.0-1.0).
        
        Returns:
            Puntuación de 0 a 100.
        """
        scores = {}
        
        # 1. ROI Score (0-100)
        if roi_percent <= 0:
            return 0.0
        # Un ROI del 8% o más es "perfecto" para el score de ROI
        scores['roi'] = min(100.0, (roi_percent / 8.0) * 100.0)
        
        # 2. Time Score (0-100) - Frescura de datos
        if snapshot_ages_seconds:
            avg_age = sum(snapshot_ages_seconds) / len(snapshot_ages_seconds)
            if avg_age <= self.max_freshness_age_seconds:
                scores['time'] = 100.0
            else:
                # Decaimiento exponencial después del umbral
                decay_factor = (avg_age - self.max_freshness_age_seconds) / 60.0  # en minutos
                scores['time'] = max(0.0, 100.0 * (0.9 ** decay_factor))
        else:
            scores['time'] = 50.0  # Sin información, neutro
        
        # 3. Event Time Decay (si conocemos la hora del evento)
        if event_start_time_utc:
            now_utc = datetime.now(timezone.utc)
            minutes_to_event = (event_start_time_utc - now_utc).total_seconds() / 60.0
            
            if minutes_to_event <= 0:
                # Evento ya empezó o acaba de empezar
                scores['time'] = min(scores['time'], 10.0)  # Penalización fuerte
            elif minutes_to_event < self.time_decay_start_minutes:
                # Decaimiento lineal en los últimos minutos
                decay = minutes_to_event / self.time_decay_start_minutes
                scores['time'] = min(scores['time'], decay * 100.0)
        
        # 4. Liquidity Score (0-100)
        # Asumimos que un stake de 1,000,000 PYG es "excelente"
        ideal_stake = 1_000_000.0
        if max_stake_allowed > 0:
            scores['liquidity'] = min(100.0, (max_stake_allowed / ideal_stake) * 100.0)
        else:
            scores['liquidity'] = 0.0
        
        # 5. Confidence Score (0-100) - basado en la fuente de datos
        scores['confidence'] = confidence_factor * 100.0
        
        # Calcular puntuación ponderada final
        final_score = 0.0
        for factor in self.weights:
            if factor in scores:
                final_score += scores[factor] * (self.weights[factor] / 100.0)
        
        return round(min(100.0, max(0.0, final_score)), 2)