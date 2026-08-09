# 🏦 Operativa Diaria de QuantBet v0.5.0

## 1. Cuándo ejecutar el pipeline

Las cuotas de fútbol cambian con frecuencia. Se recomienda ejecutar el pipeline **dos veces al día**:
- **Mañana (8:00 AM hora de Paraguay)**: revisar oportunidades tempranas.
- **Tarde (6:00 PM)**: antes de los partidos de la noche.

El sistema consulta La Liga y la Premier League.

## 2. Cómo lanzar el análisis

Tienes dos opciones:

### Opción A – Manual (rápida, ves el resultado en pantalla)
1. Abre **PowerShell** o **Símbolo del sistema**.
2. Navega hasta la carpeta del proyecto:
   ```powershell
   cd C:\Users\TuUsuario\QuantBet   # o donde tengas el proyecto
3. Activa el entorno virtual si lo usas:

powershell
venv\Scripts\activate
4. Ejecuta:
powershell
python main.py --simple
El parámetro --simple muestra la salida limpia con la distribución de $100.

### Opción B – Usando el script run_pipeline.bat
Doble clic sobre run_pipeline.bat (o desde terminal con run_pipeline.bat).
La salida se guarda automáticamente en la carpeta logs\ y también se muestra en la consola.
Ideal para programar una tarea automática (ver sección 6).

### Opción C – Dashboard web (visual)
Si quieres ver las oportunidades guardadas en la base de datos con una interfaz:
powershell
python -m src.web.app
Luego abre http://localhost:5000 en el navegador. (Debug solo se activa si has definido FLASK_DEBUG=1 en .env).

3. Interpretar la salida
Cada oportunidad se muestra así (ejemplo):

text
⚽ Athletic Club vs Getafe
   Mercado h2h | Profit 2.16%
   Athletic Club        @2.40 (pinnacle    ) -> $41.67
   Draw                 @3.50 (onexbet     ) -> $28.57
   Getafe               @3.80 (betonlineag ) -> $26.32
   Inversión total: $100.00 | Retorno: $102.16 | Ganancia: $2.16
Profit es la ganancia segura si apuestas exactamente los montos indicados en cada casa.

Los nombres de las casas aparecen coloreados para distinguirlas visualmente.

La columna -> $xx.xx es el monto sugerido para una inversión total de $100. Puedes escalarlo proporcionalmente: si quieres invertir $200, multiplica cada monto por 2.

4. Cómo ejecutar las apuestas
Abre en tu navegador o app las casas indicadas (Pinnacle, 1xBet, BetOnline.ag, Betfair).

Busca el evento exacto (mismo nombre de equipos, mismo mercado).

Confirma que la cuota coincide y que el mercado es idéntico (Over 2.5 no es Over 2.0).

Introduce los montos calculados y realiza las apuestas lo más simultáneamente posible.

Consejo: ten saldo suficiente en cada casa (~$100-$200) para no perder oportunidades.

5. Después de apostar
Registra los resultados en una hoja de cálculo con fecha, evento, casas, cuotas y montos.

Si el pipeline se ejecutó con persistencia (--no-save no está activo), las oportunidades se guardan en quantbet.db. Puedes verlas después con:

powershell
python tools/view_opportunities.py
6. Programar ejecución automática (Windows Task Scheduler)
Para no estar pendiente de ejecutarlo manualmente:

Abre el Programador de tareas de Windows.

Crea una Tarea básica:

Nombre: QuantBet Pipeline

Desencadenador: Diario, a las 08:00 y otra a las 18:00 (crea dos desencadenadores en la misma tarea).

Acción: Iniciar un programa. Selecciona el archivo run_pipeline.bat.

Marca "Ejecutar tanto si el usuario inició sesión como si no" y "Ejecutar con los máximos privilegios" si es necesario.

Acepta y guarda. Los logs aparecerán en logs\ cada día.

7. Comandos útiles adicionales
Ver todas las oportunidades guardadas (últimas 20):

powershell
python tools/view_opportunities.py
Revisar la base de datos con SQL (si tienes sqlite3 instalado):

powershell
sqlite3 quantbet.db "SELECT * FROM opportunities ORDER BY id DESC LIMIT 5;"
Forzar la recarga sin guardar (solo ver en pantalla):

powershell
python main.py --simple --no-save
Ver los logs más recientes (tras usar run_pipeline.bat):

powershell
dir logs\* | Sort-Object LastWriteTime | Select-Object -Last 1 | Get-Content
Ejecutar solo un deporte (si quieres ahorrar créditos) – cambia main.py temporalmente o modifica config.yaml para dejar solo un deporte.

8. Seguridad
No compartas nunca el archivo .env ni la base de datos quantbet.db (contienen tu clave de API).

Los logs guardados por run_pipeline.bat no incluyen la API key (la hemos sanitizado en el código).

Si usas el dashboard web, el debug está desactivado por defecto; solo se activa si creas la variable FLASK_DEBUG=1.

9. Límites de la API gratuita
The Odds API gratis permite 500 peticiones al mes.

Con dos ejecuciones diarias (2 deportes) consumes ~4 peticiones/día, lo que da margen para todo el mes.

Cuando los créditos se agoten, el pipeline no obtendrá datos y lo sabrás por los logs.