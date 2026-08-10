"""
Prueba local de extremo a extremo (sin consumir créditos de la API).
Simula un evento con cuotas de bookmakers operables y verifica
que el motor, la BD y el dashboard funcionan correctamente.
"""

import json
from src.core.arbitrage import ArbitrageEngine
from src.connectors.odds_api_provider import AggregatedEvent, Outcome
from src.storage.database import Database
from src.storage.repository import Repository
from src.config_loader import ConfigLoader

# ------------------------------------------------------------
# 1. Simular un evento con bookmakers de tu lista blanca
# ------------------------------------------------------------
evento = AggregatedEvent(
    event_name='Real Madrid vs Barcelona',
    sport='soccer_spain_la_liga',
    market='h2h',
    outcomes=[
        Outcome(bookmaker='Pinnacle', name='Real Madrid', price=2.10, point=None),
        Outcome(bookmaker='1xBet', name='Barcelona', price=4.50, point=None),
        Outcome(bookmaker='BetOnline.ag', name='Draw', price=3.50, point=None),
    ],
    timestamp='2026-08-10T20:00:00Z'
)

# ------------------------------------------------------------
# 2. Pasar por el motor de arbitraje
# ------------------------------------------------------------
engine = ArbitrageEngine()
oportunidades = engine.find_opportunities(evento)

# ------------------------------------------------------------
# 3. Aplicar umbral mínimo de beneficio
# ------------------------------------------------------------
config = ConfigLoader()
min_profit = config['arbitrage']['min_profit_percent']
validas = [o for o in oportunidades if o.profit_percent >= min_profit]

# ------------------------------------------------------------
# 4. Guardar en la base de datos
# ------------------------------------------------------------
db = Database()
repo = Repository(db)
if validas:
    opp_dicts = [{
        'event_name': o.event_name,
        'sport': o.sport,
        'market': o.market,
        'strategy': 'arbitrage',
        'details': o.details,
        'profit': o.profit,
        'profit_percent': o.profit_percent
    } for o in validas]
    repo.save_opportunities(opp_dicts)
    print('✅ Oportunidad de prueba guardada en BD.')
else:
    print('⚠️ No se encontró arbitraje con los datos de prueba (prueba con otras cuotas).')

# ------------------------------------------------------------
# 5. Mostrar el mismo resumen que verías en --simple
# ------------------------------------------------------------
if validas:
    for opp in validas:
        print(f'\n⚽ {opp.event_name} ({opp.sport}) – {opp.market}')
        for outcome in opp.details['outcomes']:
            print(f'   {outcome["outcome"]}: {outcome["bookmaker"]} @ {outcome["odds"]} (Stake: {outcome["stake"]:.2f}€)')
        print(f'   Inversión total: {opp.details["total_investment"]:.2f}€ → Retorno: {opp.details["guaranteed_return"]:.2f}€ (+{opp.profit_percent:.2f}%)')
else:
    print('🔍 No se encontraron oportunidades de arbitraje.')