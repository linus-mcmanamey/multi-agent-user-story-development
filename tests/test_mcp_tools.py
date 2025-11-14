import json
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from multi_agent_user_story_development.config import AgentConfig
from multi_agent_user_story_development.mcp.tools import (
    list_memories,
    list_memory_history,
    read_business_analysis,
    read_etl_template,
    read_memory,
    read_memory_history,
    write_memory,
)


class TestReadETLTemplate:
    """Test reading ETL template."""

    def test_read_etl_template_success(self, agent_config: AgentConfig):
        """Test successful reading of ETL template."""
        template_path = agent_config.etl_template_path
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_content = '{"cells": [], "metadata": {}}'
        template_path.write_text(template_content)
        result = read_etl_template()
        assert "isError" not in result or result["isError"] is False
        assert template_content in result["content"][0]["text"]

    def test_read_etl_template_not_found(self, agent_config: AgentConfig):
        """Test reading ETL template when file doesn't exist."""
        result = read_etl_template()
        assert result["isError"] is True
        assert "Error:" in result["content"][0]["text"]


class TestReadBusinessAnalysis:
    """Test reading business analysis documentation."""

    def test_read_business_analysis_success(self, agent_config: AgentConfig, create_sample_documentation: callable):
        """Test successful reading of business analysis documentation."""
        doc_path = create_sample_documentation("g_mg_occurrence_implementation_specs")
        result = read_business_analysis("g_mg_occurrence_implementation_specs")
        assert "isError" not in result or result["isError"] is False
        assert "Business Analysis path:" in result["content"][0]["text"]
        assert "Implementation Specifications" in result["content"][0]["text"]

    def test_read_business_analysis_not_found(self, agent_config: AgentConfig):
        """Test reading business analysis when file doesn't exist."""
        result = read_business_analysis("nonexistent_file")
        assert result["isError"] is True
        assert "Error:" in result["content"][0]["text"]

    def test_read_business_analysis_error_handling(self, agent_config: AgentConfig, create_sample_documentation: callable):
        """Test error handling when reading business analysis fails."""
        create_sample_documentation("g_mg_occurrence_implementation_specs")
        with patch.object(Path, "read_text", side_effect=PermissionError("Permission denied")):
            result = read_business_analysis("g_mg_occurrence_implementation_specs")
            assert result["isError"] is True
            assert "Error:" in result["content"][0]["text"]


class TestDeprecatedMCPTools:
    """Test deprecated MCP tools that should not be used."""

    def test_deprecated_tools_have_deprecation_notice(self):
        """Test that deprecated tools are properly marked."""
        from multi_agent_user_story_development.mcp.tools import (
            check_existing_documentation_DEPRECATED,
            check_existing_python_file_DEPRECATED,
            save_documentation_DEPRECATED,
            save_notebook_DEPRECATED,
        )
        assert "DEPRECATED" in check_existing_python_file_DEPRECATED.__name__
        assert "DEPRECATED" in check_existing_documentation_DEPRECATED.__name__
        assert "DEPRECATED" in save_documentation_DEPRECATED.__name__
        assert "DEPRECATED" in save_notebook_DEPRECATED.__name__


class TestMCPToolsIntegration:
    """Integration tests for MCP tools workflow."""

    def test_full_memory_workflow(self, agent_config: AgentConfig):
        """Test complete memory workflow: create, read, update, list."""
        content_1 = """## Summary
Initial table summary.

## Key Requirements
- Initial requirement 1
- Initial requirement 2
"""
        write_result_1 = write_memory(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12345", content=content_1)
        assert "isError" not in write_result_1 or write_result_1["isError"] is False
        read_result_1 = read_memory(layer="gold", datasource="cms", table_name="mg_occurrence")
        assert "isError" not in read_result_1 or read_result_1["isError"] is False
        assert "Initial table summary" in read_result_1["content"][0]["text"]
        content_2 = """## Summary
Updated table summary with new information.

## Key Requirements
- Updated requirement 1
- Updated requirement 2
- New requirement 3
"""
        write_result_2 = write_memory(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12346", content=content_2)
        assert "isError" not in write_result_2 or write_result_2["isError"] is False
        read_result_2 = read_memory(layer="gold", datasource="cms", table_name="mg_occurrence")
        assert "Updated table summary with new information" in read_result_2["content"][0]["text"]
        assert "US:12345" in read_result_2["content"][0]["text"]
        assert "US:12346" in read_result_2["content"][0]["text"]
        history_result = read_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12346")
        assert "isError" not in history_result or history_result["isError"] is False
        assert "Initial table summary" in history_result["content"][0]["text"]
        list_result = list_memories(layer="gold", datasource="cms")
        memory_list = json.loads(list_result["content"][0]["text"])
        assert len(memory_list) >= 1
        assert any(m["table"] == "mg_occurrence" for m in memory_list)
        list_history_result = list_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence")
        history_list = json.loads(list_history_result["content"][0]["text"])
        assert len(history_list) >= 1
        assert any(h["user_story"] == "12346" for h in history_list)

    def test_cross_layer_memory_isolation(self, agent_config: AgentConfig):
        """Test that memories are isolated by layer and datasource."""
        write_memory(layer="gold", datasource="cms", table_name="occurrence", user_story="12345", content="## Summary\nGold CMS")
        write_memory(layer="gold", datasource="fvms", table_name="occurrence", user_story="12346", content="## Summary\nGold FVMS")
        write_memory(layer="silver", datasource="cms", table_name="occurrence", user_story="12347", content="## Summary\nSilver CMS")
        cms_gold_result = read_memory(layer="gold", datasource="cms", table_name="occurrence")
        assert "Gold CMS" in cms_gold_result["content"][0]["text"]
        fvms_gold_result = read_memory(layer="gold", datasource="fvms", table_name="occurrence")
        assert "Gold FVMS" in fvms_gold_result["content"][0]["text"]
        cms_silver_result = read_memory(layer="silver", datasource="cms", table_name="occurrence")
        assert "Silver CMS" in cms_silver_result["content"][0]["text"]
        gold_list = list_memories(layer="gold")
        gold_memories = json.loads(gold_list["content"][0]["text"])
        assert len(gold_memories) == 2
        cms_gold_list = list_memories(layer="gold", datasource="cms")
        cms_gold_memories = json.loads(cms_gold_list["content"][0]["text"])
        assert len(cms_gold_memories) == 1
        assert cms_gold_memories[0]["datasource"] == "cms"

    def test_memory_changelog_accumulation(self, agent_config: AgentConfig):
        """Test that changelog accumulates across multiple user stories."""
        write_memory(layer="gold", datasource="cms", table_name="test_table", user_story="12345", content="## Summary\nVersion 1")
        write_memory(layer="gold", datasource="cms", table_name="test_table", user_story="12346", content="## Summary\nVersion 2")
        write_memory(layer="gold", datasource="cms", table_name="test_table", user_story="12347", content="## Summary\nVersion 3")
        read_result = read_memory(layer="gold", datasource="cms", table_name="test_table")
        content = read_result["content"][0]["text"]
        assert "US:12345" in content
        assert "US:12346" in content
        assert "US:12347" in content
        assert "## Changelog" in content
        list_history_result = list_memory_history(layer="gold", datasource="cms", table_name="test_table")
        history_list = json.loads(list_history_result["content"][0]["text"])
        assert len(history_list) >= 2
        us_numbers = [h["user_story"] for h in history_list]
        assert "12346" in us_numbers
        assert "12347" in us_numbers
