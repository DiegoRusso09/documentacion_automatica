@echo off
REM =========================================================
REM Guarda la clave de Gemini en las variables de usuario de
REM Windows. Solo hace falta ejecutarlo una vez.
REM La clave NO se guarda en ningun archivo del proyecto.
REM =========================================================

echo.
echo Crea tu clave en: https://aistudio.google.com/apikey
echo.
set /p GEMINI_KEY=Pega tu clave de Gemini (AIza...) y pulsa Enter:

if "%GEMINI_KEY%"=="" (
    echo No se ingreso ninguna clave. No se cambio nada.
    pause
    exit /b 1
)

setx GEMINI_API_KEY "%GEMINI_KEY%" >nul

echo.
echo Listo. Clave guardada en GEMINI_API_KEY.
echo Cierra las terminales abiertas; las nuevas ya la veran.
echo Ahora puedes ejecutar iniciar_servidor.bat
echo.
pause
