@echo off
cd /d "%~dp0"
set FLASK_APP=app
:: Ejecutamos con pythonw.exe para que el proceso de Python sea de fondo
if exist ".venv\Scripts\pythonw.exe" (
	".venv\Scripts\pythonw.exe" -m flask run --host=0.0.0.0 --port=5000
) else (
	python -m flask run --host=0.0.0.0 --port=5000
)