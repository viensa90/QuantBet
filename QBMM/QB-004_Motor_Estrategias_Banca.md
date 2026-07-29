# QuantBet Master Manual (QBMM)

## QB-004 — Motor de Estrategias y Gestión de Banca

| Propiedad | Valor |
| :--- | :--- |
| **Código QB** | QB-004 |
| **Nombre** | Motor de Estrategias y Gestión de Banca |
| **Versión** | 1.0 |
| **Estado** | APROBADO |
| **Última Revisión** | 28/07/2026 |

---

### 1. Propósito
Definir el comportamiento del módulo central de QuantBet encargado de transformar datos de mercado (en forma de `Snapshot` normalizados) en decisiones de inversión objetivas y puntuadas. Este documento especifica las estrategias iniciales, el algoritmo de puntuación de oportunidades (`Opportunity Score`), y la integración del módulo de gestión de capital (`Bankroll`) para ponderar las decisiones según el riesgo y los recursos disponibles.

### 2. Alcance
**Incluye:**
- Definición formal de las estrategias de análisis (Arbitraje, Dutching, Value Betting).
- Estructura de la entidad `Decision` y el `Opportunity Score`.
- Especificación de la entidad `Bankroll` y sus restricciones.
- La interacción entre el `Motor de Estrategias` y el `Bankroll` para validar una recomendación.

**Excluye:**
- Estrategias avanzadas de trading o modelos predictivos de IA (reservados para evolución futura).
- Implementación específica de los cálculos matemáticos (es materia de `core/arbitrage.py`, no de este documento de diseño).
- Interacción con la base de datos (el motor solo recibe objetos en memoria).

### 3. Desarrollo

#### 3.1. Entidad `Bankroll` (Gestión de Capital)
Antes de tomar cualquier decisión, el sistema debe conocer el estado del capital. La banca no es un número; es una estructura de estados.

- **Atributos Clave:**
    - `total_capital`: Capital total (realizado + no realizado).
    - `available_capital`: Capital líquido disponible para nuevas operaciones.
    - `committed_capital`: Capital inmovilizado en operaciones abiertas.
    - `currency`: Moneda base (ej. "PYG").
- **Regla de Fraccionamiento:** Se define un parámetro de configuración global `MAX_RISK_PER_OPPORTUNITY` (por defecto, 0.05, representando un 5% del capital disponible). Ninguna decisión puede recomendar una inversión total que supere este límite. El motor consulta al `Bankroll` para obtener el `max_stake` permitido en ese instante.

#### 3.2. Estrategias de Análisis (Plugins del Motor)
Cada estrategia es un módulo independiente que implementa una interfaz común y busca una ineficiencia específica.

**Estrategia 1: `ArbitrageEngine` (Surebets)**
- **Condición:** Existencia de `Snapshots` de dos o más `Bookmakers` diferentes para el mismo `Market` cuyas cuotas permitan una cobertura con ganancia garantizada (overround < 1.0).
- **Salida:** Calcula el ROI garantizado y la distribución óptima del `stake` entre los `Outcomes`.
- **Restricción:** Esta estrategia es extremadamente sensible al tiempo. Una oportunidad detectada con más de 10 segundos de antigüedad debe ser penalizada en su `Opportunity Score`.

**Estrategia 2: `ValueBettingEngine` (Apuestas de Valor)**
- **Condición:** Se necesita una "cuota de referencia" (generalmente de un mercado eficiente como Betfair o Pinnacle) o un modelo propio. Si la cuota de un `Bookmaker` para un `Outcome` es mayor a la cuota implícita de la probabilidad justa de referencia, hay valor.
- **Salida:** Calcula el `Expected Value` (EV) positivo.
- **Nota sobre el MVP:** Para el MVP, esta estrategia depende de tener al menos un conector de una fuente considerada como "referencia". Se puede construir el motor, pero permanecerá inactivo hasta que exista ese dato.

**Estrategia 3: `DutchingEngine` (Coberturas Parciales)**
- **Condición:** Similar al arbitraje, pero no requiere que la cobertura sea total. Busca distribuir el riesgo entre varios `Outcomes` para mejorar el perfil de riesgo/beneficio, incluso si no se garantiza ganancia en todos los escenarios.
- **Salida:** Calcula la distribución del `stake` que maximiza la ganancia en los escenarios seleccionados, aceptando un escenario de pérdida controlada.

#### 3.3. El `Opportunity Score` (Puntuación de Oportunidad)
Esta es la innovación que transforma una simple calculadora en un sistema de priorización. No todas las oportunidades con el mismo ROI son igual de buenas. El motor debe asignar una puntuación de 0 a 100 basada en un algoritmo que combine múltiples factores.

**Fórmula Conceptual:**
`Score = (ROI_Score * W_ROI) + (Liquidity_Score * W_LIQ) + (Time_Score * W_TIME) + (Confidence_Score * W_CONF)`
(Los pesos `W_` son configurables en `config.yaml`).

- **`ROI_Score`:** Normalizado. Un ROI del 1% podría ser 50/100, un ROI del 8% podría ser 95/100. Un ROI negativo descarta la oportunidad automáticamente.
- **`Liquidity_Score`:** Basado en el `max_stake` permitido por el `Bankroll` para esa operación. Si el capital disponible solo permite una apuesta mínima, la puntuación es baja. Si permite una apuesta significativa, es alta.
- **`Time_Score`:** Basado en la frescura del dato y el tiempo restante para el inicio del evento.
    - `Snapshot` con menos de 5 segundos: 100/100.
    - Evento que empieza en 1 minuto: el puntaje decae rápidamente.
    - Evento que empieza en 4 horas: 100/100.
- **`Confidence_Score`:** Basado en la calidad de los datos.
    - `Snapshot` proveniente de una API oficial: confianza alta.
    - `Snapshot` de web scraping: confianza media-alta.
    - `Snapshot` donde se detectó una posible inconsistencia (ej. cuotas que no cierran bien): confianza baja.

#### 3.4. Contrato de la `Decision`
El motor no imprime "Apuesta 100.000 Gs a Cerro". Devuelve un objeto `Decision` estructurado y totalmente trazable.

- **Atributos de la `Decision`:**
    - `decision_id`: UUID.
    - `strategy`: "arbitrage", "value_bet", "dutching".
    - `opportunity_score`: 0-100.
    - `snapshot_ids`: Lista de los IDs de los `Snapshot` que se usaron para calcularla (para auditoría total).
    - `recommended_stake_total`: Capital total recomendado para la operación.
    - `allocations`: Lista detallada de instrucciones. Ej: `[{"bookmaker": "Aposta.la", "market_id": "123", "outcome": "1", "stake": 45000, "odds": 2.85}]`.
    - `expected_roi`: El retorno de inversión calculado.
    - `ttl`: Tiempo de vida estimado de la oportunidad en segundos (si es 0, es inmediata).

### 4. Relaciones
- **Depende de:** `QB-002` (para `Snapshot`), `QB-003` (como implementador de la interfaz del motor).
- **Es referenciado por:** El módulo `core/` en el código, y el futuro módulo de `Alerts`.

### 5. Evolución
Se prevé que este sea el módulo con mayor evolución. Nuevas estrategias (ej. "Middle Hunting", "Correlated Outcomes") se añadirán como nuevos plugins. El algoritmo del `Opportunity Score` se calibrará inicialmente con parámetros heurísticos, pero está diseñado para ser reemplazado en el futuro por un modelo de Machine Learning entrenado con el historial de decisiones y resultados, sin cambiar la estructura del motor.