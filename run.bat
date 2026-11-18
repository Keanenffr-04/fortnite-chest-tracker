@echo off
cd /d "%~dp0"
python -c "import PySide6, mss, cv2, numpy, keyboard" 2>nul || python -m pip install -r requirements.txt
if "%~1"=="" (python main.py --app) else (python main.py %*)
pause
