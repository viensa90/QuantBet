📋 DIARIO DE PROYECTO - QuantBet (COMPLETO)
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
Versión: 0.3.1 (Optimización de Rendimiento + CI/CD)
Repositorio: https://github.com/viensa90/QuantBet
Última sesión: 17 - 31/07/2026
Estado: ✅ Sistema optimizado, probado con 5,000+ eventos y CI/CD implementado

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
│   │   ├── ci.yml              # CI - Tests y validación (NUEVO v0.3.1)
│   │   ├── stress.yml          # Tests de estrés diarios (NUEVO v0.3.1)
│   │   └── release.yml         # Creación de releases (NUEVO v0.3.1)
│   └── dependabot.yml          # Actualización automática de dependencias (NUEVO v0.3.1)
├── .pre-commit-config.yaml     # Hooks de calidad (NUEVO v0.3.1)
├── QBMM/                        # Documentación de ingeniería
├── src/
│   ├── __init__.py             # v0.3.1
│   ├── config_loader.py        # Singleton para config.yaml
│   ├── logger.py               # Logging estructurado
│   ├── domain/
│   │   └── entities.py         # Snapshot, Opportunity, MarketType, ValueBet, Dutching
│   ├── storage/
│   │   ├── database.py         # Singleton SQLite optimizado (v0.3.1)
│   │   ├── repository.py       # CRUD optimizado con índices (v0.3.1)
│   │   └── migrations.py       # Gestor de migraciones (v0.3.1)
│   ├── core/
│   │   ├── arbitrage.py        # Motor de arbitraje multi-mercado
│   │   ├── scorer.py           # Puntuador 0-100 por mercado
│   │   ├── bankroll.py         # Validador de fondos
│   │   ├── value_betting.py    # Detector con modelos reales
│   │   ├── dutching.py         # Calculador de dutching
│   │   ├── market_handlers.py  # Handlers: 1X2, Over/Under, Asian, Double Chance
│   │   ├── probability_model.py # Historical, Elo models
│   │   └── poisson_model.py    # Modelo Poisson para fútbol
│   ├── connectors/
│   │   ├── base.py             # Interfaz IDataProvider
│   │   ├── csv_provider.py     # Implementación CSV
│   │   ├── web_provider.py     # Implementación Playwright
│   │   └── factory.py          # Fábrica de conectores
│   └── web/
│       ├── __init__.py         # Módulo web
│       ├── app.py              # Flask + APIs REST (v0.3.1)
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
│   ├── test_migrations.py      # 5 tests (v0.3.1)
│   └── test_stress.py          # 6 tests de estrés (v0.3.1 NUEVO)
├── data/
│   ├── sample_events.csv       # 21 snapshots (3 eventos)
│   └── team_stats.csv          # 10 equipos (datos históricos)
├── main.py                     # CLI v0.3.1
├── config.yaml                 # Configuración centralizada v0.3.1
├── requirements.txt            # Dependencias
├── Makefile                    # Comandos de desarrollo (NUEVO v0.3.1)
├── README.md                   # Documentación pública (NUEVO v0.3.1)
└── quantbet.db                 # SQLite (autogenerada)
🔄 HISTORIAL DE SESIONES
Sesión 10 - 30/07/2026 - Value Betting y Dutching
Objetivo: Implementar estrategias de Value Betting y Dutching (Prioridad Media).

Entregables:

CREAR src/core/value_betting.py - ValueBetDetector

CREAR src/core/dutching.py - DutchingCalculator

CREAR tests/test_value_betting.py - 3 tests

CREAR tests/test_dutching.py - 4 tests

REEMPLAZAR main.py - Pipeline multi-estrategia con modos

Decisiones:

ValueBetDetector usa probabilidades justas de ejemplo (pendiente integrar modelo real)

DutchingCalculator calcula stakes proporcionales para cobertura total

Pipeline unificado: run(mode=...) selecciona la estrategia

Nuevos tests: 7 → Total tests: 26

Sesión 11 - 31/07/2026 - Conector Web con Playwright
Objetivo: Implementar conector real con Playwright para scraping web.

Entregables:

CREAR src/connectors/web_provider.py - WebProvider con Playwright sincrónico

CREAR src/connectors/factory.py - Fábrica de conectores

REEMPLAZAR config.yaml - Sección web_scraping

