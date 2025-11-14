# Multi-Agent User Story Development - Claude Code Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-1.0+-purple.svg)](https://claude.com/claude-code)

## Overview

Automated multi-agent orchestration system that generates production-ready PySpark ETL code from Azure DevOps user stories. Coordinates Business Analyst and PySpark Engineer agents with memory persistence, dual schema validation, and Azure integration.

## Key Features

### 🤖 Dual-Agent Orchestration
- **Business Analyst Agent**: Analyzes user stories, creates technical specifications (6 phases, 20-min execution)
- **PySpark Engineer Agent**: Generates production code with quality gates (8 phases, 30-min execution)
- **Non-Interactive**: Fully automated workflow without user prompts
- **Sequential Execution**: BA analysis feeds directly into PySpark implementation

### 💾 Intelligent Memory Management
- **Persistent Context**: Maintains state across multiple user stories
- **Smart Merge Logic**: Automatically consolidates knowledge from related stories
- **Historical Snapshots**: Archives previous states for each user story
- **Changelog Tracking**: Documents evolution of table transformations

### 🔍 Dual Schema Validation
- **Data Dictionary**: 69 tables (43 CMS, 26 FVMS) with business rules and NULL constraints
- **DuckDB Integration**: Validates against actual implemented schemas
- **Schema Drift Detection**: Identifies discrepancies between documentation and implementation
- **Foreign Key Discovery**: Automatically finds table relationships

### ☁️ Azure DevOps Integration
- **Work Item Retrieval**: Fetches user stories with requirements and acceptance criteria
- **Parent Story Analysis**: Traverses story hierarchies for complete context
- **Comment Extraction**: Captures technical decisions and gotchas from discussions
- **MCP Integration**: Uses `@azure-devops/mcp` server for deep integration

### 🛠️ Custom MCP Server
- **5 Memory Tools**: Template reading, business analysis, memory CRUD operations
- **Server Name**: `ba_pyspark_memory` v2.0.0
- **CLI Access**: `multi-agent-mcp` command
- **File-Based Storage**: Markdown files with smart section merging

### 🎓 10 Reusable Skills
- **azure-devops**: Azure DevOps operations (PRs, work items, pipelines)
- **multi-agent-orchestration**: Complex task coordination patterns
- **pyspark-patterns**: PySpark best practices and TableUtilities methods
- **schema-reference**: Automatic schema validation and lookup
- **wiki-auto-documenter**: Azure DevOps wiki documentation generator
- Plus 5 more utility and integration skills

### 🎣 Intelligent Hooks
- **orchestrator_interceptor.py**: Analyzes prompts, triggers multi-agent workflows
- **skill-activation-prompt**: Auto-activates relevant skills based on context
- **combined-prompt-hook**: Chains multiple hooks for comprehensive processing

### ✅ Quality Gates
- **Australian English**: Enforces spelling conventions (normalise, standardise, etc.)
- **Type Hints**: Mandatory on all parameters and returns
- **Line Length**: 240 characters (project standard)
- **Decorators**: `@synapse_error_print_handler` on all processing functions
- **Syntax Validation**: Python compilation check before completion

## Use Cases

### Primary: Automated ETL Development
```bash
# Generate complete PySpark ETL from user story
multi-agent-scaffold \
  --user-story 44687 \
  --file-name g_x_mg_statsclasscount \
  --read-layer silver \
  --write-layer gold

# Output:
# 1. Technical specification: .claude/documentation/g_x_mg_statsclasscount_implementation_specs.md
# 2. PySpark file: python_files/gold/g_x_mg_statsclasscount.py
# 3. Memory update: .claude/memory/gold/cms/statsclasscount.md
```

### Multi-Agent Workflow
```
User Story 44687 (ADO)
         │
         ▼
┌─────────────────────┐
│ Business Analyst    │
│ - Retrieve story    │
│ - Analyze comments  │
│ - Query schemas     │
│ - Create specs      │
│ - Update memory     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ PySpark Engineer    │
│ - Read specs        │
│ - Read memory       │
│ - Validate schemas  │
│ - Generate code     │
│ - Quality gates     │
└──────────┬──────────┘
           │
           ▼
    Production Code
```

## Installation

### Prerequisites
- Python 3.10+
- Claude CLI (`npm install -g @anthropic-ai/claude-code`)
- Azure CLI
- Azure DevOps Personal Access Token

