from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

import pytest

from multi_agent_user_story_development.config import AgentConfig
from multi_agent_user_story_development.mcp.tools import (
    _merge_memory_content,
    list_memories,
    list_memory_history,
    read_memory,
    read_memory_history,
    write_memory,
)


class TestWriteMemory:
    """Test memory write operations."""

    def test_write_memory_creates_new_memory(self, agent_config: AgentConfig):
        """Test creating new memory for a table."""
        content = """## Summary
Gold layer occurrence table combining CMS and FVMS data.

## Key Requirements
- Combine data from both systems
- Apply deduplication logic
"""
        result = write_memory(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12345", content=content)
        assert "isError" not in result or result["isError"] is False
        assert "Memory created" in result["content"][0]["text"]
        memory_path = agent_config.get_memory_path("gold", "cms", "mg_occurrence")
        assert memory_path.exists()
        memory_content = memory_path.read_text()
        assert "# Memory: mg_occurrence" in memory_content
        assert "**Layer**: gold" in memory_content
        assert "**Datasource**: cms" in memory_content
        assert "## Changelog" in memory_content
        assert "US:12345 - Initial creation" in memory_content
        assert "Gold layer occurrence table" in memory_content

    def test_write_memory_updates_existing_memory(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test updating existing memory with new user story content."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        new_content = """## Summary
Updated summary with new requirements from US:12346.

## Key Requirements
- New requirement from US:12346
- Additional validation rule
"""
        result = write_memory(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12346", content=new_content)
        assert "isError" not in result or result["isError"] is False
        assert "Memory updated" in result["content"][0]["text"]
        memory_path = agent_config.get_memory_path("gold", "cms", "mg_occurrence")
        memory_content = memory_path.read_text()
        assert "US:12346 - Updated" in memory_content
        assert "Updated summary with new requirements" in memory_content

    def test_write_memory_archives_previous_state(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test that previous memory state is archived to history."""
        original_memory = create_sample_memory("gold", "cms", "mg_occurrence")
        original_content = original_memory.read_text()
        new_content = """## Summary
Updated content for US:12346.
"""
        write_memory(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12346", content=new_content)
        history_path = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12346")
        assert history_path.exists()
        history_content = history_path.read_text()
        assert "# Historical Snapshot - Before US:12346" in history_content
        assert original_content in history_content

    def test_write_memory_error_handling(self, agent_config: AgentConfig):
        """Test error handling when memory write fails."""
        with patch.object(Path, "write_text", side_effect=PermissionError("Permission denied")):
            result = write_memory(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12345", content="Test content")
            assert result["isError"] is True
            assert "Error:" in result["content"][0]["text"]


class TestReadMemory:
    """Test memory read operations."""

    def test_read_memory_success(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test reading existing memory successfully."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        result = read_memory(layer="gold", datasource="cms", table_name="mg_occurrence")
        assert "isError" not in result or result["isError"] is False
        assert "Current memory for mg_occurrence" in result["content"][0]["text"]
        assert "Gold layer occurrence table" in result["content"][0]["text"]

    def test_read_memory_not_found(self, agent_config: AgentConfig):
        """Test reading memory when it doesn't exist."""
        result = read_memory(layer="gold", datasource="cms", table_name="nonexistent_table")
        assert result["isError"] is True
        assert "No memory found" in result["content"][0]["text"]

    def test_read_memory_error_handling(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test error handling when memory read fails."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        with patch.object(Path, "read_text", side_effect=PermissionError("Permission denied")):
            result = read_memory(layer="gold", datasource="cms", table_name="mg_occurrence")
            assert result["isError"] is True
            assert "Error:" in result["content"][0]["text"]


class TestReadMemoryHistory:
    """Test historical memory snapshot read operations."""

    def test_read_memory_history_success(self, agent_config: AgentConfig):
        """Test reading historical memory snapshot successfully."""
        history_path = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_content = """# Historical Snapshot - Before US:12346

## Summary
Original summary before update.
"""
        history_path.write_text(history_content)
        result = read_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="12345")
        assert "isError" not in result or result["isError"] is False
        assert "Historical snapshot for US 12345" in result["content"][0]["text"]
        assert "Original summary before update" in result["content"][0]["text"]

    def test_read_memory_history_not_found(self, agent_config: AgentConfig):
        """Test reading history when it doesn't exist."""
        result = read_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence", user_story="99999")
        assert result["isError"] is True
        assert "No historical snapshot found" in result["content"][0]["text"]


class TestListMemories:
    """Test listing current table memories."""

    def test_list_memories_all(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing all memories without filters."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("gold", "fvms", "mg_incident")
        create_sample_memory("silver", "cms", "cms_case")
        result = list_memories()
        assert "isError" not in result or result["isError"] is False
        import json
        memory_list = json.loads(result["content"][0]["text"])
        assert len(memory_list) >= 3
        assert any(m["table"] == "mg_occurrence" for m in memory_list)
        assert any(m["table"] == "mg_incident" for m in memory_list)
        assert any(m["table"] == "cms_case" for m in memory_list)

    def test_list_memories_filter_by_layer(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing memories filtered by layer."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("silver", "cms", "cms_case")
        result = list_memories(layer="gold")
        import json
        memory_list = json.loads(result["content"][0]["text"])
        assert all(m["layer"] == "gold" for m in memory_list)
        assert any(m["table"] == "mg_occurrence" for m in memory_list)

    def test_list_memories_filter_by_datasource(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing memories filtered by datasource."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("gold", "fvms", "mg_incident")
        result = list_memories(layer="gold", datasource="cms")
        import json
        memory_list = json.loads(result["content"][0]["text"])
        assert all(m["datasource"] == "cms" for m in memory_list)
        assert any(m["table"] == "mg_occurrence" for m in memory_list)

    def test_list_memories_filter_by_table_name(self, agent_config: AgentConfig, create_sample_memory: callable):
        """Test listing memories filtered by table name."""
        create_sample_memory("gold", "cms", "mg_occurrence")
        create_sample_memory("gold", "cms", "mg_incident")
        result = list_memories(layer="gold", datasource="cms", table_name="mg_occurrence")
        import json
        memory_list = json.loads(result["content"][0]["text"])
        assert len(memory_list) == 1
        assert memory_list[0]["table"] == "mg_occurrence"

    def test_list_memories_empty_result(self, agent_config: AgentConfig):
        """Test listing memories when none exist."""
        result = list_memories(layer="gold", datasource="cms")
        assert "No memories found" in result["content"][0]["text"]


class TestListMemoryHistory:
    """Test listing historical memory snapshots."""

    def test_list_memory_history_all(self, agent_config: AgentConfig):
        """Test listing all historical snapshots without filters."""
        history_path_1 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_path_1.write_text("Historical snapshot 1")
        history_path_2 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12346")
        history_path_2.write_text("Historical snapshot 2")
        result = list_memory_history()
        import json
        history_list = json.loads(result["content"][0]["text"])
        assert len(history_list) >= 2
        assert any(h["user_story"] == "12345" for h in history_list)
        assert any(h["user_story"] == "12346" for h in history_list)

    def test_list_memory_history_filter_by_table(self, agent_config: AgentConfig):
        """Test listing historical snapshots filtered by table name."""
        history_path_1 = agent_config.get_memory_history_path("gold", "cms", "mg_occurrence", "12345")
        history_path_1.write_text("Historical snapshot 1")
        history_path_2 = agent_config.get_memory_history_path("gold", "cms", "mg_incident", "12346")
        history_path_2.write_text("Historical snapshot 2")
        result = list_memory_history(layer="gold", datasource="cms", table_name="mg_occurrence")
        import json
        history_list = json.loads(result["content"][0]["text"])
        assert all(h["table"] == "mg_occurrence" for h in history_list)
        assert any(h["user_story"] == "12345" for h in history_list)

    def test_list_memory_history_empty_result(self, agent_config: AgentConfig):
        """Test listing history when none exist."""
        result = list_memory_history(layer="gold", datasource="cms", table_name="nonexistent")
        assert "No historical snapshots found" in result["content"][0]["text"]


class TestMergeMemoryContent:
    """Test memory content merge logic."""

    def test_merge_memory_updates_changelog(self):
        """Test that merge adds new user story to changelog."""
        existing = """# Memory: mg_occurrence

## Changelog
- US:12345 - Initial creation

---

## Summary
Original summary.
"""
        new_content = """## Summary
Updated summary.
"""
        merged = _merge_memory_content(existing, new_content, "12346")
        assert "US:12345 - Initial creation" in merged
        assert "US:12346 - Updated" in merged

    def test_merge_memory_updates_summary_section(self):
        """Test that merge updates the Summary section."""
        existing = """# Memory: mg_occurrence

## Changelog
- US:12345 - Initial creation

---

## Summary
Original summary.

## Key Requirements
- Original requirement
"""
        new_content = """## Summary
Updated summary with new information.
"""
        merged = _merge_memory_content(existing, new_content, "12346")
        assert "Updated summary with new information" in merged
        assert "Original summary" not in merged

    def test_merge_memory_preserves_unchanged_sections(self):
        """Test that merge preserves sections not included in new content."""
        existing = """# Memory: mg_occurrence

## Changelog
- US:12345 - Initial creation

---

## Summary
Original summary.

## Key Requirements
- Original requirement

## Business Rules
- Original business rule
"""
        new_content = """## Summary
Updated summary.
"""
        merged = _merge_memory_content(existing, new_content, "12346")
        assert "Updated summary" in merged
        assert "Original requirement" in merged
        assert "Original business rule" in merged

    def test_merge_memory_adds_new_sections(self):
        """Test that merge adds sections that don't exist in original."""
        existing = """# Memory: mg_occurrence

## Changelog
- US:12345 - Initial creation

---

## Summary
Original summary.
"""
        new_content = """## Summary
Updated summary.

## Gotchas & Special Considerations
- New gotcha from US:12346
"""
        merged = _merge_memory_content(existing, new_content, "12346")
        assert "Updated summary" in merged
        assert "## Gotchas & Special Considerations" in merged
        assert "New gotcha from US:12346" in merged

    def test_merge_memory_handles_missing_changelog(self):
        """Test that merge creates changelog if it doesn't exist."""
        existing = """# Memory: mg_occurrence

---

## Summary
Original summary.
"""
        new_content = """## Summary
Updated summary.
"""
        merged = _merge_memory_content(existing, new_content, "12346")
        assert "## Changelog" in merged
        assert "US:12346 - Updated" in merged

    def test_merge_memory_updates_multiple_sections(self):
        """Test that merge updates multiple sections at once."""
        existing = """# Memory: mg_occurrence

## Changelog
- US:12345 - Initial creation

---

## Summary
Original summary.

## Key Requirements
- Original requirement

## Business Rules
- Original rule
"""
        new_content = """## Summary
Updated summary.

## Key Requirements
- Updated requirement 1
- Updated requirement 2

## Data Quality Rules
- New validation rule
"""
        merged = _merge_memory_content(existing, new_content, "12346")
        assert "Updated summary" in merged
        assert "Updated requirement 1" in merged
        assert "Updated requirement 2" in merged
        assert "New validation rule" in merged
        assert "Original requirement" not in merged