REEMPLAZAR main.py - Soporte --source csv|web

CREAR tests/test_web_provider.py - 5 tests

Decisiones:

Playwright sincrónico para simplicidad

Lazy loading del navegador

Context manager para liberación de recursos

Nuevos tests: 5 → Total tests: 31

Sesión 12 - 31/07/2026 - Dashboard Web
Objetivo: Implementar dashboard web para visualización de oportunidades.

Entregables:

CREAR src/web/ - Módulo completo (app, templates, static)

REEMPLAZAR main.py - Comando --serve

REEMPLAZAR requirements.txt - Flask, Jinja2

CREAR tests/test_dashboard.py - 5 tests

Decisiones:

Flask por simplicidad

Dark mode por defecto

APIs REST para comunicación

Actualización automática cada 30 segundos

Nuevos tests: 5 → Total tests: 36

Sesión 13 - 31/07/2026 - Soporte Multi-Mercado Avanzado
Objetivo: Implementar soporte para mercados avanzados.

Entregables:

REEMPLAZAR src/domain/entities.py - Nuevos MarketTypes

CREAR src/core/market_handlers.py - Handlers específicos

REEMPLAZAR src/core/arbitrage.py - Motor multi-mercado

REEMPLAZAR src/core/scorer.py - Puntuación por mercado

REEMPLAZAR config.yaml - markets.enabled

REEMPLAZAR main.py - Comando --markets

CREAR tests/test_market_handlers.py - 5 tests

Decisiones:

Handlers específicos por mercado (Strategy Pattern)

Over/Under con línea configurable

Asian Handicap con handicap configurable

Double Chance con combinaciones 1X, X2, 12

Nuevos tests: 5 → Total tests: 41

Sesión 14 - 31/07/2026 - Modelo de Probabilidades Reales
Objetivo: Implementar modelo de probabilidades reales para value betting.

Entregables:

CREAR src/core/probability_model.py - HistoricalModel, EloModel

CREAR src/core/poisson_model.py - PoissonModel para fútbol

REEMPLAZAR src/core/value_betting.py - Integrar modelos reales

REEMPLAZAR config.yaml - Configuración del modelo

CREAR data/team_stats.csv - Datos de ejemplo (10 equipos)

CREAR tests/test_probability_model.py - 6 tests

Decisiones:

Modelo Historical basado en estadísticas de equipos

Modelo Elo basado en ratings dinámicos

Modelo Poisson para predicción exacta de resultados

Factory para seleccionar modelo vía configuración

Nuevos tests: 6 → Total tests: 47

Sesión 15 - 31/07/2026 - Optimización de Queries SQLite
Objetivo: Optimizar el rendimiento de la base de datos SQLite para consultas rápidas y escalabilidad.

Entregables:

CREAR src/storage/migrations.py - Gestor de migraciones con índices y optimizaciones

REEMPLAZAR src/storage/database.py - Singleton con PRAGMA de rendimiento y pool de conexiones

REEMPLAZAR src/storage/repository.py - Consultas optimizadas con índices y market_summary

REEMPLAZAR src/web/app.py - APIs usando market_summary para respuestas rápidas

REEMPLAZAR config.yaml - Sección database con parámetros de rendimiento

REEMPLAZAR main.py - Integración de migraciones al inicio, nuevos comandos --stats y --cleanup

CREAR tests/test_migrations.py - 5 pruebas de migraciones y optimizaciones

Decisiones:

8 índices creados para consultas frecuentes (timestamp, event_id, market_type, strategy, etc.)

Tabla market_summary como vista materializada para respuestas rápidas del dashboard

PRAGMA optimizados: WAL, NORMAL sync, cache 20MB, temp_store=MEMORY

Sistema de migraciones versionado para futuras actualizaciones

Comando --stats para diagnóstico y --cleanup para mantenimiento

Nuevos tests: 5 → Total tests: 52

Sesión 16 - 31/07/2026 - Tests de Estrés (1000+ eventos)
Objetivo: Validar el rendimiento del sistema con grandes volúmenes de datos.

Entregables:

CREAR tests/test_stress.py - 6 tests de estrés

REEMPLAZAR pytest.ini - Configuración para tests lentos

REEMPLAZAR requirements.txt - Añadir pytest-timeout y pytest-xdist

