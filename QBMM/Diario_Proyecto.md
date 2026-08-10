📋 DIARIO DE PROYECTO - QuantBet (v0.5.0 - OPERATIVO, COBERTURA MUNDIAL DE FÚTBOL)

🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.
Reglas implícitas (no necesito repetirlas):
- Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet
- "CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo siempre que estés completamente seguro de no romper nada)
- Al final de cada sesión, actualiza este diario con el mismo formato
- Mantén el contexto de todas las sesiones anteriores
- Los principios de arquitectura son inmutables (ver sección Principios)
- NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible
- SIEMPRE escanea minuciosamente el repositorio antes de proponer cambios

🛡️ REGLAS ESTRICTAS DE MODIFICACIÓN (ANTI-DESASTRE)

⚠️ NUNCA modificar los siguientes archivos sin una comprensión TOTAL de su función y sin preguntar primero al usuario:
- src/core/arbitrage.py (motor de arbitraje genérico: producto cartesiano, ROI real, agrupación por name+point, ignora _lay)
- src/connectors/odds_api_provider.py (conector principal: Outcome con point, filtro lista blanca, reintentos, timeout, excluye live, min_minutes_to_start)
- src/storage/repository.py (persistencia y deduplicación: save_opportunities con ventana configurable, _is_duplicate)
- src/storage/database.py (esquema de BD con índice anti-duplicados, WAL activado)
- main.py (pipeline completo, --simple, deduplicación, Telegram)
- config.yaml (41 ligas, 5 bookmakers, umbral 1.5%, excluye live, ventana dedup 1h)

⚠️ NUNCA renombrar funciones/clases clave (ej. get_logger, ArbitrageEngine, Outcome, AggregatedEvent) sin actualizar TODAS sus referencias.

⚠️ NUNCA cambiar la estructura del JSON `details` ni los nombres de los campos de la BD sin una migración explícita.

⚠️ NUNCA ejecutar `main.py` sin confirmar con el usuario el consumo de créditos (41 créditos por ejecución).

⚠️ NUNCA eliminar:
- El filtro de `_lay` en odds_api_provider.py
- La agrupación por `(name, point)` en arbitrage.py
- El filtro `exclude_live` ni `min_minutes_to_start`
- La deduplicación en repository.py

📋 SIEMPRE:
- Leer el archivo COMPLETO antes de sugerir un REEMPLAZO.
- Verificar que `get_logger` existe en `src/logger.py` (o usar `setup_logger` como alias).
- Verificar que `ConnectorFactory` se usa con el método `create`.
- Probar primero en `test_local.py` si se hacen cambios en el motor o el conector.
- Actualizar este diario al final de la sesión.

📊 RESUMEN EJECUTIVO
| Métrica | Valor |
|--------|--------|
| Proyecto | QuantBet - Sistema de Arbitraje Deportivo Automatizado |
| Versión | 0.5.0 |
| Repositorio | https://github.com/viensa90/QuantBet |
| Última sesión | 27 - 10/08/2026 |
| Estado | 🟢 OPERATIVO – Pipeline automático cada hora, 41 ligas, 5 bookmakers, deduplicación, filtro en vivo |
| Créditos | 20.000 peticiones/mes (plan de pago) |
| Consumo diario estimado | 328 créditos (1.64% del plan mensual) |
| Ejecuciones/día | 8 (10:00 + cada hora de 12:00 a 18:00) |
| Créditos por ejecución | 41 |

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.5.0)
QuantBet/
├── .env.example / .env            ✅ API key real en .env (ODDS_API_KEY)
├── .gitignore                    ✅ Protege .env, *.db, etc.
├── config.yaml                   ✅ 41 ligas, 5 bookmakers, umbral 1.5%, excl. live, dedup 1h
├── main.py                       ✅ Pipeline, --simple, deduplicación, Telegram
├── test_local.py                 🧪 Prueba local sin créditos
├── quantbet.db                   (autogenerada, WAL, índice anti-duplicados)
├── logs/                         📝 Logs diarios de ejecuciones automáticas
├── QBMM/                         ✅ Documentos maestros
├── src/
│   ├── __init__.py
│   ├── config_loader.py          ✅ .env + YAML (encoding='utf-8')
│   ├── logger.py                 ✅ get_logger + alias setup_logger
│   ├── domain/
│   │   └── entities.py           ✅ Entidades originales (compatibilidad)
│   ├── storage/
│   │   ├── database.py           ✅ WAL, índice idx_opp_event_market_profit
│   │   ├── repository.py         ✅ Deduplicación (save_opportunities retorna solo nuevas)
│   │   └── migrations.py
│   ├── core/
│   │   ├── arbitrage.py          🔥 Motor genérico (ROI real: 1/inv_sum-1, agrupa por name+point, ignora _lay)
│   │   ├── market_handlers.py    ✅ Normalización de mercados
│   │   ├── value_betting.py      (inactivo)
│   │   ├── dutching.py           (inactivo)
│   │   ├── scorer.py             (inactivo)
│   │   ├── bankroll.py           (inactivo)
│   │   └── probability_model.py (obsoleto)
│   ├── connectors/
│   │   ├── base.py
│   │   ├── csv_provider.py
│   │   ├── odds_api_provider.py  🔌 Conector principal (Outcome con point, filtro lista blanca, reintentos 3, timeout 10s, excl. live, min_minutes_to_start 10)
│   │   └── factory.py
│   ├── notifications/
│   │   ├── telegram_notifier.py  ✅ maybe_notify con emojis por bookmaker
│   │   └── email_notifier.py     (opcional)
│   └── web/
│       ├── app.py                ✅ Dashboard Flask (debug desactivado, variable FLASK_DEBUG)
│       ├── api.py                ✅ Endpoints REST (opportunities, metrics)
│       └── templates/
│           └── index.html        ✅ Dashboard visual con tarjetas detalladas
├── tests/                        ⚠️ 83 tests (necesitan actualización)
├── tools/
│   └── view_opportunities.py     ✅ Visor de BD robustecido
└── data/

🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-24: desarrollo inicial.
Sesión 25 (08/08/2026): Auditoría forense, motor genérico, corrección falsos positivos.
Sesión 26 (09/08/2026): Restauración completa tras desastre con otra IA, mejoras (lista blanca, reintentos, timeout, dashboard, logger, Telegram).
Sesión 27 (10/08/2026): 
- Corrección de porcentaje de arbitraje (ROI real: 1/inv_sum - 1).
- Filtro de partidos en vivo (exclude_live, min_minutes_to_start).
- Deduplicación automática (ventana configurable en config.yaml).
- Obtención de lista real de ligas desde la API (41 ligas de fútbol).
- Ampliación a 41 ligas (todas las disponibles en el plan).
- Configuración de tarea programada: cada hora de 12:00 a 18:00 + 10:00 (hora Paraguay).
- Logs diarios en carpeta logs/.
- Verificación final: ejecución con 41 ligas sin errores 404.

🔍 ESTADO ACTUAL (v0.5.0)
✅ Funcionando y verificado:
- Arbitraje preciso con ROI real (porcentaje correcto).
- Cobertura mundial: 41 ligas de fútbol (todas las disponibles en The Odds API).
- Bookmakers: Pinnacle, 1xBet, BetOnline.ag, Betfair, Marathonbet (lista blanca configurable).
- Solo eventos futuros (≥10 min para apostar tranquilo).
- Deduplicación en ventana de 1 h (no muestra la misma oportunidad repetida).
- Dashboard interactivo con tarjetas detalladas (stakes, bookmakers, cuotas, retorno).
- Notificaciones Telegram con emojis por bookmaker.
- Tarea programada activa: 8 ejecuciones/día (328 créditos/día = 1.64% del plan).
- Logs diarios en carpeta logs/ para auditoría.
- Pipeline a prueba de fallos: reintentos (3), timeout (10s), encoding UTF-8.

⚠️ Configuración actual (NO modificar sin consultar):
- Umbral mínimo de profit: 1.5% (config.yaml → arbitrage.min_profit_percent)
- Ventana de deduplicación: 1 hora (config.yaml → pipeline.dedup_window_hours)
- Margen pre-partido: 10 minutos (config.yaml → odds_api.min_minutes_to_start)
- Mercados: h2h, totals (config.yaml → odds_api.markets)
- Regiones: eu (config.yaml → odds_api.regions)

📊 LAS 41 LIGAS CONFIGURADAS (slugs oficiales de The Odds API)
soccer_argentina_primera_division, soccer_austria_bundesliga, soccer_belgium_first_div,
soccer_brazil_campeonato, soccer_brazil_serie_b, soccer_chile_campeonato,
soccer_china_superleague, soccer_concacaf_leagues_cup, soccer_conmebol_copa_libertadores,
soccer_conmebol_copa_sudamericana, soccer_denmark_superliga, soccer_efl_champ,
soccer_england_league1, soccer_england_league2, soccer_epl, soccer_finland_veikkausliiga,
soccer_france_ligue_one, soccer_france_ligue_two, soccer_germany_bundesliga,
soccer_germany_bundesliga2, soccer_germany_dfb_pokal, soccer_germany_liga3,
soccer_greece_super_league, soccer_italy_serie_a, soccer_italy_serie_b,
soccer_japan_j_league, soccer_korea_kleague1, soccer_mexico_ligamx,
soccer_netherlands_eredivisie, soccer_norway_eliteserien, soccer_poland_ekstraklasa,
soccer_portugal_primeira_liga, soccer_russia_premier_league, soccer_spain_la_liga,
soccer_spain_segunda_division, soccer_sweden_allsvenskan, soccer_sweden_superettan,
soccer_turkey_super_league, soccer_uefa_champs_league_qualification,
soccer_uefa_nations_league, soccer_usa_mls

🚀 PRÓXIMOS PASOS (sesión 28+)
- Evaluar las oportunidades reales generadas automáticamente.
- Si se desea, añadir otros deportes (tenis, baloncesto) usando el endpoint /sports para obtener slugs oficiales.
- Ajustar frecuencia o umbral según resultados.
- Modelo de probabilidad para Value Betting / Dutching (no prioritario, requiere datos históricos).

📌 NOTAS PARA LA PRÓXIMA IA
- El usuario está en Paraguay (UTC‑4). Las horas de la tarea programada son locales (10:00 y 12:00‑18:00 cada hora).
- La API key está en .env (ODDS_API_KEY) y NO se debe exponer.
- Créditos: 20.000/mes. Cada ejecución consume 41 créditos. Preguntar al usuario antes de ejecutar manualmente.
- Para obtener la lista oficial de deportes disponibles, usar:
  python -c "import requests, os; from dotenv import load_dotenv; load_dotenv(); key = os.getenv('ODDS_API_KEY'); r = requests.get('https://api.the-odds-api.com/v4/sports', params={'apiKey': key}); print('\n'.join([s['key'] for s in r.json() if 'soccer' in s['key']]))"
- Los logs diarios están en C:\Users\viens\QuantBet\logs\pipeline_YYYYMMDD.log.
- El dashboard se levanta con: python -m src.web.app (localhost:5000).
- La tarea programada se gestiona con los comandos Enable/Disable-ScheduledTask.