import json
from datetime import datetime
from src.storage.database import Database
from src.logger import get_logger

logger = get_logger(__name__)

class Repository:
    def __init__(self, database: Database):
        self.db = database

    def _is_duplicate(self, opp, window_hours=1):
        """Devuelve True si ya existe una oportunidad similar en las últimas 'window_hours' horas."""
        conn = self.db.get_connection()
        row = conn.execute('''
            SELECT id FROM opportunities
            WHERE event_name = ?
              AND market = ?
              AND profit_percent = ?
              AND timestamp > datetime('now', '-{} hours')
            LIMIT 1
        '''.format(window_hours), (opp['event_name'], opp['market'], opp['profit_percent'])).fetchone()
        return row is not None

    def save_opportunities(self, opportunities, dedup_window_hours=1):
        """
        Guarda oportunidades nuevas, ignorando duplicadas en la ventana indicada.
        Retorna la lista de las efectivamente guardadas.
        """
        conn = self.db.get_connection()
        saved = []
        for opp in opportunities:
            if self._is_duplicate(opp, dedup_window_hours):
                continue
            conn.execute('''
                INSERT INTO opportunities (event_name, sport, market, strategy, details, profit, profit_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                opp.get('event_name', 'Desconocido'),
                opp.get('sport', ''),
                opp.get('market', ''),
                opp.get('strategy', 'arbitrage'),
                json.dumps(opp.get('details', {})),
                opp.get('profit'),
                opp.get('profit_percent')
            ))
            saved.append(opp)
        conn.commit()
        logger.info(f"Guardadas {len(saved)} oportunidades en BD (descartadas {len(opportunities)-len(saved)} duplicadas)")
        return saved

    def get_opportunities(self, limit=100):
        conn = self.db.get_connection()
        rows = conn.execute('''
            SELECT * FROM opportunities ORDER BY timestamp DESC LIMIT ?
        ''', (limit,)).fetchall()
        return [dict(row) for row in rows]