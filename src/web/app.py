"""
Módulo web: Dashboard Flask con APIs REST
Versión: 0.3.2 - Incluye Swagger/OpenAPI
"""

from flask import Flask, render_template, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import json
from datetime import datetime
from ..config_loader import ConfigLoader
from ..storage.repository import Repository
from ..domain.entities import Event, Market
from .swagger_config import SWAGGER_TEMPLATE

def create_app():
    """Fábrica de aplicación Flask con Swagger integrado"""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Cargar configuración
    config = ConfigLoader().config
    repo = Repository()
    
    # --- Configuración Swagger ---
    SWAGGER_URL = '/swagger'
    API_URL = '/api/v1/swagger.json'
    
    @app.route(API_URL)
    def swagger_json():
        """Servir archivo OpenAPI JSON"""
        return jsonify(SWAGGER_TEMPLATE)
    
    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "QuantBet API",
            'validatorUrl': None,  # Desactivar validación externa
            'operationsSorter': 'alpha',
            'tagsSorter': 'alpha',
            'displayRequestDuration': True,
            'deepLinking': True
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    
    # --- Rutas del Dashboard ---
    @app.route('/')
    def index():
        """Página principal del dashboard"""
        return render_template('index.html')
    
    @app.route('/api/v1/metrics')
    def get_metrics():
        """Endpoint: Métricas del dashboard"""
        try:
            # Obtener estadísticas del repositorio
            snapshot_count = repo.get_snapshot_count()
            opportunities = repo.get_opportunities(limit=100)
            
            # Contar por estrategia
            strategy_counts = {
                'arbitrage': 0,
                'value_betting': 0,
                'dutching': 0
            }
            for opp in opportunities:
                if opp.get('strategy') in strategy_counts:
                    strategy_counts[opp['strategy']] += 1
            
            # Obtener mercados activos
            markets = repo.get_active_markets()
            
            return jsonify({
                'total_opportunities': len(opportunities),
                'active_markets': len(markets),
                'strategies': strategy_counts,
                'total_snapshots': snapshot_count,
                'last_update': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/markets')
    def get_markets():
        """Endpoint: Lista de mercados activos"""
        try:
            markets = repo.get_active_markets()
            result = []
            for market in markets:
                result.append({
                    'sport': market.get('sport', 'Desconocido'),
                    'market_type': market.get('market_type', 'Desconocido'),
                    'event_count': repo.get_event_count_by_market(market.get('market_type', '')),
                    'enabled': True
                })
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/opportunities')
    def get_opportunities():
        """Endpoint: Oportunidades de apuesta con filtros"""
        try:
            strategy = request.args.get('strategy')
            min_profit = request.args.get('min_profit', type=float)
            limit = request.args.get('limit', default=10, type=int)
            
            opportunities = repo.get_opportunities(limit=limit*2)  # Obtener más para filtrar
            
            # Aplicar filtros
            if strategy:
                opportunities = [o for o in opportunities if o.get('strategy') == strategy]
            
            if min_profit:
                opportunities = [o for o in opportunities if o.get('profit_percent', 0) >= min_profit]
            
            # Limitar resultados
            opportunities = opportunities[:limit]
            
            # Formatear respuesta
            result = []
            for opp in opportunities:
                result.append({
                    'event': opp.get('event', 'Evento desconocido'),
                    'sport': opp.get('sport', 'Desconocido'),
                    'market_type': opp.get('market_type', 'Desconocido'),
                    'strategy': opp.get('strategy', 'Desconocido'),
                    'profit_percent': opp.get('profit_percent', 0.0),
                    'odds': opp.get('odds', {}),
                    'timestamp': opp.get('timestamp', datetime.now().isoformat())
                })
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/snapshots')
    def get_snapshots():
        """Endpoint: Histórico de snapshots"""
        try:
            limit = request.args.get('limit', default=20, type=int)
            from_date = request.args.get('from_date')
            
            snapshots = repo.get_snapshots(limit=limit)
            
            # Filtrar por fecha si se especifica
            if from_date:
                try:
                    from_dt = datetime.fromisoformat(from_date)
                    snapshots = [s for s in snapshots if datetime.fromisoformat(s['timestamp']) >= from_dt]
                except ValueError:
                    return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
            
            return jsonify(snapshots)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/system/status')
    def get_system_status():
        """Endpoint: Estado del sistema"""
        try:
            import os
            db_size = os.path.getsize('quantbet.db') / (1024 * 1024) if os.path.exists('quantbet.db') else 0
            
            config = ConfigLoader().config
            
            return jsonify({
                'version': '0.3.2',
                'status': 'running',
                'db_size_mb': round(db_size, 2),
                'models_loaded': ['historical', 'elo', 'poisson'],
                'connectors': {
                    'csv': 'active',
                    'web': 'inactive' if config.get('web_provider', {}).get('enabled') is False else 'active'
                },
                'uptime_seconds': 0  # Implementar si se desea
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/system/config')
    def get_system_config():
        """Endpoint: Configuración del sistema"""
        try:
            config = ConfigLoader().config
            
            # Ocultar valores sensibles
            safe_config = {
                'strategies': config.get('strategies', {}),
                'markets': config.get('markets', {}).get('enabled', []),
                'thresholds': config.get('thresholds', {}),
                'probability_model': config.get('probability_model', {}).get('type', 'historical'),
                'bankroll': {
                    'initial': config.get('bankroll', {}).get('initial', 1000),
                    'currency': config.get('bankroll', {}).get('currency', 'USD')
                }
            }
            return jsonify(safe_config)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

# Ejecución directa (para desarrollo)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)