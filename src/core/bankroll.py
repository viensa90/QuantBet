"""
Gestor de Bankroll - Validación de fondos antes de ejecutar oportunidades.
"""

from typing import Dict, Tuple
from src.domain.entities import Opportunity


class BankrollManager:
    """
    Gestor de bankroll para validación pre-ejecución.
    
    Principios:
    - Validar disponibilidad de fondos antes de EJECUTAR
    - Calcular stakes óptimos por outcome
    - Prevenir sobreexposición
    """
    
    def __init__(self, total_bankroll: float = 1000.0, max_exposure: float = 0.10):
        """
        Args:
            total_bankroll: Bankroll total disponible
            max_exposure: Exposición máxima por apuesta (fracción del bankroll)
        """
        self.total_bankroll = total_bankroll
        self.max_exposure = max_exposure
        self.reserved = 0.0  # Fondos reservados para apuestas activas
    
    @property
    def available(self) -> float:
        """Bankroll disponible para nuevas apuestas."""
        return self.total_bankroll - self.reserved
    
    def validate(self, opportunity: Opportunity) -> Tuple[bool, str, Dict]:
        """
        Valida si hay fondos suficientes para ejecutar una oportunidad.
        
        Args:
            opportunity: Oportunidad a validar
        
        Returns:
            Tuple: (es_válido, mensaje, stakes_calculados)
        """
        num_outcomes = len(opportunity.outcomes)
        stake_per_outcome = self.total_bankroll * self.max_exposure
        total_required = stake_per_outcome * num_outcomes
        
        if total_required > self.available:
            return (
                False, 
                f"Fondos insuficientes: requiere ${total_required:.2f}, disponible ${self.available:.2f}", 
                {}
            )
        
        # Calcular stakes individuales
        stakes = {}
        for selection, (bookmaker, odds) in opportunity.outcomes.items():
            stakes[selection] = {
                "bookmaker": bookmaker,
                "odds": odds,
                "stake": round(stake_per_outcome, 2)
            }
        
        return True, f"Inversión requerida: ${total_required:.2f}", stakes
    
    def reserve_funds(self, amount: float) -> bool:
        """
        Reserva fondos para una apuesta.
        
        Args:
            amount: Cantidad a reservar
        
        Returns:
            True si se reservó correctamente
        """
        if amount <= self.available:
            self.reserved += amount
            return True
        return False
    
    def release_funds(self, amount: float):
        """
        Libera fondos reservados.
        
        Args:
            amount: Cantidad a liberar
        """
        self.reserved = max(0.0, self.reserved - amount)