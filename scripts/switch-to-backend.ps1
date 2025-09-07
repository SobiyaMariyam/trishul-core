# Script to switch from mock APIs to real backend APIs
# Usage: .\scripts\switch-to-backend.ps1

Write-Host "🔄 Switching from mock APIs to real backend APIs..." -ForegroundColor Blue

$apiIndexFile = "src/api/index.ts"

if (-not (Test-Path $apiIndexFile)) {
    Write-Host "❌ Error: $apiIndexFile not found" -ForegroundColor Red
    exit 1
}

# Create backup
Copy-Item $apiIndexFile "$apiIndexFile.backup"
Write-Host "💾 Created backup: $apiIndexFile.backup" -ForegroundColor Green

# Read content
$content = Get-Content $apiIndexFile -Raw

# Switch imports to backend versions
$content = $content -replace 'import \{ kavachApi \} from "\./kavach"', 'import { kavachApi } from "./backend/kavach"'
$content = $content -replace 'import \{ rudraApi \} from "\./rudra"', 'import { rudraApi } from "./backend/rudra"'
$content = $content -replace 'import \{ trinetraApi \} from "\./trinetra"', 'import { trinetraApi } from "./backend/trinetra"'

# Write back
Set-Content $apiIndexFile $content

Write-Host "✅ API imports updated successfully!" -ForegroundColor Green
Write-Host "📁 Mock APIs: src/api/[module].ts" -ForegroundColor Yellow
Write-Host "📁 Real APIs: src/api/backend/[module].ts" -ForegroundColor Yellow
Write-Host ""
Write-Host "To revert: Move-Item $apiIndexFile.backup $apiIndexFile -Force" -ForegroundColor Cyan
