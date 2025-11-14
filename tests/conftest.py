import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, Mock

import pytest

from multi_agent_user_story_development.config import AgentConfig


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary project directory with standard structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / ".claude" / "scafolding" / "output").mkdir(parents=True, exist_ok=True)
        (project_root / ".claude" / "documentation").mkdir(parents=True, exist_ok=True)
        (project_root / ".claude" / "memory").mkdir(parents=True, exist_ok=True)
        (project_root / ".claude" / "notebooks").mkdir(parents=True, exist_ok=True)
        (project_root / ".claude" / "data_dictionary").mkdir(parents=True, exist_ok=True)
        (project_root / "python_files" / "bronze").mkdir(parents=True, exist_ok=True)
        (project_root / "python_files" / "silver" / "silver_cms").mkdir(parents=True, exist_ok=True)
        (project_root / "python_files" / "gold").mkdir(parents=True, exist_ok=True)
        (project_root / "templates").mkdir(parents=True, exist_ok=True)
        (project_root / "documentation" / "ddl").mkdir(parents=True, exist_ok=True)
        (project_root / "pipeline_output" / "schema").mkdir(parents=True, exist_ok=True)
        yield project_root


@pytest.fixture
def mock_env_vars(temp_project_dir: Path) -> Generator[Dict[str, str], None, None]:
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    test_env = {
        "AGENT_PROJECT_ROOT": str(temp_project_dir),
        "AGENT_DATA_ROOT": str(temp_project_dir / "data"),
        "AZURE_DEVOPS_PAT": "test_pat_token_12345",
        "AZURE_DEVOPS_ORGANIZATION": "https://dev.azure.com/emstas",
        "AZURE_DEVOPS_PROJECT": "Program Unify",
    }
    os.environ.update(test_env)
    yield test_env
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def agent_config(mock_env_vars: Dict[str, str]) -> AgentConfig:
    """Create an AgentConfig instance with test environment."""
    return AgentConfig()


@pytest.fixture
def sample_user_story_data() -> Dict[str, Any]:
    """Sample user story data from Azure DevOps."""
    return {
        "id": 12345,
        "fields": {
            "System.Title": "Create gold layer occurrence table",
            "System.Description": "Implement g_mg_occurrence table combining CMS and FVMS data sources",
            "System.State": "Active",
            "System.AssignedTo": {"displayName": "Test User"},
            "Microsoft.VSTS.Common.AcceptanceCriteria": "- Table should include all occurrences from both systems\n- Apply deduplication logic\n- Include verification flags",
            "System.Parent": 12340,
        },
        "relations": [{"rel": "System.LinkTypes.Hierarchy-Reverse", "url": "https://dev.azure.com/emstas/_apis/wit/workItems/12340"}],
    }


@pytest.fixture
def sample_documentation_content() -> str:
    """Sample business analyst documentation content."""
    return """# g_mg_occurrence - Implementation Specifications

## User Story: US:12345
Create gold layer occurrence table combining CMS and FVMS data sources.

## Data Dictionary Reference
### Source Tables
- cms_case: Case management system records
- fvms_incident: FVMS incident records

## DuckDB Current Schema
### bronze_cms.b_cms_case
- case_id: VARCHAR(50), NOT NULL, PRIMARY KEY
- description: VARCHAR(500)
- created_date: TIMESTAMP

### bronze_fvms.b_fvms_incident
- incident_id: VARCHAR(50), NOT NULL, PRIMARY KEY
- incident_type: VARCHAR(100)
- occurred_date: TIMESTAMP

## Schema Analysis
No major discrepancies found. NULL handling matches data dictionary.

## Data Architecture
Source: bronze_cms.b_cms_case, bronze_fvms.b_fvms_incident
Target: gold.g_mg_occurrence

## Transformation Logic
1. Extract data from both bronze layers
2. Standardize date fields
3. Apply deduplication using row hash
4. Combine using union operation

## Implementation Notes
- Use full outer join for linkage
- Apply verification flags
- Include source system identifier

## Testing Requirements
- Verify record counts match expected totals
- Confirm no duplicate records
- Validate date standardization
"""


