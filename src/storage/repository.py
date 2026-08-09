"""
Repositorio para oportunidades de arbitraje.
- Solo INSERT (snapshots inmutables).
- WAL activado (desde database.py).
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Optional
from src.domain.entities import ArbitrageOpportunity
from src.storage.database import get_connection
from src.logger import logger

class OpportunityRepository:
    def save_opportunity(self, opp: ArbitrageOpportunity) -> int:
        """Guarda una oportunidad en la BD (INSERT)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO opportunities (
                sport, event_name, market, combination,
                profit_percent, bet_info, details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opp.sport,
            opp.event_name,
            opp.market,
            opp.combination,
            opp.profit_percent,
            opp.bet_info,
            json.dumps(opp.details, ensure_ascii=False),
            datetime.now().isoformat()
        ))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        logger.debug("Oportunidad guardada con ID: %d", last_id)
        return last_id

    def get_recent(self, limit: int = 10) -> List[ArbitrageOpportunity]:
        """Obtiene las últimas N oportunidades guardadas."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sport, event_name, market, combination,
                   profit_percent, bet_info, details, created_at
            FROM opportunities
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        opportunities = []
        for row in rows:
            opp = ArbitrageOpportunity(
                sport=row[0],
                event_name=row[1],
                market=row[2],
                combination=row[3],
                profit_percent=row[4],
                bet_info=row[5],
                details=json.loads(row[6]) if row[6] else {},
                created_at=row[7]
            )
            opportunities.append(opp)
        return opportunities

    def count_all(self) -> int:
        """Cuenta total de oportunidades en BD."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        count = cursor.fetchone()[0]
        conn.close()
        return count