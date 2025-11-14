import json
import subprocess
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, call, patch

import pytest

from multi_agent_user_story_development.config import AgentConfig
from multi_agent_user_story_development.orchestrator import (
    check_claude_cli,
    run_business_analyst,
    run_orchestrator,
    run_pyspark_engineer,
    setup_logging,
)


class TestSetupLogging:
    """Test logging configuration for orchestrator."""

    def test_setup_logging_configures_logger(self):
        """Test that setup_logging properly configures the logger."""
        setup_logging()


class TestCheckClaudeCLI:
    """Test Claude CLI availability checks."""

    def test_check_claude_cli_success(self, mock_claude_cli: Mock):
        """Test successful Claude CLI detection."""
        mock_claude_cli.return_value.returncode = 0
        mock_claude_cli.return_value.stdout = "claude version 1.0.0\n"
        assert check_claude_cli() is True
        mock_claude_cli.assert_called_once()
        assert mock_claude_cli.call_args[0][0] == ["claude", "--version"]

    def test_check_claude_cli_not_installed(self):
        """Test behavior when Claude CLI is not installed."""
        with patch("multi_agent_user_story_development.orchestrator.subprocess.run", side_effect=FileNotFoundError()):
            assert check_claude_cli() is False

    def test_check_claude_cli_returns_error(self, mock_claude_cli: Mock):
        """Test behavior when Claude CLI returns non-zero exit code."""
        mock_claude_cli.return_value.returncode = 1
        assert check_claude_cli() is False


