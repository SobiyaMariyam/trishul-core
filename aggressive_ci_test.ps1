# aggressive_ci_test.ps1 - Test the new aggressive module-level persistence
param(
    [int]$TestDuration = 60  # Test duration in seconds
)

Write-Host "=== AGGRESSIVE CI PERSISTENCE TEST ===" -ForegroundColor Green
Write-Host "Testing the enhanced module-level persistence with aggressive CI mode"

# Set CI-like environment
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me" 
$env:USE_INMEMORY_DB = "1"
$env:GITHUB_ACTIONS = "true"  # Simulate GitHub Actions
$env:CI = "true"  # Also set CI flag

# Clean up any existing status files
Remove-Item "api_status.json" -Force -ErrorAction SilentlyContinue
Remove-Item "heartbeat.tmp" -Force -ErrorAction SilentlyContinue

Write-Host "Starting API server with aggressive CI settings..."
$apiJob = Start-Job -ScriptBlock {
    param($WorkingDir)
    Set-Location $WorkingDir
    
    $env:SECRET_KEY = "dev-secret-for-ci"
    $env:TENANT_DOMAIN = "tenant1.lvh.me" 
    $env:USE_INMEMORY_DB = "1"
    $env:GITHUB_ACTIONS = "true"
    $env:CI = "true"
    
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info
} -ArgumentList (Get-Location)

# Wait a moment for server to start
Start-Sleep -Seconds 5

Write-Host "Checking server startup..."

# Check if server is responding
$healthCheck = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $healthCheck = $true
            Write-Host "Health check successful on attempt $i" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "Health check failed on attempt $i, retrying..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $healthCheck) {
    Write-Host "ERROR: API server failed to start or respond to health checks!" -ForegroundColor Red
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -ErrorAction SilentlyContinue
    exit 1
}

# Get API process ID
$apiProcess = Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*" } | Select-Object -First 1

if (-not $apiProcess) {
    Write-Host "WARNING: Could not identify API process ID via process list" -ForegroundColor Yellow
    $apiPid = "unknown"
} else {
    $apiPid = $apiProcess.Id
    Write-Host "API Process ID identified: $apiPid" -ForegroundColor Cyan
}

Write-Host "`nStarting aggressive persistence monitoring for $TestDuration seconds..." -ForegroundColor Green
Write-Host "Looking for module-level heartbeats every 6 seconds (CI mode)..."

$startTime = Get-Date
$endTime = $startTime.AddSeconds($TestDuration)
$heartbeatCount = 0
$statusFileUpdates = 0

while ((Get-Date) -lt $endTime) {
    # Check if API process is still running
    if ($apiPid -ne "unknown") {
        $processStillRunning = Get-Process -Id $apiPid -ErrorAction SilentlyContinue
        if (-not $processStillRunning) {
            Write-Host "CRITICAL ERROR: API process $apiPid has died!" -ForegroundColor Red
            break
        }
    }
    
    # Check for status file updates
    if (Test-Path "api_status.json") {
        try {
            $statusContent = Get-Content "api_status.json" -Raw | ConvertFrom-Json
            if ($statusContent.heartbeat -gt $heartbeatCount) {
                $heartbeatCount = $statusContent.heartbeat
                $statusFileUpdates++
                $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                Write-Host "[$elapsed s] STATUS FILE UPDATE #$statusFileUpdates - Heartbeat #$heartbeatCount from PID $($statusContent.pid)" -ForegroundColor Green
                
                if ($statusContent.ci_mode -eq $true) {
                    Write-Host "  -> CI mode confirmed active, sleep interval: $($statusContent.sleep_interval)s" -ForegroundColor Cyan
                } else {
                    Write-Host "  -> WARNING: CI mode not detected in status" -ForegroundColor Yellow
                }
            }
        }
        catch {
            Write-Host "Could not read status file: $_" -ForegroundColor Yellow
        }
    }
    
    # Check API job output for heartbeat messages
    $output = Receive-Job $apiJob -Keep
    if ($output) {
        $output | ForEach-Object {
            if ($_ -like "*Module persistence heartbeat*") {
                $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                Write-Host "[$elapsed s] CONSOLE HEARTBEAT: $_" -ForegroundColor Green
            }
            elseif ($_ -like "*[CI-DEBUG]*") {
                $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                Write-Host "[$elapsed s] CI-DEBUG: $_" -ForegroundColor Cyan
            }
        }
    }
    
    Start-Sleep -Seconds 2
}

$elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
Write-Host "`n=== AGGRESSIVE PERSISTENCE TEST RESULTS ===" -ForegroundColor Green
Write-Host "Test Duration: $elapsed seconds"
Write-Host "Status File Updates: $statusFileUpdates"
Write-Host "Final Heartbeat Count: $heartbeatCount"

# Final process check
if ($apiPid -ne "unknown") {
    $finalProcessCheck = Get-Process -Id $apiPid -ErrorAction SilentlyContinue
    if ($finalProcessCheck) {
        Write-Host "SUCCESS: API process $apiPid is still alive!" -ForegroundColor Green
    } else {
        Write-Host "FAILURE: API process $apiPid died during test!" -ForegroundColor Red
    }
} else {
    Write-Host "Process check: Unable to verify (PID unknown)" -ForegroundColor Yellow
}

# Check final status file
if (Test-Path "api_status.json") {
    try {
        $finalStatus = Get-Content "api_status.json" -Raw | ConvertFrom-Json
        Write-Host "Final Status: $($finalStatus.status) at $($finalStatus.timestamp)" -ForegroundColor Green
        Write-Host "Final PID: $($finalStatus.pid)" -ForegroundColor Green
        if ($finalStatus.ci_mode) {
            Write-Host "CI mode was correctly detected and activated" -ForegroundColor Green
        } else {
            Write-Host "WARNING: CI mode was not detected" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Could not read final status: $_" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: No status file found!" -ForegroundColor Red
}

# Cleanup
Write-Host "`nCleaning up..."
Stop-Job $apiJob -ErrorAction SilentlyContinue
Remove-Job $apiJob -ErrorAction SilentlyContinue

# Kill any remaining python processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Id -eq $apiPid } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Aggressive CI test completed!" -ForegroundColor Green

# Overall assessment
if ($statusFileUpdates -gt 0 -and $heartbeatCount -gt 0) {
    Write-Host "`nOVERALL ASSESSMENT: SUCCESS - Aggressive persistence is working!" -ForegroundColor Green
} elseif ($statusFileUpdates -eq 0 -and $heartbeatCount -eq 0) {
    Write-Host "`nOVERALL ASSESSMENT: FAILURE - No persistence activity detected!" -ForegroundColor Red
} else {
    Write-Host "`nOVERALL ASSESSMENT: PARTIAL - Some activity but not optimal" -ForegroundColor Yellow
}