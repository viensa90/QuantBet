"""
QuantBet - Módulo de Persistencia (QB-005)
Gestor de la base de datos SQLite.
"""
import sqlite3
import os
from typing import Optional

class DatabaseManager:
    """
    Administra la conexión a la base de datos SQLite.
    Patrón: Singleton simple para el MVP (una sola instancia global).
    """
    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls, db_path: str = "quantbet.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._db_path = db_path
        return cls._instance
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene la conexión actual o crea una nueva si no existe."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
            self._connection.execute("PRAGMA journal_mode=WAL")  # Mejor rendimiento concurrente
            self._connection.execute("PRAGMA foreign_keys = ON")  # Integridad referencial
            self._initialize_database()
        return self._connection
    
    def _initialize_database(self):
        """
        Crea las tablas si no existen.
        Cumple estrictamente el modelo de dominio QB-002.
        Principio: Historial Inmutable. Solo INSERT, nunca UPDATE ni DELETE sobre Snapshots y Decisions.
        """
        cursor = self._connection.cursor()
        
        # Tabla: Sports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sports (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            )
        """)
        
        # Tabla: Competitions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sport_id TEXT NOT NULL,
                FOREIGN KEY (sport_id) REFERENCES sports(id)
            )
        """)
        
        # Tabla: Events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                competition_id TEXT NOT NULL,
                start_time_utc TEXT NOT NULL,
                home_participant TEXT NOT NULL,
                away_participant TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                FOREIGN KEY (competition_id) REFERENCES competitions(id)
            )
        """)
        
        # Tabla: Bookmakers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmakers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            )
        """)
        
        # Tabla: Markets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS markets (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                type TEXT NOT NULL,
                parameters TEXT,  -- JSON string para flexibilidad
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)
        
        # Tabla: Outcomes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                id TEXT PRIMARY KEY,
                market_id TEXT NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (market_id) REFERENCES markets(id)
            )
        """)
        
        # Tabla: Snapshots (EL ACTIVO PRINCIPAL - INMUTABLE)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id TEXT PRIMARY KEY,
                bookmaker_id TEXT NOT NULL,
                market_id TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                odds_json TEXT NOT NULL,  -- Diccionario Outcome -> Cuota en formato JSON
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                hash TEXT,
                FOREIGN KEY (bookmaker_id) REFERENCES bookmakers(id),
                FOREIGN KEY (market_id) REFERENCES markets(id)
            )
        """)
        
        # Tabla: Decisions (AUDITABLE - INMUTABLE)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                strategy TEXT NOT NULL,
                opportunity_score REAL NOT NULL,
                snapshot_ids_json TEXT NOT NULL,  -- Lista de IDs en formato JSON
                recommended_stake_total REAL NOT NULL,
                expected_roi REAL NOT NULL,
                details_json TEXT,  -- Diccionario con detalles específicos
                created_at_utc TEXT NOT NULL,
                ttl_seconds INTEGER DEFAULT 0
            )
        """)
        
        # Tabla: Bankroll (Historial de cambios)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bankroll_history (
                id TEXT PRIMARY KEY,
                timestamp_utc TEXT NOT NULL,
                total_capital REAL NOT NULL,
                available_capital REAL NOT NULL,
                committed_capital REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'PYG'
            )
        """)
        
        self._connection.commit()
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self._connection:
            self._connection.close()
            self._connection = None