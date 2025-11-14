---
description: Enable Claude to orchestrate complex tasks by spawning and managing specialized sub-agents for parallel or sequential decomposition. Use when tasks have clear independent subtasks, require specialized approaches for different components, benefit from parallel processing, need fault isolation, or involve complex state management across multiple steps. Best for data pipelines, code analysis workflows, content creation pipelines, and multi-stage processing tasks.
tags: [orchestration, agents, parallel, automation, workflow]
visibility: project
---

# Multi-Agent Orchestration Skill

This skill provides intelligent task orchestration by routing work to the most appropriate execution strategy: planning discussion, single-agent background execution, or multi-agent parallel orchestration.

## When to Use This Skill

Use this skill PROACTIVELY when:
- Tasks require more than one sequential step
- Work can be parallelized across multiple independent components
- You need to analyze complexity before deciding execution strategy
- Tasks involve multiple files, layers, or domains (bronze/silver/gold)
- Code quality sweeps across multiple directories
- Feature implementation spanning multiple modules
- Complex refactoring or optimization work
- Pipeline validation or testing across all layers

## Core Capabilities

This skill integrates three orchestration commands:

### 1. `/aa_command` - Orchestration Strategy Discussion
**Purpose**: Analyze task complexity and recommend execution approach

**Use when**:
- Task complexity is unclear
- User needs guidance on best orchestration approach
- Want to plan before executing
- Determining optimal agent count and decomposition strategy

**Output**:
- Task complexity assessment (Simple/Moderate/High)
- Recommended approach (`/background` or `/orchestrate`)
- Agent breakdown (if using orchestrate)
- Dependency analysis (None/Sequential/Hybrid)
- Estimated time
- Concrete next steps with example commands

### 2. `/background` - Single Agent Background Execution
**Purpose**: Launch one specialized PySpark data engineer agent to work autonomously

**Use when**:
- Task is focused on 1-3 related files
- Work is sequential and non-parallelizable
- Complexity is moderate (not requiring decomposition)
- Single domain/layer work (e.g., fixing one gold table)
- Code review fixes for specific component
- Targeted optimization or refactoring

**Agent Type**: `pyspark-data-engineer`

**Capabilities**:
- Autonomous task execution
- Quality gate validation (syntax, linting, formatting)
- Comprehensive reporting
- Follows medallion architecture patterns
- Uses project utilities (SparkOptimiser, TableUtilities, NotebookLogger)

### 3. `/orchestrate` - Multi-Agent Parallel Orchestration
**Purpose**: Coordinate 2-8 worker agents executing independent subtasks in parallel

**Use when**:
- Task has 2+ independent subtasks
- Work can run in parallel
- Complexity is high (benefits from decomposition)
- Cross-layer or cross-domain work (multiple bronze/silver/gold tables)
- Code quality sweeps across multiple directories
- Feature implementation requiring parallel development
- Bulk operations on many files

**Agent Type**: `general-purpose` orchestrator managing `general-purpose` workers

**Capabilities**:
- Task decomposition into 2-8 subtasks
- Parallel agent launch and coordination
- JSON-based structured communication
- Quality validation across all agents
- Consolidated metrics and reporting
- Graceful failure handling

## Orchestration Decision Flow

```
User Task
    ↓
Is complexity unclear?
    YES → /aa_command (analyze and recommend)
    NO  ↓
Is task decomposable into 2+ independent subtasks?
    NO  → /background (single focused agent)
    YES ↓
How many independent subtasks?
    2-8 → /orchestrate (parallel multi-agent)
    >8  → Recommend breaking into phases or refining decomposition
```

## Usage Patterns

### Pattern 1: Planning First
When task complexity is unclear, start with strategy discussion:

