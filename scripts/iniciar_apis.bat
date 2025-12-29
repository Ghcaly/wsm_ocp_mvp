@echo off
echo Iniciando APIs...

start "WMS Converter" /MIN cmd /k "cd /d c:\prd_debian\wms_converter && venv\Scripts\activate && python app.py"
timeout /t 3 /nobreak > nul

start "WMS Boxing" /MIN cmd /k "cd /d c:\prd_debian\wms-itemsboxing && venv\Scripts\activate && python app.py"
timeout /t 3 /nobreak > nul

start "OCP Core" /MIN cmd /k "cd /d c:\prd_debian\ocp_wms_core && wms_venv\Scripts\activate && cd ocp_score-main && python master_orchestrator.py"

echo.
echo Aguardando APIs iniciarem...
timeout /t 10 /nobreak

echo.
echo APIs iniciadas!
echo - wms_converter: http://localhost:8000
echo - wms-itemsboxing: http://localhost:8001
echo - ocp_wms_core: http://localhost:5000
echo - orchestrator: http://localhost:9000
echo.
pause
