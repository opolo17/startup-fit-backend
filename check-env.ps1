$EnvFile = Join-Path $PSScriptRoot '.env'

Write-Host '[StartupFit AI] OpenAI env check'
Write-Host "  .env: $(if (Test-Path $EnvFile) { 'OK' } else { 'MISSING' })  $EnvFile"

if (-not (Test-Path $EnvFile)) {
    Write-Host ''
    Write-Host 'Create .env in this folder:' -ForegroundColor Yellow
    Write-Host '  Copy-Item .env.example .env'
    Write-Host '  notepad .env   # OPENAI_API_KEY=sk-...'
    exit 1
}

$Python = Join-Path $env:LOCALAPPDATA 'StartupFitAI-venv\Scripts\python.exe'
if (-not (Test-Path $Python)) {
    Write-Host '[Error] Run .\setup-venv.ps1 first' -ForegroundColor Red
    exit 1
}

Set-Location $PSScriptRoot
& $Python -c @"
from app.config import get_settings, env_file_hint
get_settings.cache_clear()
s = get_settings()
print('  env files:', env_file_hint())
print('  OPENAI_API_KEY loaded:', bool(s.openai_api_key))
if s.openai_api_key:
    print('  key length:', len(s.openai_api_key))
else:
    raise SystemExit(1)
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host '[Error] Key is empty in .env' -ForegroundColor Red
    exit 1
}

Write-Host '[OK] Restart .\run-server.ps1 if the server was already running.'
