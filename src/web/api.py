"""
Endpoints REST para el dashboard de QuantBet.
"""
from flask import Blueprint, jsonify, request
from src.storage.database import Database
from src.storage.repository import Repository

api_bp = Blueprint('api', __name__)

db = Database()
repo = Repository(db)


@api_bp.route('/opportunities')
def get_opportunities():
    limit = request.args.get('limit', 100, type=int)
    opportunities = repo.get_opportunities(limit=limit)
    # Convertir detalles JSON de string a objeto para el frontend
    for opp in opportunities:
        if 'details' in opp and isinstance(opp['details'], str):
            import json
            opp['details'] = json.loads(opp['details'])
    return jsonify(opportunities)


@api_bp.route('/metrics')
def get_metrics():
    conn = db.get_connection()
    total = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
    avg_profit = conn.execute("SELECT AVG(profit_percent) FROM opportunities").fetchone()[0]
    return jsonify({
        'total_opportunities': total,
        'average_profit_percent': round(avg_profit, 2) if avg_profit else 0.0
    })