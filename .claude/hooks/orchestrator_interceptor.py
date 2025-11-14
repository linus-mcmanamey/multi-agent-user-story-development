#!/usr/bin/env python3
"""
Orchestrator Interceptor Hook for Claude Code
Analyzes user prompts and injects orchestrator invocation context for complex tasks.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Configure loguru
log_dir = Path.home() / ".claude" / "hook_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "orchestrator_hook.log"

logger.remove()
logger.add(
    log_file,
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="INFO"
)
logger.add(sys.stderr, level="ERROR")


def estimate_complexity_tokens(prompt: str, complexity: str) -> dict[str, int]:
    """Estimate token usage based on complexity assessment."""
    base_prompt_tokens = len(prompt.split()) * 1.3
    token_estimates = {
        "simple_query": {
            "orchestrator_analysis": 500,
            "agent_execution": 0,
            "total_estimated": 500,
            "cost_usd": 0.0015
        },
        "moderate_task": {
            "orchestrator_analysis": 1000,
            "agent_execution": 5000,
            "total_estimated": 6000,
            "cost_usd": 0.018
        },
        "complex_task": {
            "orchestrator_analysis": 2000,
            "agent_execution": 15000,
            "total_estimated": 17000,
            "cost_usd": 0.051
        },
        "high_complexity": {
            "orchestrator_analysis": 3000,
            "agent_execution": 40000,
            "total_estimated": 43000,
            "cost_usd": 0.129
        }
    }
    return token_estimates.get(complexity, token_estimates["moderate_task"])


def should_orchestrate(prompt: str) -> tuple[bool, str, str]:
    """
    Determine if prompt needs orchestration.
    Returns: (needs_orchestration, reason, complexity_level)
    """
    prompt_lower = prompt.lower()
    word_count = len(prompt.split())

    # 1. Simple queries (skip orchestration)
    simple_patterns = ["what is", "explain", "how do", "why does", "show me", "what does", "define"]
    if any(pattern in prompt_lower for pattern in simple_patterns) and word_count < 20:
        logger.info(f"Classified as SIMPLE QUERY: {prompt[:100]}")
        return False, "simple_query", "simple_query"

    # 2. Explicit orchestration requests
    if "orchestrate" in prompt_lower or "@orchestrate" in prompt_lower:
        logger.info(f"Classified as EXPLICIT ORCHESTRATION REQUEST: {prompt[:100]}")
        return True, "explicit_request", "high_complexity"

    # 3. Cross-layer work (likely needs orchestration)
    layers_mentioned = sum(1 for layer in ["bronze", "silver", "gold"] if layer in prompt_lower)
    if layers_mentioned >= 2:
        logger.info(f"Classified as CROSS-LAYER WORK ({layers_mentioned} layers): {prompt[:100]}")
        return True, "cross_layer_work", "high_complexity"

    # 4. Broad scope indicators
    broad_keywords = ["all", "across", "entire", "multiple", "every"]
    if any(keyword in prompt_lower for keyword in broad_keywords):
        logger.info(f"Classified as BROAD SCOPE: {prompt[:100]}")
        return True, "broad_scope", "complex_task"

    # 5. Code quality sweeps
    quality_keywords = ["linting", "formatting", "type hints", "quality", "refactor", "optimize"]
    scope_keywords = ["all", "entire", "project", "codebase"]
    if any(q in prompt_lower for q in quality_keywords) and any(s in prompt_lower for s in scope_keywords):
        logger.info(f"Classified as QUALITY SWEEP: {prompt[:100]}")
        return True, "quality_sweep", "high_complexity"

    # 6. Multiple file/component work
    if any(keyword in prompt_lower for keyword in ["files", "tables", "classes", "modules", "components"]):
        if any(number in prompt for number in ["all", "multiple", "several", "many"]):
            logger.info(f"Classified as MULTI-COMPONENT WORK: {prompt[:100]}")
            return True, "multi_component", "complex_task"

    # 7. Implementation/feature requests (moderate complexity)
    action_keywords = ["implement", "create", "build", "add", "fix", "update", "modify"]
    if any(action in prompt_lower for action in action_keywords) and word_count > 10:
        logger.info(f"Classified as MODERATE TASK: {prompt[:100]}")
        return True, "implementation_task", "moderate_task"

    # 8. Default to simple handling for very short prompts
    if word_count < 5:
        logger.info(f"Classified as SIMPLE (too short): {prompt[:100]}")
        return False, "too_short", "simple_query"

    # Default: moderate orchestration for safety
    logger.info(f"Classified as DEFAULT MODERATE: {prompt[:100]}")
    return True, "default_moderate", "moderate_task"


def generate_orchestrator_context(prompt: str, reason: str, complexity: str) -> str:
    """Generate the context to inject for orchestrator analysis."""
    cost_estimate = estimate_complexity_tokens(prompt, complexity)

    context = f"""
