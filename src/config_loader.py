"""
Cargador de configuración centralizado (Singleton)
Versión: 0.3.3
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Singleton para cargar y gestionar configuración"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Cargar configuración desde archivo YAML"""
        config_path = Path(__file__).parent.parent / "config.yaml"
        
        if not config_path.exists():
            # Crear config por defecto
            self._config = self._get_default_config()
            self._save_config(config_path)
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            "strategies": {
                "arbitrage": True,
                "value_betting": True,
                "dutching": True
            },
            "markets": {
                "enabled": ["1X2", "Over/Under"]
            },
            "thresholds": {
                "min_profit_percent": 1.5,
                "min_value_probability": 0.65
            },
            "probability_model": {
                "type": "historical"
            },
            "bankroll": {
                "initial": 1000.0,
                "currency": "USD",
                "max_stake_percentage": 2.0
            },
            "csv_provider": {
                "enabled": True,
                "events_file": "data/sample_events.csv"
            },
            "web_provider": {
                "enabled": False
            },
            "database": {
                "path": "quantbet.db",
                "wal_mode": True
            },
            "web": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "swagger_enabled": True
            },
            "logs": {
                "level": "INFO",
                "format": "json",
                "console": {"enabled": True, "color": True},
                "file": {"enabled": False},
                "elasticsearch": {"enabled": False}
            }
        }
    
    def _save_config(self, path: Path):
        """Guardar configuración por defecto"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            print(f"✅ Configuración por defecto creada en {path}")
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    @property
    def config(self) -> Dict[str, Any]:
        """Obtener configuración completa"""
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración con notación de puntos"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def reload(self):
        """Recargar configuración"""
        self._load_config()


# Instancia global para acceso directo
config = ConfigLoader().config