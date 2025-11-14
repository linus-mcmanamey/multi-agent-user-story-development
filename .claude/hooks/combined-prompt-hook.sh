#!/bin/bash
set -e

# Combined hook that chains skill-activation and orchestrator-interceptor
# This ensures both hooks run on user prompt submit

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read stdin once and store it
INPUT=$(cat)

# Run skill activation hook first
SKILL_OUTPUT=$(echo "$INPUT" | bash "$SCRIPT_DIR/skill-activation-prompt.sh" 2>&1 || true)

# Run orchestrator interceptor hook
ORCHESTRATOR_OUTPUT=$(echo "$INPUT" | python3 "$SCRIPT_DIR/orchestrator_interceptor.py" 2>&1)

# Parse JSON from orchestrator
ORCHESTRATOR_CONTEXT=$(echo "$ORCHESTRATOR_OUTPUT" | jq -r '.hookSpecificOutput.additionalContext // ""' 2>/dev/null || echo "")

# Combine outputs
# If skill output exists (not empty), prepend it to orchestrator context
if [ -n "$SKILL_OUTPUT" ]; then
    COMBINED_CONTEXT="$SKILL_OUTPUT

$ORCHESTRATOR_CONTEXT"
else
    COMBINED_CONTEXT="$ORCHESTRATOR_CONTEXT"
fi

# Return JSON with combined context
jq -n \
  --arg context "$COMBINED_CONTEXT" \
  '{
    "hookSpecificOutput": {
      "hookEventName": "UserPromptSubmit",
      "additionalContext": $context
    }
  }'

exit 0
