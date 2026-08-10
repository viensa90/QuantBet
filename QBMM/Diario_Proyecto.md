📋 DIARIO DE PROYECTO - QuantBet (v0.4.2 - PREPARADO, ESPERANDO NUEVOS CRÉDITOS)

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
| Versión | 0.4.2 |
| Repositorio | https://github.com/viensa90/QuantBet |
| Última sesión | 26 - 09/08/2026 |
| Estado | 🟡 PREPARADO – Dashboard completo, notificaciones probadas, tarea programada lista. Próximamente se adquirirán 20k créditos. |
| Créditos actuales | 2 / 500 (plan gratuito) |
| Próximo plan | 20.000 peticiones/mes (compra inminente) |

🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#1 Conectores solo obtienen datos → Nunca toman decisiones
#2 Motor no conoce la fuente → Recibe snapshots, no sabe de CSV/Web
#3 Snapshots inmutables → Solo INSERT en SQLite, nunca UPDATE
#4 Decisiones auditables → Trazabilidad completa en BD
#5 Configuración externalizada → config.yaml, secretos en .env

📂 ESTRUCTURA DEL PROYECTO (v0.4.2)
QuantBet/
├── .env.example                  ✅ Plantilla variables de entorno
├── .gitignore                    ✅ Protege .env, *.db, etc.
├── config.yaml                   ✅ Umbrales, deportes, lista blanca de bookmakers
├── main.py                       ✅ Pipeline, --simple, notificaciones Telegram
├── quantbet.db                   (autogenerada, WAL activado, ejemplo insertado)
├── QBMM/                         ✅ Documentos maestros
├── src/
│   ├── __init__.py
│   ├── config_loader.py          ✅ .env + YAML
│   ├── logger.py                 ✅ Logs estructurados (get_logger + alias setup_logger)
│   ├── domain/
│   │   └── entities.py           ✅ Entidades originales (compatibilidad)
│   ├── storage/
│   │   ├── database.py           ✅ WAL, migración automática
│   │   ├── repository.py         ✅ Guarda event_name, sport, details JSON
│   │   └── migrations.py
│   ├── core/
│   │   ├── arbitrage.py          🔥 Motor genérico (agrupa por name + point, ignora _lay)
│   │   ├── market_handlers.py    ✅ Normalización de mercados
│   │   ├── value_betting.py      (inactivo)
│   │   ├── dutching.py           (inactivo)
│   │   ├── scorer.py             (inactivo)
│   │   ├── bankroll.py           (inactivo)
│   │   └── probability_model.py (obsoleto)
│   ├── connectors/
│   │   ├── base.py
│   │   ├── csv_provider.py
│   │   ├── odds_api_provider.py  🔌 Conector principal (Outcome con point, filtro lista blanca, reintentos, timeout)
│   │   └── factory.py
│   ├── notifications/
│   │   ├── telegram_notifier.py  ✅ Envío con emojis por bookmaker (probado)
│   │   └── email_notifier.py     (opcional)
│   └── web/
│       ├── app.py                ✅ Dashboard Flask (debug desactivado)
│       ├── api.py                ✅ Endpoints REST (opportunities, metrics)
│       └── templates/
│           └── index.html        ✅ Dashboard visual con tarjetas detalladas
├── tests/                        ⚠️ 83 tests (necesitan actualización)
├── tools/
│   └── view_opportunities.py     ✅ Visor de BD robustecido
└── data/

🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-24: desarrollo inicial, v0.3.4.
Sesión 25 (08/08/2026): Auditoría, motor genérico, corrección de falsos positivos.
Sesión 26 (09/08/2026): Restauración completa y mejoras finales.
- Restauración del proyecto tras intervención fallida de otra IA.
- Creación de src/web/api.py y src/web/templates/index.html (dashboard detallado).
- Corrección de logger.py (get_logger) para todos los módulos.
- Lista blanca de bookmakers (Pinnacle, 1xBet, BetOnline.ag, Betfair) en config.yaml.
- Reintentos (3) y timeout (10s) en OddsAPIProvider.
- Desactivación de Flask debug.
- Inserción de oportunidad de ejemplo (Atlético vs Villarreal) para visualizar el dashboard.
- Notificación Telegram de prueba exitosa con emojis de bookmakers.
- Tarea programada de Windows creada (deshabilitada) para ejecutar pipeline 2 veces al día.

🔍 ESTADO ACTUAL (v0.4.2)
✅ Funcionando y probado:
- Motor de arbitraje sin falsos positivos.
- Pipeline con filtro de bookmakers (solo casas operables por el usuario).
- Dashboard interactivo con desglose de stakes, cuotas, bookmakers, inversión/retorno.
- Notificaciones Telegram con emojis.
- Tarea programada lista para activar.
- Código robusto (timeout, reintentos, logs sin API key).

⚠️ Pendiente (crítico):
- Créditos actuales agotados (2/500). No ejecutar pipeline hasta disponer de nuevos créditos.
- El usuario va a adquirir el plan de 20.000 peticiones/mes en los próximos días.
- La tarea programada está deshabilitada; se activará cuando lleguen los créditos.

🚀 PRÓXIMOS PASOS (cuando lleguen los créditos de 20k)
- Actualizar la API key en .env si es necesario (si cambia con el nuevo plan).
- Activar la tarea programada con `Enable-ScheduledTask -TaskName "QuantBet Pipeline"`.
- O ejecutar manualmente `python main.py --simple` para una primera prueba con muchos créditos.
- Verificar que el dashboard refleja las oportunidades detectadas.
- Empezar a operar manualmente las oportunidades.

📌 NOTAS PARA LA PRÓXIMA IA
- El usuario reside en Paraguay y usa Windows PowerShell.
- El entorno virtual puede ser necesario si faltan paquetes (python-dotenv, requests, flask, pyyaml).
- Nunca modificar el motor de arbitraje ni añadir lógica de negocio a los conectores.
- Al iniciar la sesión, verificar el estado del repositorio y si ya se han renovado los créditos.
- El archivo .env contiene la API key real y no debe ser incluido en commits.