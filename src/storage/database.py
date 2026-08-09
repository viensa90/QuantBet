"""
Módulo de base de datos SQLite con WAL activado.
- Migración automática al iniciar.
- WAL (Write-Ahead Logging) para mejor concurrencia.
"""
import sqlite3
import os
from src.logger import logger  # ✅ Solo importamos el logger global

# Ruta de la base de datos (relativa al proyecto)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "quantbet.db")

def get_connection():
    """Retorna una conexión a la BD con WAL activado."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")   # Permite lectura/escritura simultánea
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def initialize_database():
    """Crea las tablas si no existen (migración automática)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de oportunidades de arbitraje
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT NOT NULL,
            event_name TEXT NOT NULL,
            market TEXT NOT NULL,
            combination TEXT NOT NULL,
            profit_percent REAL NOT NULL,
            bet_info TEXT NOT NULL,
            details TEXT NOT NULL,   -- JSON
            created_at TEXT NOT NULL
        )
    """)
    
    # Índices para consultas rápidas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_sport ON opportunities(sport)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_created ON opportunities(created_at DESC)")
    
    conn.commit()
    conn.close()
    logger.info("Base de datos inicializada/verificada en: %s", DB_PATH)

# Ejecutar migración al cargar el módulo
initialize_database()