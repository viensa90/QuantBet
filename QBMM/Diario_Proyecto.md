📋 DIARIO DE PROYECTO - QuantBet (v0.4.1 - ARBITRAJE REAL, FALSOS POSITIVOS ELIMINADOS)

🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.
Reglas implícitas (no necesito repetirlas):
- Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet
- "CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo siempre que estés completamente seguro de no romper nada)
- Al final de cada sesión, actualiza este diario con el mismo formato
- Mantén el contexto de todas las sesiones anteriores
- Los principios de arquitectura son inmutables (ver sección Principios)
- NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible
- SIEMPRE escanea minuciosamente el repositorio antes de proponer cambios

📊 RESUMEN EJECUTIVO
| Métrica | Valor |
|--------|--------|
| Proyecto | QuantBet - Sistema de Arbitraje Deportivo Automatizado |
| Versión | 0.4.1 |
| Repositorio | https://github.com/viensa90/QuantBet |
| Última sesión | 25 - 08/08/2026 (incluye segunda parte) |
| Estado | 🟡 FUNCIONAL con correcciones aplicadas – 1 oportunidad real detectada, pero no operada por bookmaker no disponible. Falta filtro de bookmakers. |
| Créditos restantes | 4 / 500 (plan gratuito The Odds API) |
| Deportes actuales | La Liga, Premier League |
| Mercados actuales | h2h, totals (los spreads se pidieron pero no se usan) |

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.4.1)
(La misma estructura base de v0.4.0 con cambios puntuales en dos archivos)
QuantBet/
├── .env.example ✅ Plantilla variables de entorno
├── .gitignore ✅ Protege .env, *.db, etc.
├── config.yaml ✅ Umbrales, deportes, mercados
├── main.py ✅ Pipeline, --simple, notificaciones (Telegram pendiente)
├── quantbet.db (autogenerada, WAL activado)
├── QBMM/ ✅ Documentos maestros
├── src/
│ ├── init.py
│ ├── config_loader.py ✅ Carga .env + YAML
│ ├── logger.py ✅ Logs estructurados
│ ├── domain/
│ │ └── entities.py ✅ Entidades originales (compatibilidad)
│ ├── storage/
│ │ ├── database.py ✅ WAL, migración automática
│ │ ├── repository.py ✅ Guarda event_name, sport, details JSON
│ │ └── migrations.py
│ ├── core/
│ │ ├── arbitrage.py 🔥 Motor genérico (agrupa por name + point, ignora mercados _lay)
│ │ ├── market_handlers.py ✅ Normalización de mercados
│ │ ├── value_betting.py (inactivo, requiere modelo de probabilidad)
│ │ ├── dutching.py (inactivo, requiere modelo de probabilidad)
│ │ ├── scorer.py (inactivo)
│ │ ├── bankroll.py (inactivo)
│ │ └── probability_model.py (obsoleto)
│ ├── connectors/
│ │ ├── base.py
│ │ ├── csv_provider.py
│ │ ├── odds_api_provider.py 🔌 Conector principal (Outcome con point, ignora _lay, falta filtro de bookmakers)
│ │ └── factory.py
│ ├── notifications/
│ │ ├── telegram_notifier.py ✅ Envío automático (falta enganchar token)
│ │ └── email_notifier.py (opcional)
│ └── web/
│ ├── app.py ✅ Dashboard Flask (debug activo)
│ └── api.py ✅ Endpoints REST
├── tests/ ⚠️ 83 tests (necesitan actualización)
├── tools/
│ └── view_opportunities.py ✅ Visor de BD robustecido
└── data/

🔄 HISTORIAL DE SESIONES (RESUMEN)
- Sesiones 1-24: desarrollo inicial, v0.3.4 con arbitraje solo 2 opciones.
- Sesión 25 (08/08/2026 - Parte 1): Auditoría forense y reestructuración completa.
  - Persistencia completa, SQLite WAL, .env, eliminación de código muerto.
  - Motor de arbitraje genérico (2 y 3 opciones) usando producto cartesiano de bookmakers.
  - Corrección masiva de imports y adaptación a entidades reales.
  - Primera ejecución exitosa: 41 oportunidades (luego se detectó que muchas eran falsas).
- Sesión 25 (08/08/2026 - Parte 2): Corrección crítica de falsos positivos.
  - **Problema detectado por el usuario:** over/under mezclaba líneas diferentes (2.5 vs 2.0) y mercados `h2h_lay` eran tratados como back, generando arbitrajes irreales.
  - **Solución implementada:** 
    - `Outcome` ahora incluye campo `point` (línea exacta).
    - `OddsAPIProvider` ignora cualquier mercado que contenga `_lay`.
    - `ArbitrageEngine` agrupa por `(name, point)` en lugar de solo `name`, garantizando que solo se emparejen cuotas con idéntica línea.
  - Resultado: las 41 oportunidades se redujeron a **1 oportunidad real y ejecutable** (Atlético Madrid vs Villarreal 1X2, 2.16% profit).
  - Sin embargo, esa oportunidad utilizaba Nordic Bet, no disponible en Paraguay. Por tanto, no se pudo operar.

🔍 ESTADO ACTUAL (v0.4.1)
✅ Funciona correctamente:
- Motor de arbitraje genérico preciso (sin falsos positivos por líneas o lay).
- Salida limpia con --simple.
- Persistencia completa en BD (details JSON, event_name, sport, etc.)
- WAL activado en SQLite -> sin bloqueos entre dashboard y pipeline.

