📋 DIARIO DE PROYECTO - QuantBet (v0.4.1 - ARBITRAJE REAL, FALSOS POSITIVOS ELIMINADOS)
🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.
Reglas implícitas (no necesito repetirlas):

Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet

"CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo siempre que estés completamente seguro de no romper nada)

Al final de cada sesión, actualiza este diario con el mismo formato

Mantén el contexto de todas las sesiones anteriores

Los principios de arquitectura son inmutables (ver sección Principios)

NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible

SIEMPRE escanea minuciosamente el repositorio antes de proponer cambios

📊 RESUMEN EJECUTIVO

Métrica	Valor
Proyecto	QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión	0.4.1
Repositorio	https://github.com/viensa90/QuantBet
Última sesión	25 - 08/08/2026 (incluye segunda parte)
Estado	🟢 FUNCIONAL - Solo 1 oportunidad real detectada, filtrado de líneas correcto, se prepara lista blanca de bookmakers
🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.4.1)
(Se mantiene la misma estructura base de v0.4.0 con cambios puntuales)
QuantBet/
├── .env.example                  ✅ Plantilla variables de entorno
├── .gitignore                    ✅ Protege .env, *.db, etc.
├── config.yaml                   ✅ Umbrales, deportes, mercados
├── main.py                       ✅ Pipeline, --simple, notificaciones (Telegram pendiente)
├── quantbet.db                   (autogenerada, WAL activado)
├── QBMM/                         ✅ Documentos maestros
├── src/
│   ├── __init__.py
│   ├── config_loader.py          ✅ Carga .env + YAML
│   ├── logger.py                 ✅ Logs estructurados
│   ├── domain/
│   │   └── entities.py           ✅ Entidades originales (compatibilidad)
│   ├── storage/
│   │   ├── database.py           ✅ WAL, migración automática
│   │   ├── repository.py         ✅ Guarda event_name, sport, details JSON
│   │   └── migrations.py
│   ├── core/
│   │   ├── arbitrage.py          🔥 Motor genérico (agrupa por name + point, ignora mercados _lay)
│   │   ├── market_handlers.py    ✅ Normalización de mercados
│   │   ├── value_betting.py      (inactivo)
│   │   ├── dutching.py           (inactivo)
│   │   ├── scorer.py             (inactivo)
│   │   ├── bankroll.py           (inactivo)
│   │   └── probability_model.py (obsoleto)
│   ├── connectors/
│   │   ├── base.py
│   │   ├── csv_provider.py
│   │   ├── odds_api_provider.py  🔌 Conector principal (Outcome con point, ignora _lay, por ahora sin filtro de bookmakers)
│   │   └── factory.py
│   ├── notifications/
│   │   ├── telegram_notifier.py  ✅ Envío automático (falta enganchar token)
│   │   └── email_notifier.py     (opcional)
│   └── web/
│       ├── app.py                ✅ Dashboard Flask (debug activo)
│       └── api.py                ✅ Endpoints REST
├── tests/                        ⚠️ 83 tests (necesitan actualización)
├── tools/
│   └── view_opportunities.py     ✅ Visor de BD robustecido
└── data/
🔄 HISTORIAL DE SESIONES (RESUMEN)

Sesiones 1-24: desarrollo inicial, v0.3.4 con arbitraje solo 2 opciones.

Sesión 25 (08/08/2026 - Parte 1): Auditoría forense y reestructuración completa.

Persistencia completa, SQLite WAL, .env, eliminación de código muerto.

Motor de arbitraje genérico (2 y 3 opciones) usando producto cartesiano de bookmakers.

Corrección masiva de imports y adaptación a entidades reales.

Primera ejecución exitosa: 41 oportunidades (luego se detectó que muchas eran falsas).

Sesión 25 (08/08/2026 - Parte 2): Corrección crítica de falsos positivos.

Problema detectado por el usuario: over/under mezclaba líneas diferentes (2.5 vs 2.0) y mercados h2h_lay eran tratados como back, generando arbitrajes irreales.

Solución implementada:

Outcome ahora incluye campo point (línea exacta).

OddsAPIProvider ignora cualquier mercado que contenga _lay.

ArbitrageEngine agrupa por (name, point) en lugar de solo name, garantizando que solo se emparejen cuotas con idéntica línea.

Resultado: las 41 oportunidades se redujeron a 1 oportunidad real y ejecutable (Atlético Madrid vs Villarreal 1X2, 2.16% profit).

🔍 ESTADO ACTUAL (v0.4.1)
✅ Funciona correctamente:

Motor de arbitraje genérico preciso.

Filtrado de líneas exactas y exclusión de mercados lay.

