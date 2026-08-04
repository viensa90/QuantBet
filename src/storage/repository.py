"""
Repositorio para operaciones CRUD optimizadas
Versión: 0.3.3 (COMPLETA)
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .database import get_db, Database

logger = logging.getLogger(__name__)


class Repository:
    """Repositorio optimizado con consultas eficientes"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializar repositorio
        
        Args:
            db_path: Ruta a la base de datos (opcional, usa singleton)
        """
        self.db = Database()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Asegura que las tablas existan (para compatibilidad)"""
        try:
            conn = get_db()
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='snapshots'
            """)
            if not cursor.fetchone():
                self._create_tables()
        except Exception as e:
            logger.warning(f"Error al verificar tablas: {e}")
    
    def _create_tables(self):
        """Crea las tablas base si no existen"""
        conn = get_db()
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
        logger.info("Tablas base creadas")
    
    # === SNAPSHOTS ===
    
    def save_snapshot(self, snapshot) -> int:
        """
        Guarda un snapshot optimizado con batch insert
        
        Args:
            snapshot: Objeto Snapshot (de domain.entities)
        
        Returns:
            ID del snapshot guardado
        """
        sql = """
            INSERT INTO snapshots (
                event_id, event_name, market_type, bookmaker, odds_data, timestamp, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
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
        conn = get_db()
        cursor = conn.execute(sql, params)
        return cursor.lastrowid
    
    def save_snapshots_batch(self, snapshots: List) -> int:
        """
        Guarda múltiples snapshots en un solo INSERT (batch)
        
        Args:
            snapshots: Lista de objetos Snapshot
        
        Returns:
            Número de snapshots guardados
        """
        if not snapshots:
            return 0
        
        sql = """
            INSERT INTO snapshots (
                event_id, event_name, market_type, bookmaker, odds_data, timestamp, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
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
        conn = get_db()
        conn.executemany(sql, params_list)
        return len(params_list)
    
    def get_latest_snapshots(self, limit: int = 100) -> List:
        """
        Obtiene los últimos snapshots (optimizado con índice por timestamp)
        
        Args:
            limit: Número máximo de snapshots
        
        Returns:
            Lista de objetos Snapshot
        """
        from src.domain.entities import Snapshot
        
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            ORDER BY timestamp DESC
            LIMIT ?
        """
        conn = get_db()
        cursor = conn.execute(sql, (limit,))
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
    
    def get_snapshots_by_event(self, event_id: str) -> List:
        """
        Obtiene snapshots filtrados por evento
        
        Args:
            event_id: ID del evento
        
        Returns:
            Lista de objetos Snapshot
        """
        from src.domain.entities import Snapshot
        
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            WHERE event_id = ?
            ORDER BY timestamp DESC
        """
        conn = get_db()
        cursor = conn.execute(sql, (event_id,))
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
    
    def get_snapshots_by_market(self, market_type: str, limit: int = 100) -> List:
        """
        Obtiene snapshots filtrados por tipo de mercado
        
        Args:
            market_type: Tipo de mercado (ej. "1X2", "Over/Under")
            limit: Número máximo de snapshots
        
        Returns:
            Lista de objetos Snapshot
        """
        from src.domain.entities import Snapshot
        
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            WHERE market_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        conn = get_db()
        cursor = conn.execute(sql, (market_type, limit))
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
    
    def get_snapshots_by_date_range(self, start_date: datetime, end_date: datetime) -> List:
        """
        Obtiene snapshots en un rango de fechas
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Lista de objetos Snapshot
        """
        from src.domain.entities import Snapshot
        
        sql = """
            SELECT id, event_id, event_name, market_type, bookmaker,
                   odds_data, timestamp, source
            FROM snapshots
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """
        conn = get_db()
        cursor = conn.execute(sql, (start_date.isoformat(), end_date.isoformat()))
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
    
    def get_snapshot_count(self) -> int:
        """Obtiene el número total de snapshots"""
        conn = get_db()
        cursor = conn.execute("SELECT COUNT(*) as count FROM snapshots")
        row = cursor.fetchone()
        return row['count'] if row else 0
    
    # === DECISIONES ===
    
    def save_decision(self, decision) -> int:
        """
        Guarda una decisión (oportunidad de apuesta)
        
        Args:
            decision: Objeto Decision (de domain.entities)
        
        Returns:
            ID de la decisión guardada
        """
        sql = """
            INSERT INTO decisions (
                event_id, strategy, opportunity_data, decision_data,
                opportunity_score, timestamp, executed
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            decision.event_id,
            decision.strategy,
            json.dumps(decision.opportunity_data),
            json.dumps(decision.decision_data),
            decision.opportunity_score,
            decision.timestamp.isoformat(),
            decision.executed
        )
        conn = get_db()
        cursor = conn.execute(sql, params)
        return cursor.lastrowid
    
    def save_decisions_batch(self, decisions: List) -> int:
        """
        Guarda múltiples decisiones en batch
        
        Args:
            decisions: Lista de objetos Decision
        
        Returns:
            Número de decisiones guardadas
        """
        if not decisions:
            return 0
        
        sql = """
            INSERT INTO decisions (
                event_id, strategy, opportunity_data, decision_data,
                opportunity_score, timestamp, executed
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params_list = [
            (
                d.event_id,
                d.strategy,
                json.dumps(d.opportunity_data),
                json.dumps(d.decision_data),
                d.opportunity_score,
                d.timestamp.isoformat(),
                d.executed
            )
            for d in decisions
        ]
        conn = get_db()
        conn.executemany(sql, params_list)
        return len(params_list)
    
    def get_latest_decisions(self, limit: int = 100) -> List:
        """
        Obtiene las últimas decisiones
        
        Args:
            limit: Número máximo de decisiones
        
        Returns:
            Lista de objetos Decision
        """
        from src.domain.entities import Decision
        
        sql = """
            SELECT id, event_id, strategy, opportunity_data, decision_data,
                   opportunity_score, timestamp, executed
            FROM decisions
            ORDER BY timestamp DESC
            LIMIT ?
        """
        conn = get_db()
        cursor = conn.execute(sql, (limit,))
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
    
    def get_decisions_by_strategy(self, strategy: str, limit: int = 100) -> List:
        """
        Obtiene decisiones filtradas por estrategia
        
        Args:
            strategy: Estrategia (ej. "arbitrage", "value_betting")
            limit: Número máximo de decisiones
        
        Returns:
            Lista de objetos Decision
        """
        from src.domain.entities import Decision
        
        sql = """
            SELECT id, event_id, strategy, opportunity_data, decision_data,
                   opportunity_score, timestamp, executed
            FROM decisions
            WHERE strategy = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        conn = get_db()
        cursor = conn.execute(sql, (strategy, limit))
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
    
    def get_decisions_by_event(self, event_id: str) -> List:
        """
        Obtiene decisiones filtradas por evento
        
        Args:
            event_id: ID del evento
        
        Returns:
            Lista de objetos Decision
        """
        from src.domain.entities import Decision
        
        sql = """
            SELECT id, event_id, strategy, opportunity_data, decision_data,
                   opportunity_score, timestamp, executed
            FROM decisions
            WHERE event_id = ?
            ORDER BY timestamp DESC
        """
        conn = get_db()
        cursor = conn.execute(sql, (event_id,))
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
    
    def get_decision_count(self, strategy: Optional[str] = None) -> int:
        """
        Obtiene el número total de decisiones
        
        Args:
            strategy: Filtrar por estrategia (opcional)
        
        Returns:
            Número de decisiones
        """
        conn = get_db()
        if strategy:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM decisions WHERE strategy = ?",
                (strategy,)
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) as count FROM decisions")
        row = cursor.fetchone()
        return row['count'] if row else 0
    
    def mark_decision_executed(self, decision_id: int) -> bool:
        """
        Marca una decisión como ejecutada
        
        Args:
            decision_id: ID de la decisión
        
        Returns:
            True si se actualizó correctamente
        """
        conn = get_db()
        cursor = conn.execute(
            "UPDATE decisions SET executed = 1 WHERE id = ?",
            (decision_id,)
        )
        return cursor.rowcount > 0
    
    # === ESTADÍSTICAS ===
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas del repositorio
        
        Returns:
            Diccionario con estadísticas
        """
        return self.db.get_stats()
    
    def cleanup_old_data(self, days: int) -> int:
        """
        Limpia datos antiguos
        
        Args:
            days: Días a conservar
        
        Returns:
            Número de registros eliminados
        """
        return self.db.cleanup_old_data(days)
    
    def get_market_summary(self) -> List[Dict[str, Any]]:
        """
        Obtiene resumen por tipo de mercado
        
        Returns:
            Lista de diccionarios con estadísticas por mercado
        """
        conn = get_db()
        cursor = conn.execute("""
            SELECT 
                market_type,
                COUNT(*) as total_opportunities,
                AVG(opportunity_score) as avg_score,
                MAX(opportunity_score) as max_score,
                COUNT(DISTINCT event_id) as unique_events
            FROM decisions
            GROUP BY market_type
            ORDER BY total_opportunities DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_summary(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Obtiene resumen diario de actividad
        
        Args:
            days: Número de días a incluir
        
        Returns:
            Lista de diccionarios con estadísticas diarias
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        conn = get_db()
        cursor = conn.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_decisions,
                AVG(opportunity_score) as avg_score,
                SUM(CASE WHEN executed = 1 THEN 1 ELSE 0 END) as executed_count
            FROM decisions
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (cutoff,))
        return [dict(row) for row in cursor.fetchall()]