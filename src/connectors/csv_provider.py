# src/connectors/csv_provider.py
"""
Proveedor de datos desde archivo CSV.
Implementa el contrato IDataProvider.
Principios:
- Solo obtiene datos, nunca decide.
- Normaliza los datos al formato Snapshot del dominio.
- Cada fila del CSV se convierte en un Snapshot inmutable.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from collections import defaultdict

from .base import IDataProvider
from src.domain.entities import Snapshot


class CSVProvider(IDataProvider):
    """
    Proveedor de datos simulado desde archivo CSV.
    
    El CSV debe tener al menos las columnas:
    - event_id: Identificador del evento
    - event_name: Nombre del evento
    - market_type: Tipo de mercado (1X2, Over/Under, etc.)
    - bookmaker_name: Nombre de la casa de apuestas
    - outcome_label: Etiqueta del resultado (ej: "Local", "Empate", "Visitante")
    - odds: Cuota (float)
    - timestamp: Fecha/hora en formato ISO
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
        2. Agrupa por (event_id, market_type, bookmaker_name)
        3. Convierte cada grupo en un objeto Snapshot del dominio
        4. Filtra por event_id si se especifica
        5. Retorna lista de snapshots inmutables
        
        Args:
            event_id: Opcional. Filtra snapshots por evento específico.
            
        Returns:
            Lista de Snapshot listos para el Motor de Análisis.
        """
        raw_data = self._read_csv()
        
        # Agrupar por (event_id, market_type, bookmaker_name)
        groups = defaultdict(lambda: defaultdict(dict))
        
        for row in raw_data:
            # Filtro por evento si se especifica
            if event_id and row.get('event_id') != event_id:
                continue
            
            key = (row['event_id'], row.get('market_type', '1X2'), row.get('bookmaker_name', 'unknown'))
            outcome = row.get('outcome_label', 'unknown')
            odds = float(row['odds'])
            
            # Almacenar la cuota para este resultado
            groups[key][outcome] = odds
        
        snapshots = []
        for (event_id, market_type, bookmaker), odds_data in groups.items():
            # Buscar el event_name (tomar de la primera fila del grupo)
            event_name = next(
                (row.get('event_name', '') for row in raw_data 
                 if row.get('event_id') == event_id),
                ''
            )
            
            # Buscar el timestamp (tomar de la primera fila del grupo)
            timestamp_str = next(
                (row.get('timestamp') for row in raw_data 
                 if row.get('event_id') == event_id),
                datetime.now().isoformat()
            )
            
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                timestamp = datetime.now()
            
            snapshot = Snapshot(
                event_id=event_id,
                event_name=event_name,
                market_type=market_type,
                bookmaker=bookmaker,
                odds_data=odds_data,          # Dict[str, float]
                timestamp=timestamp,
                source=self._provider_name,
                metadata={}                  # ✅ Campo añadido
            )
            snapshots.append(snapshot)
        
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