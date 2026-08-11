"""Diagnóstico completo: ¿existen oportunidades con umbral más bajo?"""
import json
from itertools import product
from src.connectors.odds_api_provider import Outcome
from src.core.arbitrage import ArbitrageEngine
from src.config_loader import ConfigLoader

config = ConfigLoader()
allowed = [b.lower() for b in config['odds_api'].get('allowed_bookmakers', [])]
print("Bookmakers permitidos:", allowed)

with open('epl_sample.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

engine = ArbitrageEngine()
total_events = 0
all_opps = []
best_inv_sum = float('inf')
best_details = None

for game in games:
    bookmakers_data = game.get("bookmakers", [])
    grouped = {}
    for bk in bookmakers_data:
        bookmaker_name = bk["title"]
        if allowed and bookmaker_name.lower() not in allowed:
            continue
        for market in bk.get("markets", []):
            market_key = market["key"]
            if "_lay" in market_key:
                continue
            for oc in market.get("outcomes", []):
                point = oc.get("point")
                key = (market_key, point)
                grouped.setdefault(key, [])
                grouped[key].append(Outcome(
                    bookmaker=bookmaker_name,
                    name=oc["name"],
                    price=oc["price"],
                    point=point
                ))
    for (market_key, point), outcomes_list in grouped.items():
        # Agrupar por nombre de outcome
        by_name = {}
        for oc in outcomes_list:
            by_name.setdefault(oc.name, []).append((oc.bookmaker, oc.price))
        outcome_keys = list(by_name.keys())
        if len(outcome_keys) < 2:
            continue
        bookmaker_lists = [by_name[name] for name in outcome_keys]
        for combo in product(*bookmaker_lists):
            odds = [p for _, p in combo]
            if any(o <= 1.0 for o in odds):
                continue
            inv_sum = sum(1/o for o in odds)
            if inv_sum < best_inv_sum:
                best_inv_sum = inv_sum
                best_details = {
                    'event': f"{game['home_team']} vs {game['away_team']}",
                    'market': market_key + (f" {point}" if point is not None else ""),
                    'outcome_keys': outcome_keys,
                    'combo': combo,
                    'inv_sum': inv_sum,
                    'profit_pct': (1/inv_sum - 1)*100 if inv_sum < 1 else None
                }

        # Ahora también pasamos por el motor oficial (que ya filtra umbral)
        from src.connectors.odds_api_provider import AggregatedEvent
        event = AggregatedEvent(
            event_name=f"{game['home_team']} vs {game['away_team']}",
            sport="soccer_epl",
            market=market_key + (f" {point}" if point is not None else ""),
            outcomes=outcomes_list
        )
        opps = engine.find_opportunities(event)
        all_opps.extend(opps)
        total_events += 1

print(f"\nTotal sub-eventos evaluados: {total_events}")
print(f"Oportunidades detectadas (umbral {config['arbitrage']['min_profit_percent']}%): {len(all_opps)}")
if all_opps:
    for opp in all_opps:
        print(f"   {opp.event_name} – {opp.market} – {opp.profit_percent:.2f}%")
else:
    print(f"Mejor inv_sum encontrado: {best_inv_sum:.4f} (necesita <1 para arbitraje)")
    if best_details and best_inv_sum < 1:
        print(f"   ¡Existe arbitraje no detectado! {best_details['event']} – {best_details['market']}")
        print(f"   Combo: {best_details['combo']}")
        print(f"   Profit: {best_details['profit_pct']:.2f}%")
    else:
        print("   No hay combinación con inv_sum < 1 en esta muestra.")