📋 DIARIO DE PROYECTO - QuantBet (COMPLETO v0.3.3 - ESTADO: EN REPARACIÓN)
🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.

Reglas implícitas (no necesito repetirlas):

Tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet

"CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo pero siempre escanea y analiza linea por linea como pre-ejecución, no escribas o modifiques una sola linea de código sin estar completamente seguro)

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
Versión	0.3.3
Repositorio	https://github.com/viensa90/QuantBet
Última sesión	22 - 01/08/2026
Estado	⚠️ EN REPARACIÓN - Errores de importación en storage
🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES)
#	Principio	Descripción
#1	Conectores solo obtienen datos	Nunca toman decisiones
#2	Motor no conoce la fuente	Recibe snapshots, no sabe de CSV/Web
#3	Snapshots inmutables	Solo INSERT en SQLite, nunca UPDATE
#4	Decisiones auditables	Trazabilidad completa en BD
#5	Configuración externalizada	config.yaml, nada hardcodeado
📂 ESTRUCTURA DEL PROYECTO (ESTADO ACTUAL)
QuantBet/
├── .github/                      ✅ OK
├── QBMM/                         ✅ OK
├── src/
│   ├── __init__.py               ✅ v0.3.3
│   ├── config_loader.py          ✅ CORREGIDO (Singleton)
│   ├── logger.py                 ✅ CORREGIDO
│   ├── logging/                  ✅ CREADO
│   │   ├── __init__.py           ✅ CREADO
│   │   └── handlers.py           ✅ CREADO
│   ├── domain/entities.py        ✅ OK
│   ├── storage/                  ⚠️ CONFLICTOS
│   │   ├── __init__.py           ⚠️ Importa get_db que no existe
│   │   ├── database.py           ⚠️ NO tiene función get_db()
│   │   ├── repository.py         ⚠️ Importa get_db() que no existe
│   │   └── migrations.py         ✅ OK
│   ├── core/                     ✅ OK
│   ├── connectors/               ✅ OK
│   ├── notifications/            ✅ OK
│   └── web/                      ✅ OK
├── tests/                        ⚠️ 83 tests (algunos fallan por imports)
├── main.py                       ✅ REEMPLAZADO (v0.3.3, ~420 líneas)
├── config.yaml                   ✅ OK
├── requirements.txt              ✅ OK (sin chart.js)
└── quantbet.db                   (autogenerada)
🔄 HISTORIAL DE SESIONES
Sesión 10 - 30/07/2026 - Value Betting y Dutching
Entregables: ValueBetDetector, DutchingCalculator y tests.

Sesión 11 - 31/07/2026 - Conector Web con Playwright
Entregables: WebProvider, Factory, configuración web.

Sesión 12 - 31/07/2026 - Dashboard Web
Entregables: Módulo web completo (Flask + APIs).

Sesión 13 - 31/07/2026 - Soporte Multi-Mercado Avanzado
Entregables: Handlers para 1X2, Over/Under, Asian Handicap, Double Chance.

Sesión 14 - 31/07/2026 - Modelo de Probabilidades Reales
Entregables: HistoricalModel, EloModel, PoissonModel.

Sesión 15 - 31/07/2026 - Optimización de Queries SQLite
Entregables: Migraciones, índices, market_summary, PRAGMA optimizados.

Sesión 16 - 31/07/2026 - Tests de Estrés (1000+ eventos)
Entregables: test_stress.py con 6 pruebas de rendimiento.

Sesión 17 - 31/07/2026 - CI/CD con GitHub Actions
Entregables: 3 workflows, dependabot, pre-commit hooks.

Sesión 18 - 31/07/2026 - Sistema de Notificaciones
Entregables: EmailNotifier, TelegramNotifier, NotificationManager.

Sesión 19 - 31/07/2026 - Soporte para Tenis
Entregables: 3 handlers (Winner, Set Handicap, Total Games) y tests.

Sesión 20 - 01/08/2026 - Soporte para Baloncesto
Entregables: 4 handlers (Moneyline, Spread, Total Points, Quarter Winner) y tests.

Sesión 21 - 01/08/2026 - Documentación API Swagger/OpenAPI
Entregables:

src/web/swagger_config.py (CREAR)

