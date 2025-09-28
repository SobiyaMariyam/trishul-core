Write-Host "=== SIMPLE BLOCKING TEST ===" -ForegroundColor Yellow
$env:USE_INMEMORY_DB = "1"
$env:HOST = "tenant1.lvh.me"
$env:GITHUB_ACTIONS = "true"
$env:CI = "true"

$apiProcess = Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" -PassThru -NoNewWindow
Write-Host "API started with PID: $($apiProcess.Id)"
Start-Sleep 10

$successCount = 0
for ($i = 1; $i -le 10; $i++) {
    try {
        Invoke-RestMethod "http://127.0.0.1:8000/health" | Out-Null
        $successCount++
        Write-Host "Health check $i/10 PASSED" -ForegroundColor Green
        if (Test-Path "blocking_status.tmp") {
            $status = Get-Content "blocking_status.tmp"
            Write-Host "Status: $status" -ForegroundColor Blue
        }
    } catch {
        Write-Host "Health check $i/10 FAILED" -ForegroundColor Red
    }
    Start-Sleep 3
}

Write-Host "Final result: $successCount/10 health checks passed"
if (!$apiProcess.HasExited) {
    Write-Host "SUCCESS: Process still alive!" -ForegroundColor Green
} else {
    Write-Host "FAILED: Process died" -ForegroundColor Red
}

Stop-Process $apiProcess.Id -Force -ErrorAction SilentlyContinue