⚠️ Problemas críticos detectados (a resolver en sesión 26):
1. **Filtro de bookmakers:** El sistema usa todas las casas que devuelve la API, pero el usuario solo puede operar en: **Pinnacle, 1xBet, BetOnline.ag, Betfair** (Sportsbook). Cualquier oportunidad que involucre otras casas (Nordic Bet, Coolbet, etc.) es inútil.
   - Solución prevista: Añadir lista blanca `allowed_bookmakers` en config.yaml y filtrar en `OddsAPIProvider`.
2. **Resiliencia del conector HTTP:** `requests.get` no tiene timeout ni reintentos. Si la API falla, el pipeline se detiene.
   - Solución prevista: timeout=10s, reintentos con backoff (máx 3).
3. **Seguridad en logs y Flask:** 
   - La API key y configuración completa se imprimen en los logs (JSON en consola). Peligroso.
   - Flask arranca con debug=True, exponiendo trazas.
   - Solución prevista: Filtrar campos sensibles en logger; desactivar debug en producción (o condicionar a variable de entorno).
4. **Créditos de API casi agotados (4/500):** Cualquier ejecución consume 2 peticiones. Debemos planificar con mucha moderación. Tras la renovación, se podrá ejecutar 1-2 veces al día.

📊 SITUACIÓN DE BOOKMAKERS Y ACCESO REAL DEL USUARIO
| Bookmaker        | ¿Tiene cuenta? | ¿Aparece en Odds API? | ¿En plan gratuito? | Notas |
|------------------|----------------|------------------------|-------------------|-------|
| Pinnacle         | ✅ Sí          | ✅ Sí                  | ✅ Sí             | Principal fuente de cuotas |
| 1xBet            | ✅ Sí          | ✅ Sí                  | ✅ Sí             | Buena cobertura |
| BetOnline.ag     | ✅ Sí          | ✅ Sí                  | ✅ Sí             | Aparece como "BetOnline.ag" |
| Betfair          | ✅ Sí (Sportsbook) | ✅ Sí (Sportsbook) | Limitado         | Solo cuotas back; las cuotas de Exchange no están en la API |
| Marathonbet      | Por probar     | Posiblemente           | Rara vez          | Podría aparecer, pero no confirmado |
| Bet365, aposta.la, 360sports.pro | ✅ Sí | ❌ No | - | No disponibles en The Odds API |

**Conclusión:** Debemos limitar el motor a **Pinnacle, 1xBet, BetOnline.ag** (y Betfair si aparece). Esto garantiza que toda oportunidad mostrada sea operable por el usuario.

🔄 PLAN DE SESIONES INMEDIATAS (AJUSTADO A PRIORIDADES)

**Sesión 26 (siguiente) – [PRIORIDAD MÁXIMA] Filtro de bookmakers + robustez + seguridad**
- Añadir `allowed_bookmakers` en config.yaml (lista blanca con los 3-4 bookmakers operables).
- Modificar `OddsAPIProvider._parse_game` para filtrar outcomes solo de esos bookmakers.
- Añadir `timeout=10` y reintentos (3, con backoff) en `requests.get`.
- Desactivar `debug=True` en Flask o condicionarlo a variable de entorno `FLASK_DEBUG`.
- Filtrar campos sensibles (apiKey) de los logs para que no aparezcan en consola ni archivos.
- **Antes de ejecutar, preguntar al usuario si desea consumir 2 créditos** (quedarán 2). Si no, esperar a la renovación del plan.
- Ejecutar `python main.py --simple` para verificar que las nuevas oportunidades solo usan bookmakers de la lista blanca.
- **Objetivo:** El sistema queda listo para operar en cuanto se renueven los créditos.

**Sesión 27 – Automatización ligera y guía de operación**
- Configurar una tarea programada (Windows Task Scheduler) para ejecutar el pipeline 1-2 veces al día en horas clave.
- Ajustar deportes en config.yaml a solo los más rentables (La Liga, Premier League) y mercados `h2h,totals`.
- Documentar el flujo operativo diario: ejecutar, interpretar salida, abrir apuestas manualmente.

**Sesión 28 (futuro, no prioritario) – Modelo de probabilidad para Value Betting / Dutching**
- Requiere datos históricos o un modelo externo. Por ahora no se activa.
- Dutching ≠ Arbitraje: Dutching cubre varios resultados pero no todos, requiere estimación de probabilidades. No se activará hasta tener modelo fiable.

🔑 INSTRUCCIONES Y CONTEXTO PARA LA IA
- Entorno: Windows PowerShell. Comandos habituales:
  ```powershell
  del quantbet.db   # si se necesita reiniciar BD
  python main.py --simple
  python -m src.web.app   # dashboard en localhost:5000
  Créditos de API: 4 restantes. No ejecutar el pipeline sin confirmación explícita del usuario, especialmente en pruebas que consuman peticiones.

Principios inmutables: no añadir lógica de negocio en conectores, mantener snapshots inmutables, config externalizada.

El usuario reside en Paraguay y solo puede operar en las casas listadas. No añadir otras fuentes ni APIs externas.

La lista blanca de bookmakers es la clave para que el sistema sea útil. Implementarla sin falta.

📁 ARCHIVOS MODIFICADOS EN SESIÓN 25 (PARTE 2) – para referencia de cambios recientes:

src/connectors/odds_api_provider.py: Outcome incluye point, se ignoran mercados con _lay, se agrupa por (market_key, point). Pendiente: filtro de bookmakers.

src/core/arbitrage.py: agrupa por (name, point). Ignora outcomes sin point si otros lo tienen.

main.py: sin cambios.

config.yaml: incluye min_profit_percent: 1.5, deportes y mercados actuales.

📌 NOTA FINAL
El sistema de arbitraje ya es fiable en su lógica. Los siguientes pasos son puramente operativos: asegurar que solo muestra oportunidades accionables y que es robusto ante fallos. Una vez completada la sesión 26, el usuario podrá operar con confianza cuando los créditos se renueven.
