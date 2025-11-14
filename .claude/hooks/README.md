# Orchestrator Hook Installation Guide

## Overview

This hook system automatically intercepts every user prompt in Claude Code and routes complex tasks through the master orchestrator agent for intelligent task decomposition and parallel execution.

## Features

✅ **Automatic Complexity Analysis** - Every prompt is analyzed for complexity
✅ **Cost Estimation** - Upfront token and cost estimates before execution
✅ **Smart Routing** - Simple queries skip orchestration, complex tasks use multi-agent
✅ **Comprehensive Logging** - All decisions logged to `~/.claude/hook_logs/`
✅ **User Approval Workflow** - Presents execution plan before proceeding
✅ **Skill Integration** - Chains with existing skill-activation hook

## Installation Status

✅ **INSTALLED AND ACTIVE**

### Components

1. **Orchestrator Interceptor** (`~/.claude/hooks/orchestrator_interceptor.py`)
   - Python script with loguru logging
   - Analyzes prompt complexity
   - Generates cost estimates
   - Injects orchestrator invocation context

2. **Combined Hook Wrapper** (`~/.claude/hooks/combined-prompt-hook.sh`)
   - Chains skill-activation with orchestrator-interceptor
   - Combines outputs from both hooks
   - Ensures seamless integration

3. **Settings Configuration** (`~/.claude/settings.json`)
   - Configured to use combined-prompt-hook.sh
   - Runs on every user-prompt-submit event

4. **Enhanced Orchestrator Agent** (`.claude/agents/orchestrator.md`)
   - Updated with cost estimation workflow
   - Includes token usage tracking in reports

## How It Works

### Flow Diagram

```
┌─────────────────────────────────────────┐
│ USER TYPES PROMPT                       │
│ "Fix linting across all layers"        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ HOOK FIRES (user-prompt-submit)        │
│ • Skill activation check                │
│ • Orchestrator complexity analysis      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ CLASSIFICATION                          │
│ • Simple Query → Skip orchestration     │
│ • Complex Task → Inject orchestrator    │
│ • Cross-layer → High complexity         │
│ • Broad scope → Complex task            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ CONTEXT INJECTION                       │
│ • Instructions to launch orchestrator   │
│ • Cost estimates                        │
│ • Complexity classification             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ CLAUDE LAUNCHES ORCHESTRATOR            │
│ • Analyzes task                         │
│ • Determines strategy                   │
│ • Presents execution plan               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ USER APPROVES                           │
│ [1] Execute Plan                        │
│ [2] Modify Plan                         │
│ [3] Skip Orchestration                  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ EXECUTION & REPORTING                   │
│ • Multi-agent coordination (if needed)  │
│ • Consolidated JSON results             │
│ • Cost tracking                         │
└─────────────────────────────────────────┘
```

### Classification Rules

#### Simple Query (No Orchestration)
- Starts with: "what is", "explain", "how do", "why does", "show me"
- Word count < 20
- **Action**: Handle directly without overhead

#### Moderate Task (Evaluate)
- Implementation/feature requests
- Single-layer work
- 4-8 files affected
- **Action**: Single agent or 2-3 parallel agents

#### High Complexity (Multi-Agent Orchestration)
- Cross-layer work (2+ layers mentioned)
- Broad scope ("all", "across", "entire", "multiple")
- Code quality sweeps ("linting", "formatting" + scope keywords)
- Multi-component work
- **Action**: 4-8 parallel agents with orchestrator coordination

### Cost Estimation

The hook provides upfront cost estimates based on Claude Sonnet pricing:
- Input: $3 per million tokens
- Output: $15 per million tokens

**Complexity Levels:**
- **Simple Query**: ~500 tokens, $0.002
- **Moderate Task**: ~6,000 tokens, $0.018
- **Complex Task**: ~17,000 tokens, $0.051
- **High Complexity**: ~43,000 tokens, $0.129

## Monitoring & Logs

### View Logs

```bash
# Tail logs in real-time
tail -f ~/.claude/hook_logs/orchestrator_hook.log

# View recent entries
tail -50 ~/.claude/hook_logs/orchestrator_hook.log

# Search for specific prompts
grep "Classified as" ~/.claude/hook_logs/orchestrator_hook.log

# View cost estimates
grep "Cost estimate" ~/.claude/hook_logs/orchestrator_hook.log
```

### Log Format

```
2025-11-10 23:00:44 | INFO     | ================================================================================
2025-11-10 23:00:44 | INFO     | Hook triggered - Session: test-2
2025-11-10 23:00:44 | INFO     | CWD: /workspaces/test
2025-11-10 23:00:44 | INFO     | Prompt: Fix all linting errors across bronze, silver, and gold layers
2025-11-10 23:00:44 | INFO     | Classified as CROSS-LAYER WORK (3 layers): Fix all linting errors...
2025-11-10 23:00:44 | INFO     | Decision: ORCHESTRATE
2025-11-10 23:00:44 | INFO     | Reason: cross_layer_work
2025-11-10 23:00:44 | INFO     | Complexity: high_complexity
2025-11-10 23:00:44 | INFO     | Cost estimate: $0.129 USD (~43,000 tokens)
2025-11-10 23:00:44 | INFO     | Hook completed successfully
2025-11-10 23:00:44 | INFO     | ================================================================================
```

### Log Rotation

- **Rotation**: Automatically rotates at 10 MB
- **Retention**: Keeps 30 days of logs
- **Location**: `~/.claude/hook_logs/orchestrator_hook.log`

## Testing

