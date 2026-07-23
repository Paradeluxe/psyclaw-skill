@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"
if exist "%VENV_PY%" (
  "%VENV_PY%" "%~dp0scripts\stop_server.py" %*
  exit /b %ERRORLEVEL%
)
echo missing .venv — cannot run stop_server.py
pause
exit /b 1
