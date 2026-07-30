# src/connectors/csv_provider.py
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from .base import IDataProvider
from src.domain.entities import Snapshot


class CSVProvider(IDataProvider):
    """
    Proveedor de datos simulado desde archivo CSV.
    
    Implementa el contrato IDataProvider para el MVP.
    Principios:
    - Solo obtiene datos, nunca decide.
    - Normaliza los datos al formato Snapshot del dominio.
    - Cada fila del CSV se convierte en un Snapshot inmutable.
    """
    
    def __init__(self, csv_path: str = "data/sample_events.csv"):
        self._csv_path = Path(csv_path)
        self._provider_name = "CSVProvider"
        
        # Validar existencia del archivo
        if not self._csv_path.exists():
            raise FileNotFoundError(
                f"Archivo CSV no encontrado: {self._csv_path}. "
                "Ejecuta primero la creación de datos de prueba."
            )
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor para trazabilidad."""
        return self._provider_name
    
    def fetch_snapshots(self, event_id: str = None) -> List[Snapshot]:
        """
        Lee el CSV y retorna snapshots normalizados.
        
        Pipeline:
        1. Lee todas las filas del CSV
        2. Convierte cada fila en un objeto Snapshot del dominio
        3. Filtra por event_id si se especifica
        4. Retorna lista de snapshots inmutables
        
        Args:
            event_id: Opcional. Filtra snapshots por evento específico.
            
        Returns:
            Lista de Snapshot listos para el Motor de Análisis.
        """
        raw_data = self._read_csv()
        snapshots = []
        
        for row in raw_data:
            # Filtro por evento si se especifica
            if event_id and row.get('event_id') != event_id:
                continue
                
            try:
                snapshot = self._row_to_snapshot(row)
                snapshots.append(snapshot)
            except (ValueError, KeyError) as e:
                print(f"⚠️  Advertencia: Fila inválida en CSV - {e}")
                continue
        
        return snapshots
    
    def _read_csv(self) -> List[Dict]:
        """
        Lee el archivo CSV completo.
        
        Returns:
            Lista de diccionarios con los datos crudos del CSV.
        """
        rows = []
        
        with open(self._csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        
        return rows
    
    def _row_to_snapshot(self, row: Dict) -> Snapshot:
        """
        Normaliza una fila CSV a objeto Snapshot del dominio.
        
        Transformación de tipos:
        - odds: str → float
        - timestamp: str (ISO) → datetime
        
        Args:
            row: Diccionario con datos crudos de una fila CSV.
            
        Returns:
            Objeto Snapshot normalizado según QB-002.
        """
        return Snapshot(
            snapshot_id=row['snapshot_id'],
            event_id=row['event_id'],
            event_name=row.get('event_name', ''),
            market_id=row['market_id'],
            market_type=row.get('market_type', '1X2'),
            outcome_id=row['outcome_id'],
            outcome_label=row.get('outcome_label', ''),
            bookmaker_id=row['bookmaker_id'],
            bookmaker_name=row.get('bookmaker_name', ''),
            odds=float(row['odds']),
            timestamp=datetime.fromisoformat(row['timestamp'])
        )
    
    def get_available_events(self) -> List[str]:
        """
        Retorna lista de event_id únicos disponibles en el CSV.
        Útil para exploración y selección de eventos.
        
        Returns:
            Lista de identificadores de eventos.
        """
        raw_data = self._read_csv()
        event_ids = set()
        for row in raw_data:
            event_ids.add(row['event_id'])
        return sorted(list(event_ids))