```
User: "I need to improve performance across all gold tables"

You: [Invoke /aa_command to analyze complexity]

aa_command analyzes:
- Task complexity: HIGH
- Recommended: /orchestrate
- Agent breakdown:
  - Agent 1: Analyze g_x_mg_* tables for bottlenecks
  - Agent 2: Analyze g_xa_* tables for bottlenecks
  - Agent 3: Review joins and aggregations across all tables
  - Agent 4: Check indexing and partitioning strategies
  - Agent 5: Implement optimization changes
  - Agent 6: Validate performance improvements
- Estimated time: 45-60 minutes

Then you proceed with /orchestrate based on recommendation
```

### Pattern 2: Direct Background Execution
When task is clearly focused and non-decomposable:

```
User: "Fix the validation issues in g_xa_mg_statsclasscount.py"

You: [Invoke /background directly]
- Task: Single file, focused fix
- Agent: pyspark-data-engineer
- Estimated time: 10-15 minutes
```

### Pattern 3: Direct Orchestration
When parallelization is obvious:

```
User: "Fix all linting errors across silver_cms, silver_fvms, and silver_nicherms"

You: [Invoke /orchestrate directly]
- Subtasks clearly decomposable
- 3 independent agents (one per database)
- Parallel execution
- Estimated time: 15-20 minutes
```

### Pattern 4: Task File Usage
When user has prepared a detailed task file:

```
User: "/background code_review_fixes.md"

You: [Invoke /background with task file]
- Reads .claude/tasks/code_review_fixes.md
- Launches agent with complete task context
- Executes all tasks in the file
```

## Task File Structure

Task files live in `.claude/tasks/` directory.

### Background Task File Format

```markdown
# Task Title

**Date Created**: 2025-11-07
**Priority**: HIGH/MEDIUM/LOW
**Estimated Total Time**: X minutes
**Files Affected**: N

## Task 1: Description
**File**: python_files/gold/g_xa_mg_statsclasscount.py
**Line**: 45
**Estimated Time**: 5 minutes
**Severity**: HIGH

**Current Code**:
```python
# problematic code
```

**Required Fix**:
```python
# fixed code
```

**Reason**: Explanation of why this needs fixing
**Testing**: How to verify the fix works

---

## Task 2: Description
...
```

### Orchestration Task File Format

```markdown
# Orchestration Task Title

**Date Created**: 2025-11-07
**Priority**: HIGH
**Estimated Total Time**: X minutes
**Complexity**: High
**Recommended Worker Agents**: 5

## Main Objective
Clear description of the overall goal

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Suggested Subtask Decomposition

### Subtask 1: Title
**Scope**: Files/components affected
**Estimated Time**: X minutes
**Dependencies**: None

**Description**: What needs to be done

**Expected Outputs**:
- Output 1
- Output 2

---

### Subtask 2: Title
...
```

## JSON Communication Protocol

All orchestrated agents communicate using structured JSON format.

### Worker Agent Response Format

```json
{
  "agent_id": "agent_1",
  "task_assigned": "Fix linting in silver_cms files",
  "status": "completed",
  "results": {
    "files_modified": [
      "python_files/silver/silver_cms/s_cms_case_file.py",
      "python_files/silver/silver_cms/s_cms_offence_report.py"
    ],
    "changes_summary": "Fixed 23 linting issues across 2 files",
    "metrics": {
      "lines_added": 15,
      "lines_removed": 8,
      "functions_added": 0,
      "issues_fixed": 23
    }
  },
  "quality_checks": {
    "syntax_check": "passed",
    "linting": "passed",
    "formatting": "passed"
  },
  "issues_encountered": [],
  "recommendations": ["Consider adding type hints to helper functions"],
  "execution_time_seconds": 180
}
```

### Orchestrator Final Report Format

