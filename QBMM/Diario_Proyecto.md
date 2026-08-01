📋 DIARIO DE PROYECTO - QuantBet (COMPLETO v0.3.1)
🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.

Reglas implícitas (no necesito repetirlas):
Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet

"CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo)

Al final de cada sesión, actualiza este diario con el mismo formato

Mantén el contexto de todas las sesiones anteriores

Los principios de arquitectura son inmutables (ver sección Principios)

NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible

#6 - Verificación Arquitectónica Pre-Ejecución (NUEVO - Sesión 15):
Antes de generar cualquier archivo nuevo o reemplazar uno existente, la IA DEBE:

Escaneo completo del repositorio: Leer todos los archivos relevantes del proyecto, incluyendo:

src/ (todos los módulos)

tests/ (para entender los casos de prueba existentes)

QBMM/ (documentación de ingeniería para entender los principios de diseño)

config.yaml, main.py, y requirements.txt

Mapeo de dependencias: Identificar explícitamente las dependencias entre los archivos que se van a modificar y el resto del sistema.

Validación de principios: Confirmar que el cambio propuesto no viola ninguno de los 5 principios de arquitectura inmutables.

Análisis de impacto: Evaluar cómo afectará el cambio a los tests existentes y a la funcionalidad general.

Reporte de coherencia: Incluir en la respuesta un breve informe de verificación que indique:

Archivos escaneados.

Dependencias identificadas.

Principios validados.

Riesgos potenciales (si los hay) y cómo se mitigan.

Esta verificación es OBLIGATORIA y debe realizarse al inicio de CADA sesión, incluso si se solicita una continuación directa.

📋 RESUMEN EJECUTIVO
Proyecto: QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión: 0.3.1 (Completo - Fútbol, Tenis y Baloncesto)
Repositorio: https://github.com/viensa90/QuantBet
Última sesión: 20 - 01/08/2026
Estado: ✅ PLATAFORMA COMPLETA - Lista para producción

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 - Conectores solo obtienen datos (nunca toman decisiones)
#2 - Motor no conoce la fuente (recibe snapshots, no sabe de CSV/Web)
#3 - Snapshots inmutables (solo INSERT en SQLite, nunca UPDATE)
#4 - Decisiones auditables (trazabilidad completa en BD)
#5 - Configuración externalizada (config.yaml, nada hardcodeado)

📂 ESTRUCTURA DEL PROYECTO
QuantBet/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # CI - Tests y validación
│   │   ├── stress.yml          # Tests de estrés diarios
│   │   └── release.yml         # Creación de releases
│   └── dependabot.yml          # Actualización automática de dependencias
├── .pre-commit-config.yaml     # Hooks de calidad
├── QBMM/                        # Documentación de ingeniería
├── src/
│   ├── __init__.py             # v0.3.1
│   ├── config_loader.py        # Singleton para config.yaml
│   ├── logger.py               # Logging estructurado
│   ├── domain/
│   │   └── entities.py         # Entidades (incluye Tenis y Baloncesto)
│   ├── storage/
│   │   ├── database.py         # Singleton SQLite optimizado
│   │   ├── repository.py       # CRUD optimizado con índices
│   │   └── migrations.py       # Gestor de migraciones
│   ├── core/
│   │   ├── arbitrage.py        # Motor de arbitraje multi-mercado
│   │   ├── scorer.py           # Puntuador 0-100 por mercado
│   │   ├── bankroll.py         # Validador de fondos
│   │   ├── value_betting.py    # Detector con modelos reales
│   │   ├── dutching.py         # Calculador de dutching
│   │   ├── market_handlers.py  # Handlers: 11 mercados (Fútbol, Tenis, Baloncesto)
│   │   ├── probability_model.py # Historical, Elo models
│   │   └── poisson_model.py    # Modelo Poisson para fútbol
│   ├── connectors/
│   │   ├── base.py             # Interfaz IDataProvider
│   │   ├── csv_provider.py     # Implementación CSV
│   │   ├── web_provider.py     # Implementación Playwright
│   │   └── factory.py          # Fábrica de conectores
│   ├── notifications/          # Sistema de notificaciones
│   │   ├── __init__.py
│   │   ├── email_notifier.py
│   │   ├── telegram_notifier.py
│   │   └── notification_manager.py
│   └── web/
│       ├── __init__.py         # Módulo web
│       ├── app.py              # Flask + APIs REST
│       ├── templates/
│       │   └── index.html      # Dashboard principal
│       └── static/
│           ├── style.css       # Dark mode
│           └── app.js          # Actualización en tiempo real
├── tests/
│   ├── test_arbitrage.py       # 5 tests
│   ├── test_integration.py     # 7 tests
│   ├── test_bankroll.py        # 7 tests
│   ├── test_value_betting.py   # 3 tests
│   ├── test_dutching.py        # 4 tests
│   ├── test_web_provider.py    # 5 tests
│   ├── test_dashboard.py       # 5 tests
│   ├── test_market_handlers.py # 5 tests
│   ├── test_probability_model.py # 6 tests
│   ├── test_migrations.py      # 5 tests
│   ├── test_stress.py          # 6 tests de estrés
│   ├── test_notifications.py   # 3 tests
│   ├── test_tennis_handlers.py # 5 tests
│   └── test_basketball_handlers.py # 6 tests
├── data/
│   ├── sample_events.csv       # Datos de ejemplo (Fútbol)
│   ├── team_stats.csv          # Datos históricos
│   ├── tennis_events.csv       # Datos de Tenis
│   └── basketball_events.csv   # Datos de Baloncesto
├── main.py                     # CLI v0.3.1
├── config.yaml                 # Configuración centralizada v0.3.1
├── requirements.txt            # Dependencias
├── Makefile                    # Comandos de desarrollo
├── README.md                   # Documentación pública
└── quantbet.db                 # SQLite (autogenerada)
🔄 HISTORIAL DE SESIONES
Sesión 10 - 30/07/2026 - Value Betting y Dutching
Entregables: Implementación de ValueBetDetector, DutchingCalculator y tests.

