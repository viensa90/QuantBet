"""
Repositorio para operaciones CRUD optimizadas
Versión: 0.3.3 (COMPLETA - con migración automática de esquema)
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .database import get_db, Database

logger = logging.getLogger(__name__)


class Repository:
    """Repositorio optimizado con consultas eficientes"""

    def __init__(self, db_path: Optional[str] = None):
        self.db = Database()
        self._ensure_tables()
        self._migrate_if_needed()

    # ------------------------------------------------------------------
    # Métodos de inicialización y migración
    # ------------------------------------------------------------------
    def _ensure_tables(self):
        """Asegura que las tablas base existan (si no, las crea)."""
        try:
            conn = get_db()
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='snapshots'
            """)
            if not cursor.fetchone():
                self._create_tables()
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='opportunities'
            """)
            if not cursor.fetchone():
                self._create_opportunities_table()
        except Exception as e:
            logger.warning(f"Error al verificar tablas: {e}")

    def _migrate_if_needed(self):
        """Elimina y recrea tablas si su estructura no coincide con la esperada."""
        expected_snapshots_cols = {
            'id', 'event_id', 'event_name', 'market_type', 'bookmaker',
            'odds_data', 'timestamp', 'source'
        }
        expected_opportunities_cols = {
            'id', 'snapshot_id', 'event_id', 'market_type', 'profit_percent',
            'odds_data', 'stakes', 'source', 'timestamp'
        }
        conn = get_db()
        try:
            # Verificar snapshots
            cursor = conn.execute("PRAGMA table_info(snapshots)")
            existing = {row['name'] for row in cursor.fetchall()}
            if existing and not expected_snapshots_cols.issubset(existing):
                logger.warning("Estructura de snapshots obsoleta. Recreando...")
                conn.execute("DROP TABLE IF EXISTS snapshots")
                self._create_tables()

            # Verificar opportunities
            cursor = conn.execute("PRAGMA table_info(opportunities)")
            existing = {row['name'] for row in cursor.fetchall()}
            if existing and not expected_opportunities_cols.issubset(existing):
                logger.warning("Estructura de opportunities obsoleta. Recreando...")
                conn.execute("DROP TABLE IF EXISTS opportunities")
                self._create_opportunities_table()
        except Exception as e:
            logger.error(f"Error durante migración: {e}")

    def _create_tables(self):
        """Crea las tablas base con la estructura actualizada."""
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

    def _create_opportunities_table(self):
        """Crea la tabla de oportunidades (arbitraje, value betting, dutching)."""
        conn = get_db()
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
        logger.info("Tabla opportunities creada")

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------
    def save_snapshot(self, snapshot) -> int:
        """
        Guarda un snapshot (objeto Snapshot).
        Retorna el ID del snapshot guardado.
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
        """Guarda múltiples snapshots en batch."""
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
        conn = get_db()
        cursor = conn.execute("SELECT COUNT(*) as count FROM snapshots")
        row = cursor.fetchone()
        return row['count'] if row else 0

    # ------------------------------------------------------------------
    # Oportunidades (Arbitraje, Value Betting, Dutching)
    # ------------------------------------------------------------------
    def save_opportunities(self, opportunities: List[Any], snapshot_id: int) -> int:
        """
        Guarda una lista de oportunidades (objetos Opportunity o dicts).
        """
        if not opportunities:
            return 0
        conn = get_db()
        try:
            cursor = conn.cursor()
            count = 0
            for opp in opportunities:
                if isinstance(opp, dict):
                    event_id = opp.get("event_id", "")
                    market_type = opp.get("market_type", "")
                    profit = opp.get("profit_percent", 0.0)
                    odds_json = json.dumps(opp.get("odds", {}))
                    stakes_json = json.dumps(opp.get("stakes", {}))
                    source = opp.get("source", "")
                    timestamp_str = opp.get("timestamp", datetime.now().isoformat())
                else:
                    event_id = opp.event_id
                    market_type = opp.market_type
                    profit = opp.profit_percent
                    odds_json = json.dumps(opp.odds)
                    stakes_json = json.dumps(opp.stakes)
                    source = opp.source
                    timestamp_str = opp.timestamp.isoformat() if hasattr(opp.timestamp, 'isoformat') else str(opp.timestamp)

                cursor.execute('''
                    INSERT INTO opportunities
                    (snapshot_id, event_id, market_type, profit_percent, odds_data, stakes, source, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot_id, event_id, market_type, profit,
                    odds_json, stakes_json, source, timestamp_str
                ))
                count += 1
            conn.commit()
            logger.info(f"Guardadas {count} oportunidades en BD")
            return count
        except Exception as e:
            logger.error(f"Error guardando oportunidades: {e}")
            conn.rollback()
            raise

    def get_opportunities_since(self, cutoff_date: datetime) -> List[Dict[str, Any]]:
        conn = get_db()
        cursor = conn.execute("""
            SELECT * FROM opportunities
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff_date.isoformat(),))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Decisiones
    # ------------------------------------------------------------------
    def save_decision(self, decision) -> int:
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
        conn = get_db()
        cursor = conn.execute(
            "UPDATE decisions SET executed = 1 WHERE id = ?",
            (decision_id,)
        )
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Estadísticas y mantenimiento
    # ------------------------------------------------------------------
    def get_stats(self) -> Dict[str, Any]:
        return self.db.get_stats()

    def cleanup_old_data(self, days: int) -> int:
        return self.db.cleanup_old_data(days)

    def get_market_summary(self) -> List[Dict[str, Any]]:
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