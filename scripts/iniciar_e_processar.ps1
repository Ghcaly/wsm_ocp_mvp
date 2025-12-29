# Script para iniciar APIs e processar XMLs
Write-Host "🚀 Iniciando APIs..." -ForegroundColor Blue

# Iniciar WMS Converter
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd c:\prd_debian\wms_converter; .\venv\Scripts\activate; Write-Host 'API WMS Converter iniciando...' -ForegroundColor Green; python app.py"
) -WindowStyle Minimized

Start-Sleep -Seconds 5

# Iniciar WMS Boxing
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd c:\prd_debian\wms-itemsboxing; .\venv\Scripts\activate; Write-Host 'API WMS Boxing iniciando...' -ForegroundColor Green; python app.py"
) -WindowStyle Minimized

Start-Sleep -Seconds 5

# Iniciar OCP Core
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd c:\prd_debian\ocp_wms_core; .\wms_venv\Scripts\activate; cd ocp_score-main; Write-Host 'API OCP Core iniciando...' -ForegroundColor Green; python master_orchestrator.py"
) -WindowStyle Minimized

Write-Host "⏳ Aguardando APIs iniciarem (15 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "✅ APIs devem estar rodando:" -ForegroundColor Green
Write-Host "   - wms_converter: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   - wms-itemsboxing: http://localhost:8001" -ForegroundColor Cyan
Write-Host "   - ocp_wms_core: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   - orchestrator: http://localhost:9000" -ForegroundColor Cyan
Write-Host ""

# Verificar APIs
Write-Host "🔍 Verificando APIs..." -ForegroundColor Blue
$apis = @(
    @{Nome="WMS Converter"; URL="http://localhost:8000/health"},
    @{Nome="WMS Boxing"; URL="http://localhost:8001/health"}
)

foreach ($api in $apis) {
    try {
        $response = Invoke-WebRequest -Uri $api.URL -TimeoutSec 2 -UseBasicParsing
        Write-Host "✓ $($api.Nome): Online" -ForegroundColor Green
    } catch {
        Write-Host "✗ $($api.Nome): Offline" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📦 Processando XMLs da pasta meus_xmls..." -ForegroundColor Blue
Write-Host ""

# Executar processamento
cd c:\prd_debian
bash -c "./PROCESSAR_MEUS_XMLS.sh"