<orchestrator-analysis-required>
ORCHESTRATOR INTERCEPTION ACTIVE

BEFORE responding to the user, you MUST:

1. Launch the master-orchestrator agent using the Task tool with subagent_type="master-orchestrator"

2. Pass this user prompt to the orchestrator for complexity analysis:
   USER PROMPT: "{prompt}"

3. Classification hint: {reason.replace('_', ' ').title()}
   Estimated complexity: {complexity.replace('_', ' ').title()}

4. COST ESTIMATION (based on initial classification):
   - Orchestrator analysis: ~{cost_estimate['orchestrator_analysis']:,} tokens
   - Estimated agent execution: ~{cost_estimate['agent_execution']:,} tokens
   - Total estimated: ~{cost_estimate['total_estimated']:,} tokens
   - Approximate cost: ${cost_estimate['cost_usd']:.3f} USD

   Note: Actual costs may vary based on orchestrator's final strategy.

5. The orchestrator will:
   - Assess complexity (Simple/Moderate/High)
   - Determine optimal execution strategy (direct tools vs single agent vs multi-agent)
   - Recommend agent count and decomposition (if multi-agent)
   - Provide detailed execution plan with time estimates
   - Refine cost estimates based on strategy

6. Present the orchestrator's plan to the user with these options:
   ┌─────────────────────────────────────────┐
   │ [1] Execute Plan                        │
   │     → Proceed with orchestrator's       │
   │       recommended approach              │
   │                                         │
   │ [2] Modify Plan                         │
   │     → User provides feedback to adjust  │
   │       strategy (agent count, approach)  │
   │                                         │
   │ [3] Skip Orchestration                  │
   │     → Handle directly without           │
   │       multi-agent coordination          │
   └─────────────────────────────────────────┘

7. Only after user approval, execute according to the chosen approach.

CRITICAL RULES:
- Do NOT start any work until orchestrator has analyzed
- Do NOT proceed without user approval of the plan
- Present cost estimates clearly in the plan
- If user chooses [3], handle task directly without orchestrator
- Log decision and execution to hook logs
</orchestrator-analysis-required>
"""
    return context


def generate_simple_context(prompt: str) -> str:
    """Generate context for simple queries that don't need orchestration."""
    return f"""
<simple-query-detected>
This prompt has been classified as a simple informational query.
Handle directly without orchestration overhead.

Query: "{prompt}"
</simple-query-detected>
"""


def main():
    try:
        # Read hook input
        hook_input = json.loads(sys.stdin.read())
        user_prompt = hook_input.get("prompt", "")
        session_id = hook_input.get("session_id", "unknown")
        cwd = hook_input.get("cwd", "unknown")

        logger.info("=" * 80)
        logger.info(f"Hook triggered - Session: {session_id}")
        logger.info(f"CWD: {cwd}")
        logger.info(f"Prompt: {user_prompt}")

        # Analyze prompt
        needs_orchestration, reason, complexity = should_orchestrate(user_prompt)

        # Log decision
        logger.info(f"Decision: {'ORCHESTRATE' if needs_orchestration else 'SKIP'}")
        logger.info(f"Reason: {reason}")
        logger.info(f"Complexity: {complexity}")

        # Generate appropriate context
        if needs_orchestration:
            additional_context = generate_orchestrator_context(user_prompt, reason, complexity)
            cost_estimate = estimate_complexity_tokens(user_prompt, complexity)
            logger.info(f"Cost estimate: ${cost_estimate['cost_usd']:.3f} USD (~{cost_estimate['total_estimated']:,} tokens)")
        else:
            additional_context = generate_simple_context(user_prompt)
            logger.info("No orchestration needed - simple query")

        # Return JSON response
        response = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": additional_context
            }
        }

        logger.info("Hook completed successfully")
        logger.info("=" * 80)

        print(json.dumps(response))
        sys.exit(0)

    except Exception as e:
        logger.error(f"Hook error: {e}")
        logger.exception("Full traceback:")
        # On error, don't block - allow prompt through without modification
        response = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ""}}
        print(json.dumps(response))
        sys.exit(0)


if __name__ == "__main__":
    main()
