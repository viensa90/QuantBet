"""
Fábrica de conectores de datos.
Selecciona el proveedor según configuración.
"""

from typing import Dict, Any, Optional
from src.connectors.base import IDataProvider
from src.connectors.csv_provider import CSVProvider
from src.connectors.web_provider import WebProvider
from src.logger import get_logger

logger = get_logger(__name__)


class ConnectorFactory:
    """Fábrica para crear proveedores de datos."""
    
    @staticmethod
    def create(source_type: str, config: Dict[str, Any]) -> IDataProvider:
        """
        Crea un proveedor de datos según el tipo.
        
        Args:
            source_type: 'csv' o 'web'
            config: Configuración completa del proyecto
            
        Returns:
            IDataProvider: Proveedor de datos
        """
        logger.info("Creando conector de tipo: %s", source_type)
        
        if source_type == 'csv':
            csv_config = config.get('csv', {})
            return CSVProvider(csv_config.get('file_path', 'data/sample_events.csv'))
            
        elif source_type == 'web':
            web_config = config.get('web_scraping', {})
            return WebProvider(web_config)
            
        else:
            raise ValueError(f"Tipo de conector no soportado: {source_type}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> IDataProvider:
        """
        Crea un proveedor usando la configuración 'connector.type'.
        
        Args:
            config: Configuración completa del proyecto
            
        Returns:
            IDataProvider: Proveedor de datos
        """
        connector_type = config.get('connector', {}).get('type', 'csv')
        return ConnectorFactory.create(connector_type, config)