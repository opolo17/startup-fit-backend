# OneDrive 폴더에서는 venv 생성이 실패할 수 있어, 로컬 AppData에 가상환경을 만듭니다.
$ErrorActionPreference = 'Stop'

$VenvPath = Join-Path $env:LOCALAPPDATA 'StartupFitAI-venv'
$BackendRoot = $PSScriptRoot
$Requirements = Join-Path $BackendRoot 'requirements.txt'

Write-Host "[StartupFit AI] Python:" -NoNewline
python --version

if (Test-Path $VenvPath) {
    Write-Host "[StartupFit AI] 기존 venv 삭제: $VenvPath"
    Remove-Item -Recurse -Force $VenvPath
}

Write-Host "[StartupFit AI] venv 생성 중 (OneDrive 밖): $VenvPath"
python -m venv $VenvPath

$Python = Join-Path $VenvPath 'Scripts\python.exe'
& $Python -m pip install --upgrade pip
& $Python -m pip install -r $Requirements

Write-Host ""
Write-Host "[완료] 가상환경 경로: $VenvPath"
Write-Host "서버 실행: .\run-server.ps1"