```json
{
  "orchestration_summary": {
    "main_task": "Fix all linting errors across silver layer",
    "total_agents_launched": 3,
    "successful_agents": 3,
    "failed_agents": 0,
    "total_execution_time_seconds": 540
  },
  "agent_results": [
    {...},
    {...},
    {...}
  ],
  "consolidated_metrics": {
    "total_files_modified": 15,
    "total_lines_added": 127,
    "total_lines_removed": 84,
    "total_functions_added": 3,
    "total_issues_fixed": 89
  },
  "quality_validation": {
    "all_syntax_checks_passed": true,
    "all_linting_passed": true,
    "all_formatting_passed": true
  },
  "consolidated_issues": [],
  "consolidated_recommendations": [
    "Consider adding type hints across all silver layer files",
    "Review error handling patterns for consistency"
  ],
  "next_steps": [
    "Run full test suite: python -m pytest python_files/testing/",
    "Execute silver layer pipeline: make run_silver",
    "Validate output in DuckDB: make harly"
  ]
}
```

## Quality Gates

All agents (background and orchestrated) MUST run these quality gates before completion:

1. **Syntax Validation**: `python3 -m py_compile <file_path>`
2. **Linting**: `ruff check python_files/`
3. **Formatting**: `ruff format python_files/`

Quality check results are included in JSON responses and validated by orchestrator.

## Complexity Assessment Guidelines

### Simple (Use /background)
- 1-3 related files
- Single layer (bronze, silver, or gold)
- Sequential steps
- Focused scope
- Estimated time: <20 minutes

**Examples**:
- Fix validation in one gold table
- Add logging to a specific module
- Refactor one ETL class
- Update configuration for one component

### Moderate (Consider /background or /orchestrate)
- 4-8 files
- Single or multiple layers
- Some parallelizable work
- Medium scope
- Estimated time: 20-40 minutes

**Decision factors**:
- If files are tightly coupled → /background
- If files are independent → /orchestrate

**Examples**:
- Fix linting across one database (e.g., silver_cms)
- Optimize all gold tables with same pattern
- Add feature to one layer

### High (Use /orchestrate)
- 8+ files OR cross-layer work
- Multiple independent components
- Highly parallelizable
- Broad scope
- Estimated time: 40+ minutes

**Examples**:
- Fix linting across all layers
- Implement feature across bronze/silver/gold
- Code quality sweep across entire project
- Performance optimization for all tables
- Test suite creation for full pipeline

## Agent Configuration

### Background Agent
```python
Task(
    subagent_type="pyspark-data-engineer",
    model="sonnet",  # or "opus" for complex tasks
    description="Fix gold table validation",
    prompt="""
    You are a PySpark data engineer working on Unify 2.1 Data Migration.

    CRITICAL INSTRUCTIONS:
    - Read and follow .claude/CLAUDE.md
    - Use .claude/rules/python_rules.md for coding standards
    - Maximum line length: 240 characters
    - No blank lines inside functions
    - Use @synapse_error_print_handler decorator
    - Use NotebookLogger for logging
    - Use TableUtilities for DataFrame operations

    TASK: {task_content}

    QUALITY GATES (MUST RUN):
    1. python3 -m py_compile <file_path>
    2. ruff check python_files/
    3. ruff format python_files/

    Provide comprehensive final report with:
    - Summary of changes
    - Files modified with line numbers
    - Quality gate results
    - Testing recommendations
    - Issues and resolutions
    - Next steps
    """
)
```

### Orchestrator Agent
```python
Task(
    subagent_type="general-purpose",
    model="sonnet",  # or "opus" for very complex orchestrations
    description="Orchestrate pipeline optimization",
    prompt="""
    You are an ORCHESTRATOR AGENT coordinating multiple worker agents.

    PROJECT CONTEXT:
    - Project: Unify 2.1 Data Migration using Azure Synapse Analytics
    - Architecture: Medallion pattern (Bronze/Silver/Gold)
    - Language: PySpark Python
    - Follow: .claude/CLAUDE.md and .claude/rules/python_rules.md

    YOUR RESPONSIBILITIES:
    1. Analyze task and decompose into 2-8 subtasks
    2. Launch worker agents (Task tool, subagent_type="general-purpose")
    3. Provide clear instructions with JSON response format
    4. Collect and validate all worker responses
    5. Aggregate results and metrics
    6. Produce final consolidated report

    MAIN TASK: {task_content}

    WORKER JSON FORMAT:
    {
      "agent_id": "unique_id",
      "task_assigned": "description",
      "status": "completed|failed|partial",
      "results": {...},
      "quality_checks": {...},
      "issues_encountered": [...],
      "recommendations": [...],
      "execution_time_seconds": 0
    }

    Work autonomously and orchestrate complete task execution.
    """
)
```

