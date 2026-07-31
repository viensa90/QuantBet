"""
src/web/app.py
Servidor Flask con APIs REST - Optimizado con market_summary
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from datetime import datetime
import logging

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.storage.database import get_db
from src.storage.repository import Repository
from src.storage.migrations import apply_migrations
from src.core.scorer import OpportunityScorer
from src.core.arbitrage import ArbitrageEngine
from src.config_loader import config

logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Singleton de repositorio
repo = None
scorer = None
arbitrage_engine = None

def init_app():
    """Inicializa la aplicación con migraciones y configuración"""
    global repo, scorer, arbitrage_engine
    
    # Aplicar migraciones
    apply_migrations()
    
    # Inicializar componentes
    repo = Repository()
    scorer = OpportunityScorer()
    arbitrage_engine = ArbitrageEngine()
    
    logger.info("Dashboard web inicializado con optimizaciones")

# === RUTAS PÚBLICAS ===

@app.route('/')
def index():
    """Dashboard principal"""
    return render_template('index.html', 
                          version=config.get('version', '0.3.0'),
                          timestamp=datetime.now().isoformat())

@app.route('/api/summary')
def get_summary():
    """API para resumen de mercado (rápido, desde market_summary)"""
    limit = request.args.get('limit', 50, type=int)
    min_opps = request.args.get('min_opportunities', 1, type=int)
    
    summary = repo.get_market_summary(limit=limit, min_opportunities=min_opps)
    return jsonify({
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "count": len(summary),
        "data": summary
    })

@app.route('/api/snapshots/latest')
def get_latest_snapshots():
    """Últimos snapshots (optimizado con índice)"""
    limit = request.args.get('limit', 20, type=int)
    snapshots = repo.get_latest_snapshots(limit=limit)
    
    return jsonify({
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "count": len(snapshots),
        "data": [
            {
                "event_id": s.event_id,
                "event_name": s.event_name,
                "market_type": s.market_type,
                "bookmaker": s.bookmaker,
                "odds": s.odds_data,
                "timestamp": s.timestamp.isoformat()
            }
            for s in snapshots
        ]
    })

@app.route('/api/opportunities/top')
def get_top_opportunities():
    """Top oportunidades (optimizado con índice)"""
    limit = request.args.get('limit', 10, type=int)
    min_score = request.args.get('min_score', 70, type=float)
    
    opportunities = repo.get_top_opportunities(limit=limit, min_score=min_score)
    return jsonify({
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "count": len(opportunities),
        "data": opportunities
    })

@app.route('/api/events/<event_id>/snapshots')
def get_event_snapshots(event_id):
    """Snapshots por evento (optimizado con índice compuesto)"""
    snapshots = repo.get_snapshots_by_event(event_id)
    return jsonify({
        "status": "success",
        "event_id": event_id,
        "count": len(snapshots),
        "data": [
            {
                "market_type": s.market_type,
                "bookmaker": s.bookmaker,
                "odds": s.odds_data,
                "timestamp": s.timestamp.isoformat()
            }
            for s in snapshots
        ]
    })

@app.route('/api/events/<event_id>/decisions')
def get_event_decisions(event_id):
    """Decisiones por evento (optimizado con índice compuesto)"""
    limit = request.args.get('limit', 20, type=int)
    decisions = repo.get_decisions_by_event(event_id, limit=limit)
    return jsonify({
        "status": "success",
        "event_id": event_id,
        "count": len(decisions),
        "data": [
            {
                "strategy": d.strategy,
                "score": d.opportunity_score,
                "data": d.opportunity_data,
                "executed": d.executed,
                "timestamp": d.timestamp.isoformat()
            }
            for d in decisions
        ]
    })

@app.route('/api/stats')
def get_stats():
    """Estadísticas de la base de datos"""
    stats = repo.get_db_stats()
    stats["timestamp"] = datetime.now().isoformat()
    return jsonify(stats)

@app.route('/api/health')
def health_check():
    """Health check para monitoreo"""
    db_stats = get_db().get_connection_stats()
    return jsonify({
        "status": "healthy",
        "version": config.get('version', '0.3.0'),
        "database": db_stats,
        "timestamp": datetime.now().isoformat()
    })

# === INICIALIZACIÓN ===

if __name__ == '__main__':
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar app
    init_app()
    
    # Obtener configuración
    host = config.get('web', {}).get('host', '0.0.0.0')
    port = config.get('web', {}).get('port', 5000)
    debug = config.get('web', {}).get('debug', True)
    
    logger.info(f"Iniciando dashboard en http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)