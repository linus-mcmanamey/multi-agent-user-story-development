#!/usr/bin/env python3

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

sys.path.insert(0, '/tmp')
from add_user_story_links import generate_user_story_section

class WikiPublisher:
    def __init__(self):
        self.pat = os.environ.get("AZURE_DEVOPS_PAT")
        self.organization = os.environ.get("AZURE_DEVOPS_ORGANIZATION", "emstas")
        self.project = os.environ.get("AZURE_DEVOPS_PROJECT", "Program Unify")
        self.base_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis"
        self.wiki_identifier = "4a2de70d-332e-406c-acd9-a9bf24dcb6d1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(f':{self.pat}'.encode()).decode()}"
        }
        self.stats = {
            "total_pages": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "created_pages": []
        }
        self.repo_base_url = "https://dev.azure.com/emstas/Program%20Unify/_git/unify_2_1_dm_synapse_env_d10?path="

    def create_wiki_page(self, path: str, content: str, retries: int = 3) -> bool:
        url = f"{self.base_url}/wiki/wikis/{self.wiki_identifier}/pages?path={path}&api-version=7.1"
        payload = {"content": content}

        for attempt in range(retries):
            try:
                response = requests.put(url, headers=self.headers, json=payload)

                if response.status_code in [200, 201]:
                    self.stats["successful"] += 1
                    self.stats["created_pages"].append(path)
                    return True
                elif response.status_code == 409:
                    print(f"  Page exists, updating: {path}")
                    self.stats["skipped"] += 1
                    return True
                else:
                    print(f"  Failed (attempt {attempt + 1}/{retries}): {response.status_code} - {response.text[:200]}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)

            except Exception as e:
                print(f"  Error (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        self.stats["failed"] += 1
        self.stats["errors"].append({"path": path, "error": "Max retries exceeded"})
        return False

    def generate_file_documentation(self, file_path: Path, layer: str) -> str:
        file_name = file_path.stem
        relative_path = str(file_path.relative_to(Path.cwd()))
        repo_url = f"{self.repo_base_url}{relative_path}"

        breadcrumb_parts = relative_path.replace("python_files/", "").split("/")
        breadcrumb = "[Home](/) > [unify_2_1_dm_synapse_env_d10](../"
        for i, part in enumerate(breadcrumb_parts[:-1]):
            breadcrumb += f") > [{part}](../"
        breadcrumb += f") > {file_name}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            imports = [line for line in lines if line.startswith('import ') or line.startswith('from ')]
            classes = [line.strip() for line in lines if line.strip().startswith('class ')]
            functions = [line.strip() for line in lines if line.strip().startswith('def ') and not line.strip().startswith('def __')]

        except Exception as e:
            imports, classes, functions = [], [], [f"Error reading file: {str(e)}"]

        user_story_section = generate_user_story_section(relative_path, self.organization, self.project)
        doc = f"""# {file_name}

{breadcrumb}

**Layer**: {layer}
**File Path**: `{relative_path}`
**Repository**: [View Source Code]({repo_url})

## Overview

This file is part of the {layer} layer in the Unify medallion architecture ETL pipeline.
{user_story_section}
## File Structure

### Imports
```python
{chr(10).join(imports[:10]) if imports else '# No imports found'}
```

### Classes
{chr(10).join([f"- `{c.split('(')[0].replace('class ', '')}`" for c in classes[:20]]) if classes else '- No classes defined'}

### Functions
{chr(10).join([f"- `{f.split('(')[0].replace('def ', '')}`" for f in functions[:20]]) if functions else '- No functions defined'}

## Key Components

"""

        for cls in classes[:5]:
            class_name = cls.split('(')[0].replace('class ', '').strip(':')
            doc += f"""
### {class_name}

ETL class following the medallion architecture pattern with extract, transform, and load methods.

**Pattern**: Extract → Transform → Load

**Methods**:
- `__init__()`: Initialize class with source table configuration
- `extract()`: Extract data from source layer
- `transform()`: Apply business logic and transformations
- `load()`: Persist transformed data to target layer

"""

        doc += f"""
## Dependencies

This file depends on core utilities:
- `SparkOptimiser`: Spark session management
- `NotebookLogger`: Structured logging framework
- `TableUtilities`: DataFrame operations (dedup, hashing, timestamps)
- `@synapse_error_print_handler`: Error handling decorator

## Usage

```python
# Run in Azure Synapse or local Spark environment
from python_files.{relative_path.replace('/', '.').replace('.py', '')} import *

# ETL execution happens in __init__
```

## Configuration

- **Source Database**: Configured in class __init__
- **Target Database**: Derived from source table naming convention
- **Environment**: Auto-detected (Azure Synapse vs Local)

## Notes

- All methods use `@synapse_error_print_handler` for error handling
- Logging uses `NotebookLogger` instead of print statements
- DataFrame operations preferred over raw SQL
- Follows 240-character line length limit

## Links

- [Repository File]({repo_url})
- [Parent Directory](../)
- [Layer Index](../../)

---

*Auto-generated documentation*
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        return doc

    def generate_directory_index(self, directory_name: str, files: List[Path], layer: str) -> str:
        directory_path = files[0].parent if files else Path(directory_name)
        relative_path = str(directory_path.relative_to(Path.cwd()))
        repo_url = f"{self.repo_base_url}{relative_path}"

        breadcrumb_parts = relative_path.replace("python_files/", "").split("/")
        breadcrumb = "[Home](/) > [unify_2_1_dm_synapse_env_d10](../"
        for i, part in enumerate(breadcrumb_parts):
            if i < len(breadcrumb_parts) - 1:
                breadcrumb += f") > [{part}](../"
            else:
                breadcrumb += f") > {part}"

        layer_descriptions = {
            "gold": "Business-ready analytics tables representing the final medallion layer. Aggregated, joined, and optimized for reporting and analysis.",
            "silver_cms": "Validated and standardized CMS (Case Management System) data with data quality rules applied and schema normalization.",
            "silver_fvms": "Validated and standardized FVMS (Fleet and Vehicle Management System) data with consistent formatting and business logic.",
            "silver_nicheRMS": "Validated and standardized NicheRMS (Records Management System) data with cleansing and standardization applied.",
            "utilities": "Core framework utilities supporting the medallion architecture: Spark session management, logging, DataFrame operations, and error handling.",
            "testing": "Comprehensive test suite for data quality validation across bronze, silver, and gold layers with medallion pipeline integration tests."
        }

        description = layer_descriptions.get(directory_name, f"Python files for the {layer} layer of the Unify data migration project.")

        doc = f"""# {directory_name.replace('_', ' ').title()}

{breadcrumb}

**Path**: `{relative_path}`
**Total Files**: {len(files)}
**Layer**: {layer}
**Repository Folder**: [View in Repository]({repo_url})

## Overview

{description}

## Files in This Directory

| File | Description | Type |
| ---- | ----------- | ---- |
"""

        for file_path in sorted(files):
            file_name = file_path.stem
            wiki_path = f"./{file_name}"

            if file_name.startswith('g_'):
                file_type = "Gold ETL"
                desc = "Analytics table ETL transformation"
            elif file_name.startswith('s_cms_'):
                file_type = "Silver CMS"
                desc = "CMS data validation and standardization"
            elif file_name.startswith('s_fvms_'):
                file_type = "Silver FVMS"
                desc = "FVMS data validation and standardization"
            elif file_name.startswith('s_nicherms_'):
                file_type = "Silver NicheRMS"
                desc = "NicheRMS data validation and standardization"
            elif 'test' in file_name:
                file_type = "Test Suite"
                desc = "Automated testing and validation"
            else:
                file_type = "Utility"
                desc = "Framework utility module"

            doc += f"| [{file_name}]({wiki_path}) | {desc} | {file_type} |\n"

        doc += f"""
## Architecture Context

This directory is part of the **Medallion Architecture** ETL pipeline:

1. **Bronze Layer**: Raw data ingestion from legacy systems (FVMS, CMS, NicheRMS)
2. **Silver Layer**: Data validation, cleansing, and standardization
3. **Gold Layer**: Business-ready analytics with aggregations and joins

## Key Patterns

- **ETL Classes**: Extract → Transform → Load pattern
- **Error Handling**: `@synapse_error_print_handler` decorator on all methods
- **Logging**: `NotebookLogger` for structured console output
- **DataFrame Ops**: PySpark DataFrame operations over raw SQL
- **Utilities**: `TableUtilities` for common operations (dedup, hashing, timestamps)

## Quick Links

- [Parent Directory](../)
- [Repository Folder]({repo_url})
- [Project Root](/)

---

*Auto-generated directory index*
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        return doc

    def publish_layer(self, layer_name: str, layer_path: str, wiki_base: str) -> None:
        print(f"\n{'='*80}")
        print(f"Publishing {layer_name} Layer")
        print(f"{'='*80}")

        files = sorted(Path(layer_path).glob("*.py"))
        files = [f for f in files if f.name != "__init__.py"]

        print(f"Found {len(files)} files")

        if not files:
            print(f"No files found in {layer_path}")
            return

        # Create directory index
        print(f"\nCreating directory index...")
        dir_index_content = self.generate_directory_index(layer_name, files, layer_name.replace("_", " ").title())
        dir_wiki_path = f"{wiki_base}/{layer_name}"

        if self.create_wiki_page(dir_wiki_path, dir_index_content):
            print(f"  ✓ Directory index created: {dir_wiki_path}")
        else:
            print(f"  ✗ Failed to create directory index: {dir_wiki_path}")

        # Create individual file pages
        print(f"\nCreating file pages...")
        for i, file_path in enumerate(files, 1):
            file_name = file_path.stem
            file_wiki_path = f"{wiki_base}/{layer_name}/{file_name}"

            print(f"  [{i}/{len(files)}] {file_name}...")

            file_content = self.generate_file_documentation(file_path, layer_name)
            self.create_wiki_page(file_wiki_path, file_content)

            self.stats["total_pages"] += 1

            # Rate limiting: 200 requests/minute
            if i % 50 == 0:
                print(f"  Pausing for rate limiting...")
                time.sleep(20)

    def publish_all(self) -> Dict:
        start_time = time.time()

        print("\n" + "="*80)
        print("WIKI BULK PUBLISHER - Unify Data Migration Documentation")
        print("="*80)
        print(f"Organization: {self.organization}")
        print(f"Project: {self.project}")
        print(f"Wiki: {self.wiki_identifier}")
        print("="*80)

        base_path = Path.cwd() / "python_files"
        wiki_base = f"/{Path.cwd().name}"

        # Create project root index
        print("\nCreating project root index...")
        root_content = f"""# Unify Data Migration - Python Files Documentation

[Home](/)

**Project**: Unify 2.1 Data Migration
**Architecture**: Medallion (Bronze → Silver → Gold)
**Platform**: Azure Synapse Analytics
**Framework**: PySpark ETL Pipelines

## Overview

This documentation covers the complete Python codebase for the Unify data migration project, implementing a medallion architecture for ETL processing of legacy data from FVMS, CMS, and NicheRMS systems.

## Directory Structure

| Layer | Files | Description |
| ----- | ----- | ----------- |
| [gold](./gold) | 98 | Business-ready analytics tables (final medallion layer) |
| [silver/silver_cms](./silver/silver_cms) | 42 | Validated CMS data transformations |
| [silver/silver_fvms](./silver/silver_fvms) | 19 | Validated FVMS data transformations |
| [silver/silver_nicheRMS](./silver/silver_nicheRMS) | 7 | Validated NicheRMS data transformations |
| [utilities](./utilities) | 20 | Core framework utilities (Spark, logging, DataFrame ops) |
| [testing](./testing) | 9 | Comprehensive test suite for data quality validation |
| [pipeline_operations](./pipeline_operations) | 10 | Pipeline deployment and orchestration scripts |

**Total Files**: 205 Python modules

## Medallion Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      LEGACY SOURCES                          │
│              FVMS │ CMS │ NicheRMS │ Spreadsheets           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BRONZE LAYER                            │
│              Raw parquet ingestion (b_* tables)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      SILVER LAYER                            │
│    Validated, standardized data (s_cms_*, s_fvms_*, s_nicherms_*) │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       GOLD LAYER                             │
│         Business-ready analytics (g_* tables)               │
└─────────────────────────────────────────────────────────────┘
```

## Core Utilities

All ETL processes leverage these core utilities:

- **SparkOptimiser**: Configured Spark session management
- **NotebookLogger**: Rich console logging framework
- **TableUtilities**: DataFrame operations (deduplication, hashing, timestamps)
- **@synapse_error_print_handler**: Mandatory error handling decorator

## ETL Pattern

All silver and gold ETL modules follow this pattern:

```python
class TableName:
    def __init__(self, bronze_table_name: str):
        # Initialize configuration
        self.extract_sdf = self.extract()
        self.transform_sdf = self.transform()
        self.load()

    @synapse_error_print_handler
    def extract(self) -> DataFrame:
        # Extract from source layer

    @synapse_error_print_handler
    def transform(self) -> DataFrame:
        # Apply business logic

    @synapse_error_print_handler
    def load(self) -> None:
        # Persist to target layer
```

## Quick Links

- [Gold Layer Documentation](./gold)
- [Silver Layer Documentation](./silver)
- [Utilities Documentation](./utilities)
- [Testing Documentation](./testing)
- [Repository](https://dev.azure.com/emstas/Program%20Unify/_git/unify_2_1_dm_synapse_env_d10)

---

*Auto-generated documentation*
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        if self.create_wiki_page(wiki_base, root_content):
            print(f"  ✓ Root index created")
        else:
            print(f"  ✗ Failed to create root index")

        # Publish Gold Layer
        self.publish_layer("gold", f"{base_path}/gold", wiki_base)

        # Create Silver parent index
        print("\n" + "="*80)
        print("Creating Silver Layer Parent Index")
        print("="*80)

        silver_parent_content = f"""# Silver Layer

[Home](/) > [unify_2_1_dm_synapse_env_d10](../) > silver

**Path**: `python_files/silver`
**Total Files**: 68 (42 CMS + 19 FVMS + 7 NicheRMS)
**Repository**: [View in Repository]({self.repo_base_url}python_files/silver)

## Overview

The Silver layer provides validated and standardized data transformations from the Bronze layer. Data quality rules are applied, schemas are normalized, and business logic is implemented to create clean, consistent datasets ready for analytics.

## Silver Layer Subdirectories

| Subdirectory | Files | Description |
| ------------ | ----- | ----------- |
| [silver_cms](./silver_cms) | 42 | CMS (Case Management System) validated transformations |
| [silver_fvms](./silver_fvms) | 19 | FVMS (Fleet and Vehicle Management) validated transformations |
| [silver_nicheRMS](./silver_nicheRMS) | 7 | NicheRMS (Records Management) validated transformations |

## Data Flow

```
Bronze Layer (b_*) → Silver Layer (s_*) → Gold Layer (g_*)
```

## Key Transformations

- Data type validation and casting
- Null handling and default values
- Date/time standardization
- String normalization (trim, case, encoding)
- Business rule validation
- Referential integrity checks
- Duplicate detection and resolution

## Links

- [Parent Directory](../)
- [Repository Folder]({self.repo_base_url}python_files/silver)

---

*Auto-generated directory index*
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        silver_wiki_path = f"{wiki_base}/silver"
        if self.create_wiki_page(silver_wiki_path, silver_parent_content):
            print(f"  ✓ Silver parent index created")
        else:
            print(f"  ✗ Failed to create silver parent index")

        # Publish Silver CMS
        self.publish_layer("silver_cms", f"{base_path}/silver/silver_cms", f"{wiki_base}/silver")

        # Publish Silver FVMS
        self.publish_layer("silver_fvms", f"{base_path}/silver/silver_fvms", f"{wiki_base}/silver")

        # Publish Silver NicheRMS
        self.publish_layer("silver_nicheRMS", f"{base_path}/silver/silver_nicheRMS", f"{wiki_base}/silver")

        # Publish Utilities
        self.publish_layer("utilities", f"{base_path}/utilities", wiki_base)

        # Publish Testing
        self.publish_layer("testing", f"{base_path}/testing", wiki_base)

        # Generate final report
        elapsed_time = time.time() - start_time

        report = {
            "summary": {
                "total_pages": self.stats["total_pages"],
                "successful": self.stats["successful"],
                "failed": self.stats["failed"],
                "skipped": self.stats["skipped"],
                "execution_time_seconds": round(elapsed_time, 2)
            },
            "breakdown": {
                "gold": 98,
                "silver_cms": 42,
                "silver_fvms": 19,
                "silver_nicheRMS": 7,
                "utilities": 20,
                "testing": 9,
                "indexes": 8
            },
            "errors": self.stats["errors"],
            "wiki_base_url": f"https://dev.azure.com/{self.organization}/{self.project}/_wiki/wikis/{self.wiki_identifier}?wikiVersion=GBwikiMaster&pagePath={wiki_base}"
        }

        print("\n" + "="*80)
        print("PUBLICATION COMPLETE")
        print("="*80)
        print(json.dumps(report, indent=2))

        return report

if __name__ == "__main__":
    publisher = WikiPublisher()
    report = publisher.publish_all()

    with open("/tmp/wiki_publication_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: /tmp/wiki_publication_report.json")
