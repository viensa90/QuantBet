"""
QuantBet - Repositorio de Persistencia (QB-005)
Funciones para guardar y recuperar entidades del dominio.
"""
import json
import sqlite3
from typing import List, Optional
from datetime import datetime, timezone

# Importamos las entidades del dominio
from src.domain.entities import (
    Snapshot, Decision, Bookmaker, Sport, Competition, 
    Event, Market, Outcome, Participant
)
from src.storage.database import DatabaseManager

class Repository:
    """
    Repositorio genérico para operaciones CRUD.
    Principio: Solo INSERT para Snapshots y Decisions (Inmutabilidad Histórica).
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager
    
    def _get_conn(self) -> sqlite3.Connection:
        return self._db.get_connection()
    
    # --- Operaciones de Escritura (Solo INSERT) ---
    
    def save_sport(self, sport: Sport):
        """Guarda un deporte si no existe."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO sports (id, name, type) VALUES (?, ?, ?)",
                (sport.id, sport.name, sport.type.value)
            )
    
    def save_competition(self, competition: Competition):
        """Guarda una competición y su deporte asociado."""
        # Primero guardamos el deporte para mantener integridad referencial
        self.save_sport(competition.sport)
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO competitions (id, name, sport_id) VALUES (?, ?, ?)",
                (competition.id, competition.name, competition.sport.id)
            )
    
    def save_event(self, event: Event):
        """Guarda un evento y sus dependencias (competición, participantes)."""
        self.save_competition(event.competition)
        with self._get_conn() as conn:
            home = next((p for p in event.participants if p.type == 'home'), None)
            away = next((p for p in event.participants if p.type == 'away'), None)
            conn.execute(
                "INSERT OR IGNORE INTO events (id, competition_id, start_time_utc, home_participant, away_participant, status) VALUES (?, ?, ?, ?, ?, ?)",
                (event.id, event.competition.id, event.start_time_utc.isoformat(), 
                 home.name if home else "N/A", away.name if away else "N/A", event.status.value)
            )
    
    def save_bookmaker(self, bookmaker: Bookmaker):
        """Guarda un bookmaker si no existe."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO bookmakers (id, name, type) VALUES (?, ?, ?)",
                (bookmaker.id, bookmaker.name, bookmaker.type.value)
            )
    
    def save_market(self, market: Market):
        """Guarda un mercado si no existe."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO markets (id, event_id, type, parameters) VALUES (?, ?, ?, ?)",
                (market.id, market.event_id, market.type, json.dumps(market.parameters))
            )
    
    def save_outcome(self, outcome: Outcome):
        """Guarda un outcome si no existe."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO outcomes (id, market_id, name) VALUES (?, ?, ?)",
                (outcome.id, outcome.market_id, outcome.name)
            )
    
    def save_snapshot(self, snapshot: Snapshot) -> bool:
        """
        Guarda un snapshot si no existe (evita duplicados exactos).
        Retorna True si se insertó, False si ya existía.
        Principio: INMUTABLE. Solo INSERT, nunca UPDATE.
        """
        # Guardamos dependencias
        self.save_bookmaker(snapshot.bookmaker)
        self.save_market(snapshot.market)
        for outcome_name in snapshot.odds.keys():
            # Creamos un outcome temporal para guardarlo si no existe
            # En un sistema real, los outcomes vendrían del Market
            pass
        
        with self._get_conn() as conn:
            try:
                # Verificamos si ya existe un snapshot idéntico (mismo bookmaker, market, timestamp y odds)
                odds_json = json.dumps(snapshot.odds, sort_keys=True)
                cursor = conn.execute(
                    "SELECT id FROM snapshots WHERE bookmaker_id = ? AND market_id = ? AND timestamp_utc = ? AND odds_json = ?",
                    (snapshot.bookmaker.id, snapshot.market.id, snapshot.timestamp_utc.isoformat(), odds_json)
                )
                if cursor.fetchone():
                    return False  # Ya existe, no lo duplicamos
                
                conn.execute(
                    "INSERT INTO snapshots (id, bookmaker_id, market_id, timestamp_utc, odds_json, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (snapshot.id, snapshot.bookmaker.id, snapshot.market.id, 
                     snapshot.timestamp_utc.isoformat(), odds_json, 'ACTIVE')
                )
                return True
            except sqlite3.IntegrityError:
                return False  # Violación de restricción (probablemente duplicado)
    
    def save_decision(self, decision: Decision):
        """Guarda una decisión. Principio: INMUTABLE."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO decisions (id, strategy, opportunity_score, snapshot_ids_json, recommended_stake_total, expected_roi, details_json, created_at_utc, ttl_seconds) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (decision.id, decision.strategy, decision.opportunity_score,
                 json.dumps(decision.snapshot_ids), decision.recommended_stake_total,
                 decision.expected_roi, json.dumps(decision.details),
                 decision.created_at_utc.isoformat(), decision.ttl_seconds)
            )