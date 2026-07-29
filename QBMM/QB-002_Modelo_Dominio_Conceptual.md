# QuantBet Master Manual (QBMM)

## QB-002 — Modelo de Dominio Conceptual

| Propiedad | Valor |
| :--- | :--- |
| **Código QB** | QB-002 |
| **Nombre** | Modelo de Dominio Conceptual |
| **Versión** | 1.0 |
| **Estado** | APROBADO |
| **Última Revisión** | 28/07/2026 |

---

### 1. Propósito
Definir el vocabulario universal, las entidades de negocio y las relaciones lógicas que representan el funcionamiento de QuantBet. Este modelo es independiente de cualquier tecnología de base de datos (SQLite, PostgreSQL, etc.) y sirve como contrato para todos los módulos del sistema. Su objetivo es responder a la pregunta: "¿Qué conceptos maneja QuantBet y cómo se relacionan entre sí?".

### 2. Alcance
**Incluye:**
- El glosario de entidades de negocio (`Bookmaker`, `Event`, `Market`, `Outcome`, `Snapshot`).
- Las reglas de integridad y relaciones entre estas entidades.
- La definición formal de la entidad `Snapshot` como activo histórico fundamental.
- El modelo de "Versiones de Mercado" para preservar la historia.

**Excluye:**
- Diagramas de tablas de bases de datos (claves foráneas, índices).
- Lógica de negocio o algoritmos de cálculo.
- Implementaciones de conectores.

### 3. Desarrollo

#### 3.1. Glosario de Entidades del Dominio

**3.1.1. `Bookmaker` (Casa de Apuestas o Mercado de Predicción)**
- **Definición:** Representa la fuente de datos. Es la entidad de la cual se obtienen las cuotas.
- **Atributos Clave:** `id`, `name` (ej. "Bet365", "Polymarket"), `type` (`TRADITIONAL_BOOKMAKER`, `PREDICTION_MARKET`, etc.).
- **Regla:** Un `Bookmaker` no es solo un nombre; es un origen de datos. Dos conectores distintos para la misma casa (ej. Web Scraping vs. API no oficial) podrían modelarse como dos `Bookmakers` diferentes si su normalización es distinta.

**3.1.2. `Competition` (Competición)**
- **Definición:** Agrupa eventos bajo una misma liga o torneo.
- **Atributos Clave:** `id`, `name` (ej. "Primera División de Paraguay", "NBA"), `sport` (referencia a la entidad `Sport`).
- **Regla:** La combinación de `name` y `sport` debe ser única.

**3.1.3. `Sport` (Deporte)**
- **Definición:** Define la naturaleza del evento, lo que a su vez determina el modelo de mercados disponibles.
- **Atributos Clave:** `id`, `name` (ej. "Fútbol", "Tenis", "Baloncesto").
- **Impacto en el Dominio:** Esta entidad es crucial. Un evento de "Fútbol" tendrá inherentemente un mercado "1X2" (con empate), mientras que uno de "Baloncesto" no. Esto no es un detalle de UI, es una restricción del dominio.

**3.1.4. `Event` (Evento)**
- **Definición:** Representa un partido o encuentro único entre participantes.
- **Atributos Clave:** `id`, `competition_id`, `start_time_utc` (obligatorio y nunca en hora local), `status` (`PENDING`, `LIVE`, `FINISHED`, `SUSPENDED`, `CANCELLED`), `participants` (lista estructurada, ej. `[{"type": "home", "name": "Cerro Porteño"}, {"type": "away", "name": "Olimpia"}]`).
- **Regla de Integridad:** Un `Event` NUNCA debe ser modificado una vez que su estado pasa a `FINISHED`. El historial de cuotas (`Snapshot`) ligado a él debe permanecer inmutable.

**3.1.5. `Market` (Mercado)**
- **Definición:** Un tipo específico de apuesta dentro de un evento.
- **Atributos Clave:** `id`, `event_id`, `type` (de un vocabulario controlado: `1X2`, `OVER_UNDER_2.5`, `MONEYLINE`, `BOTH_TEAMS_TO_SCORE`, etc.), `parameters` (un diccionario flexible, ej. `{"over_under": 2.5}` o `{"handicap": -1}`). Este enfoque evita tener tablas separadas para cada tipo de mercado.

