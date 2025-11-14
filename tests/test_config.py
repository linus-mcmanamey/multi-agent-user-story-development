import os
from pathlib import Path
from typing import Dict

import pytest

from multi_agent_user_story_development.config import AgentConfig


class TestAgentConfig:
    """Test AgentConfig creation and configuration."""

    def test_agent_config_initialization(self, agent_config: AgentConfig):
        """Test that AgentConfig initializes with correct default values."""
        assert isinstance(agent_config.project_root, Path)
        assert isinstance(agent_config.data_root, Path)
        assert agent_config.project_root.exists()

    def test_agent_config_creates_required_directories(self, agent_config: AgentConfig):
        """Test that AgentConfig creates all required directories."""
        assert agent_config.documentation_output_dir.exists()
        assert agent_config.notebook_output_dir.exists()
        assert agent_config.memory_dir.exists()

    def test_agent_config_paths_configuration(self, agent_config: AgentConfig):
        """Test that all configuration paths are properly set."""
        assert agent_config.scafolding_dir == agent_config.project_root / ".claude" / "scafolding"
        assert agent_config.duckdb_path == agent_config.data_root / "warehouse.duckdb"
        assert agent_config.ddl_dir == agent_config.project_root / "documentation" / "ddl"
        assert agent_config.schema_parquet_dir == agent_config.project_root / "pipeline_output" / "schema"
        assert agent_config.documentation_output_dir == agent_config.project_root / ".claude" / "documentation"
        assert agent_config.notebook_output_dir == agent_config.project_root / ".claude" / "notebooks"
        assert agent_config.memory_dir == agent_config.project_root / ".claude" / "memory"
        assert agent_config.templates_dir == agent_config.project_root / "templates"
        assert agent_config.etl_template_path == agent_config.templates_dir / "etl_template.ipynb"

    def test_agent_config_from_environment(self, mock_env_vars: Dict[str, str]):
        """Test that AgentConfig loads values from environment variables."""
        config = AgentConfig()
        assert str(config.project_root) == mock_env_vars["AGENT_PROJECT_ROOT"]
        assert config.ado_organization == mock_env_vars["AZURE_DEVOPS_ORGANIZATION"]
        assert config.ado_project == mock_env_vars["AZURE_DEVOPS_PROJECT"]

    def test_get_ado_pat(self, agent_config: AgentConfig, mock_env_vars: Dict[str, str]):
        """Test retrieving Azure DevOps PAT from environment."""
        pat = agent_config.get_ado_pat()
        assert pat == mock_env_vars["AZURE_DEVOPS_PAT"]

    def test_get_ado_pat_missing(self, agent_config: AgentConfig):
        """Test retrieving PAT when environment variable is not set."""
        original_pat = os.environ.pop("AZURE_DEVOPS_PAT", None)
        try:
            pat = agent_config.get_ado_pat()
            assert pat is None
        finally:
            if original_pat:
                os.environ["AZURE_DEVOPS_PAT"] = original_pat


class TestAgentConfigDocumentation:
    """Test documentation-related methods."""

    def test_get_documentation_path(self, agent_config: AgentConfig):
        """Test getting documentation file path."""
        doc_path = agent_config.get_documentation_path("g_mg_occurrence")
        assert doc_path == agent_config.documentation_output_dir / "g_mg_occurrence.md"

    def test_get_documentation_path_with_extension(self, agent_config: AgentConfig):
        """Test getting documentation path when .md extension is provided."""
        doc_path = agent_config.get_documentation_path("g_mg_occurrence.md")
        assert doc_path == agent_config.documentation_output_dir / "g_mg_occurrence.md"
        assert str(doc_path).count(".md") == 1

    def test_documentation_exists(self, agent_config: AgentConfig, create_sample_documentation: callable):
        """Test checking if documentation exists."""
        create_sample_documentation("g_mg_occurrence")
        assert agent_config.documentation_exists("g_mg_occurrence") is True
        assert agent_config.documentation_exists("nonexistent_file") is False


class TestAgentConfigNotebook:
    """Test notebook-related methods."""

    def test_get_notebook_path(self, agent_config: AgentConfig):
        """Test getting notebook file path."""
        notebook_path = agent_config.get_notebook_path("g_mg_occurrence")
        assert notebook_path == agent_config.notebook_output_dir / "g_mg_occurrence.ipynb"

    def test_get_notebook_path_with_extension(self, agent_config: AgentConfig):
        """Test getting notebook path when .ipynb extension is provided."""
        notebook_path = agent_config.get_notebook_path("g_mg_occurrence.ipynb")
        assert notebook_path == agent_config.notebook_output_dir / "g_mg_occurrence.ipynb"
        assert str(notebook_path).count(".ipynb") == 1

    def test_notebook_exists(self, agent_config: AgentConfig):
        """Test checking if notebook exists."""
        notebook_path = agent_config.get_notebook_path("test_notebook")
        notebook_path.write_text('{"cells": []}')
        assert agent_config.notebook_exists("test_notebook") is True
        assert agent_config.notebook_exists("nonexistent_notebook") is False


