import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from multi_agent_user_story_development.config import AgentConfig

config = AgentConfig()


def check_existing_python_file_DEPRECATED(file_name: str, layer: str, datasource: str) -> Dict[str, Any]:
    """DEPRECATED: Use Read tool directly to check files. This MCP tool requires user approval which blocks automation."""
    try:
        python_files_dir = config.project_root / "python_files"
        if layer == "gold":
            file_path = python_files_dir / "gold" / f"{file_name}.py"
        else:
            datasource_dir = f"{layer}_{datasource.lower()}"
            file_path = python_files_dir / layer / datasource_dir / f"{file_name}.py"
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            function_comments = []
            for i, line in enumerate(lines):
                if "#### US:" in line or "# US:" in line:
                    function_comments.append(f"Line {i + 1}: {line.strip()}")
            us_info = "\n".join(function_comments) if function_comments else "No user story comments found"
            return {"content": [{"type": "text", "text": f"Python file exists at: {str(file_path)}\n\nUser Story References:\n{us_info}\n\nREMINDER: If existing logic is no longer relevant, check the user story in comments using ADO MCP tool mcp__ado__wit_get_work_item to verify requirements before removing."}]}
        else:
            return {"content": [{"type": "text", "text": f"Python file does not exist. Will create new file at: {str(file_path)}"}]}
    except Exception as e:
        logger.error(f"Error checking Python file for {file_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def check_existing_documentation_DEPRECATED(file_name: str) -> Dict[str, Any]:
    """DEPRECATED: Agents use Write tool directly instead of these MCP tools."""
    try:
        doc_path = config.get_documentation_path(file_name)
        if doc_path.exists():
            return {"content": [{"type": "text", "text": f"Documentation exists at: {str(doc_path)}"}]}
        else:
            return {"content": [{"type": "text", "text": f"Documentation does not exist. Will create new documentation at: {str(doc_path)}"}]}
    except Exception as e:
        logger.error(f"Error checking documentation existence for {file_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def save_documentation_DEPRECATED(file_name: str, content: str) -> Dict[str, Any]:
    """DEPRECATED: Agents use Write tool directly instead of these MCP tools."""
    try:
        doc_path = config.get_documentation_path(file_name)
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(content, encoding="utf-8")
        logger.info(f"Documentation saved to: {doc_path}")
        return {"content": [{"type": "text", "text": f"Documentation successfully saved to: {str(doc_path)}"}]}
    except Exception as e:
        logger.error(f"Error saving documentation for {file_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def save_notebook_DEPRECATED(file_name: str, content: str) -> Dict[str, Any]:
    """DEPRECATED: Agents create .py files, not notebooks."""
    try:
        notebook_path = config.get_notebook_path(file_name)
        notebook_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            notebook_json = json.loads(content)
        except json.JSONDecodeError:
            return {"content": [{"type": "text", "text": "Error: Invalid JSON content for notebook"}], "isError": True}
        notebook_path.write_text(json.dumps(notebook_json, indent=2), encoding="utf-8")
        logger.info(f"Notebook saved to: {notebook_path}")
        return {"content": [{"type": "text", "text": f"Notebook successfully saved to: {str(notebook_path)}"}]}
    except Exception as e:
        logger.error(f"Error saving notebook for {file_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def read_etl_template() -> Dict[str, Any]:
    """Read and return ETL template content."""
    try:
        template_path = config.etl_template_path
        if not template_path.exists():
            return {"content": [{"type": "text", "text": f"Error: ETL template not found at {template_path}"}], "isError": True}
        template_content = template_path.read_text(encoding="utf-8")
        return {"content": [{"type": "text", "text": f"ETL Template path: {str(template_path)}\n\nContent:\n{template_content}"}]}
    except Exception as e:
        logger.error(f"Error reading ETL template: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def read_business_analysis(file_name: str) -> Dict[str, Any]:
    """Read business analyst documentation output."""
    try:
        doc_path = config.get_documentation_path(file_name)
        if not doc_path.exists():
            return {"content": [{"type": "text", "text": f"Error: Business analysis documentation not found at {doc_path}"}], "isError": True}
        doc_content = doc_path.read_text(encoding="utf-8")
        return {"content": [{"type": "text", "text": f"Business Analysis path: {str(doc_path)}\n\nContent:\n{doc_content}"}]}
    except Exception as e:
        logger.error(f"Error reading business analysis for {file_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def write_memory(layer: str, datasource: str, table_name: str, user_story: str, content: str) -> Dict[str, Any]:
    """Store/update table memory with smart merge logic. Archives previous state to history."""
    try:
        memory_path = config.get_memory_path(layer, datasource, table_name)
        history_path = config.get_memory_history_path(layer, datasource, table_name, user_story)
        if memory_path.exists():
            existing_content = memory_path.read_text(encoding="utf-8")
            history_path.write_text(f"# Historical Snapshot - Before US:{user_story}\n\n{existing_content}", encoding="utf-8")
            logger.info(f"Archived previous state to: {history_path}")
            updated_content = _merge_memory_content(existing_content, content, user_story)
            memory_path.write_text(updated_content, encoding="utf-8")
            logger.info(f"Updated memory at: {memory_path}")
            return {"content": [{"type": "text", "text": f"Memory updated at: {str(memory_path)}\nPrevious state archived to: {str(history_path)}"}]}
        else:
            formatted_content = f"# Memory: {table_name}\n**Layer**: {layer} | **Datasource**: {datasource}\n\n## Changelog\n- US:{user_story} - Initial creation\n\n---\n\n{content}"
            memory_path.write_text(formatted_content, encoding="utf-8")
            logger.info(f"Created new memory at: {memory_path}")
            return {"content": [{"type": "text", "text": f"Memory created at: {str(memory_path)}"}]}
    except Exception as e:
        logger.error(f"Error writing memory for US {user_story}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def _merge_memory_content(existing: str, new_content: str, user_story: str) -> str:
    """Merge new user story content with existing memory, updating changelog."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    changelog_pattern = r"(## Changelog\n)(.*?)(\n---|\n##)"
    match = re.search(changelog_pattern, existing, re.DOTALL)
    if match:
        changelog_section = match.group(2)
        updated_changelog = f"{match.group(1)}{changelog_section.strip()}\n- US:{user_story} - Updated {timestamp}\n{match.group(3)}"
        updated_existing = re.sub(changelog_pattern, updated_changelog, existing, count=1, flags=re.DOTALL)
    else:
        updated_existing = existing.replace("---", f"## Changelog\n- US:{user_story} - Updated {timestamp}\n\n---")
    sections_to_update = {"## Summary": True, "## Key Requirements": True, "## Data Transformations": True, "## Business Rules": True, "## Data Quality Rules": True, "## Related Tables": True, "## Gotchas & Special Considerations": True, "## Comments Insights": True}
    for section in sections_to_update:
        pattern = rf"({re.escape(section)})(.*?)(\n##|\Z)"
        new_match = re.search(pattern, new_content, re.DOTALL)
        if new_match:
            new_section_content = new_match.group(2).strip()
            existing_match = re.search(pattern, updated_existing, re.DOTALL)
            if existing_match:
                updated_existing = re.sub(pattern, f"{section}\n{new_section_content}\n\n{existing_match.group(3)}", updated_existing, count=1, flags=re.DOTALL)
            else:
                updated_existing += f"\n{section}\n{new_section_content}\n"
    return updated_existing


def read_memory(layer: str, datasource: str, table_name: str) -> Dict[str, Any]:
    """Read current table memory state (consolidated across all user stories)."""
    try:
        memory_path = config.get_memory_path(layer, datasource, table_name)
        if not memory_path.exists():
            return {"content": [{"type": "text", "text": f"No memory found for table {table_name} at {memory_path}"}], "isError": True}
        memory_content = memory_path.read_text(encoding="utf-8")
        return {"content": [{"type": "text", "text": f"Current memory for {table_name}:\n\n{memory_content}"}]}
    except Exception as e:
        logger.error(f"Error reading memory for table {table_name}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def read_memory_history(layer: str, datasource: str, table_name: str, user_story: str) -> Dict[str, Any]:
    """Read historical memory snapshot for a specific user story."""
    try:
        history_path = config.get_memory_history_path(layer, datasource, table_name, user_story)
        if not history_path.exists():
            return {"content": [{"type": "text", "text": f"No historical snapshot found for US {user_story} at {history_path}"}], "isError": True}
        history_content = history_path.read_text(encoding="utf-8")
        return {"content": [{"type": "text", "text": f"Historical snapshot for US {user_story}:\n\n{history_content}"}]}
    except Exception as e:
        logger.error(f"Error reading history for US {user_story}: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def list_memories(layer: Optional[str] = None, datasource: Optional[str] = None, table_name: Optional[str] = None) -> Dict[str, Any]:
    """List all current table memories, optionally filtered by layer/datasource/table."""
    try:
        memories = config.list_memories(layer, datasource, table_name)
        if not memories:
            filter_desc = f"layer={layer}, datasource={datasource}, table={table_name}" if any([layer, datasource, table_name]) else "all"
            return {"content": [{"type": "text", "text": f"No memories found for filter: {filter_desc}"}]}
        memory_list = []
        for mem_path in memories:
            relative_path = mem_path.relative_to(config.memory_dir)
            parts = relative_path.parts
            table = mem_path.stem
            memory_list.append({"layer": parts[0] if len(parts) > 0 else "unknown", "datasource": parts[1] if len(parts) > 1 else "unknown", "table": table, "path": str(mem_path)})
        return {"content": [{"type": "text", "text": json.dumps(memory_list, indent=2)}]}
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def list_memory_history(layer: Optional[str] = None, datasource: Optional[str] = None, table_name: Optional[str] = None) -> Dict[str, Any]:
    """List all historical memory snapshots, optionally filtered by layer/datasource/table."""
    try:
        histories = config.list_memory_history(layer, datasource, table_name)
        if not histories:
            filter_desc = f"layer={layer}, datasource={datasource}, table={table_name}" if any([layer, datasource, table_name]) else "all"
            return {"content": [{"type": "text", "text": f"No historical snapshots found for filter: {filter_desc}"}]}
        history_list = []
        for hist_path in histories:
            relative_path = hist_path.relative_to(config.memory_dir)
            parts = relative_path.parts
            user_story = hist_path.stem.replace("US_", "")
            history_list.append({"user_story": user_story, "layer": parts[0] if len(parts) > 0 else "unknown", "datasource": parts[1] if len(parts) > 1 else "unknown", "table": parts[2] if len(parts) > 2 else "unknown", "path": str(hist_path)})
        return {"content": [{"type": "text", "text": json.dumps(history_list, indent=2)}]}
    except Exception as e:
        logger.error(f"Error listing memory history: {e}")
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
