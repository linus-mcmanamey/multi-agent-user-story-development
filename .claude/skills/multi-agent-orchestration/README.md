# Multi-Agent Orchestration Skill - Quick Reference

## TL;DR

This skill provides intelligent routing for complex tasks using three commands:
1. **`/aa_command`** - Analyze and plan orchestration strategy
2. **`/background`** - Single PySpark data engineer agent (focused work)
3. **`/orchestrate`** - Multiple parallel agents (decomposable work)

## Quick Decision Tree

```
Is the task complex or unclear?
  YES → /aa_command "describe task"  (get strategy recommendation)
  NO  ↓

How many independent subtasks?
  1     → /background "task description"
  2-8   → /orchestrate "task description"
  >8    → /aa_command "task" (get phasing recommendations)
```

## Command Comparison

| Feature | `/aa_command` | `/background` | `/orchestrate` |
|---------|---------------|---------------|----------------|
| **Purpose** | Strategy planning | Single agent execution | Multi-agent coordination |
| **Agent Count** | 0 (analysis only) | 1 | 2-8 |
| **Agent Type** | N/A | pyspark-data-engineer | general-purpose |
| **Output** | Strategy recommendation | Comprehensive report | JSON consolidated report |
| **Best For** | Planning, unclear tasks | Focused work | Parallelizable work |
| **Time** | 2-5 min | 10-30 min | 20-60 min |

## Usage Examples

### Strategy Discussion
```bash
/aa_command "improve performance across all layers"
# Output: Analysis + recommendation to use /orchestrate with 5 agents
```

### Single Agent Background
```bash
/background "fix g_xa_mg_statsclasscount.py validation"
# Launches: 1 pyspark-data-engineer agent
# Time: ~15 minutes
```

### Multi-Agent Orchestration
```bash
/orchestrate "fix linting in silver_cms, silver_fvms, silver_nicherms"
# Launches: 1 orchestrator + 3 worker agents
# Time: ~20 minutes
```

## Task File Support

Both `/background` and `/orchestrate` support task files from `.claude/tasks/`:

```bash
# Background task file
/background code_review_fixes.md

# Orchestration task file
/orchestrate pipeline_optimization.md

# List available task files
/background list
/orchestrate list
```

## When to Use Each Command

### Use `/aa_command` when:
- ❓ Task complexity is unclear
- 🤔 Not sure if work should be parallelized
- 📋 Want to plan before executing
- 🎯 Need agent count and decomposition recommendations

### Use `/background` when:
- 📄 Working on 1-3 related files
- 🎯 Focused, non-decomposable work
- 🔧 Single layer (bronze, silver, or gold)
- ⚡ Sequential steps with tight coupling
- 🕐 Estimated time: <30 minutes

### Use `/orchestrate` when:
- 📚 Working on 4+ independent files
- 🔀 Parallelizable subtasks
- 🏗️ Cross-layer or cross-domain work
- 🚀 High complexity, clear decomposition
- 🕐 Estimated time: 30-60+ minutes

## JSON Response Format

All orchestrated worker agents return structured JSON:

```json
{
  "agent_id": "agent_1",
  "task_assigned": "Fix silver_cms linting",
  "status": "completed",
  "results": {
    "files_modified": ["s_cms_case.py", "s_cms_person.py"],
    "changes_summary": "Fixed 15 linting issues",
    "metrics": {
      "lines_added": 12,
      "lines_removed": 8,
      "functions_added": 0,
      "issues_fixed": 15
    }
  },
  "quality_checks": {
    "syntax_check": "passed",
    "linting": "passed",
    "formatting": "passed"
  },
  "issues_encountered": [],
  "recommendations": ["Add type hints"],
  "execution_time_seconds": 180
}
```

## Quality Gates

All agents MUST run these before completion:
```bash
python3 -m py_compile <file_path>  # Syntax validation
ruff check python_files/           # Linting
ruff format python_files/          # Formatting
```

## Integration with Project Commands

### Typical Workflow
```bash
# 1. Plan the work
/aa_command "optimize all gold tables"

# 2. Execute based on recommendation
/orchestrate "optimize all gold tables"

# 3. Commit changes
/local-commit "perf: optimize gold layer query performance"

# 4. Create PR
/pr-feature-to-staging

# 5. Write tests
/write-tests --data-validation

# 6. Update docs
/update-docs --generate-local
```

