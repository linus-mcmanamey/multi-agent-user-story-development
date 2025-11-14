import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AgentConfig:
    """Configuration for agent workflow orchestration. Paths are configurable via environment variables or defaults to plugin-relative paths."""

    data_root: Path = field(default_factory=lambda: Path(os.getenv("AGENT_DATA_ROOT", "/workspaces/data")))
    project_root: Path = field(default_factory=lambda: Path(os.getenv("AGENT_PROJECT_ROOT", os.getcwd())))
    scafolding_dir: Path = field(init=False)
    duckdb_path: Path = field(init=False)
    ddl_dir: Path = field(init=False)
    schema_parquet_dir: Path = field(init=False)
    documentation_output_dir: Path = field(init=False)
    notebook_output_dir: Path = field(init=False)
    memory_dir: Path = field(init=False)
    templates_dir: Path = field(init=False)
    etl_template_path: Path = field(init=False)
    ado_organization: str = field(default_factory=lambda: os.getenv("AZURE_DEVOPS_ORGANIZATION", "https://dev.azure.com/emstas"))
    ado_project: str = field(default_factory=lambda: os.getenv("AZURE_DEVOPS_PROJECT", "Program Unify"))

    def __post_init__(self) -> None:
        self.scafolding_dir = self.project_root / ".claude" / "scafolding"
        self.duckdb_path = self.data_root / "warehouse.duckdb"
        self.ddl_dir = self.project_root / "documentation" / "ddl"
        self.schema_parquet_dir = self.project_root / "pipeline_output" / "schema"
        self.documentation_output_dir = self.project_root / ".claude" / "documentation"
        self.notebook_output_dir = self.project_root / ".claude" / "notebooks"
        self.memory_dir = self.project_root / ".claude" / "memory"
        self.templates_dir = self.project_root / "templates"
        self.etl_template_path = self.templates_dir / "etl_template.ipynb"
        self.documentation_output_dir.mkdir(parents=True, exist_ok=True)
        self.notebook_output_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def get_ado_pat(self) -> Optional[str]:
        """Get Azure DevOps PAT from environment."""
        return os.getenv("AZURE_DEVOPS_PAT")

    def get_documentation_path(self, file_name: str) -> Path:
        """Get path for documentation file."""
        if not file_name.endswith(".md"):
            file_name = f"{file_name}.md"
        return self.documentation_output_dir / file_name

    def get_notebook_path(self, file_name: str) -> Path:
        """Get path for notebook file."""
        if not file_name.endswith(".ipynb"):
            file_name = f"{file_name}.ipynb"
        return self.notebook_output_dir / file_name

    def documentation_exists(self, file_name: str) -> bool:
        """Check if documentation file exists."""
        return self.get_documentation_path(file_name).exists()

    def notebook_exists(self, file_name: str) -> bool:
        """Check if notebook file exists."""
        return self.get_notebook_path(file_name).exists()

    def get_memory_path(self, layer: str, datasource: str, table_name: str) -> Path:
        """Get path for current table memory state (single file per table)."""
        memory_layer_path = self.memory_dir / layer / datasource
        memory_layer_path.mkdir(parents=True, exist_ok=True)
        return memory_layer_path / f"{table_name}.md"

    def get_memory_history_path(self, layer: str, datasource: str, table_name: str, user_story: str) -> Path:
        """Get path for historical user story snapshot."""
        history_path = self.memory_dir / layer / datasource / table_name / "history"
        history_path.mkdir(parents=True, exist_ok=True)
        return history_path / f"US_{user_story}.md"

    def list_memories(self, layer: Optional[str] = None, datasource: Optional[str] = None, table_name: Optional[str] = None) -> list[Path]:
        """List all memory files (current table states), optionally filtered by layer/datasource/table."""
        search_path = self.memory_dir
        if layer:
            search_path = search_path / layer
        if datasource:
            search_path = search_path / datasource
        if not search_path.exists():
            return []
        if table_name:
            target_file = search_path / f"{table_name}.md"
            return [target_file] if target_file.exists() else []
        return sorted([p for p in search_path.rglob("*.md") if "history" not in p.parts])

    def list_memory_history(self, layer: Optional[str] = None, datasource: Optional[str] = None, table_name: Optional[str] = None) -> list[Path]:
        """List all historical memory snapshots, optionally filtered by layer/datasource/table."""
        search_path = self.memory_dir
        if layer:
            search_path = search_path / layer
        if datasource:
            search_path = search_path / datasource
        if table_name:
            search_path = search_path / table_name / "history"
        if not search_path.exists():
            return []
        return sorted(search_path.rglob("US_*.md"))
