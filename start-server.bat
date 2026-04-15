@echo off
echo Starting HTTP server on port 8080...
echo.
echo Please wait...
echo.
cd /d "%~dp0"
start http://localhost:8080/psyclaw.html
python -m http.server 8080
