@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem Windows entry: repo .venv only (do not use the `py` launcher).
set "VENV_PY=%~dp0.venv\Scripts\python.exe"
set "START_PY=%~dp0start.py"
set "ERR=0"

if exist "%VENV_PY%" (
  "%VENV_PY%" "%START_PY%" %*
  set "ERR=%ERRORLEVEL%"
  goto :after
)

echo.
echo psyclaw-webui: missing .venv\Scripts\python.exe
echo Create it once in this folder:
echo   python -m venv .venv
echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
echo Then double-click start.bat again.  See docs\INSTALL.md
set "ERR=1"

:after
if not "%ERR%"=="0" (
  echo.
  echo Failed ^(exit %ERR%^).
  pause
)
exit /b %ERR%
