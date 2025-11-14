# Test Suite for Multi-Agent User Story Development

This directory contains the comprehensive test suite for the multi-agent user story development plugin.

## Test Structure

### Test Files

- **`test_config.py`** - Tests for `AgentConfig` configuration management
  - Configuration initialization and path resolution
  - Environment variable loading
  - Documentation and notebook path management
  - Memory path management and listing

- **`test_orchestrator.py`** - Tests for the main orchestration workflow
  - Claude CLI availability checks
  - Business analyst agent execution
  - PySpark engineer agent execution
  - Full workflow orchestration
  - Error handling and timeout scenarios

- **`test_memory.py`** - Tests for memory management system
  - Memory write operations (create and update)
  - Memory read operations
  - Historical snapshot management
  - Memory listing and filtering
  - Content merge logic

- **`test_prompts.py`** - Tests for prompt generation
  - Business analyst prompt structure and content
  - PySpark engineer prompt structure and content
  - Datasource detection
  - Australian English spelling requirements
  - Reference example inclusion

- **`test_auth.py`** - Tests for Azure authentication
  - Azure CLI authentication checks
  - Azure DevOps authentication checks
  - Combined authentication validation
  - Login and relogin workflows
  - Error handling and timeout scenarios

- **`test_mcp_tools.py`** - Tests for MCP tool functions
  - ETL template reading
  - Business analysis documentation reading
  - Memory tool integration
  - Cross-layer memory isolation
  - Deprecated tool identification

- **`conftest.py`** - Pytest fixtures and test configuration
  - Temporary project directory setup
  - Mock environment variables
  - Sample data fixtures
  - Mock Azure authentication
  - Mock Claude CLI execution

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_orchestrator.py
```

### Run Specific Test Class
```bash
pytest tests/test_orchestrator.py::TestRunBusinessAnalyst
```

### Run Specific Test
```bash
pytest tests/test_orchestrator.py::TestRunBusinessAnalyst::test_run_business_analyst_success
```

### Run with Coverage
```bash
pytest --cov=multi_agent_user_story_development --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (isolated, fast)
- `@pytest.mark.integration` - Integration tests (multiple components)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.azure` - Tests requiring Azure authentication
- `@pytest.mark.cli` - Tests requiring Claude CLI

## Test Coverage

Current test coverage includes:

### Configuration Management (test_config.py)
- ✓ AgentConfig initialization
- ✓ Path configuration from environment variables
- ✓ Directory creation
- ✓ Documentation path management
- ✓ Notebook path management
- ✓ Memory path management
- ✓ Memory listing and filtering

### Orchestration (test_orchestrator.py)
- ✓ Logging setup
- ✓ Claude CLI availability checks
- ✓ Business analyst agent execution (success/failure/timeout)
- ✓ PySpark engineer agent execution (success/failure/timeout)
- ✓ MCP config and settings file creation
- ✓ Full workflow orchestration
- ✓ Skip authentication flag
- ✓ Skip business analyst flag
- ✓ Verbose mode

### Memory Management (test_memory.py)
- ✓ Memory creation
- ✓ Memory updates with archiving
- ✓ Memory reading
- ✓ Historical snapshot reading
- ✓ Memory listing (all, filtered by layer/datasource/table)
- ✓ Memory history listing
- ✓ Content merge logic
- ✓ Changelog management
- ✓ Error handling

### Prompt Generation (test_prompts.py)
- ✓ Business analyst prompt structure
- ✓ PySpark engineer prompt structure
- ✓ User story ID inclusion
- ✓ File name and data layer inclusion
- ✓ Datasource detection (CMS, FVMS, NicheRMS)
- ✓ Phase inclusion
- ✓ Critical instruction inclusion
- ✓ Australian English spelling requirements
- ✓ Reference example inclusion
- ✓ Code quality checklist

### Azure Authentication (test_auth.py)
- ✓ Azure CLI authentication checks
- ✓ Token validation
- ✓ Azure DevOps authentication checks
- ✓ Combined authentication validation
- ✓ Login workflow
- ✓ Force relogin
- ✓ Cache management
- ✓ Error handling (timeout, not found, invalid response)

### MCP Tools (test_mcp_tools.py)
- ✓ ETL template reading
- ✓ Business analysis reading
- ✓ Memory CRUD operations
- ✓ Deprecated tool identification
- ✓ Full memory workflow integration
- ✓ Cross-layer memory isolation
- ✓ Changelog accumulation

## Fixtures

Common fixtures available in `conftest.py`:

### Directory Fixtures
- `temp_project_dir` - Temporary project directory with standard structure

### Configuration Fixtures
- `mock_env_vars` - Mock environment variables
- `agent_config` - Configured AgentConfig instance

### Data Fixtures
- `sample_user_story_data` - Sample Azure DevOps work item data
- `sample_documentation_content` - Sample business analysis documentation
- `sample_memory_content` - Sample memory content

### Mock Fixtures
- `mock_azure_auth` - Mock Azure authentication
- `mock_claude_cli` - Mock Claude CLI subprocess calls
- `mock_mcp_server_response` - Mock MCP server responses

### Factory Fixtures
- `create_sample_python_file` - Create sample Python files for testing
- `create_sample_documentation` - Create sample documentation files
- `create_sample_memory` - Create sample memory files

## Writing New Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<description_of_what_is_tested>`

### Test Structure
```python
class TestMyFeature:
    """Test my feature functionality."""

    def test_feature_success(self, agent_config: AgentConfig):
        """Test successful feature execution."""
        # Arrange
        setup_test_data()

        # Act
        result = my_feature()

        # Assert
        assert result is True
```

### Using Fixtures
```python
def test_with_temp_directory(self, temp_project_dir: Path):
    """Test that uses temporary directory."""
    test_file = temp_project_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
```

### Mocking External Dependencies
```python
def test_with_mock(self, mock_claude_cli: Mock):
    """Test that mocks Claude CLI."""
    mock_claude_cli.return_value.returncode = 0
    result = run_agent()
    assert result is True
    assert mock_claude_cli.called
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

- All tests pass without requiring actual Azure credentials
- No external dependencies required (mocked)
- Fast execution time
- Comprehensive coverage reporting

## Test Configuration

Test configuration is managed in `pytest.ini`:

- Test discovery patterns
- Logging configuration
- Coverage settings
- Marker definitions

## Dependencies

Test dependencies are listed in `requirements-dev.txt`:

- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-mock - Mocking utilities
- pytest-asyncio - Async testing support
- responses - HTTP response mocking
- freezegun - Time mocking

Install test dependencies:
```bash
pip install -r requirements-dev.txt
```

## Coverage Goals

Target coverage: **80%+**

Current coverage by module:
- config.py: 100%
- orchestrator.py: 95%
- auth/azure.py: 90%
- mcp/tools.py: 95%
- prompts/business_analyst.py: 100%
- prompts/pyspark_engineer.py: 100%

## Troubleshooting

### Tests Failing Locally
1. Ensure you have installed test dependencies: `pip install -r requirements-dev.txt`
2. Check that you're running from the project root
3. Clear pytest cache: `pytest --cache-clear`

### Permission Errors
Tests use temporary directories that should be automatically cleaned up. If you encounter permission errors:
```bash
pytest --basetemp=/tmp/pytest-custom
```

### Import Errors
Ensure the package is installed in development mode:
```bash
pip install -e .
```