## Common Use Cases

### Code Quality Sweep
```bash
/orchestrate "fix all linting errors across silver layer"
# 3 agents: silver_cms, silver_fvms, silver_nicherms
```

### Performance Optimization
```bash
/aa_command "optimize all gold tables"
# Recommends 5-agent approach with analysis + implementation
```

### Feature Implementation
```bash
/orchestrate "add data validation framework across all layers"
# 6 agents: design, bronze, silver, gold, tests, docs
```

### Bug Fix
```bash
/background "fix transformation logic in g_xa_statsclasscount.py"
# 1 agent: focused fix with quality gates
```

### Refactoring
```bash
/orchestrate "update all ETL classes to use new base pattern"
# 4-6 agents depending on file count
```

## Task File Structure

### Background Task File (`.claude/tasks/example_background.md`)
```markdown
# Code Review Fixes

**Date Created**: 2025-11-07
**Priority**: HIGH
**Estimated Total Time**: 25 minutes
**Files Affected**: 5

## Task 1: Fix validation logic
**File**: python_files/gold/g_xa_mg_statsclasscount.py
**Line**: 45
**Estimated Time**: 5 minutes
**Severity**: HIGH

**Current Code**:
\```python
if data is None:
    pass
\```

**Required Fix**:
\```python
if data is None:
    logger.error("Data is None, cannot proceed")
    raise ValueError("Data cannot be None")
\```

**Reason**: Missing error handling
**Testing**: Run with None data, should raise ValueError

---

(Repeat for each task)
```

### Orchestration Task File (`.claude/tasks/example_orchestrate.md`)
```markdown
# Pipeline Performance Optimization

**Date Created**: 2025-11-07
**Priority**: HIGH
**Estimated Total Time**: 60 minutes
**Complexity**: High
**Recommended Worker Agents**: 5

## Main Objective
Improve pipeline performance across all layers

## Success Criteria
- [ ] All tables profiled
- [ ] Bottlenecks identified
- [ ] Optimizations implemented
- [ ] Performance validated

## Suggested Subtask Decomposition

### Subtask 1: Profile Bronze Layer
**Scope**: All bronze tables
**Estimated Time**: 12 minutes
**Dependencies**: None

**Description**: Analyze bronze layer query performance

**Expected Outputs**:
- Performance metrics for each table
- Bottleneck identification

---

(Repeat for each subtask)
```

## Best Practices

### Do's ✅
- Use `/aa_command` when complexity is unclear
- Launch agents in parallel when possible
- Provide clear task descriptions
- Use task files for complex work
- Validate quality gates pass
- Review JSON outputs for insights

### Don'ts ❌
- Don't use orchestration for trivial tasks
- Don't exceed 8 parallel agents
- Don't skip quality gates
- Don't ignore agent failures
- Don't use for highly sequential work

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Task file not found | Check `.claude/tasks/`, use `/background list` |
| Agent not completing | Task may be too broad, break into smaller pieces |
| Quality gates failing | Review changes manually, run gates to diagnose |
| JSON parse errors | Check worker response format, orchestrator handles gracefully |

## Performance Tips

- **2-8 agents**: Optimal orchestration range
- **Parallel launch**: Use single message with multiple Task tool calls
- **Minimal context**: Avoid duplicating shared information
- **Independent subtasks**: Minimize dependencies between agents

## Related Files

- Main skill: `multi-agent-orchestration.md`
- Commands: `.claude/commands/{aa_command,background,orchestrate}.md`
- Task files: `.claude/tasks/`
- Project guide: `.claude/CLAUDE.md`
- Python rules: `.claude/rules/python_rules.md`

## Quick Command Reference

```bash
# Analysis
/aa_command "task description"

# Single agent
/background "task description"
/background task_file.md
/background list

# Multi-agent
/orchestrate "task description"
/orchestrate task_file.md
/orchestrate list
```

---

**Created**: 2025-11-07
**Version**: 1.0
**Maintainer**: Multi-agent orchestration skill
