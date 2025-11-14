# CLAUDE.md - Multi-Agent User Story Development Plugin

## What This Plugin Does

A Claude Code plugin for automated Azure DevOps user story ETL development using multi-agent orchestration. Generates PySpark ETL code from user stories using specialized AI agents for discovery, design, and implementation.

## Plugin Architecture

**Core Components**:
- `AgentOrchestrator`: Manages multi-agent workflows
- `DiscoveryAgent`: Analyzes user stories and requirements
- `DesignAgent`: Creates ETL design specifications
- `ImplementationAgent`: Generates PySpark code
- `ReviewAgent`: Validates generated code

**Integration**:
- Azure DevOps MCP for work item access
- Claude API for agent execution
- PySpark pattern templates
- Schema validation utilities

## Essential Commands

### Plugin Installation
```bash
# Install as Claude Code plugin
pip install -e .

# Verify installation
python -c "from multi_agent_user_story_development import AgentOrchestrator; print('Plugin installed')"
```

### Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Edit with your credentials
# Required: AZURE_DEVOPS_PAT, CLAUDE_API_KEY
```

### Running the Plugin
```python
from multi_agent_user_story_development import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator(
    user_story_id=44687,
    file_name="g_x_mg_statsclasscount",
    read_layer="silver",
    write_layer="gold"
)

# Execute workflow
result = orchestrator.execute()
```

## Coding Standards

### Python Style
- Type hints: ALL parameters and returns
- Line length: **240 characters** (matches Unify project)
- Blank lines: **NONE inside functions**
- Blank line after imports and between functions
- NO docstrings unless explicitly requested
- Use descriptive variable names

### Agent Design Patterns
- Each agent is a separate class with `execute()` method
- Agents receive context and return structured output
- Use Pydantic models for agent inputs/outputs
- Log all agent actions with appropriate log levels
- Handle errors gracefully with specific error types

### Plugin Integration
- Use environment variables for configuration
- No hardcoded paths (use pathlib)
- Support both development and production environments
- Validate all inputs before processing

## Configuration

`.env` contains:
- Azure DevOps credentials (PAT, organization, project)
- Claude API configuration (API key, model)
- Synapse workspace settings (optional)
- Storage account settings (optional)
- Logging level

## Skills for Detailed Knowledge

**When you need more detail**, reference these skills from the Unify project:

- **project-architecture**: Understanding medallion architecture and data flow
- **pyspark-patterns**: PySpark ETL patterns and best practices
- **schema-reference**: Schema validation and lookup utilities

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_orchestrator.py

# Run with coverage
pytest --cov=multi_agent_user_story_development tests/
```

Test structure:
- `tests/test_orchestrator.py`: Main orchestration tests
- `tests/test_agents.py`: Individual agent tests
- `tests/test_integration.py`: End-to-end integration tests

## Development Workflow

1. **Create feature branch**: `git checkout -b feature/new-capability`
2. **Make changes**: Edit code following coding standards
3. **Test locally**: Run pytest suite
4. **Commit**: Use descriptive commit messages
5. **Push**: Push to remote repository

## MCP Integration

**Azure DevOps MCP**: Work items, pipelines, PRs, repos

Required environment variables:
```bash
export AZURE_DEVOPS_PAT="<token>"
export AZURE_DEVOPS_ORGANIZATION="emstas"
export AZURE_DEVOPS_PROJECT="Program Unify"
```

## Key Principles

1. **Agent specialization** - Each agent has a single, well-defined purpose
2. **Context passing** - Agents pass structured context to downstream agents
3. **Error handling** - All agents handle errors and provide meaningful messages
4. **Logging** - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
5. **Type safety** - Use Pydantic models for all data structures
6. **Environment agnostic** - Support both local development and production
7. **Schema validation** - Always validate against source/target schemas
8. **Code generation** - Follow Unify project PySpark patterns exactly

## Hook System

