# Claude Code Skills Library

This directory contains specialized skills that extend Claude's capabilities for this project. Skills provide domain knowledge, specialized workflows, and tool integrations.

## Available Skills

### 1. **azure-devops**
On-demand Azure DevOps operations (PRs, work items, pipelines, repos) using context-efficient patterns. Loaded only when needed to avoid polluting Claude context with 50+ MCP tools.

**Location**: `azure-devops/`
**Documentation**: `azure-devops.md` or `azure-devops/skill.md`
**Use when**: Working with Azure DevOps PRs, work items, pipelines, or wiki documentation

---

### 2. **mcp-code-execution**
Context-efficient MCP integration using code execution patterns. Use when building agents that interact with MCP servers, need to manage large tool sets (50+ tools), process large datasets through tools, or require multi-step workflows with intermediate results.

**Location**: `mcp-code-execution/`
**Documentation**: `mcp-code-execution.md`
**Use when**: Need to interact with MCP servers efficiently without loading all tools into context

---

### 3. **multi-agent-orchestration**
Enable Claude to orchestrate complex tasks by spawning and managing specialized sub-agents for parallel or sequential decomposition. Use when tasks have clear independent subtasks, require specialized approaches for different components, benefit from parallel processing, need fault isolation, or involve complex state management.

**Location**: `multi-agent-orchestration/`
**Documentation**: `multi-agent-orchestration.md`
**Use when**: Complex tasks requiring coordination of multiple specialized agents (e.g., data pipelines, code analysis workflows)

---

### 4. **project-architecture**
Detailed architecture, data flow, pipeline execution, dependencies, and system design for the Unify data migration project. Use when you need deep understanding of how components interact.

**Location**: `project-architecture/`
**Documentation**: `project-architecture.md`
**Use when**: Need to understand medallion architecture, data sources (FVMS/CMS/NicheRMS), Azure integration, or configuration management

---

### 5. **project-commands**
Complete reference for all make commands, development workflows, Azure operations, and database operations. Use when you need to know how to run specific operations.

**Location**: `project-commands/`
**Documentation**: `project-commands.md`
**Use when**: Need command reference for make targets, Azure CLI operations, or database operations

---

### 6. **pyspark-patterns**
PySpark best practices, TableUtilities methods, ETL patterns, logging standards, and DataFrame operations for this project. Use when writing or debugging PySpark code.

**Location**: `pyspark-patterns/`
**Documentation**: `pyspark-patterns.md`
**Use when**: Writing ETL code, using TableUtilities, implementing logging, or optimizing DataFrame operations

---

### 7. **schema-reference**
Automatically reference and validate schemas from both legacy data sources and medallion layer data sources (bronze, silver, gold) before generating PySpark transformation code. This skill should be used proactively whenever PySpark ETL code generation is requested.

**Location**: `schema-reference/`
**Documentation**: `schema-reference.md`
**Scripts**: `scripts/extract_data_dictionary.py`
**Use when**: Generating ETL code, validating schemas, or looking up column mappings and business logic

---

### 8. **skill-creator**
Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.

**Location**: `skill-creator/`
**Documentation**: `skill-creator.md`
**Use when**: Creating new skills or updating existing skills

---

### 9. **wiki-auto-documenter**
Multi-agent orchestration system for automatically generating comprehensive Azure DevOps wiki documentation from Python codebase. Creates hierarchical wiki pages matching repository structure with bidirectional linkages between documentation and source files.

**Location**: `wiki-auto-documenter/`
**Documentation**: `wiki-auto-documenter/skill.md`
**Scripts**:
- `scripts/wiki_hierarchy_builder.py`
- `scripts/code_analyzer.py`
**Use when**: Documenting entire directories, maintaining wiki docs synchronized with code, or generating hierarchical documentation

---

### 10. **auto-code-review-gate**
Automated code review and quality gates workflow.

**Location**: `auto-code-review-gate.md`
**Use when**: Running quality gates, linting, formatting, or automated code review

---

## Configuration Files

### skill-rules.json
Contains configuration and rules for skill behavior.

## Path Configuration Notes

All skills have been updated to use dynamic path resolution instead of hardcoded paths:

- **Python scripts** use `os.getcwd()` to determine the project root
- **Environment variables** like `${PROJECT_ROOT}` are used in configuration files
- **Relative paths** are used in documentation examples

### Files Updated for Path Flexibility

1. **mcp-code-execution/mcp_configs/registry.json** - Uses `${PROJECT_ROOT}` for config paths
2. **schema-reference/scripts/extract_data_dictionary.py** - Uses `os.getcwd()` for data dictionary paths
3. **wiki-auto-documenter/scripts/wiki_hierarchy_builder.py** - Uses `os.getcwd()` for repo root
4. **wiki-auto-documenter/scripts/code_analyzer.py** - Uses `os.getcwd()` for repo root
5. **azure-devops/scripts/wiki_bulk_publisher.py** - Uses `Path.cwd()` for base paths
6. **azure-devops.md** - Uses relative paths in examples
7. **azure-devops/skill.md** - Uses relative paths in examples
8. **wiki-auto-documenter/skill.md** - Uses `os.getcwd()` in examples

## Usage

To load a skill in a Claude Code session:

```
/skill <skill-name>
```

Example:
```
/skill pyspark-patterns
```

## Development Notes

- Skills are loaded on-demand to minimize context pollution
- Each skill can have its own scripts, configuration, and documentation
- Skills can depend on other skills (documented in their respective skill files)
- All paths should be project-agnostic (no hardcoded workspace paths)

## Migration Summary

**Total skills copied**: 9 directories + 1 standalone file
**Total files copied**: 58 files
**Files updated for path flexibility**: 8 files
**No errors encountered during migration**

All skills are now portable and can be used in any project by copying the `.claude/skills/` directory.