**3.1.6. `Outcome` (Resultado)**
- **Definición:** Una posible selección dentro de un mercado.
- **Atributos Clave:** `id`, `market_id`, `name` (ej. "1", "X", "Over 2.5", "Sí").
- **Regla:** El `name` no es un string libre. Debe pertenecer a un conjunto finito para cada `type` de mercado. Por ejemplo, para el tipo `1X2`, los valores son `"1"`, `"X"`, `"2"`.

#### 3.2. La Entidad Central: `Snapshot`

**Definición:** Es la "fotografía" inmutable del estado de un `Market` específico, proveniente de un `Bookmaker` concreto, en un instante de tiempo exacto. **Este es el activo histórico más valioso del sistema.**

**Atributos Clave:**
- `id` (UUID o similar para asegurar unicidad global).
- `bookmaker_id` (quién proporcionó el dato).
- `market_id` (a qué mercado pertenece).
- `timestamp_utc` (cuándo se capturó, con precisión de milisegundos).
- `timestamp_source` (opcional, cuándo lo publicó la fuente original).
- `odds` (diccionario `Outcome -> Cuota`). Ej: `{"1": 2.55, "X": 3.20, "2": 2.70}`.
- `status` (estado del mercado en ese instante: `ACTIVE`, `SUSPENDED`, `CLOSED`).
- `hash` (un checksum de los datos para detectar duplicados y asegurar integridad).

**Reglas de Integridad del `Snapshot` (Inmutables):**
1.  **Inmutabilidad Histórica:** Un `Snapshot`, una vez guardado, **nunca se modifica ni se elimina**. Es un hecho histórico.
2.  **Adición Exclusiva:** Solo se añaden nuevos `Snapshots`. Cualquier cambio en una cuota genera un nuevo registro.
3.  **No Normalización:** Las cuotas se guardan en el `Snapshot` tal cual las proporcionó el `Bookmaker`. La normalización a cuotas decimales o probabilidades implícitas es una transformación posterior, que ocurre en la capa de análisis, pero el dato crudo se preserva. Esto es fundamental para la trazabilidad.
4.  **Identidad Única:** Dos `Snapshots` no pueden ser idénticos para el mismo `bookmaker_id`, `market_id` y `timestamp_utc`.

**Justificación (ADR-001 Conceptual):**
- **¿Por qué una entidad `Snapshot` tan estricta?**
  Para cumplir con los principios de Historial Inmutable y Decisión Auditable de QB-001. Si solo guardamos la última cuota, nunca podremos simular qué habría pasado si hubiéramos actuado 3 minutos antes. El `Snapshot` nos permite hacer "replay" de la historia del mercado con total fidelidad, habilitando el backtesting y la auditoría.

#### 3.3. Modelo de Relaciones
Bookmaker 1 ──────────── * Snapshot
Market 1 ──────────── * Snapshot
Event 1 ──────────── * Market
Competition 1 ───────── * Event
Sport 1 ──────────── * Competition

- Un `Snapshot` es la intersección en el tiempo de un `Bookmaker` y un `Market`.
- El resto de relaciones son jerarquías lógicas.

### 4. Relaciones
- **Referencia a:** `QB-001` (especialmente los principios de Modularidad, Historial Inmutable y Decisión Auditable).
- **Es referenciado por:** El futuro documento de Arquitectura de Datos (donde se definirá el esquema SQLite), los Contratos de Interfaces de Conectores (que deberán devolver objetos `Event`, `Market`, `Outcome` y `Snapshot`).

### 5. Evolución
Este modelo puede extenderse para incluir entidades como `Strategy`, `Operation` (apuesta) o `Bankroll`, pero las entidades aquí definidas representan el "núcleo de datos" y se prevé que permanezcan altamente estables. La adición de nuevos tipos de `Market` o `Sport` es una extensión natural sin impacto estructural.
