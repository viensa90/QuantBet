Actúa como un Arquitecto de Software Principal y Auditor de Código Senior con más de 20 años de experiencia en desarrollo de sistemas de misión crítica, optimización y refactorización profunda. Tu objetivo es realizar una AUDITORÍA FORENSE Y ESTRUCTURAL exhaustiva del proyecto. 
Necesito dejar de apagar incendios en este proyecto. Por lo tanto, requiero que tu análisis sea implacable, técnico, directo y sin concesiones. 

Desglosa tu auditoría estrictamente en las siguientes fases:
1. Análisis Macro: Arquitectura y Estructura General
Las busquedas sobre resultados del mundial no tiene sentido, ya terminó. explica qué está haciendo el bot y por qué lo está haciendo.
*   **Visión Global:** Evalúa el diseño arquitectónico general, patrones utilizados (o la falta de ellos) y la modularidad.
*   **Deuda Técnica Estructural:** Identifica acoplamientos fuertes, dependencias circulares o violaciones de principios SOLID y separación de responsabilidades.
*   **Puntos Ciegos Macro:** ¿Qué no estamos considerando a nivel de escalabilidad, mantenibilidad y seguridad general?
2. Análisis Meso: Módulo por Módulo (Funcionalidades)
Para cada módulo, componente o servicio encontrado:
*   **Propósito vs. Realidad:** ¿Qué se supone que hace este módulo y qué hace realmente en el código?
*   **Coherencia y Cohesión:** Evalúa si la lógica interna de cada módulo tiene sentido dentro del ecosistema del proyecto.
*   **Deficiencias y Fallas:** Critica duramente los resultados, manejo de errores, asunciones frágiles y posibles cuellos de botella.
*   **Lo que falta:** ¿Qué validaciones, casos de borde o flujos de negocio están ausentes?
3. Análisis Micro: Escaneo Línea por Línea y Código Inerte
*   **Código Inerte / Muerto (Dead Code):** Identifica funciones, variables, imports, rutas o bloques lógicos que nunca se ejecutan o que no sirven para nada.
*   **Antipatrones y Vulnerabilidades:** Señala malas prácticas sintácticas o lógicas línea por línea donde sea crítico (fugas de memoria, condiciones de carrera, inyecciones, mal manejo de estados o promesas).
*   **Incoherencias Léxicas y de Tipado:** Nombres engañosos de variables/funciones que contradicen su comportamiento real.
4. Auditoría de Ceguera Operativa ("Lo que no estamos viendo")
*   **Riesgos Ocultos:** ¿Qué problemas latentes estallarán en producción a corto/mediano plazo debido a cómo está escrito este código?
*   **Falta de Resiliencia:** Análisis de cómo el sistema maneja fallos externos, desconexiones, picos de carga o datos corruptos.
5. Plan de Acción Correctivo (Hoja de Ruta)
Para dejar de apagar incendios,implementar inmediatamente las correcciones según lo encontrado en los apartados anteriores.
a continuación el último diario del proyecto que actualizo y entrego para cada sesión como promt:
📋 DIARIO DE PROYECTO - QuantBet (v0.3.4 - EN CONSTRUCCIÓN CONTROLADA)
🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.

Reglas implícitas (no necesito repetirlas):

Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet

"CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo siempre que estés completamente seguro de no romper nada)

Al final de cada sesión, actualiza este diario con el mismo formato

Mantén el contexto de todas las sesiones anteriores

Los principios de arquitectura son inmutables (ver sección Principios)

NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible

SIEMPRE escanea minuciosamente el repositorio antes de proponer cambios

#6 - Verificación Arquitectónica Pre-Ejecución:
Antes de generar cualquier archivo nuevo o reemplazar uno existente, la IA DEBE:

Escaneo completo del repositorio: Leer todos los archivos relevantes del proyecto

Mapeo de dependencias: Identificar dependencias entre archivos

Validación de principios: Confirmar que no se violan los 5 principios

Análisis de impacto: Evaluar cómo afecta a tests existentes

Reporte de coherencia: Incluir informe de verificación

