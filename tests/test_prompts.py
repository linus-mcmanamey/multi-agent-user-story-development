from pathlib import Path

import pytest

from multi_agent_user_story_development.prompts.business_analyst import business_analyst_prompt
from multi_agent_user_story_development.prompts.pyspark_engineer import generate_implementation_prompt


class TestBusinessAnalystPrompt:
    """Test business analyst prompt generation."""

    def test_business_analyst_prompt_basic_structure(self):
        """Test that business analyst prompt contains all required sections."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "# Azure DevOps User Story Analysis & Implementation Planning" in prompt
        assert "@business-analyst" in prompt
        assert "## CONTEXT" in prompt
        assert "## PRIMARY OBJECTIVE" in prompt
        assert "## EXECUTION WORKFLOW" in prompt
        assert "## OUTPUT REQUIREMENTS" in prompt

    def test_business_analyst_prompt_includes_user_story_id(self):
        """Test that prompt includes the provided user story ID."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "User Story ID**: 12345" in prompt

    def test_business_analyst_prompt_includes_file_name(self):
        """Test that prompt includes the target file name."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "Target File**: `g_mg_occurrence.py`" in prompt
        assert "g_mg_occurrence" in prompt

    def test_business_analyst_prompt_includes_data_layers(self):
        """Test that prompt includes read and write layers."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "Data Flow**: bronze to gold" in prompt

    def test_business_analyst_prompt_detects_cms_datasource(self):
        """Test that prompt correctly detects CMS datasource from file name."""
        prompt = business_analyst_prompt(user_story="12345", file_name="s_cms_case", read_layer="bronze", write_layer="silver")
        assert "Data Source**: CMS" in prompt

    def test_business_analyst_prompt_detects_fvms_datasource(self):
        """Test that prompt correctly detects FVMS datasource from file name."""
        prompt = business_analyst_prompt(user_story="12345", file_name="s_fvms_incident", read_layer="bronze", write_layer="silver")
        assert "Data Source**: FVMS" in prompt

    def test_business_analyst_prompt_detects_nicherms_datasource(self):
        """Test that prompt correctly detects NicheRMS datasource from file name."""
        prompt = business_analyst_prompt(user_story="12345", file_name="s_nicherms_event", read_layer="bronze", write_layer="silver")
        assert "Data Source**: NICHERMS" in prompt

    def test_business_analyst_prompt_defaults_to_fvms(self):
        """Test that prompt defaults to FVMS when datasource is ambiguous."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "Data Source**: FVMS" in prompt

    def test_business_analyst_prompt_includes_phases(self):
        """Test that prompt includes all execution phases."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "### PHASE 1: User Story Retrieval & Validation" in prompt
        assert "### PHASE 1B: Parent Story & Comment Context Retrieval" in prompt
        assert "### PHASE 1C: Check Existing Table Memory" in prompt
        assert "### PHASE 2: Existing Code Analysis" in prompt
        assert "### PHASE 3: Schema Analysis" in prompt
        assert "### PHASE 4: Implementation Plan Creation" in prompt
        assert "### PHASE 5: Documentation Generation" in prompt
        assert "### PHASE 6: Update Table Memory" in prompt

    def test_business_analyst_prompt_includes_critical_instructions(self):
        """Test that prompt includes critical execution instructions."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "AUTOMATED NON-INTERACTIVE WORKFLOW" in prompt
        assert "IMMEDIATELY USE ALL REQUIRED TOOLS" in prompt
        assert "NEVER WAIT FOR CONFIRMATION" in prompt
        assert "USE AUSTRALIAN ENGLISH SPELLING" in prompt

    def test_business_analyst_prompt_includes_mcp_tool_instructions(self):
        """Test that prompt includes MCP tool usage instructions."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "mcp__ado__wit_get_work_item" in prompt
        assert "mcp__ado__wit_list_work_item_comments" in prompt
        assert "mcp__mcp-server-motherduck__query" in prompt

    def test_business_analyst_prompt_includes_memory_instructions(self):
        """Test that prompt includes memory management instructions."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "list_memories" in prompt
        assert "read_memory" in prompt
        assert "write_memory" in prompt

    def test_business_analyst_prompt_includes_schema_queries(self):
        """Test that prompt includes example SQL queries for schema analysis."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "SELECT DISTINCT database_name, schema_name, table_name" in prompt
        assert "FROM data_hub.legacy_schema" in prompt

    def test_business_analyst_prompt_includes_australian_spelling_examples(self):
        """Test that prompt includes Australian spelling examples."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "normalise" in prompt
        assert "standardise" in prompt
        assert "analyse" in prompt

    def test_business_analyst_prompt_includes_reference_example(self):
        """Test that prompt includes reference implementation example."""
        prompt = business_analyst_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold")
        assert "python_files/gold/g_ya_mg_occurence.py" in prompt
        assert "get_incident_offence_report_linkage()" in prompt


class TestPySparkEngineerPrompt:
    """Test PySpark engineer prompt generation."""

    def test_pyspark_engineer_prompt_basic_structure(self):
        """Test that PySpark engineer prompt contains all required sections."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "# PySpark Data Pipeline Implementation" in prompt
        assert "@pyspark-engineer" in prompt
        assert "## CONTEXT" in prompt
        assert "## PRIMARY OBJECTIVE" in prompt
        assert "## EXECUTION WORKFLOW" in prompt
        assert "## OUTPUT REQUIREMENTS" in prompt

    def test_pyspark_engineer_prompt_includes_user_story_id(self):
        """Test that prompt includes the provided user story ID."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "User Story ID**: 12345" in prompt

    def test_pyspark_engineer_prompt_includes_file_name(self):
        """Test that prompt includes the target file name."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "Target File**: `python_files/gold/gold_cms/g_mg_occurrence.py`" in prompt

    def test_pyspark_engineer_prompt_includes_data_layers(self):
        """Test that prompt includes read and write layers."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "Data Flow**: bronze to gold" in prompt

    def test_pyspark_engineer_prompt_includes_class_name(self):
        """Test that prompt includes the correct class name based on layer."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "Class Name**: `GoldLoader`" in prompt

    def test_pyspark_engineer_prompt_includes_doc_path(self):
        """Test that prompt includes the business analysis documentation path."""
        doc_path = Path("/tmp/test_business_analysis.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "Business Analysis**: `/tmp/test_business_analysis.md`" in prompt

    def test_pyspark_engineer_prompt_detects_cms_datasource(self):
        """Test that prompt correctly detects CMS datasource from file name."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="s_cms_case", read_layer="bronze", write_layer="silver", doc_path=doc_path)
        assert "silver_cms" in prompt

    def test_pyspark_engineer_prompt_detects_fvms_datasource(self):
        """Test that prompt correctly detects FVMS datasource from file name."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="s_fvms_incident", read_layer="bronze", write_layer="silver", doc_path=doc_path)
        assert "silver_fvms" in prompt

    def test_pyspark_engineer_prompt_includes_phases(self):
        """Test that prompt includes all execution phases."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "### PHASE 1: Read Project Guidelines" in prompt
        assert "### PHASE 2: Read Table Memory" in prompt
        assert "### PHASE 3: Read Business Analysis & Schema Documentation" in prompt
        assert "### PHASE 4: Check Existing Implementation" in prompt
        assert "### PHASE 5: Verify Schemas & Cross-Reference Documentation" in prompt
        assert "### PHASE 6: Implementation" in prompt
        assert "### PHASE 7: Code Quality Validation" in prompt
        assert "### PHASE 8: Save Implementation" in prompt

    def test_pyspark_engineer_prompt_includes_critical_instructions(self):
        """Test that prompt includes critical execution instructions."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "AUTOMATED NON-INTERACTIVE WORKFLOW" in prompt
        assert "IMMEDIATELY USE ALL REQUIRED TOOLS" in prompt
        assert "NEVER WAIT FOR CONFIRMATION" in prompt

    def test_pyspark_engineer_prompt_includes_coding_standards(self):
        """Test that prompt includes coding standards."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "Maximum line length: 240 characters" in prompt
        assert "No blank lines inside functions" in prompt
        assert "@synapse_error_print_handler" in prompt
        assert "DataFrame variables end with `_sdf` suffix" in prompt

    def test_pyspark_engineer_prompt_includes_memory_instructions(self):
        """Test that prompt includes memory management instructions."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "list_memories" in prompt
        assert "read_memory" in prompt

    def test_pyspark_engineer_prompt_includes_file_structure_template(self):
        """Test that prompt includes ETL class structure template."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "class GoldLoader:" in prompt
        assert "def extract(self) -> DataFrame:" in prompt
        assert "def transform(self) -> DataFrame:" in prompt
        assert "def load(self) -> None:" in prompt

    def test_pyspark_engineer_prompt_includes_australian_spelling_examples(self):
        """Test that prompt includes Australian spelling examples."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "normalise_data()" in prompt
        assert "standardise_column()" in prompt
        assert "analyse_values()" in prompt

    def test_pyspark_engineer_prompt_includes_data_dictionary_examples(self):
        """Test that prompt includes data dictionary integration examples."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "## DATA DICTIONARY INTEGRATION EXAMPLES" in prompt
        assert ".claude/data_dictionary/" in prompt

    def test_pyspark_engineer_prompt_includes_reference_example(self):
        """Test that prompt includes reference implementation example."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "python_files/gold/g_ya_mg_occurence.py" in prompt
        assert "get_incident_offence_report_linkage()" in prompt
        assert "### PHASE 0: Study Reference Implementation" in prompt

    def test_pyspark_engineer_prompt_includes_us_comment_pattern(self):
        """Test that prompt includes user story comment pattern."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "#### US: 12345" in prompt

    def test_pyspark_engineer_prompt_includes_quality_checklist(self):
        """Test that prompt includes code quality checklist."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "### Quality Checklist" in prompt
        assert "All coding standards from CLAUDE.md followed" in prompt
        assert "Australian English spelling used for all function and variable names" in prompt

    def test_pyspark_engineer_prompt_gold_layer_path(self):
        """Test that prompt includes correct path for gold layer files."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "python_files/gold/g_mg_occurrence.py" in prompt
        assert "Gold layer files go directly in `python_files/gold/`, NOT in subdirectories!" in prompt

    def test_pyspark_engineer_prompt_silver_layer_path(self):
        """Test that prompt includes correct path for silver layer files."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="s_cms_case", read_layer="bronze", write_layer="silver", doc_path=doc_path)
        assert "python_files/silver/silver_cms/s_cms_case.py" in prompt

    def test_pyspark_engineer_prompt_includes_existing_code_pattern(self):
        """Test that prompt includes pattern for updating existing code."""
        doc_path = Path("/tmp/test_doc.md")
        prompt = generate_implementation_prompt(user_story="12345", file_name="g_mg_occurrence", read_layer="bronze", write_layer="gold", doc_path=doc_path)
        assert "## EXAMPLE: Updating Existing File" in prompt
        assert "preserve these" in prompt.lower()
        assert "Add these NEW functions" in prompt