## Error Handling

### Worker Agent Failures
- Orchestrator captures failure details
- Marks agent status as "failed"
- Continues with other agents
- Reports failure in final summary
- Suggests recovery steps

### JSON Parse Errors
- Orchestrator logs parse error
- Attempts partial result extraction
- Marks response as invalid
- Flags for manual review
- Continues with valid responses

### Quality Check Failures
- Orchestrator flags the failure
- Includes failure details in report
- Prevents final approval
- Suggests corrective actions
- May relaunch worker with corrections

## Performance Optimization

### Parallel Execution
- Launch all independent agents simultaneously
- Use Task tool with multiple concurrent calls in single message
- Maximize parallelism for faster completion
- Monitor resource utilization

### Agent Sizing
- **2-8 agents**: Optimal for most orchestrated tasks
- **<2 agents**: Use `/background` instead
- **>8 agents**: Consider phased approach or refinement
- Balance granularity vs coordination overhead

### Context Management
- Provide minimal necessary context
- Avoid duplicating shared information
- Reference shared documentation (.claude/CLAUDE.md)
- Keep prompts focused and concise

## Best Practices

### Task Decomposition
- Break into 2-8 independent subtasks
- Avoid inter-agent dependencies when possible
- Balance workload across agents
- Group related work logically
- Consider file/component boundaries
- Respect layer separation (bronze/silver/gold)

### Worker Prompts
- Make each subtask self-contained
- Include all necessary context
- Specify exact file paths and requirements
- Define clear success criteria
- Require JSON response format
- Include quality gate validation
- Request execution metrics

### Orchestrator Design
- Keep worker tasks independent
- Provide complete context to each worker
- Assign unique, meaningful agent IDs
- Specify clear JSON response requirements
- Validate all JSON responses
- Handle worker failures gracefully
- Aggregate results systematically
- Provide actionable consolidated report

## Examples

### Example 1: Strategy Discussion
```
User: "I need to improve data quality across all layers"

Claude: [Invokes /aa_command]

Analysis:
- Task Complexity: HIGH
- Recommended Approach: /orchestrate
- Agent Breakdown:
  - Agent 1: Design quality framework and base classes
  - Agent 2: Implement bronze layer validators
  - Agent 3: Implement silver layer validators
  - Agent 4: Implement gold layer validators
  - Agent 5: Create validation tests
  - Agent 6: Update documentation
- Dependencies: Agent 1 must complete before 2-4 (hybrid approach)
- Estimated Time: 50-70 minutes
- Next Steps: Create task file, then run /orchestrate data_quality_framework.md
```

### Example 2: Background Single Agent
```
User: "Fix the transformation logic in g_xa_mg_statsclasscount.py"

Claude: [Invokes /background directly]

Launched: pyspark-data-engineer agent
Task: Fix transformation logic in single gold table
Estimated Time: 12-15 minutes
Agent will:
- Read g_xa_mg_statsclasscount.py
- Analyze transformation logic issues
- Implement fixes following medallion patterns
- Run quality gates (syntax, linting, formatting)
- Provide comprehensive report
```

