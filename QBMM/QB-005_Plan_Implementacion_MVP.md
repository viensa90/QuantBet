# QuantBet Master Manual (QBMM)

## QB-005 — Plan de Implementación del MVP

| Propiedad | Valor |
| :--- | :--- |
| **Código QB** | QB-005 |
| **Nombre** | Plan de Implementación del MVP (Fase 1) |
| **Versión** | 1.0 |
| **Estado** | APROBADO |
| **Última Revisión** | 28/07/2026 |

---

### 1. Propósito
Definir la hoja de ruta, la estructura técnica y los entregables concretos para la construcción del Producto Mínimo Viable (MVP) de QuantBet. Este plan traduce los documentos de diseño (`QB-001` a `QB-004`) en un backlog de módulos y tareas, especificando la estructura de directorios, las dependencias tecnológicas y los criterios de finalización. El objetivo es tener una aplicación de consola funcional que demuestre el flujo completo de valor: *dato -> análisis -> decisión*, sobre datos simulados o estáticos.

### 2. Alcance del MVP
**Objetivo del MVP:** Construir un núcleo funcional que pueda, desde la línea de comandos, cargar datos de cuotas, ejecutar el motor de arbitraje y emitir una decisión puntuada, sin depender de conexiones a internet ni de ninguna casa de apuestas real.

**Lo que SÍ incluye el MVP:**
- Estructura completa del proyecto Python.
- Implementación del Modelo de Dominio (`QB-002`) como clases Python.
- Implementación del `Motor de Arbitraje` como primer plugin del motor de estrategias.
- Implementación de la entidad `Bankroll` básica.
- Implementación del `Opportunity Score` básico.
- Un `IDataProvider` simulado que lee eventos y cuotas desde un archivo CSV/JSON local.
- Persistencia en `SQLite` del historial de `Snapshots` y `Decisiones`.
- Un script principal (`main.py`) que ejecute el flujo completo.
- Suite de pruebas unitarias para el motor de arbitraje.

**Lo que NO incluye el MVP:**
- Conectores a casas de apuestas reales (Playwright/Selenium).
- Web scraping o APIs externas.
- Estrategias de Value Betting o Dutching (se implementarán como plugins en la Fase 2).
- Dashboard o interfaz gráfica (Streamlit).
- Sistema de alertas (Telegram/escritorio).

### 3. Estructura del Proyecto (Físico)
Siguiendo los principios de modularidad de `QB-003`, el código se organizará así:
QuantBet/
│
├── QBMM/ # Manual Maestro (documentos)
│ ├── QB-001_Filosofia.md
│ ├── QB-002_Modelo_Dominio.md
│ ├── ...
│ └── QB-005_Plan_MVP.md
│
├── src/ # Código fuente principal
│ ├── domain/ # Implementación de QB-002
│ │ ├── init.py
│ │ ├── entities.py # Clases: Event, Market, Outcome, Snapshot, Bookmaker
│ │ └── bankroll.py # Clase Bankroll
│ │
│ ├── connectors/ # Implementación de IDataProvider (QB-003)
│ │ ├── init.py
│ │ ├── base.py # Clase base abstracta IDataProvider
│ │ └── csv_provider.py # Conector simulado para el MVP
│ │
│ ├── core/ # Motor de Estrategias (QB-004)
│ │ ├── init.py
│ │ ├── arbitrage.py # Lógica de cálculo de arbitraje
│ │ ├── scorer.py # Lógica del Opportunity Score
│ │ └── decision.py # Clase Decision
│ │
│ ├── storage/ # Capa de persistencia
│ │ ├── init.py
│ │ ├── database.py # Conexión SQLite, creación de tablas
│ │ └── repository.py # Funciones para guardar/leer Snapshots y Decisions
│ │
│ └── main.py # Script de entrada del MVP
│
├── tests/ # Pruebas unitarias y de integración
│ ├── init.py
│ ├── test_arbitrage.py
│ ├── test_scorer.py
│ └── test_bankroll.py
│
├── data/ # Datos de prueba para el MVP
│ └── sample_events.csv
│
├── config.yaml # Parámetros configurables (umbrales, pesos del scorer)
├── requirements.txt # Dependencias Python
└── README.md

