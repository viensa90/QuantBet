📋 DIARIO DE PROYECTO - QuantBet
🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.

Reglas implícitas (no necesito repetirlas):

Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet

"CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo)

Al final de cada sesión, actualiza este diario con el mismo formato

Mantén el contexto de todas las sesiones anteriores

Los principios de arquitectura son inmutables (ver sección Principios)

NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible

📋 RESUMEN EJECUTIVO
Proyecto: QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión: 0.3.0 (Multi-Mercado + Modelos de Probabilidad)
Repositorio: https://github.com/viensa90/QuantBet
Última sesión: 14 - 31/07/2026
Estado: Modelo de probabilidades reales implementado

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 - Conectores solo obtienen datos (nunca toman decisiones)

#2 - Motor no conoce la fuente (recibe snapshots, no sabe de CSV/Web)

#3 - Snapshots inmutables (solo INSERT en SQLite, nunca UPDATE)

#4 - Decisiones auditables (trazabilidad completa en BD)

#5 - Configuración externalizada (config.yaml, nada hardcodeado)

📂 ESTRUCTURA DEL PROYECTO
QuantBet/
├── QBMM/                          # Documentación de ingeniería
├── src/
│   ├── __init__.py                # v0.3.0
│   ├── config_loader.py           # Singleton para config.yaml
│   ├── logger.py                  # Logging estructurado
│   ├── domain/
│   │   └── entities.py            # Snapshot, Opportunity, MarketType, ValueBet, Dutching
│   ├── storage/
│   │   ├── database.py            # Singleton SQLite
│   │   └── repository.py          # CRUD snapshots + decisiones
│   ├── core/
│   │   ├── arbitrage.py           # Motor de arbitraje multi-mercado
│   │   ├── scorer.py              # Puntuador 0-100 por mercado
│   │   ├── bankroll.py            # Validador de fondos
│   │   ├── value_betting.py       # Detector con modelos reales
│   │   ├── dutching.py            # Calculador de dutching
│   │   ├── market_handlers.py     # Handlers: 1X2, Over/Under, Asian, Double Chance
│   │   ├── probability_model.py   # Historical, Elo models
│   │   └── poisson_model.py       # Modelo Poisson para fútbol
│   ├── connectors/
│   │   ├── base.py                # Interfaz IDataProvider
│   │   ├── csv_provider.py        # Implementación CSV
│   │   ├── web_provider.py        # Implementación Playwright
│   │   └── factory.py             # Fábrica de conectores
│   └── web/
│       ├── __init__.py            # Módulo web
│       ├── app.py                 # Flask + APIs REST
│       ├── templates/
│       │   └── index.html         # Dashboard principal
│       └── static/
│           ├── style.css          # Dark mode
│           └── app.js             # Actualización en tiempo real
├── tests/
│   ├── test_arbitrage.py          # 5 tests (incluye multi-mercado)
│   ├── test_integration.py        # 7 tests
│   ├── test_bankroll.py           # 7 tests
│   ├── test_value_betting.py      # 3 tests
│   ├── test_dutching.py           # 4 tests
│   ├── test_web_provider.py       # 5 tests
│   ├── test_dashboard.py          # 5 tests
│   ├── test_market_handlers.py    # 5 tests
│   └── test_probability_model.py  # 6 tests
├── data/
│   ├── sample_events.csv          # 21 snapshots (3 eventos)
│   └── team_stats.csv             # 10 equipos (datos históricos)
├── main.py                        # CLI con --mode, --source, --markets, --serve
├── config.yaml                    # Configuración centralizada
├── requirements.txt               # pytest, pyyaml, playwright, Flask, Jinja2
└── quantbet.db                    # SQLite (autogenerada)
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

📊 MÉTRICAS ACTUALES
Métrica	Valor
Tests totales	47
Cobertura principios	5/5 ✅
Mercados soportados	4 (1X2, Over/Under, Asian Handicap, Double Chance)
Modelos de probabilidad	3 (Historical, Elo, Poisson)
Conectores	2 (CSV, Web)
Estrategias	3 (Arbitraje, Value Betting, Dutching)
Líneas de código	~2,500
🚀 PRÓXIMOS PASOS (Priorizados)
Prioridad Media (pendiente):
~~Value Betting y Dutching~~ ✅ (Sesión 10)

~~Conectores reales con Playwright~~ ✅ (Sesión 11)

~~Dashboard web para visualización~~ ✅ (Sesión 12)

~~Soporte multi-mercado avanzado~~ ✅ (Sesión 13)

~~Modelo de probabilidades reales~~ ✅ (Sesión 14)

Optimización de queries SQLite ← SIGUIENTE

Tests de estrés (1000+ eventos)

CI/CD con GitHub Actions

Prioridad Baja:
Soporte para más deportes (tenis, baloncesto)

Integración con APIs de bookmakers (Betfair, etc.)

Sistema de notificaciones (email/telegram)

📝 DIARIO - SESIÓN 15 (PRÓXIMA)
Para iniciar Sesión 15, la IA debe:

Leer repositorio completo (ya escaneado en esta sesión)

Verificar estado actual vs este diario

Confirmar tests pasando (47/47)

Proponer siguiente ítem de Prioridad Media: Optimización de queries SQLite

Ejecutar sin pedir confirmación para lecturas

Estado actual: ✅ Todo validado y sincronizado
Total archivos: ~40
Total líneas: ~2,500
Total tests: 47

¡Listo para la Sesión 15! 🚀