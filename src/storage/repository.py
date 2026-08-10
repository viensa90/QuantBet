import json
from datetime import datetime
from src.storage.database import Database
from src.logger import get_logger

logger = get_logger(__name__)

class Repository:
    def __init__(self, database: Database):
        self.db = database

    def save_opportunities(self, opportunities):
        """Guarda una lista de oportunidades (dict) en la BD."""
        conn = self.db.get_connection()
        for opp in opportunities:
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
        conn.commit()
        logger.info(f"Guardadas {len(opportunities)} oportunidades en BD")

    def get_opportunities(self, limit=100):
        conn = self.db.get_connection()
        rows = conn.execute('''
            SELECT * FROM opportunities ORDER BY timestamp DESC LIMIT ?
        ''', (limit,)).fetchall()
        return [dict(row) for row in rows]