### 4. Stack Tecnológico del MVP
- **Lenguaje:** Python 3.10+
- **Persistencia:** SQLite (driver: `sqlite3` de la biblioteca estándar)
- **Manipulación de Datos:** `pandas` (para cargar CSVs y normalizar datos)
- **Pruebas:** `pytest`
- **Configuración:** `PyYAML`

### 5. Backlog del MVP (Semanas 1-3)
El desarrollo se dividirá en 4 hitos incrementales:

**Hito 1 (Semana 1): El Dominio y la Persistencia**
- [x] Crear la estructura de directorios.
- [x] Implementar las clases del dominio (`entities.py`, `bankroll.py`) como dataclasses.
- [x] Implementar `database.py` para crear las tablas SQLite basadas en el modelo de dominio.
- [x] Implementar `repository.py` con funciones `save_snapshot()` y `save_decision()`.
- **Prueba:** Un script que crea una entidad `Snapshot` en memoria y la guarda en `quantbet.db`.

**Hito 2 (Semana 2): El Motor y el Puntuador**
- [x] Implementar la lógica de `arbitrage.py`. Debe recibir una lista de `Snapshots` y devolver un diccionario con ROI y distribución si existe arbitraje, o `None` si no.
- [x] Implementar `scorer.py` con la fórmula simplificada de `Opportunity Score` (solo `ROI_Score` y `Time_Score` para el MVP, pesos en `config.yaml`).
- [x] Implementar la clase `Decision` y su creación a partir del resultado del motor y el puntuador.
- **Prueba:** `pytest` debe ejecutar `test_arbitrage.py` con casos de arbitraje claro, no arbitraje y datos inválidos.

**Hito 3 (Final Semana 2): El Conector Simulado**
- [x] Implementar `IDataProvider` como una clase base abstracta en `base.py`.
- [x] Implementar `CSVProvider` en `csv_provider.py` que lea `data/sample_events.csv`.
- [x] El CSV tendrá columnas: `bookmaker, event, market, outcome, odds`.
- [x] El método `get_odds()` del `CSVProvider` debe devolver objetos `Snapshot` correctamente formados.
- **Prueba:** Un script que cargue el CSV, llame al motor de arbitraje y guarde la decisión en la base de datos.

**Hito 4 (Semana 3): Integración y Script Principal**
- [x] Escribir `main.py` que ejecute el flujo completo:
    1. Cargar datos desde el `CSVProvider`.
    2. Para cada mercado, construir la lista de `Snapshots` relevantes.
    3. Ejecutar el motor de arbitraje.
    4. Si se detecta una oportunidad, calcular el `Opportunity Score`.
    5. Crear y guardar la `Decision`.
    6. Imprimir la decisión en consola como un JSON formateado.
- **Prueba de Integración:** Ejecutar `main.py` con diferentes archivos CSV de prueba y verificar la salida.

### 6. Criterios de Finalización del MVP
La Fase 1 se considerará completada cuando:
1.  `main.py` pueda ejecutarse sin errores.
2.  Se detecte correctamente un caso de arbitraje "de libro" desde el CSV.
3.  Se ignore correctamente un caso sin arbitraje.
4.  La decisión resultante se imprima en consola y se persista en `quantbet.db`.
5.  Todas las pruebas unitarias (`pytest`) pasen sin fallos.

### 7. Relaciones
- **Derivado de:** `QB-001`, `QB-002`, `QB-003`, `QB-004`. Este es el plan de acción que materializa esos documentos.
- **Control:** El avance de este backlog se registrará en el `Diario del Proyecto`. Una vez completado, este documento se actualizará a `Versión 2.0` para planificar la Fase 2 (Conectores Reales).