Salida limpia con --simple.

Persistencia completa en BD.

⚠️ Correcciones críticas necesarias para operatividad real:

Filtro de bookmakers operables: El usuario solo puede apostar en casas donde tiene cuenta:

Confirmadas: Pinnacle, 1xBet, BetOnline.ag, Betfair (Sportsbook, no Exchange).

Bet365, aposta.la, 360sports.pro no están en The Odds API. Marathonbet podría aparecer pero no confirmado.

La oportunidad detectada usaba Nordic Bet, que no está disponible en Paraguay, por lo que no se puede ejecutar.

Tarea inmediata (Sesión 26): Añadir lista blanca de bookmakers (allowed_bookmakers) en config.yaml y modificar OddsAPIProvider para filtrar solo esos.

Resiliencia del conector: falta de reintentos y timeout en las peticiones HTTP.

Seguridad: Flask corre en modo debug; logs exponen la API key y configuración completa.

Gestión de créditos: El plan gratuito (500 peticiones/mes) tiene actualmente 4 créditos restantes después de las pruebas (492 usados). Cada ejecución consume 1 petición por deporte. Se debe usar con mucha moderación hasta la renovación.

Notificaciones Telegram: El código existe pero no se ha verificado su funcionamiento con el token real.

📊 SITUACIÓN DE BOOKMAKERS DISPONIBLES

Bookmaker	¿Tiene cuenta?	¿Aparece en Odds API?	¿Incluido en plan gratuito?
Pinnacle	✅	✅	✅
1xBet	✅	✅	✅
BetOnline.ag	✅	✅	✅ (aparece como "BetOnline.ag")
Betfair	✅	✅ (Sportsbook)	Limitado en plan gratuito
Marathonbet	Por probar	Posiblemente	Poco frecuente
Bet365	✅	❌ No en la API	-
aposta.la	✅	❌ No en la API	-
360sports.pro	✅	❌ No en la API	-
Nordic Bet, Coolbet, etc.	❌	✅ pero no opera	-
La próxima sesión debe implementar filtro por lista blanca para que solo se usen Pinnacle, 1xBet, BetOnline.ag y Betfair (si aparece). Esto garantiza que toda oportunidad mostrada sea operable.

🚀 PLAN DE SESIONES INMEDIATAS

Sesión 26 (siguiente) – Filtro de bookmakers + robustez

Añadir allowed_bookmakers en config.yaml.

Modificar OddsAPIProvider para filtrar outcomes de bookmakers no permitidos.

Añadir reintentos (3 intentos con backoff) y timeout (10s) en requests.get.

Desactivar debug=True en Flask y filtrar API key de los logs.

Probar con python main.py --simple (consumirá 2 créditos, quedarán 2).

Objetivo: Oportunidades 100% operables con las casas del usuario.

Sesión 27 – Automatización y operación diaria

Configurar una tarea programada (cron / Windows Task Scheduler) para ejecutar 1 o 2 veces al día en horarios de alta liquidez.

Estrategia de ahorro de créditos: reducir deportes a solo La Liga y Premier League, mercados h2h,totals.

Guía de uso: cómo interpretar las salidas y ejecutar las apuestas manualmente.

Sesión 28 (futuro) – Mejoras opcionales

Value betting / Dutching con modelo de probabilidad real (requiere datos históricos).

Dashboard con métricas de rentabilidad acumulada.

Migración a plan de 20k peticiones cuando se haya validado la rentabilidad (30$/mes).

🔑 RECORDATORIOS PARA LA PRÓXIMA IA

El usuario ejecuta el proyecto en Windows PowerShell.

Los comandos habituales son:

powershell
del quantbet.db   # si es necesario reiniciar BD
python main.py --simple
python -m src.web.app   # para el dashboard
Los créditos de Odds API son críticos: no ejecutar el pipeline innecesariamente. Ante cualquier duda, preguntar al usuario antes de consumir peticiones.

Los principios de arquitectura (#1-#5) son inmutables. No se deben tomar decisiones de negocio en los conectores.

NO se debe integrar ninguna API externa de casas de apuestas ni Exchange. La única fuente de datos es The Odds API.

El usuario puede abrir cuentas en Marathonbet o cualquier otra casa que aparezca en la API, pero el sistema debe limitarse a la lista blanca que se configure.

Principio operativo: SOLO se usa The Odds API. Nada de APIs directas de casas de apuestas ni Exchange.

📁 DIARIO COMPLETO HASTA LA FECHA
(Este bloque constituye la memoria completa del proyecto y debe ser copiado íntegramente al iniciar un nuevo chat para mantener la continuidad.)

