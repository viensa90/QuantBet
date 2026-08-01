"""
tests/test_migrations.py
Pruebas para el sistema de migraciones y optimizaciones
Versión: 0.3.1
"""

import os
import sqlite3
import tempfile
import pytest
from pathlib import Path

from src.storage.migrations import MigrationManager, apply_migrations
from src.storage.database import Database

class TestMigrations:
    """Pruebas de integridad para migraciones"""
    
    def test_migration_creation(self):
        """Verifica que las migraciones se apliquen correctamente"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Aplicar migraciones
            MigrationManager.run_migrations(db_path)
            
            # Verificar tabla de versiones
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version';")
            assert cursor.fetchone() is not None
            
            # Verificar índices
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
            indexes = [row[0] for row in cursor.fetchall()]
            
            expected_indexes = [
                'idx_snapshots_timestamp',
                'idx_snapshots_event_id',
                'idx_snapshots_market_type',
                'idx_decisions_timestamp',
                'idx_decisions_event_id',
                'idx_decisions_strategy',
                'idx_snapshots_event_market',
                'idx_decisions_event_strategy'
            ]
            
            for idx in expected_indexes:
                assert idx in indexes, f"Índice {idx} no encontrado"
            
            # Verificar tabla market_summary
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_summary';")
            assert cursor.fetchone() is not None
            
            conn.close()
            
        finally:
            os.unlink(db_path)
    
    def test_migration_idempotency(self):
        """Verifica que las migraciones sean idempotentes"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Aplicar dos veces
            MigrationManager.run_migrations(db_path)
            MigrationManager.run_migrations(db_path)
            
            # Verificar que no haya duplicados en schema_version
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT version, COUNT(*) FROM schema_version GROUP BY version;")
            rows = cursor.fetchall()
            
            for row in rows:
                assert row[1] == 1, f"Versión {row[0]} duplicada {row[1]} veces"
            
            conn.close()
            
        finally:
            os.unlink(db_path)
    
    def test_pragma_optimizations(self):
        """Verifica que las PRAGMA de optimización se apliquen"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Inicializar Database (aplica PRAGMA)
            db = Database(db_path)
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar PRAGMA
                cursor.execute("PRAGMA journal_mode;")
                journal_mode = cursor.fetchone()[0]
                assert journal_mode.lower() in ['wal', 'memory', 'delete', 'truncate', 'persist'], \
                       f"Journal mode no válido: {journal_mode}"
                
                cursor.execute("PRAGMA synchronous;")
                sync_mode = cursor.fetchone()[0]
                assert sync_mode in [0, 1, 2, 'OFF', 'NORMAL', 'FULL'], \
                       f"Synchronous no válido: {sync_mode}"
                
                cursor.execute("PRAGMA cache_size;")
                cache_size = cursor.fetchone()[0]
                assert cache_size <= -20000 or cache_size >= 20000, \
                       f"Cache size no válido: {cache_size}"
            
            db.close()
            
        finally:
            os.unlink(db_path)
    
    def test_market_summary_constraints(self):
        """Verifica las restricciones UNIQUE en market_summary"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Aplicar migraciones
            MigrationManager.run_migrations(db_path)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Insertar registro
            cursor.execute("""
                INSERT INTO market_summary (event_id, market_type, best_opportunity, total_opportunities, avg_score)
                VALUES ('event1', '1X2', 85.5, 5, 82.3);
            """)
            conn.commit()
            
            # Intentar insertar duplicado (debe fallar)
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO market_summary (event_id, market_type, best_opportunity, total_opportunities, avg_score)
                    VALUES ('event1', '1X2', 90.0, 3, 88.0);
                """)
                conn.commit()
            
            # ON CONFLICT UPDATE debe funcionar
            cursor.execute("""
                INSERT INTO market_summary (event_id, market_type, best_opportunity, total_opportunities, avg_score)
                VALUES ('event1', '1X2', 90.0, 3, 88.0)
                ON CONFLICT(event_id, market_type) DO UPDATE SET
                    best_opportunity = excluded.best_opportunity,
                    total_opportunities = excluded.total_opportunities,
                    avg_score = excluded.avg_score;
            """)
            conn.commit()
            
            # Verificar actualización
            cursor.execute("""
                SELECT best_opportunity, total_opportunities, avg_score
                FROM market_summary
                WHERE event_id = 'event1' AND market_type = '1X2';
            """)
            row = cursor.fetchone()
            assert row[0] == 90.0
            assert row[1] == 3
            assert row[2] == 88.0
            
            conn.close()
            
        finally:
            os.unlink(db_path)
    
    def test_get_current_version(self):
        """Verifica la obtención de la versión actual"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Sin migraciones
            version = MigrationManager.get_current_version(db_path)
            assert version == 0
            
            # Aplicar migraciones
            MigrationManager.run_migrations(db_path)
            
            version = MigrationManager.get_current_version(db_path)
            assert version == 5  # Última versión de migración
            
        finally:
            os.unlink(db_path)
    
    def test_migration_status(self):
        """Verifica el estado de las migraciones"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Obtener estado antes de migrar
            status = MigrationManager.get_migration_status(db_path)
            assert status["current_version"] == 0
            assert status["total_migrations"] == 5
            assert status["pending"] == 5
            assert not status["is_up_to_date"]
            
            # Aplicar migraciones
            MigrationManager.run_migrations(db_path)
            
            # Obtener estado después de migrar
            status = MigrationManager.get_migration_status(db_path)
            assert status["current_version"] == 5
            assert status["pending"] == 0
            assert status["is_up_to_date"]
            
        finally:
            os.unlink(db_path)