# Multi-Agent Orchestration Skill - Documentation Index

Complete documentation for the multi-agent orchestration skill.

## Skill Overview

This skill integrates three slash commands to provide intelligent task orchestration:
- `/aa_command` - Strategy discussion and planning
- `/background` - Single agent background execution
- `/orchestrate` - Multi-agent parallel orchestration

**Location**: `.claude/skills/multi-agent-orchestration.md`

## Documentation Files

### 1. Main Skill File
**File**: `multi-agent-orchestration.md` (parent directory)
**Lines**: 866
**Purpose**: Complete skill specification with all capabilities, usage patterns, and integration details

**Key Sections**:
- Core capabilities (3 commands)
- Decision flow for routing tasks
- Usage patterns (planning, background, orchestration)
- JSON communication protocol
- Quality gates and success criteria
- Error handling and troubleshooting
- Performance optimization
- Integration with project workflows

### 2. Quick Reference Guide
**File**: `README.md`
**Lines**: 325
**Purpose**: Fast reference for command usage and decision-making

**Key Sections**:
- TL;DR quick decision tree
- Command comparison table
- Usage examples
- Task file structure templates
- Common use cases
- Best practices (Do's & Don'ts)
- Troubleshooting guide
- Quick command reference

**Use this when**: You need a quick reminder of which command to use

### 3. Orchestration Patterns
**File**: `PATTERNS.md`
**Lines**: 518
**Purpose**: Detailed orchestration patterns and anti-patterns

**Key Sections**:
- 8 common orchestration patterns:
  1. Parallel Independent Execution
  2. Layer-by-Layer Sequential
  3. Design-then-Implement
  4. Analyze-then-Fix
  5. Quality Gate Sweep
  6. Feature Rollout
  7. Database-Specific Work
  8. Refactoring Campaign
- Pattern selection guide
- Combining patterns
- Anti-patterns to avoid
- Pattern templates

**Use this when**: Planning complex orchestration strategies

### 4. Example Task Files
**File**: `EXAMPLE_TASKS.md`
**Lines**: 707
**Purpose**: Complete examples of background and orchestration task files

**Key Sections**:
- Background task file example (gold_validation_fixes.md)
  - 7 validation fix tasks
  - Detailed current/required code
  - Testing requirements
- Orchestration task file example (silver_layer_optimization.md)
  - 6-agent optimization workflow
  - Analysis → Fix pattern
  - JSON response formats
- Simple background task example (fix_single_table.md)

**Use this when**: Creating new task files for `.claude/tasks/`

### 5. This Index
**File**: `INDEX.md`
**Lines**: Variable
**Purpose**: Navigation guide for all documentation

## File Organization

```
.claude/skills/
├── multi-agent-orchestration.md      # Main skill file (866 lines)
└── multi-agent-orchestration/        # Supporting documentation
    ├── INDEX.md                       # This file
    ├── README.md                      # Quick reference (325 lines)
    ├── PATTERNS.md                    # Orchestration patterns (518 lines)
    └── EXAMPLE_TASKS.md              # Task file examples (707 lines)
```

## Related Project Files

### Slash Commands
- `.claude/commands/aa_command.md` - Strategy discussion command (126 lines)
- `.claude/commands/background.md` - Background agent command (237 lines)
- `.claude/commands/orchestrate.md` - Orchestration command (511 lines)

### Task Files Directory
- `.claude/tasks/` - User-created task files (optional)

### Project Guidelines
- `.claude/CLAUDE.md` - Project architecture and standards
- `.claude/rules/python_rules.md` - Python coding standards

## Quick Navigation

### I want to...

**...understand what this skill does**
→ Read: `multi-agent-orchestration.md` (sections: "Core Capabilities", "When to Use")

**...decide which command to use**
→ Read: `README.md` (section: "Quick Decision Tree")

**...plan a complex orchestration**
→ Read: `PATTERNS.md` (section: "Pattern Selection Guide")

**...create a task file**
→ Read: `EXAMPLE_TASKS.md` (all examples)

**...see usage examples**
→ Read: `multi-agent-orchestration.md` (section: "Examples")

**...troubleshoot an issue**
→ Read: `README.md` (section: "Troubleshooting") or `multi-agent-orchestration.md` (section: "Error Handling")

**...understand JSON protocol**
→ Read: `multi-agent-orchestration.md` (section: "JSON Communication Protocol")

**...learn best practices**
→ Read: `README.md` (section: "Best Practices") or `multi-agent-orchestration.md` (section: "Best Practices")

## Usage Workflow

### 1. First Time User
1. Read `README.md` for overview
2. Review examples in `multi-agent-orchestration.md`
3. Try simple command: `/background "simple task"`

