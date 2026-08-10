📋 DIARIO DE PROYECTO - QuantBet (v0.5.0 - OPERATIVO, ARBITRAJE AUTOMATIZADO)

🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.
Reglas implícitas:
- Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet
- "CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo siempre que estés completamente seguro de no romper nada)
- Al final de cada sesión, actualiza este diario con el mismo formato
- Mantén el contexto de todas las sesiones anteriores
- Los principios de arquitectura son inmutables (ver sección Principios)
- NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible
- SIEMPRE escanea minuciosamente el repositorio antes de proponer cambios

📊 RESUMEN EJECUTIVO
| Métrica | Valor |
|--------|--------|
| Proyecto | QuantBet - Sistema de Arbitraje Deportivo Automatizado |
| Versión | 0.5.0 |
| Repositorio | https://github.com/viensa90/QuantBet |
| Última sesión | 27 - 10/08/2026 |
| Estado | 🟢 OPERATIVO – Pipeline automático cada 30 min, 12 ligas, 5 bookmakers, deduplicación, filtro en vivo |
| Créditos | 20.000 peticiones/mes (plan de pago) |
| Consumo diario estimado | 168 créditos (25 % del plan mensual) |

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.5.0)
QuantBet/
├── .env.example / .env            ✅ API key real en .env
├── config.yaml                    ✅ 12 ligas, 5 bookmakers, excl. live, dedup 1h
├── main.py                        ✅ Pipeline, --simple, Telegram
├── test_local.py                  🧪 Prueba local sin créditos
├── quantbet.db                    (autogenerada, WAL)
├── src/
│   ├── config_loader.py           ✅ .env + YAML
│   ├── logger.py                  ✅ get_logger
│   ├── domain/entities.py         ✅
│   ├── storage/
│   │   ├── database.py            ✅ WAL, índice anti‑duplicados
│   │   └── repository.py          ✅ Deduplicación, guardado completo
│   ├── core/
│   │   ├── arbitrage.py           🔥 Motor genérico (ROI real, agrupa por name+point, ignora _lay)
│   │   └── market_handlers.py     ✅
│   ├── connectors/
│   │   ├── odds_api_provider.py   🔌 Filtro bookmakers, excl. live, reintentos, timeout
│   │   └── factory.py
│   ├── notifications/
│   │   └── telegram_notifier.py   ✅ Envío con emojis
│   └── web/
│       ├── app.py, api.py         ✅ Dashboard interactivo
│       └── templates/index.html   ✅ Tarjetas detalladas
├── tests/
├── tools/view_opportunities.py    ✅
└── data/

🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-24: desarrollo inicial.
Sesión 25: Auditoría, motor genérico, corrección falsos positivos.
Sesión 26: Restauración completa, mejoras (lista blanca, reintentos, timeout, dashboard).
Sesión 27 (10/08/2026): Ajuste de porcentaje (ROI real), filtro de partidos en vivo, deduplicación automática, plan de 12 ligas, programación de tarea automática cada 30 min entre 10:00 y 18:00 (hora Paraguay). Compra de 20k créditos.

🔍 ESTADO ACTUAL (v0.5.0)
✅ Funcionando y verificado:
- Arbitraje preciso con ROI real.
- Solo eventos futuros (≥10 min).
- Deduplicación en ventana de 1 h.
- Cobertura de 12 ligas de fútbol.
- Bookmakers: Pinnacle, 1xBet, BetOnline.ag, Betfair, Marathonbet (ajustable).
- Dashboard funcional y notificaciones Telegram.
- Tarea programada activa (14 ejecuciones/día, 168 créditos/día).

⚠️ Pendientes / Mejoras futuras:
- Verificar disponibilidad de Marathonbet en Paraguay.
- Añadir otros deportes (tenis, baloncesto) cuando se desee.
- Modelo de probabilidad para Value Betting / Dutching (no prioritario).

🚀 PRÓXIMOS PASOS (sesión 28+)
- Evaluar las oportunidades reales generadas automáticamente.
- Ajustar frecuencia o ligas según resultados.
- Si se desea, implementar más deportes o estrategias.
🛡️ REGLAS ESTRICTAS DE MODIFICACIÓN (ANTI-DESASTRE)

⚠️ NUNCA modificar los siguientes archivos sin una comprensión TOTAL de su función y sin preguntar primero al usuario:
- src/core/arbitrage.py (motor de arbitraje genérico)
- src/connectors/odds_api_provider.py (conector principal)
- src/storage/repository.py (persistencia y deduplicación)
- src/storage/database.py (esquema de BD y WAL)

⚠️ NUNCA renombrar funciones/clases clave (ej. get_logger, ArbitrageEngine, Outcome, AggregatedEvent) sin actualizar todas sus referencias.

⚠️ NUNCA cambiar la estructura del JSON `details` ni los nombres de los campos de la BD sin una migración explícita.

⚠️ NUNCA ejecutar `main.py` sin confirmar con el usuario el consumo de créditos.

⚠️ NUNCA eliminar el filtro de `_lay` ni la agrupación por `(name, point)`.

📋 SIEMPRE:
- Leer el archivo COMPLETO antes de sugerir un REEMPLAZO.
- Verificar que `get_logger` existe en `src/logger.py` (o usar `setup_logger` como alias).
- Verificar que `ConnectorFactory` se usa con el método `create`.
- Probar primero en `test_local.py` si se hacen cambios en el motor o el conector.
- Actualizar este diario al final de la sesión.

📌 NOTAS PARA LA PRÓXIMA IA
- El usuario está en Paraguay (UTC‑4). Las horas de la tarea programada son locales (10:00 y 12:00‑18:00).
- La API key está en .env y no se debe exponer.
- Los principios #1‑#5 son inmutables.
- Antes de hacer cambios, verificar el estado del repositorio y preguntar al usuario si hay créditos disponibles o si prefiere esperar.

Principios #1-#5 inmutables. No modificar lógica de negocio en conectores.

✅ resumen de la última Sesión – QuantBet v0.5.0 en piloto automático
Perfecto. Con la cláusula de protección integrada en el diario, el proyecto queda blindado contra futuros desastres.
Resumen de lo que dejamos funcionando:

🕐 Pipeline automático cada 30 min de 12:00 a 18:00 y a las 10:00 (hora Paraguay).

🌍 12 ligas de fútbol mundial cubiertas.

🎯 Arbitraje real con porcentaje de ROI corregido.

🧹 Deduplicación (no verás la misma oportunidad repetida en 1 h).

⚽ Filtro de partidos en vivo (solo eventos que empiezan en ≥10 min).

📊 Dashboard visual con todos los detalles operativos.

📱 Notificaciones Telegram con emojis por bookmaker.

Cualquier novedad, error o nueva idea que tengas, me avisas.