Sesión 11 - 31/07/2026 - Conector Web con Playwright
Entregables: WebProvider, Factory, configuración web.

Sesión 12 - 31/07/2026 - Dashboard Web
Entregables: Módulo web completo (Flask + APIs).

Sesión 13 - 31/07/2026 - Soporte Multi-Mercado Avanzado
Entregables: Handlers para 1X2, Over/Under, Asian Handicap, Double Chance.

Sesión 14 - 31/07/2026 - Modelo de Probabilidades Reales
Entregables: HistoricalModel, EloModel, PoissonModel.

Sesión 15 - 31/07/2026 - Optimización de Queries SQLite
Entregables: Migraciones, índices, market_summary, PRAGMA optimizados.

Sesión 16 - 31/07/2026 - Tests de Estrés (1000+ eventos)
Entregables: test_stress.py con 6 pruebas de rendimiento.

Sesión 17 - 31/07/2026 - CI/CD con GitHub Actions
Entregables: 3 workflows, dependabot, pre-commit hooks, Makefile, README.

Sesión 18 - 31/07/2026 - Sistema de Notificaciones
Entregables: EmailNotifier, TelegramNotifier, NotificationManager.

Sesión 19 - 31/07/2026 - Soporte para Tenis
Entregables: 3 handlers (Winner, Set Handicap, Total Games) y tests.

Sesión 20 - 01/08/2026 - Soporte para Baloncesto
Entregables: 4 handlers (Moneyline, Spread, Total Points, Quarter Winner) y tests.

Total de tests acumulados: 72

📊 MÉTRICAS ACTUALES (FINAL)
Métrica	Valor
Versión	0.3.1
Tests totales	72
Mercados soportados	11
Deportes soportados	3 (Fútbol, Tenis, Baloncesto)
Estrategias	3 (Arbitraje, Value Betting, Dutching)
Modelos de probabilidad	3 (Historical, Elo, Poisson)
Conectores	2 (CSV, Web)
Notificadores	2 (Email, Telegram)
Workflows CI/CD	3
Líneas de código	~4,600
Archivos totales	56
🚀 PRÓXIMOS PASOS (Opcionales / Futuro)
Prioridad Baja (Mejoras futuras ya documentadas en QBMM):
Documentación de API - Swagger/OpenAPI para endpoints del dashboard

Integración con bookmakers - Betfair, Pinnacle API

Soporte para más deportes - Béisbol, Hockey, etc.

Mejoras UI/UX - Dashboard más interactivo

Sistema de logs avanzado - Elasticsearch, Kibana

📝 DIARIO - SESIÓN 21 (PRÓXIMA)
Para iniciar Sesión 21, la IA debe:

Verificación Arquitectónica Pre-Ejecución:

Escanear todo el repositorio (archivos actualizados de Sesión 20)

Identificar el área de mejora solicitada (ej: Documentación de API)

Validar principios de arquitectura

Leer repositorio completo (ya escaneado en sesión anterior)

Verificar estado actual vs este diario

Confirmar tests pasando (72/72)

Proponer siguiente ítem de la lista de mejoras futuras.

Ejecutar sin pedir confirmación para lecturas

Estado actual: ✅ PLATAFORMA COMPLETA - 100% funcional
Total archivos: 56
Total líneas: ~4,600
Total tests: 72

¡Listo para la próxima sesión de mejora! 🚀

🔗 ENLACES ÚTILES
Repositorio: https://github.com/viensa90/QuantBet

Último commit: 3d288d7 (Agosto 1, 2026)

Documentación QBMM: Carpeta /QBMM/ en el repositorio

Dashboard: make serve o python main.py --serve

Tests: make test (rápidos) o make stress (estrés)

Fin del Diario de Proyecto - QuantBet v0.3.1