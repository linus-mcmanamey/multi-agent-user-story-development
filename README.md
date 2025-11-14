# Multi-Agent User Story Development Plugin

A Claude Code plugin that orchestrates multiple specialized agents to develop PySpark ETL transformations from Azure DevOps user stories.

## Project Overview

This plugin automates the development of medallion architecture ETL pipelines by leveraging multi-agent collaboration:

- **Business Analyst Agent**: Analyzes user story requirements and generates transformation specifications
- **PySpark Engineer Agent**: Implements optimized PySpark code following project standards
- **Orchestrator**: Coordinates agent workflows and manages context

## Features

- Automatic user story retrieval from Azure DevOps
- Multi-agent workflow orchestration
- Schema validation and mapping
- Template-based code generation
- Local memory system for data dictionaries
- MCP server integration

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.template` to `.env`
2. Configure required environment variables:
   - Azure DevOps PAT token
   - Claude API key
   - Synapse workspace details

## Usage

```bash
# Start the MCP server
python -m multi_agent_user_story_development.mcp.server

# Or use with Claude Code
make session
```

## Architecture

### Directory Structure

- `multi_agent_user_story_development/`: Core package
  - `orchestrator.py`: Agent coordination
  - `config.py`: Configuration management
  - `prompts/`: Agent prompt definitions
  - `mcp/`: MCP server implementation
  - `auth/`: Azure authentication
  - `templates/`: Prompt templates

- `.claude/`: Claude Code integration
  - `skills/`: Custom skills
  - `commands/`: Custom commands
  - `memory/`: Local memory system
  - `documentation/`: Plugin docs

## Development

### Quality Gates

```bash
python3 -m py_compile <file>
ruff check multi_agent_user_story_development/
ruff format multi_agent_user_story_development/
```

### Testing

```bash
python -m pytest tests/
```

## License

MIT License - See LICENSE file for details
