# QuantBet Master Manual (QBMM)

## QB-001 — Filosofía de QuantBet

| Propiedad | Valor |
| :--- | :--- |
| **Código QB** | QB-001 |
| **Nombre** | Filosofía de QuantBet |
| **Versión** | 1.0 |
| **Estado** | APROBADO |
| **Última Revisión** | 28/07/2026 |

---

### 1. Propósito
Definir la identidad, misión, principios y visión inmutables de QuantBet. Este capítulo establece el "porqué" detrás de cada decisión técnica y sirve como criterio de validación para todas las fases posteriores del proyecto.

### 2. Alcance
**Incluye:**
- La definición de la misión y la visión del proyecto.
- Los principios fundamentales de diseño y operación.
- La definición del problema que resuelve.
- Lo que QuantBet es y lo que explícitamente no es.

**Excluye:**
- Detalles de implementación técnica, módulos o código.
- Estrategias de apuestas específicas.
- Diseño de bases de datos o APIs.

### 3. Desarrollo

#### 3.1. Definición del Problema
Las decisiones de inversión en mercados de predicción (deportivos u otros) sin un análisis cuantitativo profundo se basan en la intuición, están sujetas a sesgos cognitivos y carecen de trazabilidad. No existe una forma sistemática de aprender de los errores y aciertos pasados para mejorar la calidad de las decisiones futuras.

#### 3.2. Misión
**QuantBet es una plataforma de inteligencia cuantitativa que transforma datos brutos de mercados en decisiones objetivas, justificadas y auditables, mediante análisis matemático, gestión del conocimiento y evaluación del riesgo.**

El propósito fundamental de QuantBet no es "encontrar apuestas", sino **asistir en la toma de decisiones de inversión de máxima calidad posible bajo un contexto dado.**

#### 3.3. Visión
Ser un sistema que:
1.  **Acumula Conocimiento:** Su activo principal es una base de datos histórica y un motor de conocimiento que se enriquecen con cada nueva información y resultado.
2.  **Evoluciona:** No es estático. Está diseñado para incorporar nuevas fuentes de datos, estrategias y modelos de análisis de forma modular.
3.  **Es Verificable:** Cualquier decisión tomada o recomendada en el pasado puede ser reconstruida, auditada y explicada con precisión.
4.  **Reduce el Error Humano:** Minimiza la influencia de sesgos emocionales y cognitivos en el proceso de decisión, basándose en reglas predefinidas y verificables.

#### 3.4. Identidad: Lo que QuantBet ES
- **Un Sistema de Toma de Decisiones:** Su núcleo es transformar `datos -> información -> conocimiento -> decisión -> resultado -> aprendizaje -> mejor conocimiento`.
- **Una Herramienta de Ingeniería:** Construido con la disciplina de un software profesional, priorizando la estabilidad, la mantenibilidad y la escalabilidad sobre la velocidad de desarrollo inicial.
- **Un Marco Objetivo:** Las recomendaciones se presentan como el resultado de una estrategia y reglas específicas, no como una corazonada. Por ejemplo: "Según la Estrategia A y la Regla 17, con los datos del Snapshot ID 12345, esta oportunidad obtiene un Score de 94/100".
- **Conectable y Agnóstico:** Su núcleo matemático y de decisión desconoce la fuente de los datos. Las casas de apuestas o mercados de predicción son solo fuentes de datos, normalizadas por conectores.

#### 3.5. Identidad: Lo que QuantBet NO ES
- **Un Ejecutor Automático de Apuestas:** QuantBet puede recomendar, pero la ejecución final es una decisión del usuario, separando la estrategia del acto de apostar.
- **Un Predictor de Resultados Deportivos:** El sistema analiza ineficiencias de mercado, probabilidades implícitas y valor, pero su objetivo no es adivinar el futuro, sino encontrar discrepancias estadísticamente ventajosas.
- **Un Proyecto de "Caja Negra":** Ninguna decisión será producto de un proceso inexplicable. La transparencia y la trazabilidad son requisitos de diseño, no características opcionales.
- **Una Solución Mágica o Libre de Riesgo:** El sistema está diseñado para gestionar el riesgo, no para eliminarlo. Minimiza errores y detecta inconsistencias, pero no puede garantizar la ausencia total de eventos adversos o pérdidas. La gestión del riesgo es una funcionalidad central, no una promesa de infalibilidad.
- **Un Producto Comercial Multiusuario (en su MVP):** Es una plataforma personal, local y privada. Las decisiones de arquitectura se tomarán pensando en un único usuario experto.

#### 3.6. Principios Fundamentales (Inmutables)
Estos principios actúan como reglas de validación para toda decisión futura (ADR y código). Ninguna decisión técnica puede contradecirlos.
1.  **Primero el Conocimiento:** La base de datos histórica (snapshots, eventos, resultados) es el activo más valioso del proyecto. Su integridad y estructura son prioritarias.
2.  **Modularidad Estricta:** Ningún módulo conoce los detalles de implementación de otro. La comunicación se realiza a través de contratos (interfaces) bien definidos.
3.  **Historial Inmutable:** Los datos (especialmente los snapshots de cuotas) nunca se sobrescriben ni se eliminan. Solo se agregan. Esto es fundamental para la reproducibilidad.
4.  **Separación de Responsabilidades:**
    - Los **Conectores** solo obtienen datos, nunca toman decisiones.
    - El **Motor Matemático** solo calcula, nunca obtiene datos ni los presenta.
    - El **Dashboard** solo muestra, nunca calcula ni almacena directamente.
5.  **Decisión Auditable:** Toda decisión (recomendación, alerta) debe ser reproducible. Debe ser posible determinar exactamente qué datos (ID de snapshot), qué regla y qué parámetro produjeron una decisión específica.
6.  **Configuración Explícita:** Ningún parámetro crítico (umbral de ROI, tiempo máximo de latencia, fracción de capital a arriesgar) debe estar "escondido" en el código. Todo debe ser externo y configurable.
7.  **Escalabilidad por Diseño:** El sistema debe funcionar igual de bien con 10 eventos y con 10,000, y con una base de datos de 1 GB o 10 GB, sin cambios en el núcleo de la arquitectura.

### 4. Relaciones
- **Referenciado por:** Todos los demás documentos del proyecto (QB-002, QB-010, ADRs, etc.).
- **Depende de:** Ninguno. Es el documento raíz.
- **ADR-000 (derivado):** La finalidad de QuantBet es transformar datos en decisiones objetivas, reproducibles y auditables.

### 5. Evolución
Este documento está diseñado para ser estable. Cualquier modificación requerirá una justificación mayor y un incremento de versión. Se prevé que se mantenga intacto durante todo el ciclo de vida del MVP.