### Quick Install
```bash
# Clone repository
git clone https://github.com/linus-mcmanamey/multi-agent-user-story-development.git
cd multi-agent-user-story-development

# Install with all dependencies
pip install -e ".[all]"

# Configure environment
cp .env.template .env
# Edit .env with your Azure credentials

# Verify installation
multi-agent-scaffold --help
multi-agent-mcp --help
```

### As Claude Code Plugin
```bash
# Clone to Claude plugins directory
cd ~/.claude/plugins/repos
git clone https://github.com/linus-mcmanamey/multi-agent-user-story-development.git

# Install dependencies
cd multi-agent-user-story-development
pip install -e ".[all]"

# Configure
cp .env.template .env
# Edit .env
```

## Configuration

### Environment Variables
```bash
# Required
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_ORGANIZATION=your_org_name
AZURE_DEVOPS_PROJECT=Your Project Name

# Optional
AGENT_DATA_ROOT=/workspaces/data
AGENT_PROJECT_ROOT=/workspaces/your_project
MOTHERDUCK_TOKEN=your_token  # If using cloud MotherDuck
```

### MCP Servers
Configure in `.claude.json` or via MCP config file:

```json
{
  "mcpServers": {
    "azure-devops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp"],
      "env": {
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}",
        "AZURE_DEVOPS_ORGANIZATION": "${AZURE_DEVOPS_ORGANIZATION}",
        "AZURE_DEVOPS_PROJECT": "${AZURE_DEVOPS_PROJECT}"
      }
    },
    "motherduck": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-motherduck", "--db-path", "/workspaces/data/warehouse.duckdb"]
    },
    "ba_pyspark_memory": {
      "type": "stdio",
      "command": "multi-agent-mcp"
    }
  }
}
```

## Usage

### CLI Command
```bash
multi-agent-scaffold \
  --user-story <ADO_WORK_ITEM_ID> \
  --file-name <python_file_name> \
  --read-layer <bronze|silver|gold> \
  --write-layer <bronze|silver|gold> \
  [--skip-auth] \
  [--skip-business-analyst]
```

### Programmatic API
```python
from multi_agent_user_story_development import AgentConfig, run_orchestrator

# Create configuration
config = AgentConfig(
    project_root="/workspaces/my_project",
    data_root="/workspaces/data"
)

# Run orchestrator
exit_code = run_orchestrator(
    user_story="44687",
    file_name="g_example_table",
    read_layer="silver",
    write_layer="gold",
    skip_auth=True
)
```

### Common Workflows

**1. Generate New ETL Table**
```bash
# User story defines new gold layer aggregation
multi-agent-scaffold --user-story 44687 --file-name g_mg_occurrence --read-layer silver --write-layer gold
```

**2. Update Existing Table**
```bash
# User story adds new transformation to existing file
multi-agent-scaffold --user-story 44688 --file-name g_mg_occurrence --read-layer silver --write-layer gold
# Agent will use Edit tool to add new functions
```

**3. Cross-Layer Migration**
```bash
# Bronze → Silver transformation
multi-agent-scaffold --user-story 44689 --file-name s_cms_case --read-layer bronze --write-layer silver
```

## Architecture

### Component Overview
```
multi_agent_user_story_development/
├── orchestrator.py          # Main workflow coordinator
├── config.py                # Configuration management
├── prompts/
│   ├── business_analyst.py  # BA agent prompt generator
│   └── pyspark_engineer.py  # PE agent prompt generator
├── mcp/
│   ├── server.py            # Custom MCP server
│   └── tools.py             # Memory management tools
└── auth/
    └── azure.py             # Azure authentication

.claude/
├── skills/                  # 10 reusable skills
├── hooks/                   # 6 intelligent hooks
└── memory/
    └── data_dictionary/     # 69 table schemas
```

### Data Flow
```
Azure DevOps → BA Agent → Technical Specs → PySpark Engineer → Production Code
                   ↓                              ↓
            Memory Update                  Quality Gates
                   ↓                              ↓
         Historical Archive              Syntax/Type/Spelling
```

## Skills Reference

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| **azure-devops** | ADO operations | PRs, work items, pipelines, repos |
| **multi-agent-orchestration** | Task coordination | Parallel/sequential agent execution |
| **pyspark-patterns** | PySpark development | TableUtilities, best practices |
| **schema-reference** | Schema validation | Auto-lookup, comparison |
| **project-architecture** | Architecture docs | Medallion layer patterns |
| **project-commands** | Command reference | Make commands, workflows |
| **mcp-code-execution** | MCP integration | Context-efficient patterns |
| **skill-creator** | Skill development | Skill creation guide |
| **wiki-auto-documenter** | Wiki generation | Azure DevOps wiki automation |
| **auto-code-review-gate** | Code review | Automated quality checks |

