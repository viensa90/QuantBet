"""
src/storage/migrations.py
Gestor de migraciones para SQLite - índices y optimizaciones
"""

import sqlite3
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class MigrationManager:
    """Gestiona migraciones de esquema e índices para SQLite"""
    
    MIGRATIONS = [
        {
            "version": 1,
            "description": "Índices para snapshots",
            "sql": [
                "CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_snapshots_event_id ON snapshots(event_id);",
                "CREATE INDEX IF NOT EXISTS idx_snapshots_market_type ON snapshots(market_type);",
                "CREATE INDEX IF NOT EXISTS idx_snapshots_bookmaker ON snapshots(bookmaker);"
            ]
        },
        {
            "version": 2,
            "description": "Índices para decisiones",
            "sql": [
                "CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_decisions_event_id ON decisions(event_id);",
                "CREATE INDEX IF NOT EXISTS idx_decisions_strategy ON decisions(strategy);",
                "CREATE INDEX IF NOT EXISTS idx_decisions_opportunity_score ON decisions(opportunity_score);"
            ]
        },
        {
            "version": 3,
            "description": "Índices compuestos para búsquedas frecuentes",
            "sql": [
                "CREATE INDEX IF NOT EXISTS idx_snapshots_event_market ON snapshots(event_id, market_type);",
                "CREATE INDEX IF NOT EXISTS idx_decisions_event_strategy ON decisions(event_id, strategy);",
                "CREATE INDEX IF NOT EXISTS idx_decisions_timestamp_strategy ON decisions(timestamp, strategy);"
            ]
        },
        {
            "version": 4,
            "description": "Tabla de resumen para dashboard (vista materializada)",
            "sql": [
                """CREATE TABLE IF NOT EXISTS market_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    best_opportunity REAL,
                    total_opportunities INTEGER,
                    avg_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(event_id, market_type)
                );""",
                "CREATE INDEX IF NOT EXISTS idx_summary_timestamp ON market_summary(timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_summary_event ON market_summary(event_id);"
            ]
        },
        {
            "version": 5,
            "description": "Configuración de rendimiento para SQLite",
            "sql": [
                "PRAGMA journal_mode=WAL;",
                "PRAGMA synchronous=NORMAL;",
                "PRAGMA cache_size=-20000;",  # 20MB cache
                "PRAGMA temp_store=MEMORY;"
            ]
        }
    ]
    
    @classmethod
    def run_migrations(cls, db_path: str = "quantbet.db"):
        """Ejecuta todas las migraciones pendientes"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla de versiones si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Obtener última versión aplicada
        cursor.execute("SELECT MAX(version) FROM schema_version;")
        result = cursor.fetchone()
        current_version = result[0] if result[0] is not None else 0
        
        logger.info(f"Versión actual de esquema: {current_version}")
        
        # Aplicar migraciones pendientes
        for migration in cls.MIGRATIONS:
            if migration["version"] > current_version:
                logger.info(f"Aplicando migración v{migration['version']}: {migration['description']}")
                for sql in migration["sql"]:
                    try:
                        cursor.execute(sql)
                    except sqlite3.OperationalError as e:
                        logger.warning(f"Error en migración v{migration['version']}: {e}")
                
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?);",
                    (migration["version"],)
                )
                conn.commit()
                logger.info(f"Migración v{migration['version']} completada")
        
        conn.close()
        logger.info("Todas las migraciones aplicadas correctamente")
    
    @classmethod
    def get_current_version(cls, db_path: str = "quantbet.db") -> int:
        """Obtiene la versión actual del esquema"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(version) FROM schema_version;")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except sqlite3.OperationalError:
            return 0
        finally:
            conn.close()

def apply_migrations(db_path: str = "quantbet.db"):
    """Función de utilidad para aplicar migraciones"""
    MigrationManager.run_migrations(db_path)