📋 DIARIO DE PROYECTO - QuantBet (v0.4.0 - FUNCIONAL, MOTOR GENÉRICO 2/3 OPCIONES)

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

📋 RESUMEN EJECUTIVO
Métrica	Valor
Proyecto	QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión	0.4.0
Repositorio	https://github.com/viensa90/QuantBet
Última sesión	25 - 08/08/2026
Estado	🟢 FUNCIONAL - Motor genérico, persistencia completa, alertas Telegram

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.4.0)
QuantBet/
├── .env.example                  ✅ Plantilla variables de entorno
├── .gitignore                    ✅ Protege .env, *.db, etc.
├── config.yaml                   ✅ Umbrales ajustables
├── main.py                       ✅ Pipeline, --simple, Telegram
├── quantbet.db                   (autogenerada, WAL activado)
├── QBMM/                         ✅ Documentos maestros
├── src/
│   ├── __init__.py
│   ├── config_loader.py          ✅ .env + YAML
│   ├── logger.py                 ✅ Logs estructurados
│   ├── domain/
│   │   └── entities.py           ✅ Snapshot, Odds
│   ├── storage/
│   │   ├── database.py           ✅ WAL, migración automática
│   │   ├── repository.py         ✅ Guarda event_name, sport, details JSON
│   │   └── migrations.py         (referencia)
│   ├── core/
│   │   ├── arbitrage.py          🔥 Motor genérico 2/3 opciones
│   │   ├── market_handlers.py    ✅ Mapeo h2h, totals, spreads
│   │   ├── value_betting.py      (inactivo hasta modelo real)
│   │   ├── dutching.py           (inactivo)
│   │   ├── scorer.py             (sin integrar)
│   │   ├── bankroll.py           (sin integrar)
│   │   └── probability_model.py (obsoleto)
│   ├── connectors/
│   │   ├── base.py
│   │   ├── csv_provider.py
│   │   ├── odds_api_provider.py  🔌 Conector principal
│   │   └── factory.py
│   ├── notifications/
│   │   ├── telegram_notifier.py  ✅ Envío automático de alertas
│   │   └── email_notifier.py     (opcional)
│   └── web/
│       ├── app.py                ✅ Dashboard Flask
│       └── api.py                ✅ Endpoints REST
├── tests/                        ⚠️ 83 tests (necesitan actualización)
├── tools/
│   └── view_opportunities.py     ✅ Visor de BD robustecido
└── data/

🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-24: desarrollo inicial, v0.3.4 con arbitraje solo 2 opciones.
Sesión 25 (08/08/2026): Auditoría forense y reestructuración completa.
- P0-P1 ejecutados: persistencia completa, SQLite WAL, .env, eliminación de código muerto.
- Motor de arbitraje genérico: soporta 2 y 3 opciones (fútbol 1X2, over/under, etc.) usando producto cartesiano de bookmakers disponibles en The Odds API.
- Notificaciones Telegram enganchadas.
- CLI modo --simple con salida limpia de stakes y bookmakers.

🔍 INFORME DE AUDITORÍA (v0.4.0)
✅ Lo que funciona correctamente
- Pipeline completo usando The Odds API (Pinnacle, 1xBet, etc.) – única fuente.
- Detección de arbitraje en mercados de 2 y 3 opciones.
- Guardado completo de oportunidades en BD (event_name, sport, market, details JSON).
- Dashboard sin bloqueos gracias a WAL.
- CLI --simple lista para operar manualmente.
- Notificaciones Telegram automáticas.
- Secretos en .env (fuera del repo).

⚠️ Pendiente (próxima sesión)
- Añadir reintentos y timeout en OddsAPIProvider (resiliencia).
- Desactivar modo debug en Flask (seguridad).
- Filtrar datos sensibles de los logs (que no aparezca la API key).
- Actualizar tests al nuevo motor.

🚀 PLAN DE SESIONES (SIN BETFAIR EXCHANGE)
Sesión 26 (siguiente):
- Añadir resiliencia: reintentos (3) y timeout (10s) en OddsAPIProvider.
- Validar cuotas >1.0 en el proveedor, con warning si se descartan.
- Desactivar debug de Flask (condicional a variable de entorno).
- Filtrar API key de los logs.
- Opcional: filtro por deporte en el pipeline (para ahorrar peticiones).

Sesión 27 (posterior):
- Dashboard mejorado: filtros por deporte, gráficos de profit diario.
- Script para programar ejecuciones automáticas (cron / task scheduler) respetando límite de peticiones.

Sesión 28 (a futuro):
- Modelo de probabilidad real (si se retoma value betting/dutching).
- Migración a plan de 20k peticiones de The Odds API cuando se valide rentabilidad.

Principio operativo: SOLO se usa The Odds API. Nada de APIs directas de casas de apuestas ni Exchange.