### Manual Test

```bash
# Test simple query
echo '{"session_id":"test","transcript_path":"","cwd":"/workspaces","permission_mode":"standard","hook_event_name":"UserPromptSubmit","prompt":"What is PySpark?"}' | python3 ~/.claude/hooks/orchestrator_interceptor.py | jq

# Test complex task
echo '{"session_id":"test","transcript_path":"","cwd":"/workspaces","permission_mode":"standard","hook_event_name":"UserPromptSubmit","prompt":"Fix linting across all bronze, silver, and gold layers"}' | python3 ~/.claude/hooks/orchestrator_interceptor.py | jq -r '.hookSpecificOutput.additionalContext'
```

### Expected Behavior

When you type a prompt in Claude Code:

1. **Simple Query** ("What is TableUtilities?")
   - Hook detects simple query
   - No orchestrator invocation
   - Claude responds directly
   - Logged as: `Decision: SKIP`

2. **Complex Task** ("Fix linting across all layers")
   - Hook detects complexity
   - Injects orchestrator instructions
   - Claude launches orchestrator
   - Presents execution plan
   - Waits for your approval
   - Logged as: `Decision: ORCHESTRATE`

## Configuration

### Adjust Classification Rules

Edit `~/.claude/hooks/orchestrator_interceptor.py`:

```python
# Add new simple patterns
simple_patterns = ["what is", "explain", "how do", "why does", "show me", "what does", "define"]

# Add new broad scope keywords
broad_keywords = ["all", "across", "entire", "multiple", "every"]

# Add new quality keywords
quality_keywords = ["linting", "formatting", "type hints", "quality", "refactor", "optimize"]
```

### Disable Hook Temporarily

```bash
# Comment out in settings.json
# "hooks": {
#   "user-prompt-submit": ".claude/hooks/combined-prompt-hook.sh"
# }
```

Or set environment variable:
```bash
export CLAUDE_DISABLE_HOOKS=1
```

### Bypass for Single Prompt

Add to your prompt:
```
@skip-orchestration <your prompt here>
```

(Note: This requires adding bypass logic to the hook script)

## Troubleshooting

### Hook Not Running

1. **Check settings.json**:
   ```bash
   cat ~/.claude/settings.json | grep -A 2 hooks
   ```

2. **Verify script is executable**:
   ```bash
   ls -l ~/.claude/hooks/*.{sh,py}
   ```

3. **Test hook directly**:
   ```bash
   echo '{"prompt":"test"}' | python3 ~/.claude/hooks/orchestrator_interceptor.py
   ```

4. **Check logs for errors**:
   ```bash
   tail -50 ~/.claude/hook_logs/orchestrator_hook.log | grep ERROR
   ```

5. **Restart Claude Code** (settings changes require restart)

### Dependencies Missing

```bash
# Verify loguru is installed
python3 -c "import loguru; print(f'loguru {loguru.__version__} installed')"

# Install if missing
pip install loguru

# Verify jq is available (for combined hook)
which jq || sudo apt-get install -y jq
```

### Hook Errors Not Blocking

The hook is designed to fail gracefully. If errors occur:
- Prompt is allowed through unchanged
- Error logged to `orchestrator_hook.log`
- Claude responds normally without orchestration

## Advanced Usage

### Custom Cost Estimates

Edit token estimates in `orchestrator_interceptor.py`:

```python
token_estimates = {
    "simple_query": {
        "orchestrator_analysis": 500,
        "agent_execution": 0,
        "total_estimated": 500,
        "cost_usd": 0.0015
    },
    # ... adjust as needed
}
```

### Add New Complexity Patterns

```python
def should_orchestrate(prompt: str) -> tuple[bool, str, str]:
    # Add your custom logic
    if "custom_pattern" in prompt_lower:
        return True, "custom_reason", "complexity_level"
```

### Integration with Other Tools

The hook can be extended to:
- Send Slack notifications for high-complexity tasks
- Log to external monitoring systems
- Query project metadata for better classification
- Integrate with time tracking tools

## Files Reference

```
~/.claude/
├── hooks/
│   ├── orchestrator_interceptor.py      # Main hook logic (Python + loguru)
│   ├── combined-prompt-hook.sh          # Wrapper to chain hooks
│   ├── skill-activation-prompt.sh       # Existing skill hook
│   ├── skill-activation-prompt.ts       # Skill TypeScript logic
│   ├── test_hook.sh                     # Test script
│   └── README.md                        # This file
├── hook_logs/
│   └── orchestrator_hook.log            # Rotating log file
└── settings.json                        # Claude Code settings

/workspaces/unify_2_1_dm_niche_rms_build_d10/.claude/
└── agents/
    └── orchestrator.md                  # Enhanced with cost estimation
```

## Next Steps

### Enhance Detection Logic

Consider adding:
- Machine learning-based complexity prediction
- Historical execution time tracking
- Project-specific patterns
- User feedback loop to improve classification

### Add Analytics

Track metrics:
- Classification accuracy
- Cost estimate variance
- User approval rate
- Time savings from orchestration

### Improve User Experience

Features to add:
- Interactive complexity adjustment
- Cost budgets and alerts
- Execution history and patterns
- Orchestration templates

## Support

For issues or questions:
1. Check logs: `~/.claude/hook_logs/orchestrator_hook.log`
2. Review this README
3. Test hook manually (see Testing section)
4. Verify dependencies (Python, loguru, jq)

---

**Status**: ✅ Active and operational
**Last Updated**: 2025-11-10
**Version**: 1.0.0
