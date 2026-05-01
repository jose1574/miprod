@echo off
cd /d "%~dp0"
set FLASK_APP=ferre
:: Ejecutamos con pythonw.exe para que el proceso de Python sea de fondo
".\venv\Scripts\pythonw.exe" -m flask run --host=0.0.0.0 --port=5000