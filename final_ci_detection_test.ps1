# final_ci_detection_test.ps1
Write-Host "=== FINAL CI DETECTION TEST ===" -ForegroundColor Green

# Set all possible CI environment variables that GitHub Actions would have
$env:SECRET_KEY = "dev-secret-for-ci"
$env:TENANT_DOMAIN = "tenant1.lvh.me" 
$env:USE_INMEMORY_DB = "1"
$env:GITHUB_ACTIONS = "true"
$env:CI = "true"
$env:RUNNER_OS = "Windows"

Write-Host "Environment variables set to simulate GitHub Actions:"
Write-Host "  GITHUB_ACTIONS = $env:GITHUB_ACTIONS" -ForegroundColor Cyan
Write-Host "  CI = $env:CI" -ForegroundColor Cyan
Write-Host "  RUNNER_OS = $env:RUNNER_OS" -ForegroundColor Cyan

# Create a temporary directory that simulates GitHub Actions structure
$tempDir = "D:\a\trishul-core\trishul-core"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

# Copy necessary files to the temp directory
Copy-Item "app" -Destination $tempDir -Recurse -Force
Copy-Item "requirements.txt" -Destination $tempDir -Force -ErrorAction SilentlyContinue
Copy-Item "pyproject.toml" -Destination $tempDir -Force -ErrorAction SilentlyContinue

Write-Host "`nChanging to simulated GitHub Actions directory: $tempDir"
Set-Location $tempDir

Write-Host "Current directory: $(Get-Location)"
Write-Host "Python executable: $((Get-Command python).Source)"

Write-Host "`nStarting API with enhanced CI detection..."

# Start API with all CI simulation
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
} -ArgumentList $tempDir

# Wait for startup
Start-Sleep -Seconds 8

# Check for CI detection in the output
Write-Host "`nChecking for CI detection messages..."
$output = Receive-Job $apiJob -Keep

$ciDetectionFound = $false
$heartbeatFound = $false

$output | ForEach-Object {
    if ($_ -like "*CI Detection:*") {
        Write-Host "CI DETECTION MESSAGE: $_" -ForegroundColor Green
        $ciDetectionFound = $true
    }
    if ($_ -like "*Module persistence heartbeat*") {
        Write-Host "HEARTBEAT DETECTED: $_" -ForegroundColor Green
        $heartbeatFound = $true
    }
    if ($_ -like "*[CI-DEBUG]*") {
        Write-Host "DEBUG: $_" -ForegroundColor Cyan
    }
}

# Wait a bit more to see if heartbeats appear
Write-Host "`nWaiting for heartbeats..."
Start-Sleep -Seconds 10

$output2 = Receive-Job $apiJob -Keep
$output2 | ForEach-Object {
    if ($_ -like "*Module persistence heartbeat*") {
        Write-Host "HEARTBEAT DETECTED: $_" -ForegroundColor Green
        $heartbeatFound = $true
    }
    if ($_ -like "*CI Detection:*") {
        Write-Host "CI DETECTION MESSAGE: $_" -ForegroundColor Green
        $ciDetectionFound = $true
    }
}

Write-Host "`n=== RESULTS ==="
Write-Host "CI Detection Message Found: $ciDetectionFound" -ForegroundColor $(if($ciDetectionFound) {'Green'} else {'Red'})
Write-Host "Heartbeat Found: $heartbeatFound" -ForegroundColor $(if($heartbeatFound) {'Green'} else {'Red'})

if ($ciDetectionFound -and $heartbeatFound) {
    Write-Host "`nSUCCESS: CI detection is working and generating heartbeats!" -ForegroundColor Green
    Write-Host "The GitHub Actions 'API process died before tests!' issue should be RESOLVED" -ForegroundColor Green
} else {
    Write-Host "`nISSUE: Something is still not working correctly" -ForegroundColor Yellow
}

# Cleanup
Stop-Job $apiJob -ErrorAction SilentlyContinue
Remove-Job $apiJob -ErrorAction SilentlyContinue

# Return to original directory
Set-Location "D:\trishul-core"

# Clean up temp directory
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nFinal CI detection test completed!" -ForegroundColor Green