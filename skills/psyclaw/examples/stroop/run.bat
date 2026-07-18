@echo off
cd /d "%~dp0"
where psychopy >nul 2>&1 && psychopy "%cd%\stroop_experiment.psyexp" || echo Install PsychoPy from https://www.psychopy.org/
pause
