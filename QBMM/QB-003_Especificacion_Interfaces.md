# QuantBet Master Manual (QBMM)

## QB-003 — Especificación de Interfaces y Contratos

| Propiedad | Valor |
| :--- | :--- |
| **Código QB** | QB-003 |
| **Nombre** | Especificación de Interfaces y Contratos |
| **Versión** | 1.0 |
| **Estado** | APROBADO |
| **Última Revisión** | 28/07/2026 |

---

### 1. Propósito
Definir los contratos de comportamiento (interfaces) para los dos subsistemas principales de QuantBet: los **Conectores de Datos** y el **Motor de Análisis**. Este documento actúa como el "traductor universal" y el guardián de la arquitectura. Su objetivo es garantizar que ningún módulo pueda acoplarse directamente a otro, cumpliendo estrictamente el principio de Modularidad Estricta definido en `QB-001`.

### 2. Alcance
**Incluye:**
- La interfaz formal `IDataProvider` que deben implementar todos los conectores.
- El contrato de entrada/salida del `Motor de Análisis` principal.
- La definición de "Capa de Normalización" como punto de desacoplamiento.
- Las reglas de manejo de errores y excepciones entre módulos.

**Excluye:**
- La lógica interna de un conector específico (Playwright vs. API).
- Los algoritmos concretos de cálculo de arbitraje o valor.
- Cómo se almacenan los datos (eso es tarea del Módulo de Persistencia, regido por `QB-002`).

### 3. Desarrollo

#### 3.1. La Capa de Normalización (El Puente)
El punto ciego más peligroso que identificamos fue la mezcla de datos crudos con análisis.
- **Regla:** El `Motor de Análisis` **NUNCA** recibe datos directamente de un `IDataProvider`.
- **Intermediario:** Existe una **Capa de Normalización** que actúa como un middleman. Toma la salida del conector (que puede ser un JSON anidado, un DataFrame de pandas, etc.) y la transforma en un objeto de dominio estándar de QuantBet (definido en `QB-002`). Solo entonces se pasa al motor.

#### 3.2. Interfaz `IDataProvider` (Contrato para Conectores)
Todo conector (ya sea para Bet365, Aposta.la o un archivo CSV local) debe implementar esta interfaz conceptual. En Python, esto se logrará usando una Clase Base Abstracta (ABC). Un conector que no cumpla este contrato es una fuente de deuda técnica y no debe integrarse en el sistema principal.

**Métodos del Contrato:**

1.  **`connect() -> bool`**
    - **Propósito:** Establecer la sesión (login, cookies, o simplemente verificar conectividad).
    - **Salida:** `True` si la conexión es exitosa, `False` en caso contrario.
    - **Regla:** Debe ser lo más ligero posible.

2.  **`disconnect()`**
    - **Propósito:** Cerrar la sesión de forma segura.

3.  **`get_events(competition_ids: list[str] = None) -> list[Event]`**
    - **Propósito:** Obtener una lista de eventos disponibles. Si se provee `competition_ids`, filtra por esas competiciones.
    - **Salida:** Una lista de objetos `Event` **normalizados** (según `QB-002`).
    - **Regla:** Un `Event` devuelto por este método debe tener sus `participants` completos. Sus mercados aún pueden estar vacíos.

4.  **`get_markets(event_id: str) -> list[Market]`**
    - **Propósito:** Obtener todos los mercados disponibles para un evento específico.
    - **Salida:** Una lista de objetos `Market` normalizados.

5.  **`get_odds(market_id: str) -> Snapshot`**
    - **Propósito:** La función más crítica. Obtener el estado actual de las cuotas para un mercado específico y devolverlo como un objeto `Snapshot` listo para ser persistido.
    - **Salida:** Un único objeto `Snapshot`.
    - **Contrato de Inmutabilidad:** Esta función no devuelve las cuotas normalizadas y calculadas. Devuelve el `Snapshot` crudo. La transformación (ej. cuota fraccional a decimal) puede hacerse aquí o en la capa de normalización, pero el `Snapshot` debe contener la representación canónica para QuantBet (cuota decimal).

#### 3.3. Contrato del Motor de Análisis
Este es el "consumidor" de los objetos de dominio. Define la forma en que se solicita un análisis y la estructura de la respuesta, que no debe depender de qué casa de apuestas originó los datos.

**Entrada:**
El motor principal expone un método de análisis que recibe una lista de `Snapshots` y parámetros de contexto.
```python
# Ejemplo conceptual
analyze_opportunities(
    snapshots: list[Snapshot],
    bankroll: Bankroll, # Definido en un futuro QB-004
    active_strategies: list[str] # ["arbitrage", "dutching"]
) -> list[Decision]
Salida: Decision
Una Decision no es una apuesta ejecutada. Es una recomendación estructurada y, sobre todo, auditable.

Atributos Clave:

decision_id: UUID único para esta recomendación.

strategy: Nombre de la estrategia que generó la decisión (ej. "arbitrage_engine_v1").

context_snapshot_ids: Lista de los IDs de los Snapshot que se usaron para el cálculo. Esto es lo que garantiza la auditoría.

opportunity_score: Puntuación de 0 a 100 basada en ROI, liquidez, tiempo restante, etc.

details: Un diccionario con los detalles específicos de la decisión. Si es arbitraje, incluirá roi, distribution (ej. {"outcome_a": 45.2, "outcome_b": 54.8}). Si es value betting, incluirá implied_probability vs. estimated_probability.

3.4. Manejo de Errores y Excepciones (Contrato Transversal)
Para que los módulos sean intercambiables, deben comportarse de forma predecible ante fallos.

Errores en Conectores (IDataProvider):

Si un conector no puede obtener datos (timeout, página caída, cambio de HTML), NUNCA debe lanzar una excepción genérica que detenga todo el sistema.

Contrato: Debe capturar la excepción, loguearla en detalle (con timestamp y conector específico) y devolver una estructura de error estandarizada o una lista vacía, permitiendo que otros conectores sigan funcionando. El sistema principal debe interpretar una lista vacía como "fuente de datos no disponible temporalmente".

Errores en el Motor de Análisis:

Si el motor recibe datos incompletos o inválidos (ej. un Snapshot donde el overround es negativo), no debe fallar.

Contrato: Debe registrar el error y marcar el Snapshot como inválido en el log, excluyéndolo del análisis.

4. Relaciones
Depende de: QB-002 (Modelo de Dominio Conceptual). Las entidades Event, Market, Outcome y Snapshot son los tipos usados en estas interfaces.

Es referenciado por: Todos los conectores futuros (connectors/bet365.py, etc.) y el módulo core/. El cumplimiento de este documento será verificado en las pruebas de integración.

5. Evolución
Las interfaces aquí definidas constituyen el "núcleo duro" y no deberían cambiar. La evolución se dará añadiendo nuevos métodos opcionales a la interfaz o nuevas estrategias al motor. Pero el contrato fundamental de get_odds() -> Snapshot y analyze() -> list[Decision] debe permanecer estable. Cualquier cambio en ellos implicaría una refactorización mayor, lo cual está justificado solo por una nueva capacidad fundamental no prevista.
