#!/bin/bash

# Script to switch from mock APIs to real backend APIs
# Usage: ./scripts/switch-to-backend.sh

echo "🔄 Switching from mock APIs to real backend APIs..."

API_INDEX_FILE="src/api/index.ts"

if [ ! -f "$API_INDEX_FILE" ]; then
    echo "❌ Error: $API_INDEX_FILE not found"
    exit 1
fi

# Create backup
cp "$API_INDEX_FILE" "$API_INDEX_FILE.backup"
echo "💾 Created backup: $API_INDEX_FILE.backup"

# Switch imports to backend versions
sed -i.tmp 's|import { kavachApi } from "./kavach"|import { kavachApi } from "./backend/kavach"|g' "$API_INDEX_FILE"
sed -i.tmp 's|import { rudraApi } from "./rudra"|import { rudraApi } from "./backend/rudra"|g' "$API_INDEX_FILE"
sed -i.tmp 's|import { trinetraApi } from "./trinetra"|import { trinetraApi } from "./backend/trinetra"|g' "$API_INDEX_FILE"

# Clean up temp files
rm -f "$API_INDEX_FILE.tmp"

echo "✅ API imports updated successfully!"
echo "📁 Mock APIs: src/api/[module].ts"
echo "📁 Real APIs: src/api/backend/[module].ts"
echo ""
echo "To revert: mv $API_INDEX_FILE.backup $API_INDEX_FILE"

# Show the changes
echo "📋 Changes made:"
diff "$API_INDEX_FILE.backup" "$API_INDEX_FILE" || true
