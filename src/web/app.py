"""
Aplicación web con Flask para dashboard de QuantBet.
"""

import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from typing import Dict, Any, List

from src.config_loader import ConfigLoader
from src.storage.database import Database
from src.storage.repository import Repository
from src.logger import get_logger

logger = get_logger(__name__)


def create_app(config_path: str = "config.yaml") -> Flask:
    """
    Crea la aplicación Flask con configuración.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Flask: Aplicación configurada
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'quantbet-dashboard-secret'
    
    # Cargar configuración
    config_loader = ConfigLoader(config_path)
    config = config_loader.load()
    
    # Inicializar repositorio
    db_path = config.get('database', {}).get('path', 'quantbet.db')
    db = Database(db_path)
    repository = Repository(db)
    
    # Almacenar en app context
    app.config['REPOSITORY'] = repository
    app.config['CONFIG'] = config
    
    # Registrar rutas
    register_routes(app)
    
    return app


def register_routes(app: Flask):
    """Registra todas las rutas del dashboard."""
    
    @app.route('/')
    def index():
        """Página principal del dashboard."""
        return render_template('index.html')
    
    @app.route('/api/snapshots')
    def get_snapshots():
        """API: Obtener snapshots recientes."""
        repository = app.config['REPOSITORY']
        limit = request.args.get('limit', 50, type=int)
        
        snapshots = repository.get_latest_snapshots(limit)
        
        return jsonify([{
            'event_id': s.event_id,
            'event_name': s.event_name,
            'source': s.source,
            'timestamp': s.timestamp.isoformat(),
            'odds': {k: float(v) for k, v in s.odds.items()},
            'market_type': s.market_type.value
        } for s in snapshots])
    
    @app.route('/api/opportunities')
    def get_opportunities():
        """API: Obtener oportunidades de arbitraje."""
        repository = app.config['REPOSITORY']
        limit = request.args.get('limit', 20, type=int)
        
        decisions = repository.get_latest_decisions(limit)
        
        return jsonify([{
            'event_id': d.event_id,
            'source': d.source,
            'strategy': d.strategy,
            'accepted': d.accepted,
            'score': float(d.score) if d.score else None,
            'stake': float(d.stake) if d.stake else None,
            'timestamp': d.timestamp.isoformat(),
            'metadata': json.loads(d.metadata) if d.metadata else {}
        } for d in decisions])
    
    @app.route('/api/status')
    def get_status():
        """API: Estado del sistema."""
        config = app.config['CONFIG']
        repository = app.config['REPOSITORY']
        
        total_snapshots = repository.count_snapshots()
        total_decisions = repository.count_decisions()
        
        return jsonify({
            'version': config.get('version', '0.2.0'),
            'status': 'running',
            'total_snapshots': total_snapshots,
            'total_decisions': total_decisions,
            'bankroll': config.get('bankroll', {}).get('initial', 1000.0),
            'currency': config.get('bankroll', {}).get('currency', 'EUR'),
            'connector_type': config.get('connector', {}).get('type', 'csv')
        })
    
    @app.route('/api/event/<event_id>')
    def get_event_detail(event_id: str):
        """API: Detalle de un evento específico."""
        repository = app.config['REPOSITORY']
        
        snapshots = repository.get_snapshots_by_event(event_id)
        decisions = repository.get_decisions_by_event(event_id)
        
        if not snapshots:
            return jsonify({'error': 'Evento no encontrado'}), 404
        
        return jsonify({
            'event_id': event_id,
            'event_name': snapshots[0].event_name if snapshots else 'Unknown',
            'snapshots': [{
                'source': s.source,
                'timestamp': s.timestamp.isoformat(),
                'odds': {k: float(v) for k, v in s.odds.items()}
            } for s in snapshots],
            'decisions': [{
                'strategy': d.strategy,
                'accepted': d.accepted,
                'score': float(d.score) if d.score else None,
                'timestamp': d.timestamp.isoformat()
            } for d in decisions]
        })