### Example 3: Parallel Orchestration
```
User: "Fix all linting errors across the silver layer"

Claude: [Invokes /orchestrate directly]

Launched: Orchestrator agent coordinating 3 workers
- Worker 1: Fix silver_cms linting errors
- Worker 2: Fix silver_fvms linting errors
- Worker 3: Fix silver_nicherms linting errors
Execution: Fully parallel (no dependencies)
Estimated Time: 15-20 minutes

Orchestrator will:
- Launch 3 agents simultaneously
- Collect JSON responses from each
- Validate quality checks passed
- Aggregate metrics (files modified, issues fixed)
- Produce consolidated report
```

### Example 4: Task File Execution
```
User: "/background code_review_fixes.md"

Claude: [Invokes /background with task file]

Found: .claude/tasks/code_review_fixes.md
Tasks: 9 code review fixes across 5 files
Priority: HIGH
Estimated Time: 27 minutes

Agent will:
- Read task file with detailed fix instructions
- Execute all 9 fixes sequentially
- Validate each fix with quality gates
- Provide comprehensive report on all changes
```

### Example 5: Complex Orchestration with Task File
```
User: "/orchestrate pipeline_optimization.md"

Claude: [Invokes /orchestrate with task file]

Found: .claude/tasks/pipeline_optimization.md
Recommended Agents: 6
Complexity: HIGH
Estimated Time: 60 minutes

Task file suggests decomposition:
- Agent 1: Profile bronze layer performance
- Agent 2: Profile silver layer performance
- Agent 3: Profile gold layer performance
- Agent 4: Analyze join strategies
- Agent 5: Implement optimization changes
- Agent 6: Validate performance improvements

Orchestrator will coordinate all 6 agents and produce consolidated metrics.
```

## Command Reference

### /aa_command - Strategy Discussion
```bash
# Analyze task complexity
/aa_command "optimize all gold tables"

# Get approach recommendations
/aa_command "implement monitoring across layers"

# Plan refactoring work
/aa_command "update all ETL classes to new pattern"
```

**Output**: Complexity assessment, recommended approach, agent breakdown, next steps

### /background - Single Agent
```bash
# Direct prompt
/background "fix validation in g_xa_mg_statsclasscount.py"

# Task file
/background code_review_fixes.md

# List available task files
/background list
```

**Output**: Agent launch confirmation, estimated time, final comprehensive report

### /orchestrate - Multi-Agent
```bash
# Direct prompt
/orchestrate "fix linting across all silver layer files"

# Task file
/orchestrate data_quality_framework.md

# List available orchestration tasks
/orchestrate list
```

**Output**: Orchestrator launch confirmation, worker count, final JSON consolidated report

## Integration with Project Workflow

### With Git Operations
```bash
# 1. Run orchestration
/orchestrate "optimize all gold tables"

# 2. After completion, commit changes
/local-commit "feat: optimize gold layer performance"

# 3. Create PR
/pr-feature-to-staging
```

### With Testing
```bash
# 1. Run orchestration
/background "add validation to gold tables"

# 2. After completion, write tests
/write-tests --data-validation

# 3. Run tests
make run_all
```

### With Documentation
```bash
# 1. Run orchestration
/orchestrate "implement new feature across layers"

# 2. After completion, update docs
/update-docs --generate-local

# 3. Sync to wiki
/update-docs --sync-to-wiki
```

## Success Criteria

### For Background Agent
- ✅ All code changes implemented
- ✅ Syntax validation passes
- ✅ Linting passes
- ✅ Code formatted
- ✅ No new issues introduced
- ✅ Comprehensive final report provided

### For Orchestrated Agents
- ✅ All worker agents launched successfully
- ✅ All worker agents returned valid JSON responses
- ✅ All quality checks passed across all agents
- ✅ No unresolved issues or failures
- ✅ Consolidated metrics calculated correctly
- ✅ Comprehensive orchestration report provided
- ✅ All files syntax validated
- ✅ All files linted and formatted

## Limitations and Considerations

### When NOT to Use Multi-Agent Orchestration
- Task is trivial (single file, simple change)
- Work is highly sequential with tight dependencies
- Task requires continuous user interaction
- Subtasks cannot be clearly defined
- Less than 2 independent components

