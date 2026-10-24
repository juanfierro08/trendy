@echo off
chcp 65001 > nul
title Trendy Radar

echo =======================================================
echo   ✨ INICIANDO TRENDY RADAR ✨
echo =======================================================
echo.

set PYTHON_CMD=python
python --version >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

echo [OK] Abriendo navegador en http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
%PYTHON_CMD% app.py

pause
