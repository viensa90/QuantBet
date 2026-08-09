"""
Dashboard web para QuantBet.
- Modo debug condicionado a variable de entorno FLASK_DEBUG.
"""
import os
import sqlite3
from flask import Flask, jsonify, render_template_string
from src.logger import logger

app = Flask(__name__)

# Ruta a la base de datos (relativa al proyecto)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "quantbet.db")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>QuantBet - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #2c3e50; color: white; }
        tr:hover { background: #f1f1f1; }
        .profit { color: green; font-weight: bold; }
        .timestamp { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>📊 QuantBet - Oportunidades de Arbitraje</h1>
    <p><span class="timestamp">Última actualización: {{ now }}</span></p>
    <table>
        <thead>
            <tr>
                <th>Deporte</th>
                <th>Evento</th>
                <th>Mercado</th>
                <th>Combinación</th>
                <th>Profit (%)</th>
                <th>Apuesta</th>
                <th>Detalles</th>
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                <td>{{ row.sport }}</td>
                <td>{{ row.event_name }}</td>
                <td>{{ row.market }}</td>
                <td>{{ row.combination }}</td>
                <td class="profit">{{ row.profit_percent }}%</td>
                <td>{{ row.bet_info }}</td>
                <td><pre style="max-height:100px; overflow:auto;">{{ row.details }}</pre></td>
            </tr>
            {% else %}
            <tr><td colspan="7">No hay oportunidades registradas.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    from datetime import datetime
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sport, event_name, market, combination,
                   profit_percent, bet_info, details, created_at
            FROM opportunities
            ORDER BY created_at DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        logger.error("Error en dashboard: %s", e)
        rows = []

    # Formatear para la plantilla
    formatted = []
    for r in rows:
        formatted.append({
            "sport": r[0],
            "event_name": r[1],
            "market": r[2],
            "combination": r[3],
            "profit_percent": round(r[4], 2),
            "bet_info": r[5],
            "details": r[6],
            "created_at": r[7]
        })

    return render_template_string(
        HTML_TEMPLATE,
        rows=formatted,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route('/api/opportunities')
def api_opportunities():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sport, event_name, market, combination,
                   profit_percent, bet_info, details, created_at
            FROM opportunities
            ORDER BY created_at DESC
            LIMIT 50
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Debug condicionado a variable de entorno (por defecto False)
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)