Decisiones:

Generador de datos masivos (hasta 5,000 eventos)

Tests de rendimiento para arbitraje, value betting y dutching

Validación de market_summary con 2,000 eventos

Pruebas de cleanup y operaciones concurrentes

Marca @pytest.mark.slow para tests de estrés

Nuevos tests: 6 → Total tests: 58

Sesión 17 - 31/07/2026 - CI/CD con GitHub Actions
Objetivo: Implementar pipelines de integración continua y despliegue continuo.

Entregables:

CREAR .github/workflows/ci.yml - CI con tests, linting y cobertura

CREAR .github/workflows/stress.yml - Tests de estrés programados

CREAR .github/workflows/release.yml - Creación automática de releases

CREAR .github/dependabot.yml - Actualización automática de dependencias

CREAR .pre-commit-config.yaml - Hooks de calidad (Black, flake8, mypy, bandit)

CREAR Makefile - Comandos de desarrollo (install, test, stress, lint, format, coverage, serve, clean)

CREAR README.md - Documentación pública con badges de CI

Decisiones:

CI ejecuta tests en Python 3.9, 3.10, 3.11

Tests de estrés ejecutados diariamente a las 2:00 AM

Cobertura mínima requerida: 70%

Pre-commit hooks para mantener calidad de código

Dependabot para mantener dependencias actualizadas

Makefile para simplificar comandos de desarrollo

📊 MÉTRICAS ACTUALES
Métrica	Valor
Versión	0.3.1
Tests totales	58
Tests de estrés	6 (5,000+ eventos)
Workflows CI/CD	3
Pre-commit hooks	12
Cobertura principios	5/5 ✅
Mercados soportados	4 (1X2, Over/Under, Asian Handicap, Double Chance)
Modelos de probabilidad	3 (Historical, Elo, Poisson)
Conectores	2 (CSV, Web)
Estrategias	3 (Arbitraje, Value Betting, Dutching)
Índices SQLite	8
Tablas de resumen	1 (market_summary)
PRAGMA optimizados	5
Líneas de código	~3,400
Archivos totales	48
🚀 PRÓXIMOS PASOS (Priorizados)
Prioridad Media (COMPLETADO):
~~Value Betting y Dutching~~ ✅ (Sesión 10)

~~Conectores reales con Playwright~~ ✅ (Sesión 11)

~~Dashboard web para visualización~~ ✅ (Sesión 12)

~~Soporte multi-mercado avanzado~~ ✅ (Sesión 13)

~~Modelo de probabilidades reales~~ ✅ (Sesión 14)

~~Optimización de queries SQLite~~ ✅ (Sesión 15)

~~Tests de estrés (1000+ eventos)~~ ✅ (Sesión 16)

~~CI/CD con GitHub Actions~~ ✅ (Sesión 17)

Prioridad Baja (pendiente):
Sistema de notificaciones (email/telegram)

Soporte para más deportes (tenis, baloncesto)

Integración con APIs de bookmakers (Betfair, etc.)

Documentación de API (Swagger/OpenAPI)

📝 DIARIO - SESIÓN 18 (PRÓXIMA)
Para iniciar Sesión 18, la IA debe:

Verificación Arquitectónica Pre-Ejecución:

Escanear todo el repositorio (archivos actualizados de Sesión 17)

Mapear dependencias del sistema de notificaciones

Validar principios de arquitectura

Leer repositorio completo (ya escaneado en sesión anterior)

Verificar estado actual vs este diario

Confirmar tests pasando (58/58)

Proponer siguiente ítem de Prioridad Baja: Sistema de notificaciones (email/telegram)

Ejecutar sin pedir confirmación para lecturas

Estado actual: ✅ Todo validado y sincronizado
Total archivos: 48
Total líneas: ~3,400
Total tests: 58
Progreso total: 8/11 tareas (73%) 🚀

¡Listo para la Sesión 18! 🎯

🔗 ENLACES ÚTILES
Repositorio: https://github.com/viensa90/QuantBet

Último commit: 3d288d7 (Agosto 1, 2026)

Documentación QBMM: Carpeta /QBMM/ en el repositorio

Dashboard: make serve o python main.py --serve

Tests: make test (rápidos) o make stress (estrés)

Fin del Diario de Proyecto - QuantBet v0.3.1