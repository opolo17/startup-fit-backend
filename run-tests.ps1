$VenvPath = Join-Path $env:LOCALAPPDATA 'StartupFitAI-venv'
$Python = Join-Path $VenvPath 'Scripts\python.exe'

if (-not (Test-Path $Python)) {
    Write-Host "[오류] .\setup-venv.ps1 을 먼저 실행하세요." -ForegroundColor Red
    exit 1
}

Set-Location $PSScriptRoot
& $Python -m pytest -q