@pytest.fixture
def sample_memory_content() -> str:
    """Sample table memory content."""
    return """# Memory: mg_occurrence
**Layer**: gold | **Datasource**: cms

## Changelog
- US:12340 - Initial creation
- US:12345 - Updated 2025-11-14

---

## Summary
Gold layer occurrence table combining CMS and FVMS incident data with deduplication and verification.

## Key Requirements
- Combine data from both CMS and FVMS systems
- Apply deduplication logic based on row hash
- Include verification flags for data quality

## Data Transformations
- **Source tables**: bronze_cms.b_cms_case, bronze_fvms.b_fvms_incident
- **Target table**: gold.g_mg_occurrence
- **Key logic**: Full outer join with verification filtering

## Business Rules
- All occurrences from both systems must be included
- Duplicate records removed using row hash
- NULL values preserved where applicable

## Data Quality Rules
- Verification flag must be 1 for valid records
- Date fields must be valid timestamps
- Required fields cannot be NULL

## Related Tables
- bronze_cms.b_cms_case
- bronze_fvms.b_fvms_incident
- bronze_cms.b_cms_incident_to_or (linkage)

## Gotchas & Special Considerations
- Use full outer join pattern from g_ya_mg_occurence.py reference
- Ensure all records from both systems are captured
- Verification flag filtering critical for data quality
"""


@pytest.fixture
def mock_azure_auth() -> Generator[Mock, None, None]:
    """Mock Azure authentication checks."""
    with pytest.mock.patch("multi_agent_user_story_development.auth.azure.subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"accessToken": "test_token"}'
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_claude_cli() -> Generator[Mock, None, None]:
    """Mock Claude CLI subprocess calls."""
    with pytest.mock.patch("multi_agent_user_story_development.orchestrator.subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def create_sample_python_file(temp_project_dir: Path) -> callable:
    """Factory fixture to create sample Python files for testing."""

    def _create_file(layer: str, datasource: str, file_name: str, content: str = None) -> Path:
        if layer == "gold":
            file_path = temp_project_dir / "python_files" / "gold" / f"{file_name}.py"
        else:
            file_path = temp_project_dir / "python_files" / layer / f"{layer}_{datasource}" / f"{file_name}.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if content is None:
            content = f'''from pyspark.sql import DataFrame

class {layer.capitalize()}Loader:
    def __init__(self, {layer}_table_name: str):
        self.{layer}_table_name = {layer}_table_name

    def extract(self) -> DataFrame:
        #### US: 12340
        return spark.read.table(self.{layer}_table_name)

    def transform(self) -> DataFrame:
        #### US: 12340
        return self.extract_sdf

    def load(self) -> None:
        pass
'''
        file_path.write_text(content)
        return file_path

    return _create_file


@pytest.fixture
def create_sample_documentation(temp_project_dir: Path, sample_documentation_content: str) -> callable:
    """Factory fixture to create sample documentation files."""

    def _create_doc(file_name: str, content: str = None) -> Path:
        doc_path = temp_project_dir / ".claude" / "documentation" / f"{file_name}.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        if content is None:
            content = sample_documentation_content
        doc_path.write_text(content)
        return doc_path

    return _create_doc


@pytest.fixture
def create_sample_memory(temp_project_dir: Path, sample_memory_content: str) -> callable:
    """Factory fixture to create sample memory files."""

    def _create_memory(layer: str, datasource: str, table_name: str, content: str = None) -> Path:
        memory_path = temp_project_dir / ".claude" / "memory" / layer / datasource / f"{table_name}.md"
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        if content is None:
            content = sample_memory_content
        memory_path.write_text(content)
        return memory_path

    return _create_memory


@pytest.fixture
def mock_mcp_server_response() -> Dict[str, Any]:
    """Mock MCP server response for tool calls."""
    return {"content": [{"type": "text", "text": "Mock MCP response"}], "isError": False}


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset AgentConfig singleton between tests to avoid state pollution."""
    yield