**Combined Prompt Hook** (`.claude/hooks/combined-prompt-hook.sh`):
- Intercepts user prompts before sending to Claude
- Injects orchestrator context when needed
- Routes plugin-specific requests appropriately

**Orchestrator Interceptor** (`.claude/hooks/orchestrator_interceptor.py`):
- Detects user story development requests
- Activates multi-agent workflow
- Returns generated code to Claude context

**Skill Activation** (`.claude/hooks/skill-activation-prompt.sh`):
- Loads relevant skills based on prompt content
- Provides schema context for ETL generation
- Activates PySpark pattern templates

## Usage Examples

### Generate ETL from User Story
```python
from multi_agent_user_story_development import AgentOrchestrator

# Full workflow
orchestrator = AgentOrchestrator(
    user_story_id=44687,
    file_name="g_x_mg_statsclasscount",
    read_layer="silver",
    write_layer="gold"
)
result = orchestrator.execute()
print(result.generated_code)
```

### Use Individual Agents
```python
from multi_agent_user_story_development.agents import DiscoveryAgent, DesignAgent

# Discovery phase
discovery = DiscoveryAgent(user_story_id=44687)
requirements = discovery.execute()

# Design phase
design = DesignAgent(requirements=requirements)
specification = design.execute()
```

### Custom Agent Configuration
```python
from multi_agent_user_story_development import AgentOrchestrator

orchestrator = AgentOrchestrator(
    user_story_id=44687,
    file_name="custom_table",
    read_layer="bronze",
    write_layer="silver",
    claude_model="claude-sonnet-4-5-20250929",
    max_retries=3
)
```

## Error Handling

All agents implement standard error handling:

```python
try:
    result = agent.execute()
except AgentExecutionError as e:
    logger.error(f"Agent failed: {e}")
    # Handle error appropriately
except SchemaValidationError as e:
    logger.error(f"Schema validation failed: {e}")
    # Handle schema errors
```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| AZURE_DEVOPS_PAT | Yes | Personal access token | `ghp_abc123...` |
| AZURE_DEVOPS_ORGANIZATION | Yes | DevOps organization | `emstas` |
| AZURE_DEVOPS_PROJECT | Yes | Project name | `Program Unify` |
| CLAUDE_API_KEY | Yes | Claude API key | `sk-ant-...` |
| CLAUDE_MODEL | No | Claude model to use | `claude-opus-4-1-20250805` |
| SYNAPSE_WORKSPACE | No | Synapse workspace name | `unify-synapse-dev` |
| SYNAPSE_DATABASE | No | Default database | `gold_cms` |
| LOG_LEVEL | No | Logging level | `INFO` |

## Troubleshooting

### Common Issues

**Import errors**:
```bash
# Reinstall plugin in editable mode
pip install -e .
```

**Azure DevOps authentication**:
```bash
# Verify PAT has correct permissions
# Required: Work Items (Read), Code (Read), Build (Read)
```

**Claude API errors**:
```bash
# Check API key is valid
# Verify model name is correct
# Check API rate limits
```

**Schema validation failures**:
```bash
# Ensure schema-reference skill is loaded
# Verify source/target layer schemas exist
# Check column name mappings
```

## Plugin Development

### Adding New Agents

1. Create agent class in `multi_agent_user_story_development/agents/`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Add Pydantic models for input/output
5. Write tests in `tests/test_agents.py`
6. Update orchestrator to include new agent

### Extending Orchestrator

1. Add new workflow methods to `AgentOrchestrator`
2. Update context passing between agents
3. Add configuration parameters
4. Update tests
5. Document new capabilities

## Integration with Unify Project

This plugin is designed to work seamlessly with the Unify data migration project:

- Generates code following Unify PySpark patterns
- Uses Unify utilities (TableUtilities, NotebookLogger, etc.)
- Validates against Unify schemas
- Follows Unify coding standards
- Integrates with Unify testing framework

When used in the Unify project, the plugin generates production-ready ETL code that can be immediately committed and tested.
