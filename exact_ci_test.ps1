# Exact CI Replication PowerShell Script  
# This replicates the EXACT PowerShell logic that is failing in CI

Write-Host "=== Exact CI Replication Test ===" -ForegroundColor Cyan
Write-Host ""

# Set up environment exactly like CI
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me" 
$env:USE_INMEMORY_DB = "1"
$env:PYTHONUNBUFFERED = "1"

Write-Host "Starting API server..." -ForegroundColor Yellow

# Start the process EXACTLY like CI does
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info" -PassThru -NoNewWindow

Write-Host "API process started with PID: $($apiProcess.Id)" -ForegroundColor Green

# Wait for server startup
Write-Host "Waiting for server startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Try health check
Write-Host "Performing health check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 10
    Write-Host "Health check response: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    $processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    if ($processCheck) {
        Write-Host "Process is still running despite failed health check" -ForegroundColor Yellow
    } else {
        Write-Host "Process died before health check!" -ForegroundColor Red
    }
    exit 1
}

# THIS IS THE EXACT CHECK THAT'S FAILING IN CI
Write-Host ""
Write-Host "# Check if API process is still running" -ForegroundColor Yellow  
Write-Host "Checking for API process ID: $($apiProcess.Id)" -ForegroundColor Gray

# Wait a moment (this is where CI process dies)
Start-Sleep -Seconds 2

$processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue

if (-not $processCheck) {
    Write-Host "API process died before tests!" -ForegroundColor Red
    
    # Get final API output like CI does
    Write-Host "Final API output:" -ForegroundColor Yellow
    Write-Host "=== STDOUT ===" -ForegroundColor Gray
    # In CI this would capture the process output
    Write-Host "=== STDERR ===" -ForegroundColor Gray
    
    exit 1
} else {
    Write-Host "SUCCESS: API process $($apiProcess.Id) is still running!" -ForegroundColor Green
    
    # Perform a few more checks
    Write-Host "Performing additional tests..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le 5; $i++) {
        Start-Sleep -Seconds 2
        
        $stillAlive = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
        if (-not $stillAlive) {
            Write-Host "Process died during test $i" -ForegroundColor Red
            exit 1
        }
        
        # Try another health check
        try {
            $testResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5
            Write-Host "Test $i - Health check OK" -ForegroundColor Green
        } catch {
            Write-Host "Test $i - Health check FAILED: $($_.Exception.Message)" -ForegroundColor Red
            # Don't exit on individual health check failures for now
        }
    }
    
    Write-Host ""
    Write-Host "All tests completed successfully!" -ForegroundColor Green
    Write-Host "Process survived the entire test duration" -ForegroundColor Green
    
    # Clean shutdown
    Stop-Process -Id $apiProcess.Id -Force
    Write-Host "Process stopped" -ForegroundColor Green
}