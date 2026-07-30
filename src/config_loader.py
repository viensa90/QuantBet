"""
Cargador de configuración desde YAML.
Singleton que carga y expone la configuración del sistema.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Carga y gestiona configuración desde config.yaml."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.config = self._load_config()
        self._initialized = True
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga configuración desde archivo YAML."""
        config_path = Path(__file__).parent.parent / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default=None):
        """Obtiene valor de configuración por clave (soporta notación punto)."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    @property
    def decision_threshold(self) -> float:
        """Umbral de decisión: Score >= threshold → EJECUTAR."""
        return float(self.get('decision.threshold', 60.0))
    
    @property
    def database_path(self) -> str:
        """Ruta a la base de datos SQLite."""
        return self.get('database.path', 'quantbet.db')
    
    @property
    def csv_path(self) -> str:
        """Ruta al archivo CSV de datos."""
        return self.get('providers.csv.path', 'data/sample_events.csv')
    
    @property
    def logging_level(self) -> str:
        """Nivel de logging (DEBUG, INFO, WARNING, ERROR)."""
        return self.get('logging.level', 'INFO')
    
    @property
    def logging_format(self) -> str:
        """Formato de mensajes de log."""
        return self.get('logging.format', '%(asctime)s - %(levelname)s - %(message)s')
    
    @property
    def logging_file(self) -> str:
        """Archivo de log."""
        return self.get('logging.file', 'quantbet.log')
    
    @property
    def bankroll_total(self) -> float:
        """Bankroll total disponible."""
        return float(self.get('bankroll.total', 1000.0))
    
    @property
    def bankroll_max_exposure(self) -> float:
        """Exposición máxima por apuesta (fracción del bankroll)."""
        return float(self.get('bankroll.max_exposure', 0.10))
    
    @property
    def scoring_weights(self) -> Dict[str, float]:
        """Pesos del scorer."""
        return {
            'roi': float(self.get('scoring.roi_weight', 0.4)),
            'liquidity': float(self.get('scoring.liquidity_weight', 0.3)),
            'confidence': float(self.get('scoring.confidence_weight', 0.3))
        }