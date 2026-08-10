"""
Fábrica de conectores de datos.
Selecciona el proveedor según configuración.
"""

from typing import Dict, Any, Optional
from src.connectors.base import IDataProvider
from src.connectors.csv_provider import CSVProvider
from src.connectors.odds_api_provider import OddsAPIProvider
from src.logger import get_logger

logger = get_logger(__name__)


class ConnectorFactory:
    """Fábrica para crear proveedores de datos."""
    
    @staticmethod
    def create(source_type: str, config: Dict[str, Any]) -> IDataProvider:
        logger.info("Creando conector de tipo: %s", source_type)
        
        if source_type == 'csv':
            csv_config = config.get('csv', {})
            return CSVProvider(csv_config.get('file_path', 'data/sample_events.csv'))
            
        elif source_type == 'oddsapi':
            odds_config = config.get('odds_api', {})
            return OddsAPIProvider(odds_config)
            
        else:
            raise ValueError(f"Tipo de conector no soportado: {source_type}")