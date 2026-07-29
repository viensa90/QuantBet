# QuantBet - Diario de Ingeniería

## Contexto General del Proyecto

**Nombre:** QuantBet
**Descripción:** Plataforma de inteligencia cuantitativa para mercados de predicción.
**Objetivo MVP:** Construir un núcleo funcional que detecte oportunidades de arbitraje desde datos locales, con arquitectura modular y pruebas automatizadas.

**Stack Tecnológico:**
- Python 3.14
- SQLite (sin ORM)
- pandas, PyYAML, pytest
- Playwright (futuro)

**Documentos de Ingeniería (QBMM):**
- `QB-001`: Filosofía y Principios Inmutables
- `QB-002`: Modelo de Dominio Conceptual
- `QB-003`: Especificación de Interfaces y Contratos
- `QB-004`: Motor de Estrategias y Gestión de Banca
- `QB-005`: Plan de Implementación del MVP
- `Diario_Proyecto.md`: Este archivo

**Principios Clave:**
1. Los Conectores solo obtienen datos, nunca deciden.
2. El Motor Matemático no conoce la fuente de datos.
3. Los Snapshots son inmutables (solo INSERT).
4. Toda decisión debe ser auditable.
5. Ningún parámetro crítico va en el código (config.yaml).

**Estructura del Proyecto:**
QuantBet/
├── QBMM/ # Documentación de ingeniería
│ ├── QBMM_Control_Metodologia.md
│ ├── QB-001 a QB-005
│ └── Diario_Proyecto.md
├── src/
│ ├── domain/
│ │ └── entities.py # Entidades: Event, Market, Snapshot, Decision, etc.
│ ├── storage/
│ │ ├── database.py # Singleton SQLite, crea 9 tablas
│ │ └── repository.py # Funciones save/get para entidades
│ ├── core/
│ │ ├── arbitrage.py # ArbitrageEngine: detecta surebets
│ │ └── scorer.py # OpportunityScorer: puntúa 0-100
│ └── connectors/ # (vacío, próximo hito)
├── tests/
│ └── test_arbitrage.py # 5 tests unitarios (pasando)
├── config.yaml # Parámetros configurables
├── requirements.txt
└── quantbet.db # Base de datos SQLite generada

---

## Sesión 1 - 28/07/2026 (Mañana)
**Objetivo:** Definir identidad del proyecto.

**Decisiones Tomadas:**
- QuantBet no es un buscador de apuestas, es un sistema de toma de decisiones.
- Principio fundamental: "Transformar datos en decisiones objetivas, reproducibles y auditables."
- ADR-000 aprobado.

**Entregables:**
- `QB-001_Filosofia_QuantBet.md` (APROBADO)

---

## Sesión 2 - 28/07/2026 (Tarde)
**Objetivo:** Diseñar el Modelo de Dominio Conceptual.

**Decisiones Tomadas:**
- `Snapshot` es la entidad central y el activo más valioso.
- Historial inmutable: los Snapshots nunca se modifican ni eliminan.
- Modelo de relaciones: Bookmaker → Snapshot ← Market, Event → Market, Competition → Event, Sport → Competition.

**Entregables:**
- `QB-002_Modelo_Dominio.md` (APROBADO)

---

## Sesión 3 - 28/07/2026
**Objetivo:** Definir interfaces y contratos.

**Decisiones Tomadas:**
- Interfaz `IDataProvider` para todos los conectores.
- Capa de Normalización entre conectores y motor.
- Contrato del Motor de Análisis: entrada `List[Snapshot]`, salida `List[Decision]`.

**Entregables:**
- `QB-003_Especificacion_Interfaces.md` (APROBADO)

---

## Sesión 4 - 28/07/2026
**Objetivo:** Diseñar el Motor de Estrategias.

**Decisiones Tomadas:**
- Estrategias iniciales: Arbitraje, Value Betting (futuro), Dutching (futuro).
- `Opportunity Score` combina ROI, tiempo, liquidez y confianza.
- `Bankroll` con fracción máxima por operación (5%).

**Entregables:**
- `QB-004_Motor_Estrategias.md` (APROBADO)

---

## Sesión 5 - 28/07/2026
**Objetivo:** Planificar el MVP.

**Decisiones Tomadas:**
- MVP no incluye scraping real (solo CSV simulado).
- 4 hitos: Dominio+DB, Motor+Scorer, CSV Provider, Integración.
- Estructura de carpetas definida.

**Entregables:**
- `QB-005_Plan_MVP.md` (APROBADO)

---

## Sesión 6 - 28/07/2026
**Objetivo:** Implementar base de datos SQLite.

**Decisiones Tomadas:**
- Singleton `DatabaseManager` para conexión única.
- PRAGMA WAL y foreign_keys activados.
- Tablas: sports, competitions, events, bookmakers, markets, outcomes, snapshots, decisions, bankroll_history.

**Errores Corregidos:**
- Error de orden de campos en `entities.py`. Los campos con default deben ir al final.

**Entregables:**
- `src/storage/database.py` (funcionando)
- `src/storage/repository.py` (funcionando)
- `entities.py` (v1.1 corregida)

---

## Sesión 7 - 28/07/2026 (Cierre)
**Objetivo:** Implementar Motor de Arbitraje y Scorer.

**Entregables:**
- `src/core/arbitrage.py` (ArbitrageEngine con cálculo de overround)
- `src/core/scorer.py` (OpportunityScorer con pesos configurables)
- `src/core/__init__.py`
- `tests/test_arbitrage.py` (5 tests: OK)

**Resultado de Tests:**
tests/test_arbitrage.py::test_arbitrage_detected PASSED
tests/test_arbitrage.py::test_no_arbitrage PASSED
tests/test_arbitrage.py::test_empty_snapshots PASSED
tests/test_arbitrage.py::test_single_snapshot PASSED
tests/test_arbitrage.py::test_snapshot_validation PASSED
5 passed in 0.16s

---

## Estado Actual del Backlog

- [x] **Hito 1:** Dominio y Persistencia (entities, database, repository)
- [x] **Hito 2:** Motor de Arbitraje y Scorer
- [ ] **Hito 3:** Conector Simulado (CSV Provider)
- [ ] **Hito 4:** Integración y main.py

---

## Próxima Sesión (Sesión 8)

**Objetivo:** Implementar Hito 3: Conector Simulado (CSV Provider).

**Archivos a crear:**
- `src/connectors/__init__.py`
- `src/connectors/base.py` (clase abstracta IDataProvider)
- `src/connectors/csv_provider.py` (implementación concreta)
- `data/sample_events.csv` (datos de prueba)

**Documentos de referencia:**
- `QB-003`: Especificación de Interfaces
- `QB-005`: Plan MVP, Hito 3

**Preparación del usuario:**
- Repositorio GitHub (publico): https://github.com/viensa90/QuantBet


SESIÓN 8 - ARRANQUE RÁPIDO
Último hito: Motor Arbitraje (5/5 tests OK).
Archivos activos: entities.py v1.1, database.py, repository.py, arbitrage.py, scorer.py.
Objetivo: Crear src/connectors/base.py + csv_provider.py + data/sample_events.csv.
Principio clave: IDataProvider como contrato (QB-003).
Backlog: Hito 3 de 4. Falta solo CSV Provider + Integración para MVP.