### 2. Planning Complex Task
1. Check `README.md` decision tree
2. Review `PATTERNS.md` for matching pattern
3. Optionally run `/aa_command "task description"` for recommendations
4. Create task file using `EXAMPLE_TASKS.md` templates

### 3. Creating Task Files
1. Review examples in `EXAMPLE_TASKS.md`
2. Choose background or orchestration template
3. Create file in `.claude/tasks/`
4. Run `/background task.md` or `/orchestrate task.md`

### 4. Advanced Orchestration
1. Study patterns in `PATTERNS.md`
2. Design custom orchestration strategy
3. Create detailed task file
4. Execute and monitor results

## Command Quick Reference

### Strategy Discussion
```bash
/aa_command "task description"
```
**Output**: Complexity analysis, recommended approach, agent breakdown

### Single Agent Background
```bash
/background "task description"
/background task_file.md
/background list
```
**Output**: Agent launch confirmation, comprehensive final report

### Multi-Agent Orchestration
```bash
/orchestrate "task description"
/orchestrate task_file.md
/orchestrate list
```
**Output**: Orchestrator launch, worker count, JSON consolidated report

## Key Concepts

### Agent Types
- **pyspark-data-engineer**: Specialized PySpark agent for `/background`
- **general-purpose**: Flexible agent for `/orchestrate` workers and orchestrator

### Execution Patterns
- **Parallel**: All agents run simultaneously (fastest)
- **Sequential**: Agents run one after another (dependencies)
- **Hybrid**: Phases of parallel execution (balanced)

### Communication
- **JSON Protocol**: Structured responses from all agents
- **Quality Gates**: Syntax, linting, formatting validation
- **Consolidated Reports**: Aggregated metrics and results

### Task Files
- **Location**: `.claude/tasks/`
- **Format**: Markdown with frontmatter
- **Types**: Background (single agent) or Orchestration (multi-agent)

## Success Criteria

### Background Agent
- ✅ All code changes implemented
- ✅ Quality gates passed (syntax, linting, formatting)
- ✅ Comprehensive final report provided

### Orchestrated Agents
- ✅ All worker agents launched and completed
- ✅ Valid JSON responses from all agents
- ✅ All quality checks passed
- ✅ Consolidated metrics calculated
- ✅ Comprehensive orchestration report provided

## Integration Points

### With Git Commands
```bash
/orchestrate "task" → /local-commit "message" → /pr-feature-to-staging
```

### With Testing
```bash
/background "task" → /write-tests --data-validation → make run_all
```

### With Documentation
```bash
/orchestrate "task" → /update-docs --generate-local → /update-docs --sync-to-wiki
```

## Performance Metrics

| Metric | Single Agent | Multi-Agent (4) | Improvement |
|--------|--------------|-----------------|-------------|
| Execution Time | 60 min | 20 min | 66% faster |
| Parallelization | None | 4x | 4x throughput |
| Complexity Handling | Moderate | High | Better scaling |

## Common Use Cases

1. **Code Quality Sweep**: Fix linting across multiple directories (orchestrate)
2. **Performance Optimization**: Analyze and optimize all tables (orchestrate)
3. **Bug Fix**: Fix single table issue (background)
4. **Feature Implementation**: Add feature across layers (orchestrate)
5. **Refactoring**: Update code patterns project-wide (orchestrate)
6. **Validation**: Add validation to specific file (background)

## Limitations

- Maximum 8 parallel agents (orchestrate)
- Background supports only 1 agent
- Task files must be in `.claude/tasks/`
- Quality gates are mandatory

## Version History

- **v1.0** (2025-11-07): Initial skill creation
  - Integrated aa_command, background, orchestrate
  - Created comprehensive documentation
  - Added patterns and examples

## Maintainer Notes

### Adding New Patterns
1. Document in `PATTERNS.md`
2. Add example in `EXAMPLE_TASKS.md`
3. Update `README.md` quick reference
4. Update main skill file if needed

### Updating Task Examples
1. Create new example in `EXAMPLE_TASKS.md`
2. Test with actual commands
3. Document results and learnings

### Skill Improvements
1. Monitor usage patterns
2. Collect user feedback
3. Refine decision trees and examples
4. Update documentation

## Support

For issues or questions:
1. Check troubleshooting sections
2. Review examples for similar cases
3. Consult project guidelines (`.claude/CLAUDE.md`)
4. Ask for clarification with specific context

## Related Skills

- `schema-reference` - Schema validation for PySpark code
- `azure-devops` - Azure DevOps operations
- `mcp-code-execution` - MCP integration patterns

---

**Created**: 2025-11-07
**Last Updated**: 2025-11-07
**Version**: 1.0
**Total Documentation**: ~2,400 lines across 4 files
**Status**: Production Ready
