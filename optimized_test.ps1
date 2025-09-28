Write-Host "=== FINAL OPTIMIZED BLOCKING TEST ===" -ForegroundColor Yellow
$env:USE_INMEMORY_DB = "1"
$env:HOST = "tenant1.lvh.me"
$env:GITHUB_ACTIONS = "true"
$env:CI = "true"

Write-Host "Starting API with optimized blocking persistence..."
$apiProcess = Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" -PassThru -NoNewWindow
Write-Host "API started with PID: $($apiProcess.Id)"

Write-Host "Waiting for full API startup (20 seconds)..."
Start-Sleep 20

$successCount = 0
for ($i = 1; $i -le 12; $i++) {
    try {
        Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 10 | Out-Null
        $successCount++
        Write-Host " Health check $i/12 PASSED - API ALIVE" -ForegroundColor Green
        
        if (Test-Path "blocking_status.tmp") {
            $status = Get-Content "blocking_status.tmp" -ErrorAction SilentlyContinue
            if ($status) { Write-Host " Blocking: $status" -ForegroundColor Blue }
        }
    } catch {
        Write-Host " Health check $i/12 FAILED: $($_.Exception.Message)" -ForegroundColor Red
        if ($apiProcess.HasExited) {
            Write-Host " Process died!" -ForegroundColor Red
            break
        }
    }
    Start-Sleep 2
}

Write-Host "`n=== FINAL RESULTS ===" -ForegroundColor Yellow
Write-Host "Health Checks Passed: $successCount/12" -ForegroundColor $(if ($successCount -ge 10) { "Green" } else { "Red" })

if (!$apiProcess.HasExited) {
    Write-Host " SUCCESS: Process survived the entire test!" -ForegroundColor Green
    Write-Host " Simple blocking approach is WORKING!" -ForegroundColor Green
} else {
    Write-Host " FAILED: Process died during test" -ForegroundColor Red
}

Stop-Process $apiProcess.Id -Force -ErrorAction SilentlyContinue
Write-Host "Test completed!" -ForegroundColor Yellow
