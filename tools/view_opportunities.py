#!/usr/bin/env python3
"""
Muestra las oportunidades guardadas en la BD con detalle para operar.
Uso:
  python tools/view_opportunities.py
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "quantbet.db"

def main():
    if not DB_PATH.exists():
        print("❌ No se encontró la base de datos. Ejecuta primero el pipeline.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener oportunidades con el nombre del evento desde snapshots
    cursor.execute("""
        SELECT o.id, o.event_id, o.market_type, o.profit_percent,
               o.odds_data, o.stakes, o.source, o.timestamp,
               s.event_name
        FROM opportunities o
        LEFT JOIN snapshots s ON o.snapshot_id = s.id
        ORDER BY o.profit_percent DESC
    """)
    rows = cursor.fetchall()

    if not rows:
        print("📭 No hay oportunidades guardadas.")
        return

    print(f"\n📊 {len(rows)} OPORTUNIDADES DETECTADAS (ordenadas por beneficio)\n")
    print("=" * 80)

    for r in rows:
        event_name = r["event_name"] or "Evento desconocido"
        market = r["market_type"]
        profit = r["profit_percent"]
        source = r["source"]
        odds = json.loads(r["odds_data"])
        stakes = json.loads(r["stakes"])

        # Separar bookmakers y sus cuotas
        bm_details = []
        total_investment = 0.0
        for bm, sel_odds in odds.items():
            for sel, odd in sel_odds.items():
                bm_details.append(f"{bm}: {sel} @ {odd:.2f}")
            # stakes también está por bookmaker
            if isinstance(stakes, dict):
                # Las claves de stakes pueden ser 'stake_selection1', 'stake_selection2'
                # pero no están vinculadas directamente al bookmaker. Lo mostramos genérico.
                pass

        # Mostrar stakes si existen
        stake_info = ""
        if isinstance(stakes, dict):
            parts = []
            for k, v in stakes.items():
                parts.append(f"{k}: ${v:.2f}")
                if 'stake' in k:
                    total_investment += v
            stake_info = " | ".join(parts)

        print(f"🏆 {event_name}")
        print(f"   Mercado: {market}  |  Beneficio: {profit:.2f}%")
        print(f"   Origen: {source}")
        for detail in bm_details:
            print(f"   📌 {detail}")
        if stake_info:
            print(f"   💵 Stakes sugeridos: {stake_info}")
            print(f"   💰 Inversión total: ${total_investment:.2f}")
        print("-" * 80)

    conn.close()

if __name__ == "__main__":
    main()