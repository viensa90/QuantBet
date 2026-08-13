📋 DIARIO DE PROYECTO - QuantBet (v0.6.0 - ARBITRAJE EN VIVO Y LOGS COMPLETOS)

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
⚠️ NUNCA modificar sin comprensión TOTAL y sin preguntar primero al usuario:
- src/core/arbitrage.py (motor genérico: producto cartesiano, ROI real 1/inv_sum-1, agrupa por name+point, ignora _lay)
- src/connectors/odds_api_provider.py (conector principal: Outcome con point, filtro lista blanca, reintentos 3, timeout 10s, excluye/en vivo, is_live calculado)
- src/storage/repository.py (persistencia y deduplicación: save_opportunities con ventana configurable, _is_duplicate)
- src/storage/database.py (esquema BD con índice anti-duplicados, WAL activado)
- main.py (pipeline completo, --simple, --log-file, resumen con fecha/hora y live)
- config.yaml (41 ligas, 5 bookmakers, umbral 0.4%, excluye_live false, dedup 0h, 3 mercados)

⚠️ NUNCA renombrar funciones/clases clave (get_logger, ArbitrageEngine, Outcome, AggregatedEvent, etc.) sin actualizar TODAS las referencias.
⚠️ NUNCA cambiar la estructura del JSON `details` sin migración explícita.
⚠️ NUNCA ejecutar `main.py` sin confirmar consumo de créditos (41 créditos/ejecución).
⚠️ NUNCA eliminar: filtro `_lay`, agrupación por `(name, point)`, cálculo ROI, filtro de bookmakers, deduplicación.
📋 SIEMPRE: leer archivo completo antes de REEMPLAZAR, verificar get_logger, ConnectorFactory, probar con test_local.py antes de cambios en motor/conector, actualizar este diario al final.

📊 RESUMEN EJECUTIVO
| Métrica | Valor |
|--------|--------|
| Proyecto | QuantBet - Sistema de Arbitraje Deportivo Automatizado |
| Versión | 0.6.0 |
| Repositorio | https://github.com/viensa90/QuantBet |
| Última sesión | 28 - 12/08/2026 |
| Estado | 🟢 OPERATIVO – Arbitraje en vivo y pre-partido, 41 ligas, 5 bookmakers, logs completos, notificaciones con fecha/hora/live |
| Créditos | 20.000 peticiones/mes (plan de pago) |
| Consumo diario estimado | 328 créditos (1.64% del plan mensual) |
| Ejecuciones/día | 8 (10:00 + cada hora 12:00-18:00) |
| Créditos por ejecución | 41 |

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.6.0)
QuantBet/
├── .env.example / .env            ✅ API key real en .env
├── config.yaml                   ✅ 41 ligas, 5 bookmakers, umbral 0.4%, excl. live false, dedup 0h, 3 mercados
├── main.py                       ✅ Pipeline, --simple, --log-file, resumen con fecha/hora y live
├── diagnostico.py                🧪 Diagnóstico bookmakers (1 crédito)
├── test_local.py                 🧪 Prueba local sin API
├── quantbet.db                   (autogenerada, WAL, contiene oportunidades)
├── logs/                         📝 Logs por ejecución (pipeline_YYYYMMDD_HHMMSS.log)
├── src/
│   ├── config_loader.py          ✅ .env + YAML (encoding='utf-8')
│   ├── logger.py                 ✅ get_logger + alias setup_logger
│   ├── domain/entities.py        ✅ Entidades originales
│   ├── storage/
│   │   ├── database.py           ✅ WAL, índice anti-duplicados
│   │   └── repository.py         ✅ Deduplicación, guardado completo
│   ├── core/
│   │   ├── arbitrage.py          🔥 Motor genérico (ROI real, agrupa name+point, is_live, event_time)
│   │   └── market_handlers.py    ✅ Normalización de mercados
│   ├── connectors/
│   │   └── odds_api_provider.py  🔌 Filtro bookmakers, reintentos, timeout, is_live, event_time
│   ├── notifications/
│   │   └── telegram_notifier.py  ✅ maybe_notify con emojis, fecha/hora, live
│   └── web/
│       ├── app.py                ✅ Dashboard Flask
│       ├── api.py                ✅ Endpoints REST
│       └── templates/index.html  ✅ Dashboard visual con fecha/hora, live badge
├── tests/                        ⚠️ 83 tests (necesitan actualización)
├── tools/view_opportunities.py   ✅ Visor de BD
└── data/

🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-24: desarrollo inicial.
Sesión 25: Auditoría, motor genérico, corrección falsos positivos.
Sesión 26: Restauración completa, mejoras (lista blanca, reintentos, timeout, dashboard, logger, Telegram).
Sesión 27: Corrección ROI, filtro live (exclude_live inicial true), deduplicación, 41 ligas oficiales.
Sesión 28 (12/08/2026):
- Diagnóstico de bookmakers: 21 detectados, solo 5 operables para PY (Pinnacle, 1xBet, BetOnline.ag, Betfair, Marathonbet).
- Mercados ampliados a h2h,totals,spreads.
- Umbral bajado a 0.4% para captar oportunidades pequeñas.
- Habilitado arbitraje en vivo (exclude_live: false) y deduplicación en 0.
- Añadido fecha/hora y etiqueta EN VIVO en resumen, Telegram y dashboard.
- Logs completos con API key enmascarada mediante --log-file.
- Detección de oportunidades reales: 7 y 4 en pruebas, incluyendo una live de +19.75% (Palmeiras vs Cerro) y +114% (Bragantino vs Mineiro, verificada manualmente en vivo).
- Tarea programada funcionando con logs automáticos.

🔍 ESTADO ACTUAL (v0.6.0)
✅ Funciona:
- Arbitraje en vivo y pre-partido.
- Cobertura 41 ligas, 3 mercados (h2h, totals, spreads).
- Filtro por 5 bookmakers operables.
- Detección de oportunidades con ROI real.
- Notificaciones Telegram con fecha/hora y live.
- Dashboard con tarjetas detalladas.
- Logs automáticos por ejecución.
- Tarea programada 8 ejecuciones/día.

⚠️ Consideraciones:
- Arbitraje en vivo: cuotas cambian rápido, verificar manualmente antes de apostar.
- Margenes típicos: pre-partido 0.4-0.8%; en vivo pueden superar 10%.
- Dedup en 0: todas las oportunidades se registran, incluso variantes del mismo partido.
- La API no provee minuto de juego; el emoji LIVE se infiere de la hora de inicio vs ahora.

🚀 PRÓXIMOS PASOS (sesión 29+)
- Evaluar rentabilidad real tras varios días de operación.
- Ajustar umbral, frecuencia o ligas según resultados.
- Posible adición de ligas sudamericanas nocturnas para live.
- Modelo de probabilidad para Value Betting/Dutching (no prioritario).

📌 NOTAS PARA LA PRÓXIMA IA
- Usuario en Paraguay (UTC-4). Horas clave: 12:00-18:00 Europa, 20:00-23:00 Sudamérica.
- API key en .env, no exponer.
- Créditos: 41 por ejecución. Consultar al usuario antes de ejecuciones manuales.
- Comandos comunes:
  python main.py --simple --log-file logs\pipeline_manual.log
  python -m src.web.app
  python diagnostico.py
  python test_local.py
- Logs: C:\Users\viens\QuantBet\logs\pipeline_YYYYMMDD_HHMMSS.log