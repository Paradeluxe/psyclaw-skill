@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem Debug entry: .venv-debug only (fall back to .venv if missing).
rem Production uses start.bat + .venv + port 8876; debug uses 8877.

set "DEBUG_VENV_PY=%~dp0.venv-debug\Scripts\python.exe"
set "PROD_VENV_PY=%~dp0.venv\Scripts\python.exe"
set "START_DEBUG_PY=%~dp0start_debug.py"
set "ERR=0"

if exist "%DEBUG_VENV_PY%" (
  "%DEBUG_VENV_PY%" "%START_DEBUG_PY%" %*
  set "ERR=%ERRORLEVEL%"
  goto :after
)

echo.
echo psyclaw-webui DEBUG: missing .venv-debug\Scripts\python.exe
if exist "%PROD_VENV_PY%" (
  echo Falling back to production .venv ^(debug toolbar may be missing^).
  "%PROD_VENV_PY%" "%START_DEBUG_PY%" %*
  set "ERR=%ERRORLEVEL%"
  goto :after
)

echo Create the debug venv once in this folder:
echo   python -m venv .venv-debug
echo   .venv-debug\Scripts\python.exe -m pip install -r requirements-debug.txt
echo Then run start_debug.bat again.
set "ERR=1"

:after
if not "%ERR%"=="0" (
  echo.
  echo Failed ^(exit %ERR%^).
  pause
)
exit /b %ERR%