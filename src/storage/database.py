"""
src/storage/database.py
Singleton para conexión SQLite optimizada
Versión: 0.3.1
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """Singleton para gestión de conexión SQLite con optimizaciones"""
    
    _instance: Optional['Database'] = None
    _connection: Optional[sqlite3.Connection] = None
    _db_path: str = "quantbet.db"
    
    def __new__(cls, db_path: str = "quantbet.db"):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._db_path = db_path
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa la conexión con optimizaciones de rendimiento"""
        if self._connection is None:
            # Asegurar directorio
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self._connection = sqlite3.connect(
                self._db_path,
                timeout=10.0,  # Timeout para operaciones bloqueadas
                check_same_thread=False,  # Permitir uso en múltiples hilos
                isolation_level=None  # Modo autocommit
            )
            
            # PRAGMAS de rendimiento
            self._connection.execute("PRAGMA journal_mode=WAL;")
            self._connection.execute("PRAGMA synchronous=NORMAL;")
            self._connection.execute("PRAGMA cache_size=-20000;")  # 20MB
            self._connection.execute("PRAGMA temp_store=MEMORY;")
            self._connection.execute("PRAGMA foreign_keys=ON;")
            
            # Row factory para acceso por nombre de columna
            self._connection.row_factory = sqlite3.Row
            
            logger.info(f"Base de datos SQLite inicializada: {self._db_path}")
            logger.info("Optimizaciones aplicadas: WAL, NORMAL sync, cache 20MB")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager para obtener conexión"""
        if self._connection is None:
            self._initialize()
        
        try:
            yield self._connection
        except sqlite3.Error as e:
            logger.error(f"Error en operación SQLite: {e}")
            self._connection.rollback()
            raise
        finally:
            # No cerramos la conexión, solo liberamos recursos si es necesario
            pass
    
    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager para obtener cursor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Ejecuta SQL directamente con parámetros"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor
    
    def executemany(self, sql: str, params: list) -> sqlite3.Cursor:
        """Ejecuta SQL con múltiples parámetros"""
        with self.get_cursor() as cursor:
            cursor.executemany(sql, params)
            return cursor
    
    def close(self):
        """Cierra la conexión (para testing/cleanup)"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Conexión SQLite cerrada")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la conexión"""
        if not self._connection:
            return {"status": "not_initialized"}
        
        cursor = self._connection.cursor()
        
        try:
            # Obtener tamaño de la BD
            cursor.execute("SELECT page_count * page_size FROM pragma_page_count, pragma_page_size;")
            size_bytes = cursor.fetchone()[0]
            
            # Obtener número de tablas
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            table_count = cursor.fetchone()[0]
            
            # Estado de WAL
            cursor.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0]
            
        except sqlite3.Error as e:
            logger.warning(f"Error al obtener estadísticas: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
        
        return {
            "status": "connected",
            "db_path": self._db_path,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "table_count": table_count,
            "journal_mode": journal_mode,
            "cache_size": -20000  # 20MB
        }

# Función de utilidad para acceder a la instancia
def get_db(db_path: str = "quantbet.db") -> Database:
    """Retorna la instancia singleton de Database"""
    return Database(db_path)