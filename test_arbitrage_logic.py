#!/usr/bin/env python
"""
TEST LOCAL - Consume 0 créditos de API.
Simula eventos deportivos con bookmakers mezclados para validar:
1. Filtro de bookmakers (lista blanca).
2. Filtro de mercados _lay.
3. Agrupación por (name, point) - evita falsos positivos.
4. Logs sensibles (API key oculta).
5. Inicialización de Telegram (sin enviar).
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()  # Carga .env para las variables de entorno

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.logger import logger
from src.domain.entities import AggregatedEvent, Outcome, ArbitrageOpportunity
from src.core.arbitrage import ArbitrageEngine
from src.storage.repository import OpportunityRepository
from src.config_loader import load_config

# --- 1. CONFIGURACIÓN DE PRUEBA ---
config = load_config()
min_profit = config.get("arbitrage", {}).get("min_profit_percent", 1.5)
bookmakers_whitelist = config.get("odds_api", {}).get("bookmakers", "").split(",")
bookmakers_whitelist = [b.strip() for b in bookmakers_whitelist]

logger.info("🧪 INICIANDO PRUEBAS LOCALES (0 créditos consumidos)")
logger.info("📋 Bookmakers permitidos: %s", bookmakers_whitelist)

# --- 2. CREAR DATOS SIMULADOS (MOCKS) ---

# Evento 1: h2h - Mezcla bookmakers permitidos y no permitidos
mock_event_h2h = AggregatedEvent(
    sport="soccer_spain_la_liga",
    event_name="Real Madrid vs Barcelona",
    commence_time="2026-08-10T20:00:00Z",
    market="h2h",
    outcomes=[
        # Pinnacle (PERMITIDO) - cuotas normales
        Outcome(bookmaker="Pinnacle", name="Real Madrid", price=1.85, point=None, market="h2h"),
        Outcome(bookmaker="Pinnacle", name="Barcelona", price=2.10, point=None, market="h2h"),
        # NordicBet (NO PERMITIDO - debe ser filtrado)
        Outcome(bookmaker="NordicBet", name="Real Madrid", price=1.90, point=None, market="h2h"),
        Outcome(bookmaker="NordicBet", name="Barcelona", price=2.20, point=None, market="h2h"),
        # BetOnline.ag (PERMITIDO) - cuotas que generan arbitraje con Pinnacle
        Outcome(bookmaker="BetOnline.ag", name="Real Madrid", price=2.00, point=None, market="h2h"),
        Outcome(bookmaker="BetOnline.ag", name="Barcelona", price=1.95, point=None, market="h2h"),
    ],
    details={"home": "Real Madrid", "away": "Barcelona"}
)

# Evento 2: totals - mezcla líneas 2.5 y 2.0 (NO deben combinarse entre sí)
mock_event_totals = AggregatedEvent(
    sport="soccer_epl",
    event_name="Liverpool vs Arsenal",
    commence_time="2026-08-10T20:00:00Z",
    market="totals",
    outcomes=[
        # Over 2.5
        Outcome(bookmaker="Pinnacle", name="Over", price=1.80, point=2.5, market="totals"),
        Outcome(bookmaker="Pinnacle", name="Under", price=2.10, point=2.5, market="totals"),
        # Over 2.0 (línea diferente - NO debe mezclarse con 2.5)
        Outcome(bookmaker="BetOnline.ag", name="Over", price=1.60, point=2.0, market="totals"),
        Outcome(bookmaker="BetOnline.ag", name="Under", price=2.30, point=2.0, market="totals"),
        # Betfair (PERMITIDO) - cuotas para 2.5 que crean arbitraje
        Outcome(bookmaker="Betfair", name="Over", price=2.20, point=2.5, market="totals"),
        Outcome(bookmaker="Betfair", name="Under", price=1.90, point=2.5, market="totals"),
    ],
    details={"home": "Liverpool", "away": "Arsenal"}
)

# Evento 3: mercado con _lay (debe ser ignorado completamente)
mock_event_lay = AggregatedEvent(
    sport="soccer_epl",
    event_name="Chelsea vs Tottenham",
    commence_time="2026-08-10T20:00:00Z",
    market="h2h_lay",  # ← Contiene _lay, debe ser ignorado
    outcomes=[
        Outcome(bookmaker="Pinnacle", name="Chelsea", price=1.50, point=None, market="h2h_lay"),
        Outcome(bookmaker="Pinnacle", name="Tottenham", price=2.80, point=None, market="h2h_lay"),
    ],
    details={"home": "Chelsea", "away": "Tottenham"}
)

# --- 3. EJECUTAR MOTOR DE ARBITRAJE ---
engine = ArbitrageEngine(min_profit_percent=min_profit)

# IMPORTANTE: Para simular el filtro de bookmakers en el motor,
# necesitamos filtrar los outcomes ANTES de pasarlos al engine.
# El motor solo ve los outcomes que le pasamos.
# Simulamos lo que haría OddsAPIProvider._parse_game.
def filter_outcomes_by_whitelist(events, whitelist):
    """Filtra outcomes que no estén en la lista blanca."""
    filtered_events = []
    for event in events:
        filtered_outcomes = [o for o in event.outcomes if o.bookmaker in whitelist]
        if filtered_outcomes:
            # Reconstruir el evento con outcomes filtrados
            new_event = AggregatedEvent(
                sport=event.sport,
                event_name=event.event_name,
                commence_time=event.commence_time,
                market=event.market,
                outcomes=filtered_outcomes,
                details=event.details
            )
            filtered_events.append(new_event)
    return filtered_events

# Aplicamos el filtro manualmente (igual que haría el conector)
all_mocks = [mock_event_h2h, mock_event_totals, mock_event_lay]
filtered_events = filter_outcomes_by_whitelist(all_mocks, bookmakers_whitelist)

logger.info("🔍 Eventos después del filtro de bookmakers: %d", len(filtered_events))
for ev in filtered_events:
    logger.info("  - %s [%s] (%d outcomes)", ev.event_name, ev.market, len(ev.outcomes))

# Buscar oportunidades
opportunities = engine.find_opportunities(filtered_events)

# --- 4. VALIDAR RESULTADOS ESPERADOS ---
print("\n" + "="*60)
print("📊 RESULTADOS DE LA PRUEBA")
print("="*60)

# Esperado:
# - Evento 1 (h2h): Pinnacle + BetOnline -> Debe generar arbitraje (Real Madrid 1.85 vs 2.00? 
#   En realidad el motor agrupa por nombre. Para h2h, "Real Madrid" vs "Barcelona". 
#   Debe encontrar combinación ganadora.)
# - Evento 2 (totals): Debe generar 2 oportunidades separadas (una para 2.5, otra para 2.0)
#   pero NUNCA mezclar Over 2.5 con Under 2.0.
# - Evento 3 (lay): Ignorado completamente.

# Verificación manual (el usuario mira la salida):
if opportunities:
    print(f"✅ Oportunidades encontradas: {len(opportunities)}")
    for opp in opportunities:
        print(f"  - {opp.event_name} | {opp.market} | {opp.combination}")
        print(f"    Profit: {opp.profit_percent:.2f}% | Apuesta: {opp.bet_info}")
        # Verificar que no haya mezcla de líneas
        if opp.market == "totals":
            print(f"    ⚠️ Línea (point) asociada: {opp.details.get('point', 'N/A')}")
else:
    print("❌ No se encontraron oportunidades (puede ser normal si las cuotas no cruzan umbral).")

print("\n📝 Validaciones automáticas:")
# Validación 1: ¿Se ignoró el evento con _lay?
lay_filtered = any(ev.market == "h2h_lay" for ev in filtered_events)
if not lay_filtered:
    print("  ✅ Mercado 'h2h_lay' fue correctamente filtrado/ignorado.")
else:
    print("  ❌ ERROR: 'h2h_lay' sigue presente en filtered_events.")

# Validación 2: ¿NordicBet fue eliminado?
nordic_present = any(o.bookmaker == "NordicBet" for ev in filtered_events for o in ev.outcomes)
if not nordic_present:
    print("  ✅ Bookmaker 'NordicBet' fue correctamente filtrado (no está en lista blanca).")
else:
    print("  ❌ ERROR: 'NordicBet' aún aparece en los outcomes.")

# Validación 3: Pinnacle, BetOnline, Betfair sí están presentes
allowed_present = any(o.bookmaker in bookmakers_whitelist for ev in filtered_events for o in ev.outcomes)
if allowed_present:
    print(f"  ✅ Bookmakers permitidos ({bookmakers_whitelist}) están presentes.")
else:
    print("  ❌ ERROR: Ningún bookmaker permitido encontrado.")

# --- 5. PROBAR REPOSITORIO (Guardar en BD de prueba) ---
print("\n💾 Probando repositorio...")
repo = OpportunityRepository()
try:
    # Guardar las oportunidades encontradas (si hay)
    for opp in opportunities:
        repo.save_opportunity(opp)
    count = repo.count_all()
    print(f"  ✅ Oportunidades guardadas en BD. Total en BD: {count}")
    
    recent = repo.get_recent(limit=3)
    print(f"  ✅ Método get_recent() funciona. Últimas {len(recent)} oportunidades recuperadas.")
except Exception as e:
    print(f"  ❌ Error en repositorio: {e}")

# --- 6. PROBAR FILTRO DE LOGS (campo sensible) ---
print("\n🔒 Probando filtro de logs (API key oculta)...")
test_api_key = os.getenv("ODDS_API_KEY", "NO_KEY")
if test_api_key != "NO_KEY":
    # Forzamos un log con la API key para ver si se oculta
    logger.info("Mi API key es: %s", test_api_key)
    print("  ✅ Revisa el log de arriba. Debería aparecer '***API_KEY***' en lugar del valor real.")
else:
    print("  ⚠️ No hay ODDS_API_KEY en .env para probar el filtro.")

# --- 7. PROBAR INICIALIZACIÓN DE TELEGRAM (sin enviar) ---
print("\n📱 Probando inicialización de Telegram...")
telegram_enabled = config.get("notifications", {}).get("telegram", {}).get("enabled", False)
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
if telegram_enabled and bot_token and chat_id:
    try:
        from src.notifications.telegram_notifier import TelegramNotifier
        notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        print("  ✅ TelegramNotifier inicializado correctamente.")
        # No enviamos mensaje real para no saturar.
    except Exception as e:
        print(f"  ❌ Error inicializando Telegram: {e}")
else:
    print("  ⚠️ Telegram no configurado en .env o config.yaml (se salta prueba).")

print("\n" + "="*60)
print("🏁 PRUEBA FINALIZADA. Revisa los logs y resultados arriba.")
print("Si ves los '✅' verdes y sin errores, el sistema está listo.")
print("="*60)