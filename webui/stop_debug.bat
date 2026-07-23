@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem Stop the debug server (port 8877 by default).
set "DEBUG_VENV_PY=%~dp0.venv-debug\Scripts\python.exe"
set "PROD_VENV_PY=%~dp0.venv\Scripts\python.exe"
set "STOP_PY=%~dp0scripts\stop_server.py"
set "ERR=0"

set "PSYCLAW_PORT=8877"

if exist "%DEBUG_VENV_PY%" (
  "%DEBUG_VENV_PY%" "%STOP_PY%"
  set "ERR=%ERRORLEVEL%"
  goto :after
)
if exist "%PROD_VENV_PY%" (
  "%PROD_VENV_PY%" "%STOP_PY%"
  set "ERR=%ERRORLEVEL%"
  goto :after
)
echo No venv found for stop. Using system python.
python "%STOP_PY%"
set "ERR=%ERRORLEVEL%"

:after
if not "%ERR%"=="0" (
  echo.
  echo Failed ^(exit %ERR%^).
  pause
)
exit /b %ERR%