class TestAgentConfigMemory:
    """Test memory-related methods."""

    def test_get_memory_path(self, agent_config: AgentConfig):
        """Test getting current memory file path."""
        memory_path = agent_config.get_memory_path("gold", "cms", "mg_occurrence")
        assert memory_path == agent_config.memory_dir / "gold" / "cms" / "mg_occurrence.md"

    def test_get_memory_path_creates_parent_directories(self, agent_config: AgentConfig):
        """Test that getting memory path creates parent directories."""
        memory_path = agent_config.get_memory_path("silver", "fvms", "fvms_incident")
        assert memory_path.parent.exists()

    def test_get_memory_history_path(self, agent_config: AgentConfig):
        """Test getting historical memory snapshot path."""
        history_path = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        assert history_path == agent_config.memory_dir / "gold" / "cms" / "mg_occurrence" / "history" / "US_12345.md"

    def test_get_memory_history_path_creates_directories(self, agent_config: AgentConfig):
        """Test that getting history path creates parent directories."""
        history_path = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        assert history_path.parent.exists()

    def test_list_memories_empty(self, agent_config: AgentConfig):
        """Test listing memories when none exist."""
        memories = agent_config.list_memories()
        assert memories == []

    def test_list_memories_all(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing all memories without filters."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("gold", "fvms", "mg_incident")
        create_sample_memory("silver", "cms", "cms_case")
        memories = agent_config.list_memories()
        assert len(memories) == 3

    def test_list_memories_filter_by_layer(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing memories filtered by layer."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("silver", "cms", "cms_case")
        gold_memories = agent_config.list_memories(layer="gold")
        assert len(gold_memories) == 1
        assert gold_memories[0].parts[-3] == "gold"

    def test_list_memories_filter_by_datasource(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing memories filtered by datasource."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("gold", "fvms", "mg_incident")
        cms_memories = agent_config.list_memories(layer="gold", datasource="cms")
        assert len(cms_memories) == 1
        assert cms_memories[0].parts[-2] == "cms"

    def test_list_memories_filter_by_table_name(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing memories filtered by table name."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("gold", "cms", "mg_incident")
        occurrence_memories = agent_config.list_memories(layer="gold", datasource="cms", table_name="mg_occurrence")
        assert len(occurrence_memories) == 1
        assert occurrence_memories[0].stem == "mg_occurrence"

    def test_list_memories_excludes_history_directory(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test that listing memories excludes files in history subdirectories."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        history_path = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_path.write_text("Historical snapshot")
        memories = agent_config.list_memories(layer="gold", datasource="cms")
        assert len(memories) == 1
        assert "history" not in memories[0].parts

    def test_list_memory_history_empty(self, agent_config: AgentConfig):
        """Test listing memory history when none exist."""
        histories = agent_config.list_memory_history()
        assert histories == []

    def test_list_memory_history_all(self, agent_config: AgentConfig):
        """Test listing all historical snapshots without filters."""
        history_path_1 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_path_1.write_text("Snapshot 1")
        history_path_2 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12346")
        history_path_2.write_text("Snapshot 2")
        histories = agent_config.list_memory_history()
        assert len(histories) == 2

    def test_list_memory_history_filter_by_table(self, agent_config: AgentConfig):
        """Test listing historical snapshots filtered by table name."""
        history_path_1 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_path_1.write_text("Snapshot 1")
        history_path_2 = agent_config.get_memory_history_path("gold", "cms", "mg_incident", "12346")
        history_path_2.write_text("Snapshot 2")
        histories = agent_config.list_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence")
        assert len(histories) == 1
        assert histories[0].stem == "US_12345"

    def test_list_memory_history_sorted(self, agent_config: AgentConfig):
        """Test that historical snapshots are returned sorted."""
        history_path_3 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12347")
        history_path_3.write_text("Snapshot 3")
        history_path_1 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_path_1.write_text("Snapshot 1")
        history_path_2 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12346")
        history_path_2.write_text("Snapshot 2")
        histories = agent_config.list_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence")
        assert len(histories) == 3
        assert histories[0].stem == "US_12345"
        assert histories[1].stem == "US_12346"
        assert histories[2].stem == "US_12347"
