"""
Gestor de base de datos SQLite optimizado
Versión: 0.3.3 (COMPLETA)
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import threading
import os

from ..config_loader import ConfigLoader


class Database:
    """Singleton para gestión de base de datos SQLite optimizada"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Database, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = ConfigLoader().config.get("database", {})
        self.db_path = self.config.get("path", "quantbet.db")
        self._initialized = True
        self._connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializar base de datos con optimizaciones"""
        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Conectar y optimizar
        conn = self.get_connection()
        
        # Configuraciones de rendimiento
        if self.config.get("wal_mode", True):
            conn.execute("PRAGMA journal_mode=WAL")
        
        if self.config.get("cache_size", 10000):
            conn.execute(f"PRAGMA cache_size={self.config.get('cache_size', 10000)}")
        
        conn.execute(f"PRAGMA synchronous={self.config.get('sync_mode', 'NORMAL')}")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=30000000000")
        
        # Crear tablas
        self._create_tables()
        
        # Crear índices
        self._create_indexes()
    
    def _create_tables(self):
        """Crear tablas si no existen"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla: snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                event_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                event_id TEXT NOT NULL,
                sport TEXT NOT NULL,
                market_type TEXT NOT NULL,
                event_name TEXT NOT NULL,
                odds TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            )
        """)
        
        # Tabla: opportunities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                event_id TEXT NOT NULL,
                sport TEXT NOT NULL,
                market_type TEXT NOT NULL,
                strategy TEXT NOT NULL,
                profit_percent REAL,
                odds TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            )
        """)
        
        # Tabla: market_summary (para estadísticas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_type TEXT NOT NULL,
                sport TEXT NOT NULL,
                opportunity_count INTEGER,
                avg_profit REAL,
                max_profit REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def _create_indexes(self):
        """Crear índices para optimizar queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Índice para búsquedas por timestamp
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_timestamp ON opportunities(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
        
        # Índice para búsquedas por estrategia
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_strategy ON opportunities(strategy)")
        
        # Índice para búsquedas por deporte/mercado
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_sport ON opportunities(sport, market_type)")
        
        # Índice para búsquedas por snapshot
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_snapshot ON opportunities(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_snapshot ON events(snapshot_id)")
        
        conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30
            )
            # Permitir acceso por nombre de columna
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Ejecutar query y devolver cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def executemany(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """Ejecutar múltiples queries en batch"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Ejecutar query y devolver todos los resultados como dicts"""
        cursor = self.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Ejecutar query y devolver un resultado como dict"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insertar registro y devolver ID"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.execute(query, tuple(data.values()))
        return cursor.lastrowid
    
    def insert_batch(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insertar múltiples registros en batch"""
        if not data_list:
            return 0
        
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['?'] * len(data_list[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        params_list = [tuple(data.values()) for data in data_list]
        cursor = self.executemany(query, params_list)
        return len(params_list)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        stats = {}
        
        # Total snapshots
        result = self.fetch_one("SELECT COUNT(*) as count FROM snapshots")
        stats["total_snapshots"] = result["count"] if result else 0
        
        # Total oportunidades
        result = self.fetch_one("SELECT COUNT(*) as count FROM opportunities")
        stats["total_opportunities"] = result["count"] if result else 0
        
        # Por estrategia
        results = self.fetch_all(
            "SELECT strategy, COUNT(*) as count FROM opportunities GROUP BY strategy"
        )
        for row in results:
            stats[f"{row['strategy']}_count"] = row["count"]
        
        # Última ejecución
        result = self.fetch_one(
            "SELECT timestamp FROM snapshots ORDER BY timestamp DESC LIMIT 1"
        )
        stats["last_execution"] = result["timestamp"] if result else "N/A"
        
        # Tamaño de la base de datos
        if os.path.exists(self.db_path):
            stats["db_size_mb"] = os.path.getsize(self.db_path) / (1024 * 1024)
        else:
            stats["db_size_mb"] = 0
        
        return stats
    
    def cleanup_old_data(self, days: int) -> int:
        """Eliminar datos antiguos y devolver número de registros eliminados"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Eliminar oportunidades antiguas
        cursor.execute(
            "DELETE FROM opportunities WHERE timestamp < ?",
            (cutoff_str,)
        )
        opp_count = cursor.rowcount
        
        # Eliminar eventos antiguos
        cursor.execute(
            "DELETE FROM events WHERE timestamp < ?",
            (cutoff_str,)
        )
        event_count = cursor.rowcount
        
        # Eliminar snapshots antiguos
        cursor.execute(
            "DELETE FROM snapshots WHERE timestamp < ?",
            (cutoff_str,)
        )
        snap_count = cursor.rowcount
        
        conn.commit()
        
        return opp_count + event_count + snap_count
    
    def vacuum(self):
        """Optimizar la base de datos"""
        conn = self.get_connection()
        conn.execute("VACUUM")
        conn.commit()


# --- ALIAS PARA COMPATIBILIDAD CON CÓDIGO EXISTENTE ---
DatabaseManager = Database


# --- FUNCIÓN DE CONVENIENCIA PARA REPOSITORY.PY ---
def get_db(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Obtener conexión a la base de datos (función de conveniencia)
    
    Args:
        db_path: Ruta opcional a la base de datos (ignorada, usa singleton)
    
    Returns:
        Conexión SQLite
    """
    return Database().get_connection()