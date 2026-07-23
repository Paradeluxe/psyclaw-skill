@echo off
echo === PsyClaw monorepo install ===

set "MONOREPO_DIR=%USERPROFILE%\psyclaw"
if not "%~1"=="" set "MONOREPO_DIR=%~1"

REM 1. Clone or update monorepo
if exist "%MONOREPO_DIR%\.git" (
  echo Monorepo already exists — updating...
  git -C "%MONOREPO_DIR%" pull
) else (
  echo Cloning Paradeluxe/psyclaw to %MONOREPO_DIR%...
  git clone https://github.com/Paradeluxe/psyclaw.git "%MONOREPO_DIR%"
)

REM 2. Skill install instructions
echo.
echo === Skill install ===
echo Skill source: %MONOREPO_DIR%\skills\psyclaw\
echo.
echo Install command depends on your AI CLI:
echo   Hermes:      cd %MONOREPO_DIR% ^&^& hermes install Paradeluxe/psyclaw/skills/psyclaw
echo   Claude Code:  copy %MONOREPO_DIR%\skills\psyclaw to .claude\skills\
echo   Generic:     Point your agent at %MONOREPO_DIR%\skills\psyclaw\
echo.

REM 3. WebUI setup
echo === WebUI setup ===
set "WEBUI_DIR=%MONOREPO_DIR%\webui"
cd /d "%WEBUI_DIR%"

if not exist ".venv" (
  echo Creating Python venv...
  python -m venv .venv
)

echo Installing Flask dependencies...
".venv\Scripts\pip" install -r requirements.txt

echo Remembering webui path...
python scripts/user_config.py remember

echo.
echo === Install complete ===
echo Monorepo:  %MONOREPO_DIR%
echo WebUI:     %WEBUI_DIR%
echo Start:     cd %WEBUI_DIR% ^&^& python start.py
echo URL:       http://127.0.0.1:8876
pause