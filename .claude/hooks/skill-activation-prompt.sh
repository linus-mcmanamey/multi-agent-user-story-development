#!/bin/bash
set -e

# Get the script's directory (resolves symlinks)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to hooks directory
cd "$SCRIPT_DIR"

# Run TypeScript hook with npx tsx
cat | npx --yes tsx skill-activation-prompt.ts