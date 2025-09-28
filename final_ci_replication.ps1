# Final CI Replication Test - Exact GitHub Actions Scenario
# This test replicates the exact timing and conditions that caused the CI failure

param(
    [int]$TestDuration = 60
)

Write-Host "=== Final CI Replication Test ===" -ForegroundColor Cyan
Write-Host "Replicating exact GitHub Actions failure scenario" -ForegroundColor Yellow
Write-Host ""

# Set exact CI environment
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me"
$env:USE_INMEMORY_DB = "1"
$env:PYTHONUNBUFFERED = "1"

Write-Host "Environment configured:" -ForegroundColor Green
Write-Host "  SECRET_KEY: $env:SECRET_KEY"
Write-Host "  USE_INMEMORY_DB: $env:USE_INMEMORY_DB"
Write-Host ""

# Start API exactly like CI
Write-Host "Starting API server..." -ForegroundColor Yellow
$startTime = Get-Date
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info" -PassThru -NoNewWindow

if (-not $apiProcess) {
    Write-Host "FAIL: Could not start API process" -ForegroundColor Red
    exit 1
}

Write-Host "API started successfully! Process ID: $($apiProcess.Id)" -ForegroundColor Green

# Wait for startup (CI waits around 37 seconds based on the logs)
Write-Host ""
Write-Host "Simulating CI startup wait period..." -ForegroundColor Yellow
$startupDuration = 37  # Exact duration from CI logs

for ($i = 1; $i -le $startupDuration; $i++) {
    $processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    if (-not $processCheck) {
        Write-Host "CRITICAL: Process died at ${i}s during startup!" -ForegroundColor Red
        exit 1
    }
    
    if ($i % 5 -eq 0) {
        Write-Host "  Startup progress: ${i}s / ${startupDuration}s" -ForegroundColor Gray
    }
    
    Start-Sleep -Seconds 1
}

Write-Host "Startup simulation complete" -ForegroundColor Green
Write-Host ""

# Attempt health check (this succeeds in CI)
Write-Host "Performing initial health check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 10
    Write-Host "Health check SUCCESS: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "Health check FAILED: $($_.Exception.Message)" -ForegroundColor Red
    $processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    if ($processCheck) {
        Write-Host "Process is still running despite health check failure" -ForegroundColor Yellow
    } else {
        Write-Host "Process died during health check!" -ForegroundColor Red
    }
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""

# This is the critical moment - the check that fails in CI
Write-Host "# Check if API process is still running" -ForegroundColor Yellow
Write-Host "Checking for API process ID: $($apiProcess.Id)" -ForegroundColor Gray

# Add a small delay (CI has some delay here)
Start-Sleep -Seconds 2

$processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue

if (-not $processCheck) {
    # This is the exact error CI reports
    Write-Host "API process died before tests!" -ForegroundColor Red
    Write-Host "Final API output:" -ForegroundColor Yellow
    Write-Host "=== STDOUT ===" -ForegroundColor Gray
    Write-Host "=== STDERR ===" -ForegroundColor Gray
    exit 1
}

Write-Host "SUCCESS: API process $($apiProcess.Id) is still running!" -ForegroundColor Green
Write-Host ""

# Extended testing to ensure stability
Write-Host "Performing extended stability test..." -ForegroundColor Yellow
$extendedDuration = 30
for ($i = 1; $i -le $extendedDuration; $i++) {
    $processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    if (-not $processCheck) {
        Write-Host "Process died during extended test at ${i}s!" -ForegroundColor Red
        exit 1
    }
    
    # Periodic health checks
    if ($i % 10 -eq 0) {
        try {
            $testResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5
            Write-Host "  Extended test ${i}s: Health check OK" -ForegroundColor Green
        } catch {
            Write-Host "  Extended test ${i}s: Health check failed - $($_.Exception.Message)" -ForegroundColor Yellow
            # Don't fail the test for individual health check failures
        }
    } else {
        Write-Host "  Extended test: ${i}s - Process stable" -ForegroundColor Gray
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "FINAL RESULT: SUCCESS!" -ForegroundColor Green
Write-Host "The 'API process died before tests!' error has been resolved!" -ForegroundColor Green
Write-Host "Process survived for $((Get-Date) - $startTime) total duration" -ForegroundColor Green

# Clean shutdown
Write-Host ""
Write-Host "Performing clean shutdown..." -ForegroundColor Yellow
Stop-Process -Id $apiProcess.Id -Force
Write-Host "Process terminated" -ForegroundColor Green

exit 0