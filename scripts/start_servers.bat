@echo off
title Todomotortaller - Iniciando Servidores
echo ============================================
echo   Todomotortaller - Inicio de Servidores
echo ============================================
echo.

:: Mata procesos en puertos 8000 (backend) y 8080 (frontend)
echo [1/3] Deteniendo servidores anteriores...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /r ":8000 .*LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /r ":8080 .*LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: Inicia backend (uvicorn) en ventana nueva
echo [2/3] Iniciando backend en puerto 8000...
start "Backend - Todomotortaller" cmd /c "cd /d "%~dp0.." && "%~dp0..\venv\Scripts\python" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Espera unos segundos para que el backend se inicie
timeout /t 4 /nobreak >nul

:: Inicia frontend (npm serve) en ventana nueva
echo [3/3] Iniciando frontend en puerto 8080...
start "Frontend - Todomotortaller" cmd /c "cd /d "%~dp0..\frontend" && npm run serve"

echo.
echo ============================================
echo   Servidores iniciados correctamente
echo   Backend:  http://localhost:8000
echo.
echo   Frontend (con candado, necesario para
echo   las notificaciones y el PWA):
echo     PC:      https://localhost:8080
echo     Otros:   https://192.168.0.194:8080
echo.
echo   IMPORTANTE: el certificado es autofirmado.
echo   La PRIMERA vez que abras la pagina en cada
echo   dispositivo saldra un aviso. Pulsa:
echo       Avanzado  ->  Continuar
echo   Despues ya no vuelve a molestar.
echo ============================================
echo.
echo  Presiona cualquier tecla para cerrar esta ventana...
pause >nul
