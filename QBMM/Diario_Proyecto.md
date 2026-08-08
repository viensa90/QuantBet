📋 DIARIO DE PROYECTO - QuantBet (v0.4.0 - FUNCIONAL, MOTOR GENÉRICO 2/3 OPCIONES)
🚀 INSTRUCCIONES PARA IA (Nuevo Chat)
Al iniciar un nuevo chat, copia TODO este archivo como primer mensaje.
Reglas implícitas: tienes autorización total para leer el repositorio completo en GitHub: https://github.com/viensa90/QuantBet
"CREAR" = archivo nuevo | "REEMPLAZAR" = sobrescribir archivo existente (pásame contenido completo siempre que estés completamente seguro de no romper nada).
Al final de cada sesión, actualiza este diario con el mismo formato. Mantén el contexto de todas las sesiones anteriores. Los principios de arquitectura son inmutables.
NUNCA digas "no puedo acceder" - el repositorio es público y siempre accesible.
SIEMPRE escanea minuciosamente el repositorio antes de proponer cambios.

Principios inmutables (#1-#5) – se mantienen.

📋 RESUMEN EJECUTIVO

Métrica	Valor
Proyecto	QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión	0.4.0
Repositorio	https://github.com/viensa90/QuantBet
Última sesión	25 - 08/08/2026
Estado	🟢 FUNCIONAL - Motor genérico, persistencia completa, alertas Telegram
🎯 PRINCIPIOS DE ARQUITECTURA (INMUTABLES) (sin cambios)

📂 ESTRUCTURA DEL PROYECTO
Se han eliminado ~1000 líneas de código muerto: web_provider, probability_model falso, scorer, bankroll no integrados. El pipeline solo usa OddsAPI y el motor genérico.

🔄 HISTORIAL DE SESIONES (RESUMEN)
Sesiones 1-24: desarrollo inicial, v0.3.4 con arbitraje solo 2 opciones.
Sesión 25 (08/08/2026): Auditoría forense y reestructuración completa.

P0-P1 ejecutados: persistencia completa en BD (event_name, sport, market, details JSON), SQLite WAL, .env para secretos, eliminación de código muerto.

Motor de arbitraje genérico: soporta 2 y 3 opciones (fútbol 1X2, over/under, etc.) usando producto cartesiano de bookmakers. Calcula stakes automáticamente.

Integración con Telegram (mensajes con la mejor oportunidad).

CLI modo --simple con salida limpia de stakes y bookmakers.

🔍 ESTADO ACTUAL TRAS SESIÓN 25

✅ Lo que funciona correctamente

Pipeline completo usando OddsAPI con todos los bookmakers disponibles (Pinnacle, 1xBet, etc.).

Detección de arbitraje en mercados de 2 y 3 opciones (incluido over/under, ganador, etc.).

Guardado completo de oportunidades en SQLite con esquema robusto.

Dashboard web (Flask) sin bloqueos gracias a WAL.

CLI limpia con --simple.

Notificaciones Telegram enganchadas.

Secretos centralizados en .env (fuera del repo).

⚠️ Lo que falta o está planificado

Value Betting / Dutching: desactivados hasta tener modelo de probabilidad real.

Conexión con Betfair Exchange para arbitraje con lay (fútbol sin tres bookmakers).

Optimización del consumo de API (límites y frecuencia).

Tests actualizados para el nuevo motor.

🚀 PRÓXIMOS PASOS

Probar el sistema con datos reales y ajustar umbrales.

(Sesión 26) Afinamiento de la experiencia de usuario: dashboard mejorado, filtros por deporte.

(Sesión 27) Integración de Betfair Exchange cuando esté disponible.

FIN DEL DIARIO