class TestRunBusinessAnalyst:
    """Test business analyst agent execution."""

    def test_run_business_analyst_success(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test successful business analyst agent execution."""
        doc_path = create_sample_documentation("g_mg_occurrence_implementation_specs")
        mock_claude_cli.return_value.returncode = 0
        result = run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is True
        assert doc_path.exists()
        assert mock_claude_cli.called
        call_args = mock_claude_cli.call_args[0][0]
        assert call_args[0] == "claude"
        assert "-p" in call_args
        assert "--dangerously-skip-permissions" in call_args

    def test_run_business_analyst_creates_prompt_file(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test that business analyst creates prompt file before execution."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        mock_claude_cli.return_value.returncode = 0
        run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        prompt_file = agent_config.project_root / ".claude" / "scafolding" / "output" / "ba_prompt_g_mg_occurrence.txt"
        assert prompt_file.exists()
        prompt_content = prompt_file.read_text()
        assert "User Story ID**: 12345" in prompt_content
        assert "g_mg_occurrence" in prompt_content

    def test_run_business_analyst_creates_mcp_config(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test that business analyst creates MCP config file."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        claude_config = {"projects": {str(agent_config.project_root): {"mcpServers": {"test_server": {"command": "test", "args": []}}}}}
        claude_config_file = agent_config.project_root / ".claude.json"
        claude_config_file.write_text(json.dumps(claude_config))
        mock_claude_cli.return_value.returncode = 0
        run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        mcp_config_file = agent_config.project_root / ".claude" / "scafolding" / "output" / "mcp_config.json"
        assert mcp_config_file.exists()
        mcp_config = json.loads(mcp_config_file.read_text())
        assert "mcpServers" in mcp_config
        assert "test_server" in mcp_config["mcpServers"]

    def test_run_business_analyst_creates_settings_file(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test that business analyst creates agent settings file."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        mock_claude_cli.return_value.returncode = 0
        run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        settings_file = agent_config.project_root / ".claude" / "scafolding" / "output" / "agent_settings.json"
        assert settings_file.exists()
        settings = json.loads(settings_file.read_text())
        assert "permissions" in settings
        assert "allow" in settings["permissions"]
        assert "mcp__*" in settings["permissions"]["allow"]

    def test_run_business_analyst_timeout(self, agent_config: AgentConfig, mock_claude_cli: Mock):
        """Test business analyst agent timeout handling."""
        mock_claude_cli.side_effect = subprocess.TimeoutExpired("claude", 1200)
        result = run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is False

    def test_run_business_analyst_failure(self, agent_config: AgentConfig, mock_claude_cli: Mock):
        """Test business analyst agent failure handling."""
        mock_claude_cli.return_value.returncode = 1
        result = run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is False

    def test_run_business_analyst_success_without_exact_doc_name(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test successful execution when documentation has alternate name."""
        create_sample_documentation("g_mg_occurrence_alternate_name")
        mock_claude_cli.return_value.returncode = 0
        result = run_business_analyst("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is True


class TestRunPySparkEngineer:
    """Test PySpark engineer agent execution."""

    def test_run_pyspark_engineer_success(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable, create_sample_python_file: callable):
        """Test successful PySpark engineer agent execution."""
        doc_path = create_sample_documentation("g_mg_occurrence_implementation_specs")
        python_file = create_sample_python_file("gold", "cms", "g_mg_occurrence")
        mock_claude_cli.return_value.returncode = 0
        result = run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is True
        assert doc_path.exists()
        assert python_file.exists()

    def test_run_pyspark_engineer_missing_documentation(self, agent_config: AgentConfig, mock_claude_cli: Mock):
        """Test PySpark engineer fails when documentation is missing."""
        result = run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is False
        mock_claude_cli.assert_not_called()

    def test_run_pyspark_engineer_creates_prompt_file(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable, create_sample_python_file: callable):
        """Test that PySpark engineer creates prompt file before execution."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        create_sample_python_file("gold", "cms", "g_mg_occurrence")
        mock_claude_cli.return_value.returncode = 0
        run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        prompt_file = agent_config.project_root / ".claude" / "scafolding" / "output" / "pyspark_prompt_g_mg_occurrence.txt"
        assert prompt_file.exists()
        prompt_content = prompt_file.read_text()
        assert "User Story ID**: 12345" in prompt_content
        assert "g_mg_occurrence" in prompt_content

    def test_run_pyspark_engineer_timeout(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test PySpark engineer agent timeout handling."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        mock_claude_cli.side_effect = subprocess.TimeoutExpired("claude", 1800)
        result = run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is False

    def test_run_pyspark_engineer_failure(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test PySpark engineer agent failure handling."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        mock_claude_cli.return_value.returncode = 1
        mock_claude_cli.return_value.stderr = "Error occurred"
        result = run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is False

    def test_run_pyspark_engineer_success_without_python_file(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test successful execution even when Python file is not created (permission issues)."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        mock_claude_cli.return_value.returncode = 0
        result = run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is True

    def test_run_pyspark_engineer_finds_alternate_doc_name(self, agent_config: AgentConfig, mock_claude_cli: Mock, create_sample_documentation: callable, create_sample_python_file: callable):
        """Test PySpark engineer finds documentation with alternate name."""
        create_sample_documentation("g_mg_occurrence_alternate_name")
        create_sample_python_file("gold", "cms", "g_mg_occurrence")
        mock_claude_cli.return_value.returncode = 0
        result = run_pyspark_engineer("12345", "g_mg_occurrence", "bronze", "gold", agent_config)
        assert result is True


class TestRunOrchestrator:
    """Test main orchestrator workflow."""

    def test_run_orchestrator_full_success(self, mock_claude_cli: Mock, mock_azure_auth: Mock, create_sample_documentation: callable, create_sample_python_file: callable):
        """Test full orchestrator workflow with both agents."""
        with patch("multi_agent_user_story_development.orchestrator.AzureLogin") as mock_auth_class:
            mock_auth = Mock()
            mock_auth.check_full_authentication.return_value = (True, {"azure_cli": True, "azure_devops": True})
            mock_auth_class.return_value = mock_auth
            with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
                mock_config = Mock()
                mock_config.project_root = Path("/tmp/test")
                mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
                mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
                mock_config_class.return_value = mock_config
                mock_config.documentation_output_dir.mkdir(parents=True, exist_ok=True)
                doc_path = mock_config.get_documentation_path("g_mg_occurrence")
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                doc_path.write_text("# Test documentation")
                (mock_config.project_root / "python_files" / "gold").mkdir(parents=True, exist_ok=True)
                (mock_config.project_root / "python_files" / "gold" / "g_mg_occurrence.py").write_text("# Test file")
                mock_claude_cli.return_value.returncode = 0
                exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=False)
                assert exit_code == 0
                assert mock_claude_cli.call_count >= 2

    def test_run_orchestrator_skip_auth(self, mock_claude_cli: Mock):
        """Test orchestrator with authentication check skipped."""
        with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
            mock_config = Mock()
            mock_config.project_root = Path("/tmp/test")
            mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
            mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
            mock_config_class.return_value = mock_config
            mock_config.documentation_output_dir.mkdir(parents=True, exist_ok=True)
            doc_path = mock_config.get_documentation_path("g_mg_occurrence")
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test documentation")
            (mock_config.project_root / "python_files" / "gold").mkdir(parents=True, exist_ok=True)
            (mock_config.project_root / "python_files" / "gold" / "g_mg_occurrence.py").write_text("# Test file")
            mock_claude_cli.return_value.returncode = 0
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True)
            assert exit_code == 0

    def test_run_orchestrator_skip_business_analyst(self, mock_claude_cli: Mock, create_sample_documentation: callable):
        """Test orchestrator skipping business analyst when documentation exists."""
        with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
            mock_config = Mock()
            mock_config.project_root = Path("/tmp/test")
            mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
            mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
            mock_config_class.return_value = mock_config
            mock_config.documentation_output_dir.mkdir(parents=True, exist_ok=True)
            doc_path = mock_config.get_documentation_path("g_mg_occurrence")
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test documentation")
            (mock_config.project_root / "python_files" / "gold").mkdir(parents=True, exist_ok=True)
            (mock_config.project_root / "python_files" / "gold" / "g_mg_occurrence.py").write_text("# Test file")
            mock_claude_cli.return_value.returncode = 0
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True, skip_business_analyst=True)
            assert exit_code == 0
            assert mock_claude_cli.call_count == 1

    def test_run_orchestrator_skip_business_analyst_no_docs(self):
        """Test orchestrator fails when skipping BA without existing documentation."""
        with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
            mock_config = Mock()
            mock_config.project_root = Path("/tmp/test")
            mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
            mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
            mock_config_class.return_value = mock_config
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True, skip_business_analyst=True)
            assert exit_code == 1

    def test_run_orchestrator_claude_cli_not_available(self):
        """Test orchestrator fails when Claude CLI is not available."""
        with patch("multi_agent_user_story_development.orchestrator.check_claude_cli", return_value=False):
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True)
            assert exit_code == 1

    def test_run_orchestrator_auth_failure(self):
        """Test orchestrator fails when Azure authentication is not valid."""
        with patch("multi_agent_user_story_development.orchestrator.AzureLogin") as mock_auth_class:
            mock_auth = Mock()
            mock_auth.check_full_authentication.return_value = (False, {"azure_cli": False, "azure_devops": False})
            mock_auth_class.return_value = mock_auth
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=False)
            assert exit_code == 1

    def test_run_orchestrator_business_analyst_failure(self, mock_claude_cli: Mock):
        """Test orchestrator fails when business analyst agent fails."""
        with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
            mock_config = Mock()
            mock_config.project_root = Path("/tmp/test")
            mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
            mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
            mock_config_class.return_value = mock_config
            mock_claude_cli.return_value.returncode = 1
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True)
            assert exit_code == 1

    def test_run_orchestrator_pyspark_engineer_failure(self, mock_claude_cli: Mock):
        """Test orchestrator fails when PySpark engineer agent fails."""
        with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
            mock_config = Mock()
            mock_config.project_root = Path("/tmp/test")
            mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
            mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
            mock_config_class.return_value = mock_config
            mock_config.documentation_output_dir.mkdir(parents=True, exist_ok=True)
            doc_path = mock_config.get_documentation_path("g_mg_occurrence")
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test documentation")

            def side_effect(*args, **kwargs):
                if args[0][0] == "claude" and any("ba_prompt" in str(arg) for arg in args[0]):
                    return Mock(returncode=0)
                return Mock(returncode=1)

            mock_claude_cli.side_effect = side_effect
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True)
            assert exit_code == 1

    def test_run_orchestrator_verbose_mode(self, mock_claude_cli: Mock):
        """Test orchestrator with verbose logging enabled."""
        with patch("multi_agent_user_story_development.orchestrator.AgentConfig") as mock_config_class:
            mock_config = Mock()
            mock_config.project_root = Path("/tmp/test")
            mock_config.documentation_output_dir = Path("/tmp/test/.claude/documentation")
            mock_config.get_documentation_path = Mock(return_value=Path("/tmp/test/.claude/documentation/g_mg_occurrence_implementation_specs.md"))
            mock_config_class.return_value = mock_config
            mock_config.documentation_output_dir.mkdir(parents=True, exist_ok=True)
            doc_path = mock_config.get_documentation_path("g_mg_occurrence")
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text("# Test documentation")
            (mock_config.project_root / "python_files" / "gold").mkdir(parents=True, exist_ok=True)
            (mock_config.project_root / "python_files" / "gold" / "g_mg_occurrence.py").write_text("# Test file")
            mock_claude_cli.return_value.returncode = 0
            exit_code = run_orchestrator(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", skip_auth=True, verbose=True)
            assert exit_code == 0
