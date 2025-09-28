# Ultimate CI Test - Exact GitHub Actions Replication
# This test tries to exactly match the failure timing from CI

Write-Host "=== Ultimate CI Test ===" -ForegroundColor Cyan
Write-Host "Exact GitHub Actions timing replication" -ForegroundColor Yellow
Write-Host ""

# Set exact environment
$env:SECRET_KEY = "dev-secret-for-ci"
$env:USE_INMEMORY_DB = "1"

# Start API server
Write-Host "Starting API server..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info" -PassThru -NoNewWindow

Write-Host "API process started with PID: $($apiProcess.Id)" -ForegroundColor Green
Write-Host ""

# Wait exact timing from CI logs
Write-Host "Waiting for API startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 8  # Let it fully start

# Health check (this works in CI)
Write-Host "Performing health check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 10
    Write-Host "Health check SUCCESS: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "Health check FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# The critical moment - this is where CI fails
Write-Host "# Check if API process is still running" -ForegroundColor Yellow
Write-Host "Checking for API process ID: $($apiProcess.Id)" -ForegroundColor Gray

# Small delay like CI
Start-Sleep -Seconds 3

# The exact check that fails in CI
$processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue

if (-not $processCheck) {
    Write-Host "API process died before tests!" -ForegroundColor Red
    
    # Check the status file
    if (Test-Path "api_status.json") {
        $status = Get-Content "api_status.json" | ConvertFrom-Json
        Write-Host "Status file shows: PID $($status.pid), Status: $($status.status)" -ForegroundColor Yellow
    } else {
        Write-Host "No status file found" -ForegroundColor Yellow
    }
    
    exit 1
} else {
    Write-Host "SUCCESS: Process $($apiProcess.Id) is still alive!" -ForegroundColor Green
    
    # Check both persistence mechanisms
    if (Test-Path "api_status.json") {
        $status = Get-Content "api_status.json" | ConvertFrom-Json
        Write-Host "Status file confirms: PID $($status.pid), Heartbeat: $($status.heartbeat)" -ForegroundColor Cyan
    }
    
    # Extended test - monitor for 60 more seconds
    Write-Host ""
    Write-Host "Running extended stability test (60 seconds)..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le 12; $i++) {  # 12 * 5 = 60 seconds
        Start-Sleep -Seconds 5
        
        $stillAlive = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
        if (-not $stillAlive) {
            Write-Host "Process died at ${i}0 seconds!" -ForegroundColor Red
            exit 1
        }
        
        # Check status file updates
        if (Test-Path "api_status.json") {
            $currentStatus = Get-Content "api_status.json" | ConvertFrom-Json
            $timestamp = [datetime]::Parse($currentStatus.timestamp)
            $secondsAgo = ((Get-Date) - $timestamp).TotalSeconds
            Write-Host "  ${i}0s: Process alive, last heartbeat $([math]::Round($secondsAgo))s ago" -ForegroundColor Green
        } else {
            Write-Host "  ${i}0s: Process alive" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "ULTIMATE SUCCESS!" -ForegroundColor Green
    Write-Host "Process survived complete extended test" -ForegroundColor Green
    Write-Host "The CI 'API process died before tests!' error is RESOLVED" -ForegroundColor Green
}

# Clean shutdown
Write-Host ""
Write-Host "Stopping process..." -ForegroundColor Gray
Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
Write-Host "Test completed" -ForegroundColor Gray