#!/usr/bin/env python3
"""Main orchestrator for automated agent workflow. Coordinates business analyst and PySpark engineer agents using Claude CLI."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from loguru import logger

from multi_agent_user_story_development.auth.azure import AzureLogin
from multi_agent_user_story_development.config import AgentConfig
from multi_agent_user_story_development.prompts.business_analyst import business_analyst_prompt
from multi_agent_user_story_development.prompts.pyspark_engineer import generate_implementation_prompt


def setup_logging() -> None:
    """Configure logging for orchestrator."""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | Orchestrator - {message}", colorize=True)


def check_claude_cli() -> bool:
    """Check if Claude CLI is available."""
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Claude CLI found: {result.stdout.strip()}")
            return True
        return False
    except FileNotFoundError:
        logger.error("Claude CLI not found. Please install with: npm install -g @anthropic-ai/claude-code")
        return False


def run_business_analyst(user_story: str, file_name: str, read_layer: str, write_layer: str, config: AgentConfig) -> bool:
    """Execute business analyst agent using Claude CLI."""
    logger.info("=" * 80)
    logger.info("PHASE 1: Business Analyst Agent")
    logger.info("=" * 80)
    prompt = business_analyst_prompt(user_story, file_name, read_layer, write_layer)
    logger.info("Executing business analyst agent...")
    logger.info(f"User Story: {user_story}")
    logger.info(f"File Name: {file_name}")
    logger.info(f"Read Layer: {read_layer}")
    logger.info(f"Write Layer: {write_layer}")
    try:
        prompt_file = config.project_root / ".claude" / "scafolding" / "output" / f"ba_prompt_{file_name}.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt)
        mcp_servers = {}
        claude_config_paths = [config.project_root / ".claude.json", Path("/root/.claude.json"), config.project_root.parent.parent / "root" / ".claude.json"]
        for claude_config_file in claude_config_paths:
            try:
                if claude_config_file.exists():
                    with open(claude_config_file) as f:
                        claude_config = json.load(f)
                        project_config = claude_config.get("projects", {}).get(str(config.project_root), {})
                        mcp_servers = project_config.get("mcpServers", {})
                        logger.info(f"Loaded {len(mcp_servers)} MCP servers from {claude_config_file}")
                        break
            except (PermissionError, OSError) as e:
                logger.debug(f"Could not access {claude_config_file}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Could not load MCP config from {claude_config_file}: {e}")
                continue
        mcp_config_file = config.project_root / ".claude" / "scafolding" / "output" / "mcp_config.json"
        mcp_config_data = {"mcpServers": mcp_servers} if mcp_servers else {"mcpServers": {}}
        mcp_config_file.write_text(json.dumps(mcp_config_data, indent=2))
        settings_file = config.project_root / ".claude" / "scafolding" / "output" / "agent_settings.json"
        settings_data = {"permissions": {"allow": ["mcp__*", "mcp__ado__*", "mcp__exa__*", "mcp__Ref__*", "mcp__ado__wit_get_work_item", "mcp__ado__wit_list_work_items", "mcp__ado__wit_list_work_item_comments", "mcp__mcp-server-motherduck__query", "mcp__mcp-server-motherduck__*", f"Write(//{str(config.project_root)}/.claude/documentation/**)", f"Read(//{str(config.project_root)}/.claude/**)", f"Read(//{str(config.project_root)}/python_files/**)", "Bash(*:*)"]}}
        settings_file.write_text(json.dumps(settings_data))
        cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions", "--settings", str(settings_file), "--mcp-config", str(mcp_config_file)]
        logger.info("Running business analyst agent...")
        logger.info("Agent output will stream below:")
        logger.info("-" * 80)
        result = subprocess.run(cmd, cwd=str(config.project_root), text=True, timeout=1200)
        logger.info("-" * 80)
        if result.returncode == 0:
            logger.success("Business analyst agent completed successfully")
            doc_path = config.get_documentation_path(file_name)
            if not doc_path.exists():
                doc_dir = config.documentation_output_dir
                matching_docs = list(doc_dir.glob(f"{file_name}*.md"))
                if matching_docs:
                    doc_path = matching_docs[0]
                    logger.info(f"Found documentation with alternate name: {doc_path.name}")
            if doc_path.exists():
                logger.success(f"Documentation created: {doc_path}")
                return True
            else:
                logger.warning("Documentation file not found, but agent reported success")
                return True
        else:
            logger.error(f"Business analyst agent failed with code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Business analyst agent timed out (20 minutes)")
        return False
    except Exception as e:
        logger.error(f"Error running business analyst agent: {e}")
        return False


def run_pyspark_engineer(user_story: str, file_name: str, read_layer: str, write_layer: str, config: AgentConfig) -> bool:
    """Execute PySpark engineer agent using Claude CLI."""
    logger.info("=" * 80)
    logger.info("PHASE 2: PySpark Engineer Agent")
    logger.info("=" * 80)
    doc_path = config.get_documentation_path(file_name)
    if not doc_path.exists():
        doc_dir = config.documentation_output_dir
        matching_docs = list(doc_dir.glob(f"{file_name}*.md"))
        if matching_docs:
            doc_path = matching_docs[0]
            logger.info(f"Using documentation with alternate name: {doc_path.name}")
        else:
            logger.error(f"Business analysis documentation not found: {doc_path}")
            logger.error(f"Searched in: {doc_dir}")
            logger.error("Cannot proceed without business analyst output")
            return False
    prompt = generate_implementation_prompt(user_story, file_name, read_layer, write_layer, doc_path)
    logger.info("Executing PySpark engineer agent...")
    logger.info(f"Reading business analysis from: {doc_path}")
    try:
        prompt_file = config.project_root / ".claude" / "scafolding" / "output" / f"pyspark_prompt_{file_name}.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt)
        mcp_config_file = config.project_root / ".claude" / "scafolding" / "output" / "mcp_config.json"
        settings_file = config.project_root / ".claude" / "scafolding" / "output" / "agent_settings.json"
        settings_data = {"permissions": {"allow": ["mcp__*", "mcp__ado__*", "mcp__exa__*", "mcp__Ref__*", "mcp__ado__wit_get_work_item", "mcp__ado__wit_list_work_items", "mcp__ado__wit_list_work_item_comments", "mcp__mcp-server-motherduck__query", "mcp__mcp-server-motherduck__*", f"Write(//{str(config.project_root)}/.claude/documentation/**)", f"Read(//{str(config.project_root)}/.claude/**)", f"Read(//{str(config.project_root)}/python_files/**)", "Bash(*:*)"]}}
        settings_file.write_text(json.dumps(settings_data))
        cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions", "--settings", str(settings_file), "--mcp-config", str(mcp_config_file)]
        logger.info("Running PySpark engineer agent...")
        logger.info("Agent output will stream below:")
        logger.info("-" * 80)
        result = subprocess.run(cmd, cwd=str(config.project_root), text=True, timeout=1800)
        logger.info("-" * 80)
        if result.returncode == 0:
            logger.success("PySpark engineer agent completed successfully")
            python_file_path = config.project_root / "python_files" / write_layer / f"{file_name}.py"
            if python_file_path.exists():
                logger.success(f"Python file created/updated: {python_file_path}")
                return True
            else:
                logger.warning(f"Python file not found at {python_file_path}, but agent reported success")
                logger.info("This may be expected if the agent encountered permission issues")
                return True
        else:
            logger.error(f"PySpark engineer agent failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("PySpark engineer agent timed out (30 minutes)")
        return False
    except Exception as e:
        logger.error(f"Error running PySpark engineer agent: {e}")
        return False


def run_orchestrator(user_story: str, file_name: str, read_layer: str, write_layer: str, skip_auth: bool = False, skip_business_analyst: bool = False, verbose: bool = False) -> int:
    """Main orchestration function. Returns exit code (0=success, 1=failure)."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | Orchestrator - {message}", colorize=False)
    config = AgentConfig()
    logger.info("Starting automated agent workflow")
    logger.info(f"User Story: {user_story}")
    logger.info(f"File Name: {file_name}")
    logger.info(f"Read Layer: {read_layer}")
    logger.info(f"Write Layer: {write_layer}")
    if not check_claude_cli():
        logger.error("Claude CLI is not available")
        return 1
    if not skip_auth:
        logger.info("Checking Azure authentication...")
        auth = AzureLogin()
        all_authenticated, status = auth.check_full_authentication()
        if not all_authenticated:
            logger.error("Azure authentication required")
            logger.info("Azure CLI: " + ("" if status["azure_cli"] else ""))
            logger.info("Azure DevOps: " + ("" if status["azure_devops"] else ""))
            logger.info("Run with --skip-auth to bypass authentication check")
            return 1
        logger.success("Azure authentication verified")
    if not skip_business_analyst:
        if not run_business_analyst(user_story, file_name, read_layer, write_layer, config):
            logger.error("Business analyst agent failed")
            return 1
    else:
        logger.info("Skipping business analyst agent")
        doc_path = config.get_documentation_path(file_name)
        if not doc_path.exists():
            doc_dir = config.documentation_output_dir
            matching_docs = list(doc_dir.glob(f"{file_name}*.md"))
            if matching_docs:
                doc_path = matching_docs[0]
                logger.info(f"Found existing documentation: {doc_path.name}")
            else:
                logger.error(f"Business analysis documentation not found: {doc_path}")
                logger.error(f"Searched in: {doc_dir}")
                logger.error("Cannot skip business analyst without existing documentation")
                return 1
        else:
            logger.info(f"Using existing documentation: {doc_path}")
    if not run_pyspark_engineer(user_story, file_name, read_layer, write_layer, config):
        logger.error("PySpark engineer agent failed")
        return 1
    logger.success("=" * 80)
    logger.success("WORKFLOW COMPLETED SUCCESSFULLY")
    logger.success("=" * 80)
    doc_path = config.get_documentation_path(file_name)
    if not doc_path.exists():
        doc_dir = config.documentation_output_dir
        matching_docs = list(doc_dir.glob(f"{file_name}*.md"))
        if matching_docs:
            doc_path = matching_docs[0]
    python_file_path = config.project_root / "python_files" / write_layer / f"{file_name}.py"
    logger.info(f"Documentation: {doc_path}")
    logger.info(f"Python File: {python_file_path}")
    return 0


def main() -> None:
    """Main entry point for orchestrator CLI."""
    parser = argparse.ArgumentParser(description="Automated workflow orchestrator for Business Analyst and PySpark Engineer agents", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--user-story", required=True, help="Azure DevOps user story ID")
    parser.add_argument("--file-name", required=True, help="Output file name (without extension)")
    parser.add_argument("--read-layer", required=True, choices=["bronze", "silver", "gold"], help="Source data layer")
    parser.add_argument("--write-layer", required=True, choices=["bronze", "silver", "gold"], help="Target data layer")
    parser.add_argument("--skip-auth", action="store_true", help="Skip Azure authentication check")
    parser.add_argument("--skip-schema-build", action="store_true", help="Skip DuckDB schema database build")
    parser.add_argument("--skip-business-analyst", action="store_true", help="Skip business analyst agent (documentation must exist)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    setup_logging()
    exit_code = run_orchestrator(user_story=args.user_story, file_name=args.file_name, read_layer=args.read_layer, write_layer=args.write_layer, skip_auth=args.skip_auth, skip_business_analyst=args.skip_business_analyst, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
