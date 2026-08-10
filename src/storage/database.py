import sqlite3
from pathlib import Path
from src.logger import get_logger

logger = get_logger(__name__)

class Database:
    def __init__(self, db_path='quantbet.db'):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._enable_wal()
        self._migrate()

    def _enable_wal(self):
        self.conn.execute("PRAGMA journal_mode=WAL")
        logger.info("SQLite WAL mode enabled")

    def _migrate(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL DEFAULT 'Desconocido',
                sport TEXT,
                market TEXT,
                strategy TEXT,
                details TEXT,
                profit REAL,
                profit_percent REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_opp_event_market_profit 
            ON opportunities(event_name, market, profit_percent, timestamp)
        ''')
        self.conn.commit()

    def get_connection(self):
        return self.conn