# Backend API server (venv in LocalAppData, outside OneDrive)
$ErrorActionPreference = 'Stop'

$Port = 8000
$VenvPath = Join-Path $env:LOCALAPPDATA 'StartupFitAI-venv'
$Python = Join-Path $VenvPath 'Scripts\python.exe'

if (-not (Test-Path $Python)) {
    Write-Host '[Error] venv not found. Run: .\setup-venv.ps1' -ForegroundColor Red
    exit 1
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $processId = $listener.OwningProcess
    $name = (Get-Process -Id $processId -ErrorAction SilentlyContinue).ProcessName
    Write-Host "[Error] Port $Port is already in use (PID $processId, $name)." -ForegroundColor Red
    Write-Host '        Another uvicorn may still be running from a previous session.'
    Write-Host '        Fix: .\stop-server.ps1   then   .\run-server.ps1'
    exit 1
}

Set-Location $PSScriptRoot

& $Python -c "from app.config import get_settings; exit(0 if get_settings().openai_api_key else 1)" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host '[Warn] OPENAI_API_KEY not loaded. Run: .\check-env.ps1' -ForegroundColor Yellow
    Write-Host '       Copy-Item .env.example .env  and set OPENAI_API_KEY'
}

Write-Host "[StartupFit AI] Starting server at http://127.0.0.1:$Port"
Write-Host '[StartupFit AI] Press Ctrl+C to stop'
& $Python -m uvicorn app.main:app --reload --port $Port
