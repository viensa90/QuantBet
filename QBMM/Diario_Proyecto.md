# QuantBet - Diario de Proyecto

## 🚀 INSTRUCCIONES PARA IA (Nuevo Chat)

**Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.**

Reglas implícitas (no necesito repetirlas):
- Tienes autorización total para leer el repositorio completo en GitHub: `https://github.com/viensa90/QuantBet`
- "CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo)
- Al final de cada sesión, actualiza este diario con el mismo formato
- Mantén el contexto de todas las sesiones anteriores
- Los principios de arquitectura son inmutables (ver sección Principios)

---

## 📋 RESUMEN EJECUTIVO

**Proyecto:** QuantBet - Sistema de Arbitraje Deportivo Automatizado  
**Versión:** 0.2.0 (MVP + Value Betting & Dutching)  
**Repositorio:** https://github.com/viensa90/QuantBet  
**Última sesión:** 10 - 30/07/2026  
**Estado:** Estrategias adicionales implementadas

---

## 🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)

1. **#1 - Conectores solo obtienen datos** (nunca toman decisiones)
2. **#2 - Motor no conoce la fuente** (recibe snapshots, no sabe de CSV/Web)
3. **#3 - Snapshots inmutables** (solo INSERT en SQLite, nunca UPDATE)
4. **#4 - Decisiones auditables** (trazabilidad completa en BD)
5. **#5 - Configuración externalizada** (config.yaml, nada hardcodeado)

---

## 📂 ESTRUCTURA DEL PROYECTO
QuantBet/
├── QBMM/ # Documentación de ingeniería
├── src/
│ ├── init.py # v0.2.0
│ ├── config_loader.py # Singleton para config.yaml
│ ├── logger.py # Logging estructurado
│ ├── domain/
│ │ └── entities.py # Snapshot, Opportunity, ScoredOpportunity
│ ├── storage/
│ │ ├── database.py # Singleton SQLite
│ │ └── repository.py # CRUD snapshots + decisiones
│ ├── core/
│ │ ├── arbitrage.py # Motor de arbitraje
│ │ ├── scorer.py # Puntuador 0-100
│ │ ├── bankroll.py # Validador de fondos
│ │ ├── value_betting.py # Detector de value bets
│ │ └── dutching.py # Calculador de dutching
│ └── connectors/
│ ├── base.py # Interfaz IDataProvider
│ └── csv_provider.py # Implementación CSV
├── tests/
│ ├── test_arbitrage.py # 5 tests unitarios
│ ├── test_integration.py # 7 tests integración
│ ├── test_bankroll.py # 7 tests bankroll
│ ├── test_value_betting.py # 3 tests value betting
│ └── test_dutching.py # 4 tests dutching
├── data/
│ └── sample_events.csv # 21 snapshots (3 eventos)
├── main.py # CLI + Pipeline multi-estrategia
├── config.yaml # Configuración centralizada
├── requirements.txt # pytest, pyyaml
└── quantbet.db # SQLite (autogenerada)

---

## 🔄 HISTORIAL DE SESIONES

### Sesión 10 - 30/07/2026 - Value Betting y Dutching

**Objetivo:** Implementar estrategias de Value Betting y Dutching (Prioridad Media).

**Entregables:**
- CREAR `src/core/value_betting.py` - ValueBetDetector
- CREAR `src/core/dutching.py` - DutchingCalculator
- CREAR `tests/test_value_betting.py` - 3 tests
- CREAR `tests/test_dutching.py` - 4 tests
- REEMPLAZAR `main.py` - Pipeline multi-estrategia con modos (`--mode arbitrage|value|dutching|all`)

**Decisiones:**
- ValueBetDetector usa probabilidades justas de ejemplo (pendiente integrar modelo real).
- DutchingCalculator calcula stakes proporcionales para cobertura total.
- Pipeline unificado: `run(mode=...)` selecciona la estrategia.
- Probabilidades justas por defecto: `{"Local":0.40, "Empate":0.30, "Visitante":0.30}`.

**Nuevos tests:** 7 (3 value + 4 dutching) → Total tests: 26  
**Principios impactados:** #2 reforzado (motor no conoce fuente, aplica a value/dutching también).

---

### Sesión 9 - 29/07/2026 - Deuda Técnica Prioritaria

**Objetivo:** Resolver 3 items de deuda técnica del MVP.

**Entregables:**
- CREAR `src/config_loader.py` - Singleton ConfigLoader
- CREAR `src/logger.py` - Logging estructurado
- CREAR `src/core/bankroll.py` - BankrollManager
- CREAR `tests/test_bankroll.py` - 7 tests
- REEMPLAZAR `config.yaml` - Agregar decision.threshold, bankroll, logging
- REEMPLAZAR `main.py` - Integrar ConfigLoader, Bankroll, Logging

**Principios impactados:** #5 completado, #4 reforzado.

---

### Sesión 8 - 28/07/2026 - MVP: Integración Final

**Objetivo:** Implementar Hito 4 - Pipeline completo con CLI.

**Entregables:**
- CREAR `src/__init__.py`
- CREAR `main.py` - Pipeline 7 pasos + CLI
- CREAR `tests/test_integration.py` - 7 tests integración

---

### Sesión 7 - 27/07/2026 - Conector Simulado

**Objetivo:** Implementar Hito 3 - CSV Provider.

**Entregables:**
- CREAR `src/connectors/base.py`, `csv_provider.py`
- CREAR `data/sample_events.csv` (21 snapshots)

---

### Sesión 6 - 26/07/2026 - Motor de Arbitraje y Scorer

**Objetivo:** Implementar Hito 2 - Core.

**Entregables:**
- CREAR `src/core/arbitrage.py`, `scorer.py`
- CREAR `tests/test_arbitrage.py` (5 tests)

---

### Sesión 5 - 25/07/2026 - Dominio y Persistencia

**Objetivo:** Implementar Hito 1 - Base de datos y entidades.

**Entregables:**
- CREAR `src/domain/entities.py`
- CREAR `src/storage/database.py`, `repository.py`

---

## 📊 MÉTRICAS ACTUALES

- **Tests totales:** 26 (5 arbitraje + 7 integración + 7 bankroll + 3 value + 4 dutching)
- **Cobertura principios:** 5/5 ✅
- **Snapshots prueba:** 21 (3 eventos)
- **Oportunidad garantizada:** EVT-003 (Surebet 3.76%)
- **Deuda técnica:** 0 items críticos

---

## 🚀 PRÓXIMOS PASOS (Priorizados)

### Prioridad Alta (completada):
1. ~~Mover umbral a config.yaml~~ ✅ (Sesión 9)
2. ~~Validación de bankroll~~ ✅ (Sesión 9)
3. ~~Logging estructurado~~ ✅ (Sesión 9)

### Prioridad Media (parcial):
4. ~~Value Betting y Dutching~~ ✅ (Sesión 10)
5. Conectores reales con Playwright (scraping web)
6. Dashboard web para visualización
7. Soporte multi-mercado avanzado (Over/Under, Asian Handicap)
8. Integración de modelo de probabilidades reales para value betting

### Prioridad Baja:
9. Optimización de queries SQLite
10. Tests de estrés (1000+ eventos)
11. CI/CD con GitHub Actions

---

## 📝 DIARIO - SESIÓN 11 (PRÓXIMA)

**Para iniciar Sesión 11, la IA debe:**
1. Leer repositorio completo
2. Verificar estado actual vs este diario
3. Confirmar tests pasando (26/26)
4. Proponer siguiente ítem de Prioridad Media (probablemente scraping con Playwright o dashboard)
5. Ejecutar sin pedir confirmación para lecturas