**Alternative**: Use standard tools (Read, Edit, Write) or single `/background` agent

### Agent Count Guidelines
- **2-3 agents**: Small to medium parallelizable tasks
- **4-6 agents**: Medium to large tasks with clear decomposition
- **7-8 agents**: Very large tasks with many independent components
- **>8 agents**: Consider breaking into phases or hybrid approach

### Resource Considerations
- Each agent consumes computational resources
- Parallel execution may strain system resources
- Monitor execution time across agents
- Consider sequential phasing for very large tasks

## Troubleshooting

### Issue: Task File Not Found
**Solution**:
- Check file exists in `.claude/tasks/`
- Verify exact filename (case-sensitive)
- Use `/background list` or `/orchestrate list` to see available files

### Issue: Agent Not Completing
**Solution**:
- Check agent complexity (may need more time)
- Review task scope (may be too broad)
- Consider breaking into smaller subtasks
- Switch from `/orchestrate` to `/background` for simpler tasks

### Issue: Quality Gates Failing
**Solution**:
- Review code changes made by agent
- Check for syntax errors or linting issues
- Manually run quality gates to diagnose
- May need to refine task instructions

### Issue: JSON Parse Errors
**Solution**:
- Check worker agent response format
- Verify JSON structure is valid
- Orchestrator should handle gracefully
- Review worker prompt for JSON format requirements

## Advanced Patterns

### Hybrid Sequential-Parallel
```
Phase 1: Single agent designs framework
         ↓ (outputs JSON schema)
Phase 2: 4 agents implement in parallel using schema
         ↓ (outputs implementations)
Phase 3: Single agent validates and integrates
```

### Recursive Orchestration
```
Main Orchestrator
    ↓
Sub-Orchestrator 1 (bronze layer)
    ↓
    Workers: bronze_cms, bronze_fvms, bronze_nicherms
    ↓
Sub-Orchestrator 2 (silver layer)
    ↓
    Workers: silver_cms, silver_fvms, silver_nicherms
```

### Incremental Validation
```
Agent 1: Implement changes → Worker reports
         ↓
Orchestrator validates → Approves/Rejects
         ↓
Agent 2: Builds on Agent 1 → Worker reports
         ↓
Orchestrator validates → Approves/Rejects
         ↓
Continue...
```

## Related Project Patterns

### Medallion Architecture Orchestration
```
Bronze Layer → Silver Layer → Gold Layer
Each layer can have parallel agents:
- bronze_cms, bronze_fvms, bronze_nicherms
- silver_cms, silver_fvms, silver_nicherms
- gold_x_mg, gold_xa, gold_xb
```

### Quality Gate Orchestration
```
Agent 1: Syntax validation (all files)
Agent 2: Linting (all files)
Agent 3: Formatting (all files)
Agent 4: Unit tests
Agent 5: Integration tests
Agent 6: Data validation tests
```

### Feature Implementation Orchestration
```
Agent 1: Design and base classes
Agent 2: Bronze layer implementation
Agent 3: Silver layer implementation
Agent 4: Gold layer implementation
Agent 5: Testing suite
Agent 6: Documentation
Agent 7: Configuration updates
```

## Skill Activation

This skill is loaded on-demand. When user requests involve:
- "optimize all tables"
- "fix across multiple layers"
- "implement feature in all databases"
- "code quality sweep"
- Complex multi-step tasks

You should PROACTIVELY consider using this skill to route work appropriately.

## Further Reading

- `.claude/commands/aa_command.md` - Strategy discussion command
- `.claude/commands/background.md` - Single agent background execution
- `.claude/commands/orchestrate.md` - Multi-agent orchestration
- `.claude/tasks/` - Example task files
- `.claude/CLAUDE.md` - Project guidelines and patterns
- `.claude/rules/python_rules.md` - Python coding standards