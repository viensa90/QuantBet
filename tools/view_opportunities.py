#!/usr/bin/env python3
"""
Muestra solo las oportunidades de arbitraje SEGURAS (mercados de 2 opciones).
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "quantbet.db"

# Mercados donde ganar y perder son eventos complementarios (sin empate)
SAFE_MARKETS = {
    "Over/Under", "Tennis Winner", "Basketball Moneyline",
    "Tennis Total Games", "Basketball Total Points",
    "Asian Handicap", "Tennis Set Handicap", "Basketball Spread"
}

def main():
    if not DB_PATH.exists():
        print("❌ Base de datos no encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.event_id, o.market_type, o.profit_percent,
               o.odds_data, o.stakes, o.source, s.event_name
        FROM opportunities o
        LEFT JOIN snapshots s ON o.snapshot_id = s.id
        WHERE o.market_type IN ({})
        ORDER BY o.profit_percent DESC
    """.format(','.join('?'*len(SAFE_MARKETS))), list(SAFE_MARKETS))
    rows = cursor.fetchall()

    if not rows:
        print("📭 No hay oportunidades seguras guardadas.")
        return

    print(f"\n📊 {len(rows)} OPORTUNIDADES SEGURAS (sin riesgo de empate)\n")
    for r in rows:
        event = r["event_name"] or r["event_id"]
        market = r["market_type"]
        profit = r["profit_percent"]
        odds = json.loads(r["odds_data"])
        stakes = json.loads(r["stakes"])

        print(f"🏆 {event}  |  {market}  |  +{profit:.2f}%")
        for bm, sel_odds in odds.items():
            for sel, odd in sel_odds.items():
                print(f"   📌 {bm}: {sel} @ {odd:.2f}")
        if isinstance(stakes, dict):
            total = sum(v for k, v in stakes.items() if 'stake' in k)
            print(f"   💵 Inversión: ${total:.2f}  |  Ganancia: ${(total * profit / 100):.2f}")
        print("-" * 80)
    conn.close()

if __name__ == "__main__":
    main()