# 8000 포트에서 listen 중인 프로세스 종료 (이전 uvicorn 정리용)
$Port = 8000
$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if (-not $listeners) {
    Write-Host "[StartupFit AI] Port $Port is free. You can run .\run-server.ps1"
    exit 0
}

foreach ($conn in $listeners) {
    $processId = $conn.OwningProcess
    $name = (Get-Process -Id $processId -ErrorAction SilentlyContinue).ProcessName
    Write-Host "[StartupFit AI] Stopping PID $processId ($name) on port $Port..."
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1
$still = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($still) {
    Write-Host "[Error] Port $Port is still in use. Close the app manually or reboot." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Port $Port is free. Run: .\run-server.ps1"
