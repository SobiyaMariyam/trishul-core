# Advanced Process Monitoring Script
# This script helps troubleshoot the exact CI process monitoring issue

param(
    [int]$MonitorDuration = 120,
    [string]$ProcessName = "python"
)

Write-Host "=== Advanced Process Monitoring Script ===" -ForegroundColor Cyan
Write-Host "Monitoring process detection in CI-like environment" -ForegroundColor Yellow
Write-Host ""

# Setup environment
$env:SECRET_KEY = "dev-secret-for-ci"
$env:USE_INMEMORY_DB = "1"

Write-Host "Starting API server..." -ForegroundColor Yellow
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" -PassThru -NoNewWindow

$startTime = Get-Date
Write-Host "Process started - PID: $($apiProcess.Id)" -ForegroundColor Green
Write-Host ""

# Monitor for startup
Write-Host "Monitoring startup..." -ForegroundColor Yellow
for ($i = 1; $i -le 20; $i++) {
    # Multiple process detection methods
    $method1 = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    $method2 = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Id -eq $apiProcess.Id}
    $method3 = Get-WmiObject -Class Win32_Process -Filter "ProcessId=$($apiProcess.Id)" -ErrorAction SilentlyContinue
    
    $status = @{
        "Method1_DirectPID" = if ($method1) { "FOUND" } else { "NOT_FOUND" }
        "Method2_NameFilter" = if ($method2) { "FOUND" } else { "NOT_FOUND" }
        "Method3_WMI" = if ($method3) { "FOUND" } else { "NOT_FOUND" }
    }
    
    Write-Host "  ${i}s - Direct PID: $($status.Method1_DirectPID), Name Filter: $($status.Method2_NameFilter), WMI: $($status.Method3_WMI)" -ForegroundColor Gray
    
    if (-not $method1 -and -not $method2 -and -not $method3) {
        Write-Host "CRITICAL: All detection methods failed at ${i}s!" -ForegroundColor Red
        break
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""

# Wait for health endpoint to be ready
Write-Host "Waiting for API to be ready..." -ForegroundColor Yellow
$apiReady = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5
        if ($response) {
            Write-Host "API ready at ${i}s: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
            $apiReady = $true
            break
        }
    } catch {
        if ($i % 5 -eq 0) {
            Write-Host "  Still waiting for API... (${i}s)" -ForegroundColor Gray
        }
    }
    Start-Sleep -Seconds 1
}

if (-not $apiReady) {
    Write-Host "API never became ready, but continuing monitoring..." -ForegroundColor Yellow
}

Write-Host ""

# Extended monitoring with multiple detection methods
Write-Host "Starting extended monitoring..." -ForegroundColor Yellow
$monitoringStart = Get-Date
$lastHeartbeat = $null

for ($elapsed = 0; $elapsed -lt $MonitorDuration; $elapsed += 5) {
    # Multiple process detection methods
    $directPID = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
    $nameFilter = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Id -eq $apiProcess.Id}
    $wmi = Get-WmiObject -Class Win32_Process -Filter "ProcessId=$($apiProcess.Id)" -ErrorAction SilentlyContinue
    
    # Check status file if available
    $statusFile = $null
    if (Test-Path "api_status.json") {
        try {
            $statusContent = Get-Content "api_status.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
            $statusFile = $statusContent
        } catch {
            $statusFile = "ERROR_READING_FILE"
        }
    }
    
    # Build status report
    $report = @{
        "ElapsedSeconds" = $elapsed
        "DirectPID" = if ($directPID) { "ALIVE" } else { "DEAD" }
        "NameFilter" = if ($nameFilter) { "ALIVE" } else { "DEAD" }
        "WMI" = if ($wmi) { "ALIVE" } else { "DEAD" }
        "StatusFile" = if ($statusFile) { 
            if ($statusFile -eq "ERROR_READING_FILE") { 
                "ERROR" 
            } else { 
                "PID:$($statusFile.pid) HB:$($statusFile.heartbeat)" 
            }
        } else { 
            "NO_FILE" 
        }
    }
    
    # Determine overall status
    $processAlive = $directPID -or $nameFilter -or $wmi
    $statusColor = if ($processAlive) { "Green" } else { "Red" }
    $statusText = if ($processAlive) { "ALIVE" } else { "DEAD" }
    
    Write-Host "${elapsed}s: $statusText - DirectPID:$($report.DirectPID) NameFilter:$($report.NameFilter) WMI:$($report.WMI) File:$($report.StatusFile)" -ForegroundColor $statusColor
    
    # If process appears dead according to all methods, this is the CI failure point
    if (-not $processAlive) {
        Write-Host "FAILURE DETECTED: Process appears dead to all detection methods!" -ForegroundColor Red
        Write-Host "This matches the CI failure: 'API process died before tests!'" -ForegroundColor Red
        
        # Try one more health check to see if API is actually still responding
        try {
            $finalResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5
            Write-Host "PARADOX: Process detection failed but API still responds: $($finalResponse | ConvertTo-Json)" -ForegroundColor Magenta
        } catch {
            Write-Host "Confirmed: API is not responding either" -ForegroundColor Red
        }
        
        break
    }
    
    # Periodic health checks
    if ($elapsed % 20 -eq 0 -and $elapsed -gt 0) {
        try {
            $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5
            Write-Host "  Health check OK at ${elapsed}s" -ForegroundColor Cyan
        } catch {
            Write-Host "  Health check FAILED at ${elapsed}s: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    Start-Sleep -Seconds 5
}

$totalDuration = (Get-Date) - $startTime
Write-Host ""
Write-Host "Monitoring completed after $($totalDuration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Cyan

# Final process check
$finalCheck = Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue
if ($finalCheck) {
    Write-Host "FINAL RESULT: SUCCESS - Process survived monitoring period" -ForegroundColor Green
} else {
    Write-Host "FINAL RESULT: FAILURE - Process was not detected at end" -ForegroundColor Red
}

# Clean shutdown
try {
    if (Get-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue) {
        Stop-Process -Id $apiProcess.Id -Force
        Write-Host "Process terminated" -ForegroundColor Gray
    }
} catch {
    Write-Host "Process cleanup completed" -ForegroundColor Gray
}