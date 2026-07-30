# src/connectors/__init__.py
"""
Módulo de conectores para QuantBet.
Principio: Los Conectores solo obtienen datos, nunca deciden.
"""

from .base import IDataProvider
from .csv_provider import CSVProvider

__all__ = ['IDataProvider', 'CSVProvider']