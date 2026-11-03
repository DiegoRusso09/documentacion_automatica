@echo off
REM =========================================================
REM Arranca el servidor local en http://127.0.0.1:8000
REM =========================================================

cd /d "%~dp0"

REM Si la terminal se abrio antes de configurar_gemini.bat,
REM leemos la clave directamente de las variables de usuario.
if "%GEMINI_API_KEY%"=="" (
    for /f "tokens=2,*" %%a in ('reg query HKCU\Environment /v GEMINI_API_KEY 2^>nul ^| find "GEMINI_API_KEY"') do set "GEMINI_API_KEY=%%b"
)

set PYTHONIOENCODING=utf-8

REM Muestra la cadena de proveedores de IA y si cada uno responde.
echo Comprobando proveedores de IA...
.venv\Scripts\python scripts\probar_proveedores.py
echo.

start "" http://127.0.0.1:8000

.venv\Scripts\python -m uvicorn oic_doc_generator.main:app --host 127.0.0.1 --port 8000

pause