📋 RESUMEN EJECUTIVO
Métrica	Valor
Proyecto	QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión	0.3.4
Repositorio	https://github.com/viensa90/QuantBet
Última sesión	24 - 07/08/2026
Estado	🟡 EN DESARROLLO - Pipeline funcional, mejoras críticas en curso
🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#	Principio	Descripción	Verificación
#1	Conectores solo obtienen datos	Nunca toman decisiones	✅ CSVProvider, OddsAPIProvider solo leen
#2	Motor no conoce la fuente	Recibe snapshots, no sabe de CSV/Web	✅ Todas las estrategias reciben Snapshot
#3	Snapshots inmutables	Solo INSERT en SQLite, nunca UPDATE	✅ Snapshot.to_dict() y guardado en BD
#4	Decisiones auditables	Trazabilidad completa en BD	✅ Cada oportunidad guardada con timestamp
#5	Configuración externalizada	config.yaml, nada hardcodeado	✅ Todas las configuraciones en YAML
📂 ESTRUCTURA DEL PROYECTO (VERSIÓN ACTUAL)
text
QuantBet/
├── .github/                      ✅ OK
├── QBMM/                         ✅ OK
├── src/
│   ├── __init__.py               ✅ v0.3.4
│   ├── config_loader.py          ✅ Singleton con defaults
│   ├── logger.py                 ✅ Logs estructurados
│   ├── logging/                  ✅ OK
│   ├── domain/
│   │   └── entities.py           ✅ (Snapshot con metadata)
│   ├── storage/
│   │   ├── __init__.py           ✅ (Corregido import)
│   │   ├── database.py           ✅ (Índices arreglados, auto-migración)
│   │   ├── repository.py         ✅ (Migración automática, save_opportunities con dict/obj)
│   │   └── migrations.py         ✅ (Conservado para referencia)
│   ├── core/
│   │   ├── __init__.py           ✅
│   │   ├── arbitrage.py          ✅ (Solo mercados 2-opciones, seguro)
│   │   ├── scorer.py             ✅
│   │   ├── bankroll.py           ✅
│   │   ├── value_betting.py      ✅ (falta modelo real)
│   │   ├── dutching.py           ✅
│   │   ├── market_handlers.py    ✅
│   │   ├── probability_model.py  ✅ (solo 4 equipos)
│   │   └── poisson_model.py      ✅
│   ├── connectors/
│   │   ├── base.py               ✅
│   │   ├── csv_provider.py       ✅
│   │   ├── web_provider.py       ✅
│   │   ├── odds_api_provider.py  ✅ (multi-bookmaker)
│   │   └── factory.py            ✅ (soporta 'oddsapi')
│   ├── notifications/            ✅ (email, telegram)
│   └── web/                      ✅ (Flask, Swagger)
├── tests/                        ✅ 83 tests
├── main.py                       ✅ (modo --simple planificado)
├── config.yaml                   ✅ (umbrales ajustables)
├── data/                         ✅
├── tools/
│   └── view_opportunities.py     ⚠️ (necesita robustez)
└── quantbet.db                   (autogenerada)
🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-23: Desarrollo inicial, implementación de todas las estrategias, 83 tests, v0.3.3 listo para producción.

Sesión 24 (06-07/08/2026): Integración con The Odds API real. Correcciones de importación, mapeo de mercados, múltiples bookmakers. Corrección de errores de BD y motor de arbitraje. Sistema detecta oportunidades reales. Pendiente: mejoras críticas listadas abajo.

🔍 INFORME DE AUDITORÍA (v0.3.4)
✅ Lo que funciona correctamente
Pipeline completo (CSV y OddsAPI).

Motor de arbitraje seguro (solo mercados de 2 opciones).

Value Betting y Dutching implementados (pendientes de datos de probabilidad reales).

Base de datos con migración automática (esquema actualizado).

Dashboard web (estructura, endpoints funcionando).

Conectores respetando principios #1, #2, #3.

