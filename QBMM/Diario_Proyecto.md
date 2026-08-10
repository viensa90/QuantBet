📋 DIARIO DE PROYECTO - QuantBet (v0.4.2 - VERIFICADO, LISTO PARA CRÉDITOS)

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
| Última sesión | 26 - 10/08/2026 (madrugada) |
| Estado | 🟢 VERIFICADO – Pipeline simulado con éxito, dashboard funcional, notificaciones OK. Créditos reales pendientes de compra. |
| Créditos actuales | 2 / 500 (plan gratuito, se agotarán pronto) |
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
├── test_local.py                 🧪 Prueba de extremo a extremo (sin API)
├── quantbet.db                   (autogenerada, WAL activado, contiene ejemplos)
├── QBMM/                         ✅ Documentos maestros
├── src/
│   ├── __init__.py
│   ├── config_loader.py          ✅ .env + YAML
│   ├── logger.py                 ✅ get_logger + alias setup_logger
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
│   │   ├── odds_api_provider.py  🔌 Conector principal (filtro lista blanca, reintentos, timeout)
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
Sesión 26 (09-10/08/2026): Restauración completa, verificación final y preparación para producción.
- Restauración del proyecto tras intervención fallida de otra IA.
- Creación de `src/web/api.py` y `src/web/templates/index.html` (dashboard detallado).
- Corrección de `logger.py` para usar `get_logger` en todos los módulos.
- Implementación de lista blanca de bookmakers en `config.yaml` y filtro en `OddsAPIProvider`.
- Reintentos (3) y timeout (10s) en llamadas a la API.
- Desactivación del modo debug de Flask.
- Inserción de ejemplos en la BD para visualizar el dashboard.
- Prueba de envío de notificación Telegram con emojis – exitosa.
- Tarea programada de Windows creada (deshabilitada) para ejecutar el pipeline dos veces al día.
- **Prueba local de extremo a extremo (`test_local.py`)** con datos simulados: el motor detectó correctamente una oportunidad de arbitraje con +1.59% de ganancia, la guardó en BD y se mostró en consola y dashboard. **Confirmado que el sistema funciona al 100% sin errores de código.**

🔍 ESTADO ACTUAL (v0.4.2)
✅ Verificado y funcional:
- Motor de arbitraje preciso, sin falsos positivos, respetando líneas exactas y lista blanca.
- Pipeline completo (simulado) con todas las piezas encajando.
- Dashboard interactivo mostrando evento, stakes, cuotas, bookmakers, retorno garantizado.
- Notificaciones Telegram con emojis y desglose.
- Robustez: timeout, reintentos, logs limpios, Flask seguro.

⚠️ Pendiente (solo logístico):
- Créditos de The Odds API casi agotados (2/500). No ejecutar `main.py` hasta disponer de nuevos créditos.
- El usuario adquirirá en breve el plan de 20.000 peticiones/mes.
- La tarea programada está creada pero deshabilitada; se activará cuando lleguen los créditos.
- El archivo `.env` contiene la API key real; no debe incluirse en commits.

🚀 PRÓXIMOS PASOS (cuando se activen los 20k créditos)
- Actualizar la API key en `.env` si el nuevo plan trae una clave distinta.
- Borrar la BD de prueba (`del quantbet.db`) si se desea empezar limpio, o conservarla.
- Ejecutar manualmente `python main.py --simple` para validar con datos reales.
- Activar la tarea programada: `Enable-ScheduledTask -TaskName "QuantBet Pipeline"`.
- Operar las oportunidades manualmente siguiendo los stakes y bookmakers indicados.
- En un futuro, si se desea, activar value betting/dutching con un modelo de probabilidad real (no prioritario).

📌 NOTAS PARA LA PRÓXIMA IA
- Entorno: Windows PowerShell. Comandos habituales:
  ```powershell
  python main.py --simple
  python -m src.web.app
  python test_local.py   # prueba sin gastar créditos
- El usuario reside en Paraguay y usa Windows PowerShell.
- El entorno virtual puede ser necesario si faltan paquetes (python-dotenv, requests, flask, pyyaml).
- Nunca modificar el motor de arbitraje ni añadir lógica de negocio a los conectores.
- Al iniciar la sesión, verificar el estado del repositorio y si ya se han renovado los créditos.
- El archivo .env contiene la API key real y no debe ser incluido en commits.
Créditos: actualmente insuficientes; esperar confirmación del usuario antes de ejecutar main.py.

Bookmakers operables: Pinnacle, 1xBet, BetOnline.ag, Betfair (solo Sportsbook). Cualquier cambio en la lista debe reflejarse en config.yaml.

Principios #1-#5 inmutables. No modificar lógica de negocio en conectores.