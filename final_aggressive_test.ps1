# final_aggressive_test.ps1 - Ultimate aggressive persistence test
Write-Host "=== FINAL AGGRESSIVE PERSISTENCE TEST ===" -ForegroundColor Red
Write-Host "Testing the new MEGA-AGGRESSIVE multi-threaded persistence system"

# Set full CI environment like GitHub Actions
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me" 
$env:USE_INMEMORY_DB = "1"
$env:GITHUB_ACTIONS = "true"
$env:CI = "true"
$env:RUNNER_OS = "Windows"

Write-Host "Environment configured for maximum CI simulation" -ForegroundColor Yellow
Write-Host "Starting API with AGGRESSIVE persistence..."

# Clean up any existing files
Remove-Item "api_status.json" -Force -ErrorAction SilentlyContinue
Get-ChildItem "ci_activity_*.tmp" -Force -ErrorAction SilentlyContinue | Remove-Item -Force

$startTime = Get-Date
$apiJob = Start-Job -ScriptBlock {
    param($WorkingDir)
    Set-Location $WorkingDir
    
    $env:SECRET_KEY = "dev-secret-for-ci"
    $env:TENANT_DOMAIN = "tenant1.lvh.me" 
    $env:USE_INMEMORY_DB = "1"
    $env:GITHUB_ACTIONS = "true"
    $env:CI = "true"
    $env:RUNNER_OS = "Windows"
    
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info
} -ArgumentList (Get-Location)

# Wait for startup
Write-Host "Waiting for server startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check startup logs
$output = Receive-Job $apiJob -Keep
$aggressiveStarted = $false
$threadsCount = 0

$output | ForEach-Object {
    if ($_ -like "*AGGRESSIVE module-level persistence*") {
        Write-Host "AGGRESSIVE PERSISTENCE STARTED: $_" -ForegroundColor Green
        $aggressiveStarted = $true
    }
    if ($_ -like "*Started * aggressive persistence threads*") {
        Write-Host "THREAD COUNT: $_" -ForegroundColor Cyan
        if ($_ -match "Started (\d+) aggressive") {
            $threadsCount = [int]$matches[1]
        }
    }
    if ($_ -like "*[CI-DEBUG]*") {
        Write-Host "STARTUP DEBUG: $_" -ForegroundColor Cyan
    }
}

if (-not $aggressiveStarted) {
    Write-Host "ERROR: Aggressive persistence did not start!" -ForegroundColor Red
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Aggressive persistence started with $threadsCount threads" -ForegroundColor Green

# Test health endpoint
Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "Health check passed: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -ErrorAction SilentlyContinue
    exit 1
}

# Monitor for 90 seconds looking for all types of heartbeats
Write-Host "`nMonitoring AGGRESSIVE persistence activity for 90 seconds..." -ForegroundColor Yellow

$monitorEnd = (Get-Date).AddSeconds(90)
$cpuBurnerCount = 0
$networkKeepaliveCount = 0
$fileIoCount = 0
$megaHeartbeatCount = 0
$statusUpdates = 0

while ((Get-Date) -lt $monitorEnd) {
    # Check API job output
    $newOutput = Receive-Job $apiJob -Keep
    $newOutput | ForEach-Object {
        $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
        
        if ($_ -like "*AGGRESSIVE CPU burner active*") {
            $cpuBurnerCount++
            Write-Host "[$elapsed s] CPU BURNER: $_" -ForegroundColor Red
        }
        elseif ($_ -like "*Network keepalive*") {
            $networkKeepaliveCount++
            Write-Host "[$elapsed s] NETWORK: $_" -ForegroundColor Blue
        }
        elseif ($_ -like "*File I/O keepalive*") {
            $fileIoCount++
            Write-Host "[$elapsed s] FILE I/O: $_" -ForegroundColor Magenta
        }
        elseif ($_ -like "*MEGA-PERSISTENT heartbeat*") {
            $megaHeartbeatCount++
            Write-Host "[$elapsed s] MEGA-HEARTBEAT: $_" -ForegroundColor Green
        }
    }
    
    # Check status file
    if (Test-Path "api_status.json") {
        try {
            $status = Get-Content "api_status.json" -Raw | ConvertFrom-Json
            if ($status.heartbeat -gt $statusUpdates) {
                $statusUpdates = $status.heartbeat
                $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)
                Write-Host "[$elapsed s] STATUS UPDATE: Heartbeat #$($status.heartbeat), Threads: $($status.active_threads)" -ForegroundColor Yellow
            }
        } catch {}
    }
    
    Start-Sleep -Seconds 2
}

$totalTime = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 1)

Write-Host "`n=== FINAL AGGRESSIVE TEST RESULTS ===" -ForegroundColor Red
Write-Host "Total Test Time: $totalTime seconds"
Write-Host "CPU Burner Activities: $cpuBurnerCount"
Write-Host "Network Keepalive Activities: $networkKeepaliveCount"
Write-Host "File I/O Activities: $fileIoCount"
Write-Host "MEGA-Heartbeats: $megaHeartbeatCount"
Write-Host "Status File Updates: $statusUpdates"

# Check if API process is still alive
$apiProcess = Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*" } | Select-Object -First 1
if ($apiProcess) {
    Write-Host "`nSUCCESS: API process $($apiProcess.Id) is STILL ALIVE after $totalTime seconds!" -ForegroundColor Green
} else {
    Write-Host "`nFAILURE: API process died during test!" -ForegroundColor Red
}

# Check final status
if (Test-Path "api_status.json") {
    try {
        $finalStatus = Get-Content "api_status.json" -Raw | ConvertFrom-Json
        Write-Host "Final Status: $($finalStatus.status)" -ForegroundColor Green
        Write-Host "Final PID: $($finalStatus.pid)" -ForegroundColor Green
        Write-Host "CI Mode: $($finalStatus.ci_mode)" -ForegroundColor Green
    } catch {
        Write-Host "Could not read final status: $_" -ForegroundColor Yellow
    }
}

# Overall assessment
$totalActivity = $cpuBurnerCount + $networkKeepaliveCount + $fileIoCount + $megaHeartbeatCount
if ($totalActivity -ge 10 -and $apiProcess) {
    Write-Host "`nFINAL VERDICT: ULTIMATE SUCCESS!" -ForegroundColor Green
    Write-Host "The AGGRESSIVE persistence system is working perfectly!" -ForegroundColor Green
    Write-Host "GitHub Actions 'API process died before tests!' should be COMPLETELY RESOLVED!" -ForegroundColor Green
} else {
    Write-Host "`nFINAL VERDICT: Still having issues" -ForegroundColor Red
    Write-Host "Total Activities: $totalActivity (should be >= 10)" -ForegroundColor Yellow
    Write-Host "Process Alive: $($apiProcess -ne $null)" -ForegroundColor Yellow
}

# Cleanup
Write-Host "`nCleaning up..."
Stop-Job $apiJob -ErrorAction SilentlyContinue
Remove-Job $apiJob -ErrorAction SilentlyContinue

# Kill any remaining python processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "FINAL AGGRESSIVE TEST COMPLETED!" -ForegroundColor Red