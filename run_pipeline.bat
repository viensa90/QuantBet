@echo off
REM QuantBet Pipeline Launcher para Windows Task Scheduler o uso manual
REM Guarda la salida en logs con marca de tiempo

cd /d "%~dp0"

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat >nul 2>&1
)

REM Crear carpeta logs si no existe
if not exist logs mkdir logs

REM Generar nombre de archivo de log con fecha/hora (formato seguro)
for /f "tokens=1-4 delims=/- " %%a in ('date /t') do (
    set day=%%a
    set month=%%b
    set year=%%c
)
for /f "tokens=1-4 delims=:., " %%a in ('time /t') do (
    set hour=%%a
    set minute=%%b
)
set timestamp=%year%%month%%day%_%hour%%minute%
set LOGFILE=logs\pipeline_%timestamp%.log

echo ============================================= >> "%LOGFILE%"
echo Iniciando pipeline QuantBet %date% %time% >> "%LOGFILE%"
python main.py --simple >> "%LOGFILE%" 2>&1
echo Pipeline finalizado %date% %time% >> "%LOGFILE%"
echo ============================================= >> "%LOGFILE%"

REM Si se ejecuta manualmente, muestra el log por consola
if not "%1"=="silent" type "%LOGFILE%"