## Testing

### Run Tests
```bash
# All tests (149 test cases)
pytest

# With coverage report
pytest --cov=multi_agent_user_story_development --cov-report=html

# Specific test module
pytest tests/test_orchestrator.py -v

# With markers
pytest -m "unit"  # Unit tests only
pytest -m "integration"  # Integration tests only
```

### Test Coverage
- **config**: 25 tests (path management, environment variables)
- **orchestrator**: 22 tests (agent execution, workflows)
- **memory**: 35 tests (CRUD, merge logic, changelog)
- **prompts**: 39 tests (BA/PE prompt validation)
- **auth**: 23 tests (Azure CLI, DevOps authentication)
- **mcp_tools**: 5 tests (memory workflows)

## Coding Standards

### Australian English Spelling
```python
# CORRECT
def normalise_data(df: DataFrame) -> DataFrame:
    return df.withColumn("normalised_col", ...)

# INCORRECT
def normalize_data(df: DataFrame) -> DataFrame:
    return df.withColumn("normalized_col", ...)
```

### PySpark Patterns
```python
from pyspark.sql import DataFrame
from utilities.session_optimiser import TableUtilities, NotebookLogger, synapse_error_print_handler

class GoldLoader:
    def __init__(self, silver_table_name: str):
        self.extract_sdf = self.extract()
        self.transform_sdf = self.transform()
        self.load()

    @synapse_error_print_handler
    def extract(self) -> DataFrame:
        return spark.read.table(self.silver_table_name)

    @synapse_error_print_handler
    def transform(self) -> DataFrame:
        #### US: 44687
        transform_sdf = self.extract_sdf
        # Transformation chain (no blank lines)
        return transform_sdf

    @synapse_error_print_handler
    def load(self) -> None:
        table_utilities.save_as_table(self.transform_sdf, "gold_db.table")
```

## Troubleshooting

### Common Issues

**1. Azure DevOps Authentication Failed**
```bash
# Check PAT validity
az devops configure --list

# Set correct environment variables
export AZURE_DEVOPS_PAT=your_token
export AZURE_DEVOPS_ORGANIZATION=your_org
export AZURE_DEVOPS_PROJECT="Your Project"
```

**2. Claude CLI Not Found**
```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

**3. Agent Timeout**
```bash
# Business Analyst: default 20 minutes
# PySpark Engineer: default 30 minutes
# For complex user stories, this is expected

# Check logs
tail -f ~/.claude/hook_logs/orchestrator_hook.log
```

**4. Memory Merge Conflicts**
```bash
# View current memory state
cat .claude/memory/gold/cms/table_name.md

# View historical snapshots
ls .claude/memory/gold/cms/table_name/history/

# Manual merge if needed
cat .claude/memory/gold/cms/table_name/history/US_12345.md
```

## Performance

### Execution Times
- **Business Analyst**: 5-15 minutes (typical), 20 minutes (max)
- **PySpark Engineer**: 10-20 minutes (typical), 30 minutes (max)
- **Full Workflow**: 15-35 minutes end-to-end

### Resource Usage
- **Memory**: ~500 MB (agent execution)
- **Disk**: ~300 KB per data dictionary, ~50 KB per memory file
- **API Calls**: 20-50 Claude API requests per workflow

## Support & Contribution

### Issues
Report issues at: https://github.com/linus-mcmanamey/multi-agent-user-story-development/issues

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### License
MIT License - see LICENSE file for details

## Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com/claude) - AI foundation
- [Claude Code](https://claude.com/claude-code) - Development environment
- [Azure DevOps](https://azure.microsoft.com/en-us/products/devops) - Work item management
- [PySpark](https://spark.apache.org/docs/latest/api/python/) - ETL framework
- [DuckDB](https://duckdb.org/) - Schema validation

Based on scaffolding from the [Unify Data Migration Project](https://github.com/linus-mcmanamey/unify_2_1_plugin)

## Author

**Linus McMananey**
- GitHub: [@linus-mcmanamey](https://github.com/linus-mcmanamey)
- Email: linus.mcmanamey@gmail.com

---

⭐ **Star this repository** if you find it useful!

📖 **Read the full documentation** in [README.md](README.md)

🧪 **Try the demo** with the included test suite

💬 **Questions?** Open an issue or discussion
