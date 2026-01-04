# iniciar_apis.ps1 - Iniciar APIs necessarias

# Get-Process python -ErrorAction SilentlyContinue | Stop-Process
# powershell -ExecutionPolicy Bypass -File "C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp_binpack\wsm_ocp_mvp\scripts\iniciar_apis.ps1"

Write-Host ""
Write-Host "Iniciando APIs..." -ForegroundColor Blue
Write-Host ""

$BASE = "C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp_binpack\wsm_ocp_mvp"
$PYTHON = "C:\Users\BRKEY864393\OneDrive - Anheuser-Busch InBev\My Documents\projetos\ocp_binpack\.venv\Scripts\python.exe"
$LOG_DIR = "$BASE\logs"

# Criar diretorio de logs
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR | Out-Null
}

# 1. WMS Converter (porta 8002)
Write-Host "Iniciando WMS Converter (porta 8002)..." -ForegroundColor Cyan
$converterLog = "$LOG_DIR\converter_error.log"
$converter = Start-Process -FilePath $PYTHON `
    -ArgumentList "`"$BASE\wms_converter\api.py`"" `
    -WorkingDirectory "$BASE\wms_converter" `
    -RedirectStandardError $converterLog `
    -WindowStyle Hidden `
    -PassThru

Start-Sleep -Seconds 3

# 2. WMS Boxing (porta 8001)
Write-Host "Iniciando WMS Boxing (porta 8001)..." -ForegroundColor Cyan
$boxingLog = "$LOG_DIR\boxing_error.log"
$boxing = Start-Process -FilePath $PYTHON `
    -ArgumentList "`"$BASE\wms-itemsboxing\src\app.py`"" `
    -WorkingDirectory "$BASE\wms-itemsboxing" `
    -RedirectStandardError $boxingLog `
    -WindowStyle Hidden `
    -PassThru

Write-Host ""
Write-Host "Aguardando APIs iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar
Write-Host ""
Write-Host "Verificando APIs..." -ForegroundColor Cyan
Write-Host ""

try {
    Invoke-WebRequest -Uri "http://localhost:8002/health" -TimeoutSec 5 -ErrorAction Stop | Out-Null
    Write-Host "OK - WMS Converter: Online (http://localhost:8002)" -ForegroundColor Green
} catch {
    Write-Host "ERRO - WMS Converter: Offline" -ForegroundColor Red
    Write-Host "Log de erro:" -ForegroundColor Yellow
    if (Test-Path $converterLog) {
        Get-Content $converterLog -Tail 20
    }
    Write-Host ""
}

try {
    Invoke-WebRequest -Uri "http://localhost:8001/api/items-boxing/health/" -TimeoutSec 5 -ErrorAction Stop | Out-Null
    Write-Host "OK - WMS Boxing: Online (http://localhost:8001)" -ForegroundColor Green
} catch {
    Write-Host "ERRO - WMS Boxing: Offline" -ForegroundColor Red
    Write-Host "Log de erro:" -ForegroundColor Yellow
    if (Test-Path $boxingLog) {
        Get-Content $boxingLog -Tail 20
    }
    Write-Host ""
}

Write-Host ""
Write-Host "Processo concluido!" -ForegroundColor Green
Write-Host ""
Write-Host "Para parar os servicos:" -ForegroundColor Yellow
Write-Host "  Get-Process python | Stop-Process" -ForegroundColor Gray
Write-Host ""
Write-Host "Logs completos em: $LOG_DIR" -ForegroundColor Gray
Write-Host ""