Configuración externalizada (principio #5).

83 tests unitarios (sin romper).

⚠️ Lo que falta o requiere ajuste
Persistencia completa de oportunidades – actualmente no se guardan event_name, strategy, sport, dificultando la visualización.

Dashboard no muestra datos completos – por la carencia anterior, la tabla y gráficos están vacíos o con “Evento desconocido”.

Salida de consola abrumadora – logs JSON mezclados con resumen, sin opción de modo limpio.

Notificaciones no enganchadas al pipeline – aunque el código existe, no se invoca tras detectar oportunidades.

Falta de cobertura para 1X2 (fútbol) – solo arbitrable con Exchange (lay) o 3 bookmakers.

Modelos de probabilidad sin datos reales – value betting no genera resultados por falta de histórico.

Consumo de API – para operación diaria necesitamos un plan de créditos optimizado.

Scripts auxiliares (view_opportunities.py) con fallos menores de formato.

🚀 PLAN DE SESIONES PARA FINALIZAR EL PROYECTO
Cada sesión ataca un módulo concreto, respetando los principios QBMM y sin romper lo ya construido.

Sesión 25 (actual) – Auditoría y planificación
Archivos: QBMM/diario_proyecto.md
Acción: Actualizar el diario con el estado real y el plan.
Resultado: Tú pegas el diario en el próximo chat y la IA continúa exactamente donde quedamos.

Sesión 26 – Persistencia y visualización completa
Objetivo: Que el dashboard y cualquier consulta muestren toda la información necesaria para operar.
Cambios:
- Modificar Repository.save_opportunities para guardar event_name, strategy, sport y timestamp de forma explícita.
- Actualizar la tabla opportunities (agregar columnas) de forma automática con la migración ya existente.
- Ajustar endpoints del dashboard (/api/v1/opportunities, /api/v1/metrics) para devolver esos campos.
- Corregir tools/view_opportunities.py para que maneje correctamente los formatos de odds (evitando el error de float).
Resultado: Abrir http://localhost:5000 tras cualquier pipeline mostrará los eventos, el mercado, la estrategia, los bookmakers y las ganancias esperadas.

Sesión 27 – CLI amigable (modo “limpio”)
Objetivo: Poder ejecutar python main.py --mode all --source oddsapi --simple y ver solo el resumen de oportunidades sin logs JSON.
Cambios:
- Añadir argumento --simple a main.py.
- En run_pipeline, si simple es True, suprimir logs de nivel INFO en consola (solo WARNING/ERROR).
- Mejorar print_summary para incluir detalles de stakes y bookmakers de forma compacta.
Resultado: Información lista para operar en un vistazo.

Sesión 28 – Notificaciones automáticas (Telegram)
Objetivo: Recibir un mensaje de Telegram cada vez que el pipeline encuentre oportunidades con beneficio > 1.5%.
Cambios:
- Crear un NotificationManager que lea la configuración de Telegram.
- Llamarlo al final de run_pipeline (si hay oportunidades y save=True).
- El mensaje incluirá número de oportunidades, mejor evento y enlace al dashboard local.
Resultado: Alertas en tiempo real sin necesidad de estar mirando la consola.

Sesión 29 – Arbitraje de fútbol (1X2) con Exchange (cuando Betfair KYC esté listo)
Objetivo: Cubrir el mercado más líquido sin riesgo de empate.
Cambios:
- Implementar BetfairProvider (conector) usando la API oficial con certificado SSL.
- Modificar ArbitrageEngine para que, al detectar un mercado 1X2 y tener datos de Betfair Exchange, calcule el arbitraje de tres vías (lay al empate + back a 1 y 2).
- Añadir lógica para detectar cuando hay tres bookmakers tradicionales con las mejores cuotas complementarias.
Resultado: El fútbol se vuelve arbitrable, multiplicando las oportunidades.

Sesión 30 – Afinamiento y puesta en producción
Objetivo: Dejar el sistema listo para uso diario continuado.
Cambios:
- Ajustar umbrales definitivos (min_profit_percent = 1.5).
- Optimizar consumo de API (3 bookmakers, 1 deporte prioritario si es necesario).
- Prueba de ciclo completo con créditos reales durante una semana.
- Documentación final en el diario.
Resultado: QuantBet operativo y rentable.