src/web/app.py (REEMPLAZAR - v0.3.2)

tests/test_swagger.py (CREAR - 5 tests)

config.yaml (ACTUALIZAR)

requirements.txt (ACTUALIZAR)

Sesión 22 - 01/08/2026 - UI/UX + Logs Avanzados + REPARACIONES
Entregables (UI/UX + Logs):

src/logging/handlers.py (CREAR)

tests/test_logger.py (CREAR - 6 tests)

src/logger.py (REEMPLAZAR - v0.3.3)

src/web/templates/index.html (REEMPLAZAR)

src/web/static/style.css (REEMPLAZAR)

src/web/static/app.js (REEMPLAZAR)

config.yaml (REEMPLAZAR - sección logs)

Entregables (Reparaciones):

src/config_loader.py (REEMPLAZAR - corregido)

main.py (REEMPLAZAR - versión completa ~420 líneas)

src/storage/__init__.py (REEMPLAZAR - corregido)

src/storage/database.py (REEMPLAZAR - con get_db())

src/storage/repository.py (REEMPLAZAR - corregido)

⚠️ ERRORES ACTUALES IDENTIFICADOS
Error 1: Importación de get_db
ImportError: cannot import name 'get_db' from 'src.storage.database'
Causa: El archivo repository.py intenta importar get_db() pero database.py no la define.

Solución propuesta: Añadir función get_db() al final de database.py:
def get_db() -> sqlite3.Connection:
    """Obtener conexión a la base de datos (función de conveniencia)"""
    return Database().get_connection()
Error 2: Importación de DatabaseManager
ImportError: cannot import name 'DatabaseManager' from 'src.storage.database'
ImportError: cannot import name 'DatabaseManager' from 'src.storage.database'
🔧 PRÓXIMOS PASOS (PRIORIDAD ALTA - PRÓXIMA SESIÓN)
Objetivo: Hacer que el proyecto sea FUNCIONAL y ejecutable.

Tareas pendientes:
Corregir src/storage/database.py:

Añadir función get_db()

Añadir alias DatabaseManager = Database

Corregir src/storage/repository.py:

Asegurar que usa get_db() correctamente

Corregir src/storage/__init__.py:

Exportar get_db y DatabaseManager

Verificar todos los imports:

main.py → debe importar Database correctamente

src/web/app.py → debe importar Repository correctamente

src/logger.py → debe importar handlers correctamente

Ejecutar pruebas de verificación:
python -c "from src.storage.database import Database, DatabaseManager, get_db; print('✅ OK')"
python -c "from src.storage import Database, Repository; print('✅ OK')"
python -c "from src.web.app import create_app; print('✅ OK')"
python main.py --help
python main.py --mode all --source csv --limit 5
📊 MÉTRICAS ACTUALES
Métrica	Valor
Versión	0.3.3
Tests totales	83
Archivos totales	61
Líneas de código	~5,200
Estado	⚠️ No funcional (errores de importación)
📝 INSTRUCCIONES PARA PRÓXIMA SESIÓN
Para la IA que inicie la siguiente sesión:

1. Escanea TODO el repositorio minuciosamente antes de proponer cambios.

2. Prioridad ÚNICA: Corregir los errores de importación en src/storage/.

3. Archivos a REEMPLAZAR:

src/storage/database.py (añadir get_db y DatabaseManager)

src/storage/repository.py (asegurar compatibilidad)

src/storage/__init__.py (exportar correctamente)

4. Comandos de verificación OBLIGATORIOS después de cada cambio:
python -c "from src.storage.database import Database, DatabaseManager, get_db; print('✅ Database OK')"
python -c "from src.storage import Database, Repository; print('✅ Storage OK')"
python -c "from src.web.app import create_app; print('✅ Web OK')"
python main.py --help
5. NO proponer nuevas funcionalidades hasta que el proyecto sea FUNCIONAL.

6. Actualizar este diario al finalizar la sesión con el estado final.
🔗 ENLACES ÚTILES
Repositorio: https://github.com/viensa90/QuantBet

Dashboard: python main.py --serve (cuando funcione)

Tests: python -m pytest tests/ -v (cuando funcionen)

Fin del Diario de Proyecto - QuantBet v0.3.3 (EN REPARACIÓN) 🔧