"""
Aplicación web Flask para el dashboard de QuantBet.
Versión: 0.3.3 (Robusto para BD nueva)
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.config_loader import ConfigLoader
from src.storage.repository import Repository
from src.logger import get_logger
import os

logger = get_logger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    config = ConfigLoader().config
    app.config.update(config.get('web', {}))
    
    repo = Repository()
    
    # ----------------------------------------------------------------
    # Rutas del dashboard
    # ----------------------------------------------------------------
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/v1/system/status')
    def system_status():
        return jsonify({
            "status": "running",
            "version": "0.3.3",
            "timestamp": repo.get_stats().get('last_execution', '')
        })
    
    @app.route('/api/v1/opportunities')
    def get_opportunities():
        limit = request.args.get('limit', 10, type=int)
        try:
            # Intentamos obtener las últimas oportunidades guardadas
            conn = repo.db.get_connection()
            cursor = conn.execute('''
                SELECT * FROM opportunities
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            opps = []
            for row in rows:
                opps.append({
                    "id": row["id"],
                    "event_id": row["event_id"],
                    "market_type": row["market_type"],
                    "profit_percent": row["profit_percent"],
                    "odds": row["odds_data"],
                    "stakes": row["stakes"],
                    "source": row["source"],
                    "timestamp": row["timestamp"]
                })
            return jsonify(opps)
        except Exception as e:
            logger.error(f"Error obteniendo oportunidades: {e}")
            return jsonify({"error": "No se pudieron obtener las oportunidades. ¿Ya ejecutaste el pipeline?"}), 500
    
    @app.route('/api/v1/metrics')
    def get_metrics():
        try:
            stats = repo.get_stats()
            # Construir métricas para el dashboard
            metrics = {
                "total_opportunities": 0,
                "arbitrage_count": 0,
                "value_betting_count": 0,
                "dutching_count": 0,
                "avg_profit_percent": 0.0,
                "total_events_tracked": stats.get('total_snapshots', 0),
                "db_size_mb": stats.get('db_size_mb', 0.0),
                "last_execution": stats.get('last_execution', 'Nunca')
            }
            
            # Intentar obtener desglose por estrategia
            try:
                conn = repo.db.get_connection()
                cursor = conn.execute("SELECT COUNT(*) as cnt FROM opportunities")
                total_opps = cursor.fetchone()["cnt"]
                metrics["total_opportunities"] = total_opps
                
                # Por tipo de estrategia (si la tabla tiene columna 'source')
                # Esto depende de cómo guardes la estrategia; asumimos que source incluye el nombre
                for strategy in ['arbitrage', 'value_betting', 'dutching']:
                    cursor = conn.execute(
                        "SELECT COUNT(*) as cnt FROM opportunities WHERE source LIKE ?",
                        (f"%{strategy}%",)
                    )
                    metrics[f"{strategy}_count"] = cursor.fetchone()["cnt"]
                
                # Beneficio promedio
                cursor = conn.execute("SELECT AVG(profit_percent) as avg_profit FROM opportunities")
                avg_profit = cursor.fetchone()["avg_profit"]
                if avg_profit:
                    metrics["avg_profit_percent"] = round(avg_profit, 2)
            except Exception as e:
                logger.warning(f"No se pudieron calcular métricas detalladas: {e}")
            
            return jsonify(metrics)
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return jsonify({"error": "Error interno al obtener métricas"}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)