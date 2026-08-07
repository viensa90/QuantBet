"""
Gestor de base de datos SQLite para QuantBet.
Optimizado con WAL, caché y migraciones.
"""
import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Singleton para la conexión
_connection: Optional[sqlite3.Connection] = None


def get_db() -> sqlite3.Connection:
    """Obtiene la conexión singleton a la BD."""
    global _connection
    if _connection is None:
        db_path = os.environ.get("QUANTBET_DB", "quantbet.db")
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA cache_size=10000")
        _connection.execute("PRAGMA synchronous=NORMAL")
    return _connection


class Database:
    """Gestor de base de datos con inicialización y estadísticas."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("QUANTBET_DB", "quantbet.db")
        self._initialize_database()

    def _initialize_database(self):
        """Crea las tablas e índices si no existen."""
        conn = get_db()
        try:
            # Tablas principales (ya se crean desde repository, pero por si acaso)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    event_name TEXT,
                    market_type TEXT NOT NULL,
                    bookmaker TEXT,
                    odds_data TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    source TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id INTEGER,
                    event_id TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    profit_percent REAL DEFAULT 0.0,
                    odds_data TEXT,
                    stakes TEXT,
                    source TEXT,
                    timestamp DATETIME NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    opportunity_data TEXT NOT NULL,
                    decision_data TEXT NOT NULL,
                    opportunity_score REAL,
                    timestamp DATETIME NOT NULL,
                    executed BOOLEAN DEFAULT 0
                )
            """)
            self._create_indexes()
            logger.debug("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"Error inicializando BD: {e}")
            raise

    def _create_indexes(self):
        """Crea índices para optimizar consultas."""
        conn = get_db()
        cursor = conn.cursor()
        # Índices para snapshots
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_event ON snapshots(event_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_market ON snapshots(market_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp)")
        # Índices para opportunities
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_event ON opportunities(event_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_market ON opportunities(market_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_source ON opportunities(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opps_timestamp ON opportunities(timestamp)")
        # Índices para decisions
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_event ON decisions(event_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_strategy ON decisions(strategy)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp)")
        conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        return get_db()

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de la BD."""
        conn = get_db()
        try:
            cursor = conn.execute("SELECT COUNT(*) as total FROM snapshots")
            total_snapshots = cursor.fetchone()["total"]
            cursor = conn.execute("SELECT COUNT(*) as total FROM opportunities")
            total_opportunities = cursor.fetchone()["total"]
            cursor = conn.execute("SELECT COUNT(*) as total FROM decisions")
            total_decisions = cursor.fetchone()["total"]
            # Tamaño del archivo
            db_size = os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0.0
            # Última ejecución
            cursor = conn.execute("SELECT MAX(timestamp) as last FROM snapshots")
            last = cursor.fetchone()["last"]
            return {
                "total_snapshots": total_snapshots,
                "total_opportunities": total_opportunities,
                "total_decisions": total_decisions,
                "db_size_mb": round(db_size, 2),
                "last_execution": last or "Nunca"
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def cleanup_old_data(self, days: int) -> int:
        """Elimina registros antiguos."""
        cutoff = datetime.now().isoformat()
        conn = get_db()
        try:
            cursor = conn.execute("DELETE FROM snapshots WHERE timestamp < ?", (cutoff,))
            deleted_snap = cursor.rowcount
            cursor = conn.execute("DELETE FROM opportunities WHERE timestamp < ?", (cutoff,))
            deleted_opp = cursor.rowcount
            cursor = conn.execute("DELETE FROM decisions WHERE timestamp < ?", (cutoff,))
            deleted_dec = cursor.rowcount
            conn.commit()
            return deleted_snap + deleted_opp + deleted_dec
        except Exception as e:
            logger.error(f"Error limpiando datos: {e}")
            conn.rollback()
            return 0