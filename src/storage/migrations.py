"""
src/storage/migrations.py
Gestor de migraciones para SQLite - índices y optimizaciones
Versión: 0.3.1
"""

import sqlite3
import logging
from typing import List, Dict, Any
from pathlib import Path

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
        # Asegurar que el directorio existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
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
        applied_count = 0
        for migration in cls.MIGRATIONS:
            if migration["version"] > current_version:
                logger.info(f"Aplicando migración v{migration['version']}: {migration['description']}")
                for sql in migration["sql"]:
                    try:
                        cursor.execute(sql)
                    except sqlite3.OperationalError as e:
                        logger.warning(f"Error en migración v{migration['version']}: {e}")
                        # Continuar con la siguiente sentencia SQL
                        continue
                
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?);",
                    (migration["version"],)
                )
                conn.commit()
                applied_count += 1
                logger.info(f"Migración v{migration['version']} completada")
        
        conn.close()
        if applied_count > 0:
            logger.info(f"Se aplicaron {applied_count} migraciones")
        else:
            logger.info("No hay migraciones pendientes")
    
    @classmethod
    def get_current_version(cls, db_path: str = "quantbet.db") -> int:
        """Obtiene la versión actual del esquema"""
        if not Path(db_path).exists():
            return 0
            
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
    
    @classmethod
    def get_migration_status(cls, db_path: str = "quantbet.db") -> Dict[str, Any]:
        """Obtiene el estado de las migraciones"""
        current = cls.get_current_version(db_path)
        total = len(cls.MIGRATIONS)
        
        return {
            "current_version": current,
            "total_migrations": total,
            "pending": total - current,
            "is_up_to_date": current >= total,
            "migrations": [
                {
                    "version": m["version"],
                    "description": m["description"],
                    "applied": m["version"] <= current
                }
                for m in cls.MIGRATIONS
            ]
        }

def apply_migrations(db_path: str = "quantbet.db"):
    """Función de utilidad para aplicar migraciones"""
    MigrationManager.run_migrations(db_path)