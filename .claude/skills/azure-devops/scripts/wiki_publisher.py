#!/usr/bin/env python3
"""Wiki Publisher for Python Utilities Documentation.

Generates comprehensive markdown documentation for Python utility files
and publishes them to Azure DevOps wiki using REST API.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from base64 import b64encode

class AzureDevOpsWikiPublisher:
    """Publishes documentation to Azure DevOps Wiki via REST API."""

    def __init__(self, organization: str, project: str, pat: str, wiki_identifier: str):
        """Initialize wiki publisher with Azure DevOps connection details.

        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token for authentication
            wiki_identifier: Wiki identifier (usually wiki name)
        """
        self.organization = organization
        self.project = project
        self.wiki_identifier = wiki_identifier
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wiki_identifier}"

        # Encode PAT for basic auth
        auth_string = f":{pat}"
        b64_auth = b64encode(auth_string.encode()).decode()

        self.headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.api_version = "7.1-preview.1"
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retries": 0
        }

    def create_or_update_page(self, path: str, content: str, max_retries: int = 3) -> Optional[Dict]:
        """Create or update a wiki page with retry logic.

        Args:
            path: Wiki page path (e.g., /utilities/cms_enums)
            content: Markdown content for the page
            max_retries: Maximum number of retry attempts

        Returns:
            Response data dict if successful, None otherwise
        """
        url = f"{self.base_url}/pages?path={path}&api-version={self.api_version}"

        for attempt in range(max_retries):
            try:
                self.stats["total_requests"] += 1

                # Try to get existing page first
                get_response = requests.get(url, headers=self.headers)

                if get_response.status_code == 200:
                    # Page exists, update it
                    existing_page = get_response.json()
                    etag = existing_page.get("eTag")

                    headers = self.headers.copy()
                    headers["If-Match"] = etag

                    payload = {"content": content}

                    response = requests.put(url, headers=headers, json=payload)

                    if response.status_code in [200, 201]:
                        self.stats["successful_requests"] += 1
                        return response.json()

                elif get_response.status_code == 404:
                    # Page doesn't exist, create it
                    payload = {"content": content}

                    response = requests.put(url, headers=self.headers, json=payload)

                    if response.status_code in [200, 201]:
                        self.stats["successful_requests"] += 1
                        return response.json()

                # If we get here, something failed
                print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed: {response.status_code}")
                print(f"     Response: {response.text[:200]}")

                if attempt < max_retries - 1:
                    self.stats["retries"] += 1
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    time.sleep(wait_time)

            except Exception as e:
                print(f"  ❌ Request error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    self.stats["retries"] += 1
                    time.sleep(2)

        self.stats["failed_requests"] += 1
        return None


def generate_directory_index(file_docs: List[Dict]) -> str:
    """Generate markdown for directory index page.

    Args:
        file_docs: List of file documentation dicts with name, description, components

    Returns:
        Markdown string for index page
    """
    md = [
        "# Utilities",
        "",
        "**Path**: `python_files/utilities/`",
        f"**Total Files**: {len(file_docs)}",
        "",
        "## Overview",
        "",
        "Core utilities supporting the Unify data migration medallion architecture. Includes Spark session management, ",
        "enumeration mappings, database utilities, and development tools.",
        "",
        "## Files in This Directory",
        "",
        "| File | Description | Key Components |",
        "|------|-------------|----------------|"
    ]

    for doc in sorted(file_docs, key=lambda x: x["name"]):
        name = doc["name"].replace(".py", "")
        desc = doc["description"]
        components = doc["components"]
        md.append(f"| [{name}](/unify_2_1_dm_synapse_env_d10/utilities/{name}) | {desc} | {components} |")

    md.extend([
        "",
        "## Key Categories",
        "",
        "- **Core Utilities**: session_optimiser, local_spark_connection",
        "- **Enum Mappings**: cms_enums, fvms_enums",
        "- **Database Tools**: create_duckdb_database, database_inspector, warehouse_duckdb_builder",
        "- **Data Processing**: data_generator, data_ingestion, parquet_to_csv",
        "- **Development Tools**: makefile_ui, vscode_file_watcher",
        "- **Schema Management**: generate_schema, process_data_dictionary_pipeline",
        "",
        "---",
        f"*Auto-generated directory index - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])

    return "\n".join(md)


def generate_file_documentation(filename: str, description: str, classes: List[str],
                                functions: List[str], enums: List[str], imports: List[str]) -> str:
    """Generate markdown documentation for a single file.

    Args:
        filename: Name of the Python file
        description: File description
        classes: List of class names
        functions: List of function names
        enums: List of enum names
        imports: List of import statements

    Returns:
        Markdown string for file documentation
    """
    name_without_ext = filename.replace(".py", "")

    md = [
        f"# {name_without_ext}",
        "",
        f"**File Path**: `python_files/utilities/{filename}`",
        f"**Repository Link**: [View Source](https://dev.azure.com/emstas/Program%20Unify/_git/unify_2_1_dm_synapse_env_d10?path=/python_files/utilities/{filename}&version=GBfeature/uat_fixes_linus)",
        "**Category**: Utility",
        "",
        "## Overview",
        "",
        description,
        ""
    ]

    # Key Components section
    if classes or functions or enums:
        md.append("## Key Components")
        md.append("")

        if classes:
            md.append("### Classes")
            md.append("")
            for cls in classes:
                md.append(f"- `{cls}`")
            md.append("")

        if functions:
            md.append("### Functions")
            md.append("")
            for func in functions:
                md.append(f"- `{func}()`")
            md.append("")

        if enums:
            md.append("### Enums")
            md.append("")
            for enum in enums:
                md.append(f"- `{enum}`")
            md.append("")

    # Dependencies
    if imports:
        md.append("## Dependencies")
        md.append("")
        md.append("### External Imports")
        md.append("")
        for imp in imports:
            md.append(f"- {imp}")
        md.append("")

    md.extend([
        "---",
        "*Auto-generated documentation*",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*"
    ])

    return "\n".join(md)


def main():
    """Main execution function."""
    start_time = time.time()

    print("=" * 80)
    print("📚 Azure DevOps Wiki Publisher - Python Utilities Documentation")
    print("=" * 80)
    print()

    # Get environment variables
    pat = os.getenv("AZURE_DEVOPS_PAT")
    if not pat:
        print("❌ ERROR: AZURE_DEVOPS_PAT environment variable not set")
        sys.exit(1)

    organization = "emstas"
    project = "Program Unify"
    wiki_identifier = "Program-Unify.wiki"

    # Initialize publisher
    publisher = AzureDevOpsWikiPublisher(organization, project, pat, wiki_identifier)

    # File documentation metadata
    file_docs = [
        {
            "name": "cms_enums.py",
            "description": "CMS system enumeration mappings and constants for data transformations",
            "components": "20 enums, 23 dataclasses",
            "classes": ["EnumMappingBase", "RelationshipMapping", "SuspectInvolvedMapping", "OffenceReportStatus"],
            "functions": [],
            "enums": ["IncidentEnum", "PersonEnum", "GenderMap", "IncidentStatusMap"],
            "imports": ["dataclasses", "enum"]
        },
        {
            "name": "create_duckdb_database.py",
            "description": "DuckDB database management utility for schema metadata and legacy data",
            "components": "1 class, 3 functions",
            "classes": ["DuckDBSchemaManager"],
            "functions": ["create_legacy_schema_table", "load_legacy_data_tables"],
            "enums": [],
            "imports": ["duckdb", "pathlib", "typing"]
        },
        {
            "name": "data_dictionary_key_appender.py",
            "description": "Appends primary and foreign key metadata to data dictionary markdown files",
            "components": "1 class, 1 main function",
            "classes": ["DataDictionaryKeyAppender"],
            "functions": ["main"],
            "enums": [],
            "imports": ["duckdb", "pathlib", "re"]
        },
        {
            "name": "data_generator.py",
            "description": "Azure Blob Storage downloader for legacy data acquisition with parallel downloads",
            "components": "1 class, 2 functions",
            "classes": ["StorageDownloader"],
            "functions": ["download_legacy_data", "main"],
            "enums": [],
            "imports": ["azure.storage.blob", "azure.identity", "concurrent.futures"]
        },
        {
            "name": "data_ingestion.py",
            "description": "Legacy SQL Server data ingestion and transformation via JDBC",
            "components": "1 class, 1 main function",
            "classes": ["UtilityFunctions"],
            "functions": ["main"],
            "enums": [],
            "imports": ["pyspark.sql", "pathlib", "yaml"]
        },
        {
            "name": "database_inspector.py",
            "description": "Database inspection utilities for medallion architecture analysis",
            "components": "1 class, 1 function",
            "classes": ["DatabaseInspector"],
            "functions": ["describe_database_with_sql"],
            "enums": [],
            "imports": ["pyspark.sql", "typing"]
        },
        {
            "name": "excel_to_json_converter.py",
            "description": "Excel to JSON conversion utility with data type handling",
            "components": "1 function",
            "classes": [],
            "functions": ["convert_excel_to_json"],
            "enums": [],
            "imports": ["json", "pandas", "pathlib"]
        },
        {
            "name": "fvms_enums.py",
            "description": "FVMS/NicheRMS enumeration mappings for data transformations",
            "components": "16 enums",
            "classes": [],
            "functions": [],
            "enums": ["IncidentEnum", "PersonEnum", "GenderMap", "PersonKARelationshipType"],
            "imports": ["enum"]
        },
        {
            "name": "generate_schema.py",
            "description": "Database schema extraction and export to cloud storage",
            "components": "1 class",
            "classes": ["GenerateSchemaLoader"],
            "functions": [],
            "enums": [],
            "imports": ["pyspark.sql", "datetime"]
        },
        {
            "name": "local_spark_connection.py",
            "description": "Spark connector with SQL Server JDBC connectivity and metadata extraction",
            "components": "3 classes",
            "classes": ["UtilityFunctions", "SparkConnectorError", "sparkConnector"],
            "functions": [],
            "enums": [],
            "imports": ["pyspark.sql", "yaml", "loguru"]
        },
        {
            "name": "makefile_ui.py",
            "description": "Textual-based interactive Makefile menu with real-time output streaming",
            "components": "2 classes, 2 functions",
            "classes": ["ParameterInputScreen", "MakefileMenuApp"],
            "functions": ["parse_makefile", "get_target_categories"],
            "enums": [],
            "imports": ["textual", "subprocess", "pathlib"]
        },
        {
            "name": "parquet_to_csv.py",
            "description": "Convert Parquet files to tab-delimited CSV using PySpark",
            "components": "4 functions",
            "classes": [],
            "functions": ["create_spark_session", "read_parquet_directory", "write_to_csv", "main"],
            "enums": [],
            "imports": ["pyspark.sql", "loguru", "sys"]
        },
        {
            "name": "process_data_dictionary_pipeline.py",
            "description": "Data dictionary processing pipeline for PDF extraction and markdown generation",
            "components": "11 functions",
            "classes": [],
            "functions": ["extract_table_names_after_tables_heading", "build_table_page_index", "extract_table_from_page"],
            "enums": [],
            "imports": ["pymupdf", "json", "re", "pathlib"]
        },
        {
            "name": "rebuild_database_advanced.py",
            "description": "Advanced database rebuilding utility with multiple rebuild strategies",
            "components": "1 class, 1 function",
            "classes": ["AdvancedDatabaseRebuilder"],
            "functions": ["example_usage"],
            "enums": [],
            "imports": ["pyspark.sql", "pathlib", "os"]
        },
        {
            "name": "rebuild_database_from_parquet.py",
            "description": "Simple database rebuilding from parquet files with prefix support",
            "components": "1 class",
            "classes": ["DatabaseRebuilder"],
            "functions": [],
            "enums": [],
            "imports": ["pyspark.sql", "pathlib", "os"]
        },
        {
            "name": "session_optimiser.py",
            "description": "Core PySpark session optimization and utilities for medallion architecture",
            "components": "5 classes, 30+ methods",
            "classes": ["SparkOptimiser", "NotebookLogger", "TimestampFormatter", "TableUtilities", "GenerateSchemaLoader"],
            "functions": ["synapse_error_handler", "log_dataframe_info"],
            "enums": [],
            "imports": ["pyspark.sql", "rich", "pytz", "functools"]
        },
        {
            "name": "show_spark_databases.py",
            "description": "Display all Spark databases and tables in formatted list",
            "components": "Main script",
            "classes": [],
            "functions": [],
            "enums": [],
            "imports": ["pathlib", "local_spark_connection"]
        },
        {
            "name": "synthetic_data_generator.py",
            "description": "Generate synthetic test data for Bronze layer databases",
            "components": "2 functions",
            "classes": [],
            "functions": ["get_settings_from_yaml", "generate_database"],
            "enums": [],
            "imports": ["pyspark.sql", "local_spark_connection", "loguru"]
        },
        {
            "name": "vscode_file_watcher.py",
            "description": "VSCode file watcher monitoring workspace state changes",
            "components": "1 class, 1 function",
            "classes": ["VSCodeFileWatcher"],
            "functions": ["main"],
            "enums": [],
            "imports": ["watchdog", "pathlib", "time"]
        },
        {
            "name": "warehouse_duckdb_builder.py",
            "description": "Build DuckDB database from parquet warehouse files with incremental updates",
            "components": "1 class, 1 function",
            "classes": ["WarehouseDuckDBBuilder"],
            "functions": ["main"],
            "enums": [],
            "imports": ["duckdb", "pathlib", "argparse"]
        }
    ]

    wiki_urls = []
    errors = []

    # First, create the parent page
    print("📄 Creating parent page...")
    parent_content = """# unify_2_1_dm_synapse_env_d10

