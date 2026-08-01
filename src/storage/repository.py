"""
src/storage/repository.py
CRUD optimizado para snapshots y decisiones
Versión: 0.3.1
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.storage.database import get_db
from src.domain.entities import Snapshot, Decision

logger = logging.getLogger(__name__)

class Repository:
    """Repositorio optimizado con consultas eficientes"""
    
    def __init__(self, db_path: str = "quantbet.db"):
        self.db = get_db(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Asegura que las tablas existan (para compatibilidad)"""
        try:
            # Verificar si la tabla snapshots existe
            cursor = self.db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='snapshots';
            """)
            if not cursor.fetchone():
                # Crear tablas si no existen (para tests)
                self._create_tables()
        except Exception as e:
            logger.warning(f"Error al verificar tablas: {e}")
    
    def _create_tables(self):
        """Crea las tablas base si no existen"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                event_name TEXT,
                market_type TEXT NOT NULL,
                bookmaker TEXT,
                odds_data TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                source TEXT
            );
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                strategy TEXT NOT NULL,
                opportunity_data TEXT NOT NULL,
                decision_data TEXT NOT NULL,
                opportunity_score REAL,
                timestamp DATETIME NOT NULL,
                executed BOOLEAN DEFAULT 0
            );
        """)
        logger.info("Tablas base creadas")
    
    # === SNAPSHOTS ===
    
    def save_snapshot(self, snapshot: Snapshot) -> int:
        """Guarda un snapshot optimizado con batch insert"""
        sql = """
            INSERT INTO snapshots (
                event_id, event_name, market_type, bookmaker,
                odds_data, timestamp, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            snapshot.event_id,
            snapshot.event_name,
            snapshot.market_type,
            snapshot.bookmaker,
            json.dumps(snapshot.odds_data),
            snapshot.timestamp.isoformat(),
            snapshot.source
        )
        
        cursor = self.db.execute(sql, params)
        return cursor.lastrowid
    
    def save_snapshots_batch(self, snapshots: List[Snapshot]) -> int:
        """Guarda múltiples snapshots en un solo INSERT (batch)"""
        if not snapshots:
            return 0
        
        sql = """
            INSERT INTO snapshots (
                event_id, event_name, market_type, bookmaker,
                odds_data, timestamp, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        params_list = [
            (
                s.event_id,
                s.event_name,
                s.market_type,
                s.bookmaker,
                json.dumps(s.odds_data),
                s.timestamp.isoformat(),
                s.source
            )
            for s in snapshots
        ]
        
        self.db.executemany(sql, params_list)
        return len(params_list)
    
    def get_latest_snapshots(self, limit: int = 100) -> List[Snapshot]:
        """Obtiene los últimos snapshots (optimizado con índice por timestamp)"""
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            ORDER BY timestamp DESC
            LIMIT ?;
        """
        cursor = self.db.execute(sql, (limit,))
        rows = cursor.fetchall()
        
        return [
            Snapshot(
                event_id=row['event_id'],
                event_name=row['event_name'],
                market_type=row['market_type'],
                bookmaker=row['bookmaker'],
                odds_data=json.loads(row['odds_data']),
                timestamp=datetime.fromisoformat(row['timestamp']),
                source=row['source']
            )
            for row in rows
        ]
    
    def get_snapshots_by_event(self, event_id: str) -> List[Snapshot]:
        """Obtiene snapshots por evento (optimizado con índice compuesto)"""
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            WHERE event_id = ?
            ORDER BY timestamp DESC;
        """
        cursor = self.db.execute(sql, (event_id,))
        rows = cursor.fetchall()
        
        return [
            Snapshot(
                event_id=row['event_id'],
                event_name=row['event_name'],
                market_type=row['market_type'],
                bookmaker=row['bookmaker'],
                odds_data=json.loads(row['odds_data']),
                timestamp=datetime.fromisoformat(row['timestamp']),
                source=row['source']
            )
            for row in rows
        ]
    
    def get_latest_snapshot_by_event_market(self, event_id: str, market_type: str) -> Optional[Snapshot]:
        """Obtiene el snapshot más reciente para un evento y mercado específico"""
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            WHERE event_id = ? AND market_type = ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        cursor = self.db.execute(sql, (event_id, market_type))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return Snapshot(
            event_id=row['event_id'],
            event_name=row['event_name'],
            market_type=row['market_type'],
            bookmaker=row['bookmaker'],
            odds_data=json.loads(row['odds_data']),
            timestamp=datetime.fromisoformat(row['timestamp']),
            source=row['source']
        )
    
    # === DECISIONES ===
    
    def save_decision(self, decision: Decision) -> int:
        """Guarda una decisión"""
        sql = """
            INSERT INTO decisions (
                event_id, strategy, opportunity_data, decision_data,
                opportunity_score, timestamp, executed
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            decision.event_id,
            decision.strategy,
            json.dumps(decision.opportunity_data),
            json.dumps(decision.decision_data),
            decision.opportunity_score,
            decision.timestamp.isoformat(),
            1 if decision.executed else 0
        )
        
        cursor = self.db.execute(sql, params)
        return cursor.lastrowid
    
    def save_decisions_batch(self, decisions: List[Decision]) -> int:
        """Guarda múltiples decisiones en batch"""
        if not decisions:
            return 0
        
        sql = """
            INSERT INTO decisions (
                event_id, strategy, opportunity_data, decision_data,
                opportunity_score, timestamp, executed
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        params_list = [
            (
                d.event_id,
                d.strategy,
                json.dumps(d.opportunity_data),
                json.dumps(d.decision_data),
                d.opportunity_score,
                d.timestamp.isoformat(),
                1 if d.executed else 0
            )
            for d in decisions
        ]
        
        self.db.executemany(sql, params_list)
        return len(params_list)
    
    def get_decisions_by_event(self, event_id: str, limit: int = 50) -> List[Decision]:
        """Obtiene decisiones por evento (optimizado con índice compuesto)"""
        sql = """
            SELECT id, event_id, strategy, opportunity_data, decision_data,
                   opportunity_score, timestamp, executed
            FROM decisions
            WHERE event_id = ?
            ORDER BY timestamp DESC
            LIMIT ?;
        """
        cursor = self.db.execute(sql, (event_id, limit))
        rows = cursor.fetchall()
        
        return [
            Decision(
                event_id=row['event_id'],
                strategy=row['strategy'],
                opportunity_data=json.loads(row['opportunity_data']),
                decision_data=json.loads(row['decision_data']),
                opportunity_score=row['opportunity_score'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                executed=bool(row['executed'])
            )
            for row in rows
        ]
    
    def get_top_opportunities(self, limit: int = 20, min_score: float = 70.0) -> List[Dict[str, Any]]:
        """Obtiene las mejores oportunidades (optimizado con índice)"""
        sql = """
            SELECT event_id, strategy, opportunity_score, 
                   opportunity_data, timestamp
            FROM decisions
            WHERE opportunity_score >= ?
            ORDER BY opportunity_score DESC
            LIMIT ?;
        """
        cursor = self.db.execute(sql, (min_score, limit))
        rows = cursor.fetchall()
        
        return [
            {
                "event_id": row['event_id'],
                "strategy": row['strategy'],
                "score": row['opportunity_score'],
                "data": json.loads(row['opportunity_data']),
                "timestamp": row['timestamp']
            }
            for row in rows
        ]
    
    # === MARKET SUMMARY (Vista Materializada) ===
    
    def update_market_summary(self, event_id: str, market_type: str, 
                              best_opportunity: float, total_opportunities: int,
                              avg_score: float):
        """Actualiza o inserta el resumen de mercado para dashboard rápido"""
        sql = """
            INSERT INTO market_summary (
                event_id, market_type, best_opportunity,
                total_opportunities, avg_score, timestamp
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(event_id, market_type) DO UPDATE SET
                best_opportunity = excluded.best_opportunity,
                total_opportunities = excluded.total_opportunities,
                avg_score = excluded.avg_score,
                timestamp = CURRENT_TIMESTAMP;
        """
        self.db.execute(sql, (event_id, market_type, best_opportunity, 
                              total_opportunities, avg_score))
    
    def get_market_summary(self, limit: int = 50, min_opportunities: int = 1) -> List[Dict[str, Any]]:
        """Obtiene el resumen de mercado para el dashboard (rápido)"""
        sql = """
            SELECT event_id, market_type, best_opportunity,
                   total_opportunities, avg_score, timestamp
            FROM market_summary
            WHERE total_opportunities >= ?
            ORDER BY best_opportunity DESC, avg_score DESC
            LIMIT ?;
        """
        cursor = self.db.execute(sql, (min_opportunities, limit))
        rows = cursor.fetchall()
        
        return [
            {
                "event_id": row['event_id'],
                "market_type": row['market_type'],
                "best_opportunity": row['best_opportunity'],
                "total_opportunities": row['total_opportunities'],
                "avg_score": row['avg_score'],
                "timestamp": row['timestamp']
            }
            for row in rows
        ]
    
    # === ESTADÍSTICAS Y MANTENIMIENTO ===
    
    def get_db_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos"""
        stats = {
            "snapshots": {},
            "decisions": {},
            "summary": {}
        }
        
        try:
            # Conteo de snapshots
            cursor = self.db.execute("SELECT COUNT(*) FROM snapshots;")
            stats["snapshots"]["total"] = cursor.fetchone()[0]
            
            # Conteo por mercado
            cursor = self.db.execute("""
                SELECT market_type, COUNT(*) as count
                FROM snapshots
                GROUP BY market_type;
            """)
            stats["snapshots"]["by_market"] = {row['market_type']: row['count'] for row in cursor.fetchall()}
            
            # Último snapshot
            cursor = self.db.execute("""
                SELECT MAX(timestamp) as last_timestamp
                FROM snapshots;
            """)
            row = cursor.fetchone()
            stats["snapshots"]["last_timestamp"] = row['last_timestamp'] if row else None
            
            # Conteo de decisiones
            cursor = self.db.execute("SELECT COUNT(*) FROM decisions;")
            stats["decisions"]["total"] = cursor.fetchone()[0]
            
            # Conteo por estrategia
            cursor = self.db.execute("""
                SELECT strategy, COUNT(*) as count
                FROM decisions
                GROUP BY strategy;
            """)
            stats["decisions"]["by_strategy"] = {row['strategy']: row['count'] for row in cursor.fetchall()}
            
            # Score promedio
            cursor = self.db.execute("SELECT AVG(opportunity_score) FROM decisions;")
            result = cursor.fetchone()
            stats["decisions"]["avg_score"] = round(result[0] or 0, 2)
            
            # Resumen de mercado
            cursor = self.db.execute("SELECT COUNT(*) FROM market_summary;")
            stats["summary"]["total_markets"] = cursor.fetchone()[0]
            
        except Exception as e:
            logger.warning(f"Error al obtener estadísticas: {e}")
            stats["error"] = str(e)
        
        return stats
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Limpia datos antiguos para mantener rendimiento"""
        if days_to_keep <= 0:
            logger.warning("days_to_keep debe ser mayor que 0")
            return
        
        # Eliminar snapshots antiguos
        sql_snapshots = """
            DELETE FROM snapshots
            WHERE timestamp < datetime('now', ?);
        """
        days_param = f"-{days_to_keep} days"
        cursor = self.db.execute(sql_snapshots, (days_param,))
        deleted_snapshots = cursor.rowcount
        
        # Eliminar decisiones antiguas (conservar las de mayor score)
        sql_decisions = """
            DELETE FROM decisions
            WHERE timestamp < datetime('now', ?)
            AND opportunity_score < 50;
        """
        cursor = self.db.execute(sql_decisions, (days_param,))
        deleted_decisions = cursor.rowcount
        
        # Limpiar summary antiguo
        sql_summary = """
            DELETE FROM market_summary
            WHERE timestamp < datetime('now', ?);
        """
        cursor = self.db.execute(sql_summary, (days_param,))
        deleted_summary = cursor.rowcount
        
        # Vacuum para compactar BD
        self.db.execute("VACUUM;")
        
        logger.info(f"Limpieza completada: {deleted_snapshots} snapshots, "
                   f"{deleted_decisions} decisiones, {deleted_summary} resúmenes eliminados")
        logger.info(f"Datos anteriores a {days_to_keep} días eliminados")