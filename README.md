# Multi-Agent User Story Development Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-9966ff.svg)](https://claude.ai/claude-code)

A Claude Code plugin that orchestrates specialized AI agents to automatically develop production-ready PySpark ETL transformations from Azure DevOps user stories. Built for medallion architecture data pipelines (Bronze → Silver → Gold) in Azure Synapse Analytics.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Use Case Scenarios](#use-case-scenarios)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Components](#components)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview

This plugin automates the end-to-end development of data transformation pipelines by breaking down complex ETL requirements into specialized tasks handled by purpose-built AI agents. It bridges the gap between business requirements in Azure DevOps and production-ready PySpark code.

### What It Does

1. **Analyzes** user stories from Azure DevOps to understand requirements
2. **Generates** technical specifications with schema mappings and transformation logic
3. **Implements** production-ready PySpark code following project standards
4. **Maintains** historical context through a memory system
5. **Validates** code quality and adherence to coding standards

### Key Features

- **Multi-Agent Orchestration**: Coordinates specialized agents (Business Analyst, PySpark Engineer) for complex workflows
- **Business Analyst Agent**:
  - Retrieves and analyzes Azure DevOps user stories
  - Queries schema metadata from DuckDB and data dictionaries
  - Generates comprehensive technical specifications
  - Maintains table memory for historical context
- **PySpark Engineer Agent**:
  - Implements transformations based on specifications
  - Follows strict coding standards (240-char lines, type hints, error handlers)
  - Preserves existing code and user story references
  - Uses Australian English spelling conventions
- **MCP Server Integration**: Custom tools for memory management and documentation
- **Memory Management**: Persistent table-level memory with changelog and history snapshots
- **Azure DevOps Integration**: Direct integration with work items, comments, and parent stories
- **Data Dictionary Support**: Leverages source system documentation for business context
- **Schema Validation**: Cross-references data dictionaries with current DuckDB schemas

## Use Case Scenarios

### Scenario 1: New Gold Layer Table
```bash
# Create a new analytics table from silver layer sources
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name g_xa_mg_cms_mo \
  --read-layer silver \
  --write-layer gold
```

**What Happens:**
1. Business Analyst retrieves US:44687, analyzes requirements
2. Queries schemas for silver CMS tables and gold target
3. Generates technical spec with column mappings and transformations
4. PySpark Engineer creates new Python file with ETL class
5. Memory system stores context for future enhancements

### Scenario 2: Updating Existing Silver Table
```bash
# Add new transformation to existing silver table
python -m multi_agent_user_story_development.orchestrator \
  --user-story 45123 \
  --file-name s_cms_case \
  --read-layer bronze \
  --write-layer silver \
  --skip-business-analyst  # Reuse existing documentation
```

**What Happens:**
1. PySpark Engineer reads existing `s_cms_case.py`
2. Identifies existing functions and US references
3. Adds new transformation functions alongside existing code
4. Updates `transform()` method to chain new logic
5. Preserves all existing US comments

### Scenario 3: Cross-System Linkage Table
```bash
# Create linkage between CMS and FVMS systems
python -m multi_agent_user_story_development.orchestrator \
  --user-story 46001 \
  --file-name g_mg_occurrence_linkage \
  --read-layer silver \
  --write-layer gold
```

**What Happens:**
1. Business Analyst identifies cross-system requirements
2. References approved linkage pattern from `g_ya_mg_occurence.py`
3. Specifies full outer join pattern for CMS-FVMS data
4. PySpark Engineer implements using verified reference pattern
5. Includes verification flags and comprehensive ID mappings

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User/Developer Request                      │
│          (Azure DevOps User Story + Target File Spec)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator (Main Entry)                     │
│  • Validates inputs and authentication                          │
│  • Coordinates agent execution phases                           │
│  • Manages timeouts and error handling                          │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────────┐  ┌───────────────────────────────┐
│  Business Analyst Agent    │  │   PySpark Engineer Agent      │
│  (Claude CLI subprocess)   │  │   (Claude CLI subprocess)     │
│                            │  │                               │
│  Phase 1: User Story       │  │  Phase 1: Read CLAUDE.md      │
│  Phase 2: Parent Context   │  │  Phase 2: Read Memory         │
│  Phase 3: Table Memory     │  │  Phase 3: Read BA Specs       │
│  Phase 4: Schema Analysis  │  │  Phase 4: Check Existing File │
│  Phase 5: Documentation    │  │  Phase 5: Verify Schemas      │
│  Phase 6: Update Memory    │  │  Phase 6: Implementation      │
└────────────┬───────────────┘  └───────────┬───────────────────┘
             │                               │
             │   MCP Tools & Resources       │
             │   ┌─────────────────────┐     │
             ├──►│ Azure DevOps MCP    │◄────┤
             │   │ • Work items        │     │
             │   │ • Comments          │     │
             │   └─────────────────────┘     │
             │   ┌─────────────────────┐     │
             ├──►│ MotherDuck MCP      │◄────┤
             │   │ • DuckDB schemas    │     │
             │   │ • Legacy metadata   │     │
             │   └─────────────────────┘     │
             │   ┌─────────────────────┐     │
             ├──►│ Memory MCP Server   │◄────┤
             │   │ • Table memory      │     │
             │   │ • History snapshots │     │
             │   └─────────────────────┘     │
             │   ┌─────────────────────┐     │
             └──►│ File System         │◄────┘
                 │ • Data dictionaries │
                 │ • Documentation     │
                 │ • Python files      │
                 └─────────────────────┘
```

### Component Overview

**Orchestrator** (`orchestrator.py`):
- Entry point for automated workflows
- Manages sequential execution of Business Analyst → PySpark Engineer
- Handles Azure authentication and Claude CLI validation
- Provides progress logging and error recovery

**Business Analyst Agent** (`prompts/business_analyst.py`):
- Analyzes Azure DevOps user stories and related context
- Queries schemas from DuckDB and data dictionary files
- Generates technical specifications for implementation
- Updates consolidated table memory with new requirements

**PySpark Engineer Agent** (`prompts/pyspark_engineer.py`):
- Implements PySpark transformations based on BA specifications
- Follows strict coding standards (type hints, error handlers, formatting)
- Preserves existing code and maintains US references
- Uses Australian English spelling for all identifiers

**MCP Server** (`mcp/server.py`, `mcp/tools.py`):
- Custom tools for memory management (read/write/list)
- Documentation and template access
- Integrates with Claude CLI for agent execution

**Configuration** (`config.py`):
- Environment-aware path management
- Azure DevOps connection settings
- Memory and documentation directory structure

**Hooks** (`.claude/hooks/`):
- `orchestrator_interceptor.py`: Analyzes prompts for complexity
- `combined-prompt-hook.sh`: Injects skill context
- `skill-activation-prompt.sh`: Enables skill loading

### Data Flow

```
User Story (Azure DevOps)
    │
    ▼
Business Analyst Agent
    │
    ├──► Retrieve work item (ADO MCP)
    ├──► Check parent story and comments (ADO MCP)
    ├──► Read table memory (Memory MCP)
    ├──► Read data dictionaries (File System)
    ├──► Query DuckDB schemas (MotherDuck MCP)
    │
    ▼
Technical Specifications (.md)
    │
    ▼
PySpark Engineer Agent
    │
    ├──► Read BA specifications
    ├──► Read table memory (Memory MCP)
    ├──► Check existing Python file
    ├──► Verify schemas (MotherDuck MCP)
    │
    ▼
PySpark ETL Code (.py)
    │
    ▼
Memory Update (Memory MCP)
    │
    ├──► Archive previous state to history/
    ├──► Update consolidated table memory
    └──► Add changelog entry
```

## Installation

### Prerequisites

- **Python 3.10+**: Required for type hints and modern syntax
- **Claude CLI**: Install with `npm install -g @anthropic-ai/claude-code`
- **Azure CLI**: For Azure authentication (`az login`)
- **Git**: For version control
- **Azure DevOps PAT**: Personal Access Token with work item read permissions
- **Claude API Key**: From Anthropic console

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/emstas/multi-agent-user-story-development.git
   cd multi-agent-user-story-development
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies (optional)**
   ```bash
   pip install -e ".[dev]"  # Includes pytest, ruff, mypy
   ```

5. **Install MCP support (optional)**
   ```bash
   pip install -e ".[mcp]"  # Includes MCP server dependencies
   ```

### Environment Setup

1. **Copy environment template**
   ```bash
   cp .env.template .env
   ```

2. **Configure environment variables**
   ```bash
   # Edit .env with your credentials
   nano .env  # or use your preferred editor
   ```

   Required variables:
   ```bash
   # Azure DevOps
   AZURE_DEVOPS_PAT=your_personal_access_token
   AZURE_DEVOPS_ORGANIZATION=emstas
   AZURE_DEVOPS_PROJECT=Program Unify

   # Claude API
   CLAUDE_API_KEY=your_claude_api_key
   CLAUDE_MODEL=claude-opus-4-1-20250805
   ```

3. **Authenticate with Azure**
   ```bash
   az login
   ```

4. **Verify Claude CLI**
   ```bash
   claude --version
   ```

## Quick Start

### Simple Usage Example

```bash
# Run the orchestrator with a user story
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name g_xa_mg_cms_mo \
  --read-layer silver \
  --write-layer gold
```

**What this does:**
1. Retrieves Azure DevOps user story 44687
2. Analyzes requirements for a gold layer table
3. Generates technical specifications in `.claude/documentation/`
4. Implements PySpark code in `python_files/gold/`
5. Updates table memory in `.claude/memory/gold/`

### Understanding the Output

After successful execution, you'll find:

**Documentation** (`.claude/documentation/g_xa_mg_cms_mo_implementation_specs.md`):
- Executive summary of requirements
- Schema mappings (source → target)
- Transformation specifications
- Testing scenarios

**Python Code** (`python_files/gold/g_xa_mg_cms_mo.py`):
- Complete ETL class with extract/transform/load
- Transformation functions with US references
- Type hints and error handlers
- Follows project coding standards

**Memory** (`.claude/memory/gold/cms/mg_cms_mo.md`):
- Consolidated table context
- Changelog of user stories
- Business rules and transformations
- Related tables and gotchas

**History Snapshot** (`.claude/memory/gold/cms/mg_cms_mo/history/US_44687.md`):
- Point-in-time snapshot before this user story
- Useful for understanding requirement evolution

## Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_DEVOPS_PAT` | Yes | - | Personal Access Token for Azure DevOps API |
| `AZURE_DEVOPS_ORGANIZATION` | Yes | `emstas` | Azure DevOps organization name |
| `AZURE_DEVOPS_PROJECT` | Yes | `Program Unify` | Project name in Azure DevOps |
| `CLAUDE_API_KEY` | Yes | - | API key from Anthropic console |
| `CLAUDE_MODEL` | No | `claude-opus-4-1-20250805` | Claude model to use for agents |
| `SYNAPSE_WORKSPACE` | No | - | Azure Synapse workspace name (for schema validation) |
| `SYNAPSE_DATABASE` | No | - | Default database for Synapse queries |
| `STORAGE_ACCOUNT_NAME` | No | - | Azure storage account (for direct file access) |
| `STORAGE_CONTAINER` | No | - | Storage container name |
| `HOOK_LOGS_DIR` | No | `~/.claude/hook_logs` | Directory for hook execution logs |
| `ORCHESTRATOR_MAX_AGENTS` | No | `5` | Maximum concurrent agents |
| `ORCHESTRATOR_TIMEOUT_SECONDS` | No | `300` | Orchestrator timeout (5 minutes) |
| `AGENT_MAX_RETRIES` | No | `3` | Retry attempts for failed agents |
| `AGENT_TIMEOUT_SECONDS` | No | `120` | Individual agent timeout (2 minutes) |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `AGENT_DATA_ROOT` | No | `/workspaces/data` | Root directory for data files |
| `AGENT_PROJECT_ROOT` | No | `$PWD` | Project root directory |

### Configuration File Options

The plugin uses `AgentConfig` dataclass in `config.py` for path management:

```python
from multi_agent_user_story_development.config import AgentConfig

config = AgentConfig()
# Access configured paths
doc_path = config.get_documentation_path("my_table")
memory_path = config.get_memory_path("gold", "cms", "mg_case")
```

**Key Paths:**
- `documentation_output_dir`: `.claude/documentation/`
- `memory_dir`: `.claude/memory/`
- `notebook_output_dir`: `.claude/notebooks/` (deprecated)
- `templates_dir`: `templates/`
- `ddl_dir`: `documentation/ddl/`
- `duckdb_path`: `/workspaces/data/warehouse.duckdb`

### MCP Server Setup

The plugin includes a custom MCP server for memory management. To use it:

1. **Configure in Claude settings** (`.claude.json`):
   ```json
   {
     "mcpServers": {
       "ba_pyspark_memory": {
         "command": "python",
         "args": ["-m", "multi_agent_user_story_development.mcp.server"],
         "cwd": "/path/to/multi-agent-user-story-development"
       }
     }
   }
   ```

2. **Available MCP Tools:**
   - `read_etl_template`: Get ETL template content
   - `read_business_analysis`: Read BA documentation
   - `write_memory`: Store/update table memory
   - `read_memory`: Read current table state
   - `list_memories`: List all table memories

### Azure Authentication

The orchestrator checks Azure authentication before running agents:

```bash
# Authenticate with Azure CLI
az login

# Verify authentication
az account show

# Set Azure DevOps organization (if needed)
az devops configure --defaults organization=https://dev.azure.com/emstas
```

**Skip authentication check** (for testing):
```bash
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name test_table \
  --read-layer silver \
  --write-layer gold \
  --skip-auth
```

## Usage

### CLI Usage Examples

#### Basic Execution
```bash
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name g_xa_mg_cms_mo \
  --read-layer silver \
  --write-layer gold
```

#### Skip Business Analyst (Use Existing Docs)
```bash
# If documentation already exists, skip BA and run only PySpark Engineer
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name g_xa_mg_cms_mo \
  --read-layer silver \
  --write-layer gold \
  --skip-business-analyst
```

#### Verbose Logging
```bash
# Enable debug-level logging
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name g_xa_mg_cms_mo \
  --read-layer silver \
  --write-layer gold \
  --verbose
```

#### Skip Authentication Check
```bash
# For testing without Azure authentication
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name test_table \
  --read-layer bronze \
  --write-layer silver \
  --skip-auth
```

### Programmatic API Usage

```python
from multi_agent_user_story_development.orchestrator import run_orchestrator
from multi_agent_user_story_development.config import AgentConfig

# Initialize configuration
config = AgentConfig()

# Run orchestrator programmatically
exit_code = run_orchestrator(
    user_story="44687",
    file_name="g_xa_mg_cms_mo",
    read_layer="silver",
    write_layer="gold",
    skip_auth=False,
    skip_business_analyst=False,
    verbose=True
)

if exit_code == 0:
    print("Workflow completed successfully!")
else:
    print("Workflow failed!")
```

### Common Workflows

#### Workflow 1: New Gold Table from Silver Sources
```bash
# Step 1: Create technical specs and implementation
python -m multi_agent_user_story_development.orchestrator \
  --user-story 45001 \
  --file-name g_mg_incident_summary \
  --read-layer silver \
  --write-layer gold

# Step 2: Review generated files
cat .claude/documentation/g_mg_incident_summary_implementation_specs.md
cat python_files/gold/g_mg_incident_summary.py

# Step 3: Test implementation
python python_files/gold/g_mg_incident_summary.py
```

#### Workflow 2: Update Existing Silver Table
```bash
# Step 1: Run with existing documentation
python -m multi_agent_user_story_development.orchestrator \
  --user-story 45123 \
  --file-name s_cms_case \
  --read-layer bronze \
  --write-layer silver \
  --skip-business-analyst

# Step 2: Review changes (new functions added)
git diff python_files/silver/s_cms_case.py

# Step 3: Check memory update
cat .claude/memory/silver/cms/cms_case.md
```

#### Workflow 3: Cross-System Linkage
```bash
# Step 1: Generate linkage table
python -m multi_agent_user_story_development.orchestrator \
  --user-story 46001 \
  --file-name g_mg_occurrence_linkage \
  --read-layer silver \
  --write-layer gold

# Step 2: Verify linkage pattern
grep -A 20 "full_outer" python_files/gold/g_mg_occurrence_linkage.py

# Step 3: Test linkage query
python python_files/gold/g_mg_occurrence_linkage.py
```

### Advanced Usage Patterns

#### Custom Memory Queries
```python
from multi_agent_user_story_development.config import AgentConfig

config = AgentConfig()

# List all gold layer memories
gold_memories = config.list_memories(layer="gold")
for mem in gold_memories:
    print(f"Table: {mem.stem}, Path: {mem}")

# Read specific table memory
memory_path = config.get_memory_path("gold", "cms", "mg_case")
if memory_path.exists():
    content = memory_path.read_text()
    print(content)

# List memory history for a table
history = config.list_memory_history(layer="gold", datasource="cms", table_name="mg_case")
for hist in history:
    print(f"User Story: {hist.stem}, Path: {hist}")
```

#### Batch Processing Multiple User Stories
```python
import subprocess

user_stories = [
    {"us": "45001", "file": "g_mg_incident_summary", "read": "silver", "write": "gold"},
    {"us": "45002", "file": "g_mg_case_summary", "read": "silver", "write": "gold"},
    {"us": "45003", "file": "g_mg_occurrence_stats", "read": "silver", "write": "gold"},
]

for story in user_stories:
    cmd = [
        "python", "-m", "multi_agent_user_story_development.orchestrator",
        "--user-story", story["us"],
        "--file-name", story["file"],
        "--read-layer", story["read"],
        "--write-layer", story["write"]
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Failed: US:{story['us']}")
        break
```

## Components

### Orchestrator (`orchestrator.py`)

**Responsibilities:**
- Validate inputs and check prerequisites
- Coordinate sequential agent execution
- Manage timeouts and error handling
- Log progress and results

**Key Functions:**
- `check_claude_cli()`: Verify Claude CLI availability
- `run_business_analyst()`: Execute BA agent subprocess
- `run_pyspark_engineer()`: Execute PySpark agent subprocess
- `run_orchestrator()`: Main coordination function

**Timeouts:**
- Business Analyst: 20 minutes (1200 seconds)
- PySpark Engineer: 30 minutes (1800 seconds)

### Business Analyst Agent (`prompts/business_analyst.py`)

**Phases:**
1. **User Story Retrieval**: Get work item from Azure DevOps
2. **Parent Context**: Check parent story and comments
3. **Table Memory**: Read existing memory for context
4. **Existing Code Analysis**: Check for existing Python file
5. **Schema Analysis**: Query data dictionaries and DuckDB
6. **Implementation Plan**: Create transformation specifications
7. **Documentation**: Save technical specs to `.claude/documentation/`
8. **Memory Update**: Update consolidated table memory

**Output:**
- Technical specifications (`.md` file)
- Updated table memory (`.claude/memory/`)
- History snapshot (`history/US_*.md`)

### PySpark Engineer Agent (`prompts/pyspark_engineer.py`)

**Phases:**
1. **Read Guidelines**: Load `CLAUDE.md` for coding standards
2. **Read Memory**: Check table memory for context
3. **Read BA Specs**: Load technical specifications
4. **Check Existing**: Determine if file exists
5. **Verify Schemas**: Query DuckDB to confirm schemas
6. **Implementation**: Create/update Python file
7. **Quality Validation**: Check coding standards
8. **Save**: Write Python file to `python_files/`

**Coding Standards:**
- Line length: 240 characters
- Type hints on all functions
- `@synapse_error_print_handler` decorator
- Australian English spelling (normalise, standardise, etc.)
- No blank lines inside functions
- `#### US: {id}` comments on new functions

**Output:**
- PySpark ETL code (`.py` file)
- Preserved existing functions with US references

### MCP Server (`mcp/server.py`, `mcp/tools.py`)

**Available Tools:**

1. **`read_etl_template`**
   - Returns ETL template content
   - No parameters

2. **`read_business_analysis`**
   - Parameters: `file_name` (str)
   - Returns BA documentation content

3. **`write_memory`**
   - Parameters: `layer`, `datasource`, `table_name`, `user_story`, `content`
   - Stores/updates table memory
   - Archives previous state to history
   - Merges content with existing memory

4. **`read_memory`**
   - Parameters: `layer`, `datasource`, `table_name`
   - Returns current consolidated table memory

5. **`list_memories`**
   - Parameters (optional): `layer`, `datasource`, `table_name`
   - Lists all current table memories

**Memory Structure:**
```
.claude/memory/
├── gold/
│   ├── cms/
│   │   ├── mg_case.md                    # Current consolidated state
│   │   └── mg_case/
│   │       └── history/
│   │           ├── US_44687.md           # Snapshot before US:44687
│   │           └── US_45123.md           # Snapshot before US:45123
│   └── fvms/
│       └── incident.md
└── silver/
    └── cms/
        └── cms_case.md
```

### Configuration (`config.py`)

**`AgentConfig` Dataclass:**
- Environment-aware path management
- Azure DevOps connection settings
- Memory and documentation directory structure

**Key Methods:**
- `get_documentation_path(file_name)`: Get documentation file path
- `get_memory_path(layer, datasource, table_name)`: Get current memory path
- `get_memory_history_path(layer, datasource, table_name, user_story)`: Get history snapshot path
- `list_memories(layer, datasource, table_name)`: List current memories
- `list_memory_history(layer, datasource, table_name)`: List history snapshots

### Hooks (`.claude/hooks/`)

**`orchestrator_interceptor.py`:**
- Analyzes user prompts for complexity
- Determines if orchestration is needed
- Provides cost estimates
- Injects orchestrator context

**`combined-prompt-hook.sh`:**
- Injects skill context into prompts
- Activates relevant skills based on keywords

**`skill-activation-prompt.sh`:**
- Enables skill loading for agents

### Skills (`.claude/skills/`)

Available skills for deep knowledge:

- **`project-architecture`**: Medallion architecture, data sources, Azure integration
- **`project-commands`**: Make command reference, workflows, operations
- **`pyspark-patterns`**: TableUtilities, DataFrame operations, logging
- **`schema-reference`**: Schema validation and lookup
- **`azure-devops`**: Azure DevOps MCP integration
- **`multi-agent-orchestration`**: Multi-agent workflow patterns
- **`mcp-code-execution`**: MCP server integration patterns
- **`wiki-auto-documenter`**: Wiki documentation generation

## Development

### Setting Up Development Environment

1. **Clone and install**
   ```bash
   git clone https://github.com/emstas/multi-agent-user-story-development.git
   cd multi-agent-user-story-development
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```

2. **Configure pre-commit hooks** (optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. **Set up IDE**
   - VSCode: Install Python extension
   - PyCharm: Configure virtual environment
   - Set line length to 240 in formatter settings

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=multi_agent_user_story_development --cov-report=html

# Run specific test file
python -m pytest tests/test_orchestrator.py

# Run specific test
python -m pytest tests/test_memory.py::test_write_memory -v
```

**Test Structure:**
- `tests/test_orchestrator.py`: Orchestrator workflow tests
- `tests/test_memory.py`: Memory system tests
- `tests/__init__.py`: Test utilities

### Contributing Guidelines

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/multi-agent-user-story-development.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and test**
   ```bash
   # Run quality gates
   ruff check multi_agent_user_story_development/
   ruff format multi_agent_user_story_development/
   python -m pytest tests/
   ```

4. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new memory query feature"
   git commit -m "fix: resolve orchestrator timeout issue"
   git commit -m "docs: update README with new examples"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

**Commit Message Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

### Code Standards

**Python Style:**
- Line length: **240 characters** (configured in `pyproject.toml`)
- Type hints: Required on all function parameters and returns
- Docstrings: Optional (not enforced)
- Naming: `snake_case` for functions/variables, `PascalCase` for classes
- Spelling: Australian English for identifiers (normalise, colour, etc.)

**Quality Checks:**
```bash
# Syntax check
python3 -m py_compile multi_agent_user_story_development/orchestrator.py

# Linting
ruff check multi_agent_user_story_development/

# Formatting
ruff format multi_agent_user_story_development/

# Type checking (optional)
mypy multi_agent_user_story_development/
```

**Ruff Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 240
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Claude CLI Not Found
```
Error: Claude CLI not found. Please install with: npm install -g @anthropic-ai/claude-code
```

**Solution:**
```bash
npm install -g @anthropic-ai/claude-code
claude --version  # Verify installation
```

#### Issue: Azure Authentication Failed
```
Error: Azure authentication required
```

**Solution:**
```bash
az login
az account show  # Verify authentication
az devops configure --defaults organization=https://dev.azure.com/emstas
```

Or skip authentication for testing:
```bash
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name test_table \
  --read-layer silver \
  --write-layer gold \
  --skip-auth
```

#### Issue: Business Analyst Timeout
```
Error: Business analyst agent timed out (20 minutes)
```

**Solution:**
- Check Azure DevOps connectivity
- Verify DuckDB database is accessible
- Check for large data dictionary files
- Consider splitting complex user stories

#### Issue: Documentation Not Found
```
Error: Business analysis documentation not found
```

**Solution:**
```bash
# Check documentation directory
ls -la .claude/documentation/

# Run BA agent first (without skip)
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name g_xa_mg_cms_mo \
  --read-layer silver \
  --write-layer gold
# (Do NOT use --skip-business-analyst on first run)
```

#### Issue: Memory File Not Found
```
Error: No memory found for table mg_case
```

**Solution:**
This is normal for first-time runs. Memory will be created automatically. If memory should exist:
```bash
# Check memory directory structure
ls -la .claude/memory/gold/cms/

# List all memories
python -c "
from multi_agent_user_story_development.config import AgentConfig
config = AgentConfig()
memories = config.list_memories(layer='gold', datasource='cms')
for m in memories: print(m)
"
```

#### Issue: MCP Server Not Starting
```
Error: Claude Agent SDK not installed. Cannot start MCP server.
```

**Solution:**
```bash
pip install ".[mcp]"
# Or manually:
pip install mcp
```

#### Issue: Schema Query Failed
```
Error: DuckDB query failed
```

**Solution:**
- Verify MotherDuck MCP is configured in `.claude.json`
- Check DuckDB file exists: `/workspaces/data/warehouse.duckdb`
- Ensure `data_hub.legacy_schema` table exists
- Test query manually:
  ```bash
  duckdb /workspaces/data/warehouse.duckdb
  SELECT COUNT(*) FROM data_hub.legacy_schema;
  ```

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with verbose flag
python -m multi_agent_user_story_development.orchestrator \
  --user-story 44687 \
  --file-name test_table \
  --read-layer silver \
  --write-layer gold \
  --verbose
```

**Log Locations:**
- Orchestrator logs: stderr (console output)
- Hook logs: `~/.claude/hook_logs/orchestrator_hook.log`
- Agent output: Streamed to console during execution

### Logging

The plugin uses `loguru` for structured logging:

```python
from loguru import logger

logger.info("Starting workflow")
logger.success("Workflow completed successfully")
logger.error("Workflow failed with error")
logger.debug("Detailed debug information")
```

**Log Format:**
```
2025-11-14 10:30:45 | INFO     | Orchestrator - Starting automated agent workflow
2025-11-14 10:30:46 | INFO     | Orchestrator - User Story: 44687
2025-11-14 10:30:47 | SUCCESS  | Orchestrator - Business analyst agent completed successfully
```

**Hook Logs** (`~/.claude/hook_logs/orchestrator_hook.log`):
```bash
tail -f ~/.claude/hook_logs/orchestrator_hook.log
```

## License

MIT License

Copyright (c) 2024 Program Unify

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

This plugin was developed as part of the **Program Unify** data migration project to Azure Synapse Analytics.

**Built With:**
- [Claude Code](https://claude.ai/claude-code) - Anthropic's official CLI for Claude
- [Anthropic Claude](https://www.anthropic.com/) - Large language model for AI agents
- [Azure DevOps](https://azure.microsoft.com/en-us/products/devops/) - Work item management
- [Azure Synapse Analytics](https://azure.microsoft.com/en-us/products/synapse-analytics/) - Data warehouse platform
- [PySpark](https://spark.apache.org/docs/latest/api/python/) - Distributed data processing
- [DuckDB](https://duckdb.org/) - Embedded analytical database

**Based on:**
- Unify Project Scaffolding - Medallion architecture patterns
- Claude Code Plugin System - MCP integration and skill framework

**Contributors:**
- Program Unify Team
- Azure Migration Engineering

**Special Thanks:**
- Anthropic for Claude Code and the Model Context Protocol (MCP)
- The PySpark and Azure communities for best practices
- Contributors to the Unify project knowledge base

---

**Project Links:**
- [GitHub Repository](https://github.com/emstas/multi-agent-user-story-development)
- [Issue Tracker](https://github.com/emstas/multi-agent-user-story-development/issues)
- [Azure DevOps Project](https://dev.azure.com/emstas/Program%20Unify)

**Documentation:**
- [Claude Code Documentation](https://claude.ai/claude-code/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [PySpark Best Practices](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart.html)

**Version:** 0.1.0 (Alpha)

Last Updated: 2025-11-14
