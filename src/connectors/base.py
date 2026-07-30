# src/connectors/base.py
from abc import ABC, abstractmethod
from typing import List
from src.domain.entities import Snapshot


class IDataProvider(ABC):
    """
    Contrato fundamental para todos los conectores de datos.
    
    Principio QB-003: Los Conectores solo obtienen datos, nunca deciden.
    La lógica de negocio reside exclusivamente en el Motor.
    """
    
    @abstractmethod
    def fetch_snapshots(self, event_id: str = None) -> List[Snapshot]:
        """
        Obtiene snapshots de cuotas desde la fuente de datos.
        
        Args:
            event_id: Identificador opcional para filtrar por evento.
            
        Returns:
            Lista de objetos Snapshot normalizados según el dominio.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna el nombre único del proveedor.
        Fundamental para auditoría y trazabilidad de decisiones.
        """
        pass