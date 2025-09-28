# Advanced CI Test PowerShell Script
# This replicates the exact PowerShell logic used in GitHub Actions CI

param(
    [int]$TimeoutSeconds = 60,
    [int]$MaxRetries = 3
)

Write-Host "=== Advanced CI Test PowerShell Script ===" -ForegroundColor Cyan
Write-Host "Replicating exact GitHub Actions CI behavior" -ForegroundColor Gray
Write-Host ""

# Set environment variables exactly like CI
Write-Host "Setting up environment..." -ForegroundColor Yellow
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me"
$env:USE_INMEMORY_DB = "1"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Environment variables set:" -ForegroundColor Green
Write-Host "  SECRET_KEY: $env:SECRET_KEY"
Write-Host "  TENANT_DOMAIN: $env:TENANT_DOMAIN"  
Write-Host "  USE_INMEMORY_DB: $env:USE_INMEMORY_DB"
Write-Host ""

# Start the API server in background (exactly like CI)
Write-Host "Starting API server..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info" -PassThru -NoNewWindow

if (-not $apiProcess) {
    Write-Host "FAIL: Could not start API process" -ForegroundColor Red
    exit 1
}

Write-Host "API process started with PID: $($apiProcess.Id)" -ForegroundColor Green
Write-Host ""

# Wait for server to be ready
Write-Host "Waiting for server to be ready..." -ForegroundColor Yellow
$serverReady = $false
$attempts = 0
$maxAttempts = 30

while (-not $serverReady -and $attempts -lt $maxAttempts) {
    $attempts++
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response) {
            $serverReady = $true
            Write-Host "Server is ready! Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
        }
    }
    catch {
        if ($attempts % 5 -eq 0) {
            Write-Host "  Still waiting... (attempt $attempts/$maxAttempts)" -ForegroundColor Gray
        }
        Start-Sleep -Seconds 1
    }
}

if (-not $serverReady) {
    Write-Host "TIMEOUT: Server did not become ready" -ForegroundColor Red
    
    # Check if process is still running
    $processStillRunning = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    if ($processStillRunning) {
        Write-Host "Process is still running but not responding" -ForegroundColor Yellow
        Stop-Process -Id $apiProcess.Id -Force
    } else {
        Write-Host "Process has already died" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""

# Perform health check (exactly like CI test)
Write-Host "Performing health check test..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -Headers @{"Host"="tenant1.lvh.me"} -TimeoutSec 10
    Write-Host "Health check PASSED: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "Health check FAILED: $($_.Exception.Message)" -ForegroundColor Red
    
    # Check process status immediately after failed request
    $processStatus = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    if ($processStatus) {
        Write-Host "Process is still running after failed health check" -ForegroundColor Yellow
    } else {
        Write-Host "Process died after health check!" -ForegroundColor Red
    }
    
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""

# Monitor process stability (this is where CI fails)
Write-Host "Monitoring process stability..." -ForegroundColor Yellow
$monitoringDuration = 15  # seconds
$startTime = Get-Date
$checkInterval = 1  # second

while (((Get-Date) - $startTime).TotalSeconds -lt $monitoringDuration) {
    $processCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    
    if (-not $processCheck) {
        $elapsed = ((Get-Date) - $startTime).TotalSeconds
        Write-Host "CRITICAL: Process died after $([math]::Round($elapsed, 1)) seconds!" -ForegroundColor Red
        
        # This is exactly what CI reports
        Write-Host "API process died before tests!" -ForegroundColor Red
        exit 1
    }
    
    # Log progress
    $elapsed = ((Get-Date) - $startTime).TotalSeconds
    if ($elapsed % 5 -lt 1) {
        Write-Host "  Process still alive after $([math]::Round($elapsed, 1))s" -ForegroundColor Gray
    }
    
    Start-Sleep -Seconds $checkInterval
}

Write-Host ""

# Final health check
Write-Host "Performing final health check..." -ForegroundColor Yellow
try {
    $finalResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -Headers @{"Host"="tenant1.lvh.me"} -TimeoutSec 10
    Write-Host "Final health check PASSED: $($finalResponse | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "Final health check FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Final process check
$finalProcessCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
if ($finalProcessCheck) {
    Write-Host ""
    Write-Host "SUCCESS: Process survived the entire test!" -ForegroundColor Green
    Write-Host "Process PID $($apiProcess.Id) is still running" -ForegroundColor Green
    
    # Clean shutdown
    Write-Host "Stopping process..." -ForegroundColor Yellow
    Stop-Process -Id $apiProcess.Id -Force
    Write-Host "Process stopped" -ForegroundColor Green
    
    exit 0
} else {
    Write-Host ""
    Write-Host "FAIL: Process died during testing" -ForegroundColor Red
    exit 1
}