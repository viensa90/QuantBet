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
**Versión:** 0.1.0 (MVP + Mejoras)  
**Repositorio:** https://github.com/viensa90/QuantBet  
**Última sesión:** 9 - 29/07/2026  
**Estado:** MVP completado + Deuda técnica prioritaria resuelta

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
│ ├── init.py # v0.1.0
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
│ │ └── bankroll.py # Validador de fondos
│ └── connectors/
│ ├── base.py # Interfaz IDataProvider
│ └── csv_provider.py # Implementación CSV
├── tests/
│ ├── test_arbitrage.py # 5 tests unitarios
│ ├── test_integration.py # 7 tests integración
│ └── test_bankroll.py # 7 tests bankroll
├── data/
│ └── sample_events.csv # 21 snapshots (3 eventos)
├── main.py # CLI + Pipeline 7 pasos
├── config.yaml # Configuración centralizada
├── requirements.txt # pytest, pyyaml
└── quantbet.db # SQLite (autogenerada)

---

## 🔄 HISTORIAL DE SESIONES

### Sesión 9 - 29/07/2026 - Deuda Técnica Prioritaria

**Objetivo:** Resolver 3 items de deuda técnica del MVP.

**Entregables:**
- CREAR `src/config_loader.py` - Singleton ConfigLoader (notación punto)
- CREAR `src/logger.py` - Logging estructurado (consola + archivo)
- CREAR `src/core/bankroll.py` - BankrollManager (validación pre-ejecución)
- CREAR `tests/test_bankroll.py` - 7 tests unitarios
- REEMPLAZAR `config.yaml` - Agregar decision.threshold, bankroll, logging
- REEMPLAZAR `main.py` - Integrar ConfigLoader, Bankroll, Logging

**Decisiones:**
- Umbral de decisión movido a `config.yaml` → Principio #5 completado ✅
- BankrollManager valida fondos antes de EJECUTAR (stake = 10% del total)
- Logging reemplaza todos los `print()` (niveles: INFO, WARNING, ERROR)
- ConfigLoader usa patrón Singleton (misma instancia en todo el pipeline)

**Deuda técnica resuelta:**
- ✅ Umbral hardcodeado → `config.yaml` (Principio #5)
- ✅ Sin validación bankroll → `BankrollManager` (QB-004)
- ✅ Prints → Logging estructurado

**Principios impactados:** #5 completado, #4 reforzado (decisiones ahora incluyen reason y stakes)

---

### Sesión 8 - 28/07/2026 - MVP: Integración Final

**Objetivo:** Implementar Hito 4 - Pipeline completo con CLI.

**Entregables:**
- CREAR `src/__init__.py` - Identidad del paquete
- CREAR `main.py` - Pipeline 7 pasos + CLI (argparse)
- CREAR `tests/test_integration.py` - 6 tests integración

**Pipeline:** 1. Obtener → 2. Persistir → 3. Agrupar → 4. Detectar → 5. Puntuar → 6. Decidir → 7. Reportar

**Umbral:** Score ≥ 60 → EJECUTAR, < 60 → SALTAR

**Comandos CLI:**
```bash
python main.py                    # Pipeline completo
python main.py --event EVT-003    # Evento específico
python main.py --list-events      # Listar eventos
python main.py --csv datos.csv    # CSV personalizado
Sesión 7 - 27/07/2026 - Conector Simulado
Objetivo: Implementar Hito 3 - CSV Provider.

Entregables:

CREAR src/connectors/base.py - Interfaz IDataProvider

CREAR src/connectors/csv_provider.py - CSVProvider

CREAR data/sample_events.csv - 21 snapshots de prueba

Eventos: EVT-001, EVT-002, EVT-003 (EVT-003 con surebet garantizado 3.76%)

Sesión 6 - 26/07/2026 - Motor de Arbitraje y Scorer
Objetivo: Implementar Hito 2 - Core.

Entregables:

CREAR src/core/arbitrage.py - ArbitrageEngine

CREAR src/core/scorer.py - OpportunityScorer

CREAR tests/test_arbitrage.py - 5 tests unitarios

Scoring: ROI (40%) + Liquidez (30%) + Confianza (30%)

Sesión 5 - 25/07/2026 - Dominio y Persistencia
Objetivo: Implementar Hito 1 - Base de datos y entidades.

Entregables:

CREAR src/domain/entities.py - Snapshot, Opportunity, ScoredOpportunity

CREAR src/storage/database.py - Singleton SQLite

CREAR src/storage/repository.py - CRUD inmutable

📊 MÉTRICAS ACTUALES
Tests totales: 19 (5 arbitraje + 7 integración + 7 bankroll)

Cobertura principios: 5/5 ✅

Snapshots prueba: 21 (3 eventos)

Oportunidad garantizada: EVT-003 (Surebet 3.76%)

Deuda técnica: 0 items críticos

🚀 PRÓXIMOS PASOS (Priorizados)
Prioridad Alta:
1. ~~Mover umbral a config.yaml~~ ✅ (Sesión 9)
2. ~~Validación de bankroll~~ ✅ (Sesión 9)
3. ~~Logging estructurado~~ ✅ (Sesión 9)

Prioridad Media:
4. Conectores reales con Playwright (scraping web)
5. Value Betting y Dutching (estrategias QB-004)
6. Dashboard web para visualización
7. Soporte multi-mercado (Over/Under, Asian Handicap)

Prioridad Baja:
8. Optimización de queries SQLite
9. Tests de estrés (1000+ eventos)
10. CI/CD con GitHub Actions

📝 DIARIO - SESIÓN 10 (PRÓXIMA)
Para iniciar Sesión 10, la IA debe:
1. Leer repositorio completo
2. Verificar estado actual vs este diario
3. Confirmar tests pasando (19/19)
4. Proponer siguiente item de Prioridad Media
5. Ejecutar sin pedir confirmación para lecturas

---

## 📊 RESUMEN FINAL SESIÓN 9

### Archivos creados/reemplazados:
1. ✅ CREAR `src/config_loader.py`
2. ✅ CREAR `src/logger.py`
3. ✅ CREAR `src/core/bankroll.py`
4. ✅ CREAR `tests/test_bankroll.py`
5. ✅ REEMPLAZAR `config.yaml`
6. ✅ REEMPLAZAR `main.py`
7. ✅ REEMPLAZAR `Diario_Proyecto.md`

### Deuda técnica resuelta:
- ✅ Principio #5 completado (umbral en config.yaml)
- ✅ QB-004: Bankroll validado antes de ejecutar
- ✅ Logging estructurado implementado

### Total tests: 19 (todos deberían pasar)

### Para la próxima sesión:
La IA leerá este diario como primer mensaje y tendrá contexto completo para continuar con Prioridad Media (conectores reales, value betting, dashboard).
