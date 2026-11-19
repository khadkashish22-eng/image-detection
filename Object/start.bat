@echo off
cd /d "%~dp0"
if not exist ".python-runtime\python.exe" (
  echo Local Python runtime is missing.
  pause
  exit /b 1
)
echo Open http://127.0.0.1:8000/ in your browser.
".python-runtime\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
pause