**Repository**: Unify Data Migration - Azure Synapse PySpark ETL Pipelines
**Architecture**: Medallion (Bronze → Silver → Gold)

## Documentation Structure

- [Utilities](/unify_2_1_dm_synapse_env_d10/utilities) - Core utility modules

---
*Auto-generated project documentation*
"""
    parent_path = "/unify_2_1_dm_synapse_env_d10"
    parent_result = publisher.create_or_update_page(parent_path, parent_content)
    if parent_result:
        print(f"  ✅ Parent page created: {parent_path}")
    else:
        print(f"  ❌ Failed to create parent page - continuing anyway...")

    # Create directory index page
    print("\n📄 Creating directory index page...")
    index_content = generate_directory_index(file_docs)
    index_path = "/unify_2_1_dm_synapse_env_d10/utilities"

    index_result = publisher.create_or_update_page(index_path, index_content)
    if index_result:
        wiki_url = f"https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wiki_identifier}?pagePath={index_path}"
        wiki_urls.append(wiki_url)
        print(f"  ✅ Index page created: {index_path}")
    else:
        errors.append(f"Failed to create index page: {index_path}")
        print(f"  ❌ Failed to create index page")

    # Create individual file pages
    print(f"\n📄 Creating {len(file_docs)} file documentation pages...")
    for i, doc in enumerate(file_docs, 1):
        filename = doc["name"]
        name_without_ext = filename.replace(".py", "")

        print(f"\n[{i}/{len(file_docs)}] Processing {filename}...")

        file_content = generate_file_documentation(
            filename,
            doc["description"],
            doc["classes"],
            doc["functions"],
            doc["enums"],
            doc["imports"]
        )

        file_path = f"/unify_2_1_dm_synapse_env_d10/utilities/{name_without_ext}"

        result = publisher.create_or_update_page(file_path, file_content)
        if result:
            wiki_url = f"https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wiki_identifier}?pagePath={file_path}"
            wiki_urls.append(wiki_url)
            print(f"  ✅ Page created: {file_path}")
        else:
            errors.append(f"Failed to create page: {file_path}")
            print(f"  ❌ Failed to create page")

        # Rate limiting - wait between requests
        if i < len(file_docs):
            time.sleep(0.5)

    # Generate final report
    execution_time = time.time() - start_time

    result = {
        "agent_id": "wiki-publisher",
        "status": "completed" if not errors else "completed_with_errors",
        "pages_created": len(wiki_urls) - 1,  # Exclude index
        "pages_updated": 0,
        "index_pages_created": 1,
        "wiki_urls": wiki_urls,
        "hierarchy_map": {
            "/unify_2_1_dm_synapse_env_d10/utilities": {
                "type": "index",
                "files": [doc["name"].replace(".py", "") for doc in file_docs]
            }
        },
        "api_metrics": publisher.stats,
        "errors": errors,
        "warnings": [],
        "execution_time_seconds": round(execution_time, 2)
    }

    print("\n" + "=" * 80)
    print("📊 Wiki Publishing Summary")
    print("=" * 80)
    print(f"\n✅ Status: {result['status']}")
    print(f"📄 Pages Created: {result['pages_created']}")
    print(f"📑 Index Pages: {result['index_pages_created']}")
    print(f"⏱️  Execution Time: {result['execution_time_seconds']}s")
    print(f"\n📈 API Metrics:")
    print(f"   Total Requests: {publisher.stats['total_requests']}")
    print(f"   Successful: {publisher.stats['successful_requests']}")
    print(f"   Failed: {publisher.stats['failed_requests']}")
    print(f"   Retries: {publisher.stats['retries']}")

    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"   - {error}")

    print(f"\n🔗 Wiki Base URL:")
    print(f"   https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wiki_identifier}/274/unify_2_1_dm_synapse_env_d10")

    # Write JSON output
    output_file = "/tmp/wiki_publisher_result.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Full results saved to: {output_file}")
    print("\n" + "=" * 80)

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
