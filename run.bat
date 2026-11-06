@echo off
setlocal
cd /d "%~dp0"
if "%PYTHONPATH%"=="" (
    set "PYTHONPATH=%~dp0src"
) else (
    set "PYTHONPATH=%~dp0src;%PYTHONPATH%"
)
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m nfc_coil_calculator
) else (
    python -m nfc_coil_calculator
)
if errorlevel 1 pause
