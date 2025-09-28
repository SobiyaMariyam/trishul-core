# graduated_persistence_test.ps1
Write-Host "=== GRADUATED PERSISTENCE TEST ===" -ForegroundColor Green
Write-Host "Testing the new graduated persistence approach that starts light and ramps up"

# Set CI environment 
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me" 
$env:USE_INMEMORY_DB = "1"
$env:GITHUB_ACTIONS = "true"
$env:CI = "true"
$env:RUNNER_OS = "Windows"

Write-Host "Starting API with graduated persistence..."
$sw = [System.Diagnostics.Stopwatch]::StartNew()

# Start API
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
Start-Sleep -Seconds 3

Write-Host "Elapsed: $($sw.Elapsed.TotalSeconds)s - Checking for startup messages..."

# Check startup output
$output = Receive-Job $apiJob -Keep
$fastapiStarted = $false
$lightModeFound = $false
$aggressiveModeFound = $false

$output | ForEach-Object {
    if ($_ -like "*FastAPI app created*") {
        Write-Host "✅ FASTAPI STARTUP: $_" -ForegroundColor Green
        $fastapiStarted = $true
    }
    if ($_ -like "*Light CPU activity during startup*") {
        Write-Host "✅ LIGHT MODE: $_" -ForegroundColor Cyan
        $lightModeFound = $true
    }
    if ($_ -like "*AGGRESSIVE CPU burner active*") {
        Write-Host "✅ AGGRESSIVE MODE: $_" -ForegroundColor Yellow
        $aggressiveModeFound = $true
    }
    if ($_ -like "*INFO:*Started server*") {
        Write-Host "✅ UVICORN STARTED: $_" -ForegroundColor Green
    }
    if ($_ -like "*INFO:*Application startup complete*") {
        Write-Host "✅ APP STARTUP COMPLETE: $_" -ForegroundColor Green
    }
}

# Wait a bit more for the transition to aggressive mode
Write-Host "`nElapsed: $($sw.Elapsed.TotalSeconds)s - Waiting for aggressive mode transition..."
Start-Sleep -Seconds 5

$output2 = Receive-Job $apiJob -Keep
$output2 | ForEach-Object {
    if ($_ -like "*AGGRESSIVE CPU burner active*") {
        Write-Host "✅ AGGRESSIVE MODE ACTIVATED: $_" -ForegroundColor Yellow
        $aggressiveModeFound = $true
    }
}

# Test health endpoint
Write-Host "`nElapsed: $($sw.Elapsed.TotalSeconds)s - Testing health endpoint..."
$healthWorking = $false

for ($i = 1; $i -le 3; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Headers @{Host="tenant1.lvh.me"} -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health check $i passed: $($response.StatusCode) - $($response.Content)" -ForegroundColor Green
            $healthWorking = $true
            break
        }
    }
    catch {
        Write-Host "❌ Health check $i failed: $_" -ForegroundColor Red
        Start-Sleep -Seconds 2
    }
}

Write-Host "`n=== GRADUATED PERSISTENCE RESULTS ==="
Write-Host "FastAPI Started: $fastapiStarted" -ForegroundColor $(if($fastapiStarted) {'Green'} else {'Red'})
Write-Host "Light Mode Found: $lightModeFound" -ForegroundColor $(if($lightModeFound) {'Green'} else {'Yellow'})
Write-Host "Aggressive Mode Found: $aggressiveModeFound" -ForegroundColor $(if($aggressiveModeFound) {'Green'} else {'Yellow'})
Write-Host "Health Endpoint Working: $healthWorking" -ForegroundColor $(if($healthWorking) {'Green'} else {'Red'})

if ($fastapiStarted -and $healthWorking) {
    Write-Host "`n🎉 SUCCESS: Graduated persistence allows FastAPI to start properly!" -ForegroundColor Green
    Write-Host "The GitHub Actions CI issue should be RESOLVED with this approach." -ForegroundColor Green
} else {
    Write-Host "`n❌ FAILURE: FastAPI still not starting properly" -ForegroundColor Red
}

# Cleanup
Stop-Job $apiJob -ErrorAction SilentlyContinue
Remove-Job $apiJob -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "`nGraduated persistence test completed!" -ForegroundColor Green