---
name: project-architecture
description: Detailed architecture, data flow, pipeline execution, dependencies, and system design for the Unify data migration project. Use when you need deep understanding of how components interact.
---

# Project Architecture

Comprehensive architecture documentation for the Unify data migration project.

## Medallion Architecture Deep Dive

### Bronze Layer
**Purpose**: Raw data ingestion from parquet files
**Location**: `python_files/pipeline_operations/bronze_layer_deployment.py`
**Process**:
1. Lists parquet files from Azure ADLS Gen2 or local storage
2. Creates bronze databases: `bronze_cms`, `bronze_fvms`, `bronze_nicherms`
3. Reads parquet files and applies basic transformations
4. Adds versioning, row hashes, and data source columns

### Silver Layer
**Purpose**: Validated, standardized data organized by source
**Location**: `python_files/silver/` (cms, fvms, nicherms subdirectories)
**Process**:
1. Drops and recreates silver databases
2. Recursively finds all Python files in `python_files/silver/`
3. Executes each silver transformation file in sorted order
4. Uses threading for parallel execution (currently commented out)

### Gold Layer
**Purpose**: Business-ready, aggregated analytical datasets
**Location**: `python_files/gold/`
**Process**:
1. Creates business-ready analytical tables in `gold_data_model` database
2. Executes transformations from `python_files/gold/`
3. Aggregates and joins data across multiple silver tables

## Data Sources

### FVMS (Family Violence Management System)
- **Tables**: 32 tables
- **Key tables**: incident, person, address, risk_assessment
- **Purpose**: Family violence incident tracking and management

### CMS (Case Management System)
- **Tables**: 19 tables
- **Key tables**: offence_report, case_file, person, victim
- **Purpose**: Criminal offence investigation and case management

### NicheRMS (Records Management System)
- **Tables**: 39 TBL_* tables
- **Purpose**: Legacy records management system

## Azure Integration

### Storage (ADLS Gen2)
- **Containers**: `bronze-layer`, `code-layer`, `legacy_ingestion`
- **Authentication**: Managed Identity (`AZURE_MANAGED_IDENTITY_CLIENT_ID`)
- **Path Pattern**: `abfss://container@account.dfs.core.windows.net/path`

### Key Services
- **Key Vault**: `AuE-DataMig-Dev-KV` for secret management
- **Synapse Workspace**: `auedatamigdevsynws`
- **Spark Pool**: `dm8c64gb`

## Environment Detection Pattern

All processing scripts auto-detect their runtime environment:

```python
if "/home/trusted-service-user" == env_vars["HOME"]:
    # Azure Synapse Analytics production environment
    import notebookutils.mssparkutils as mssparkutils
    spark = SparkOptimiser.get_optimised_spark_session()
    DATA_PATH_STRING = "abfss://code-layer@auedatamigdevlake.dfs.core.windows.net"
else:
    # Local development environment using Docker Spark container
    from python_files.utilities.local_spark_connection import sparkConnector
    config = UtilityFunctions.get_settings_from_yaml("configuration.yaml")
    connector = sparkConnector(...)
    DATA_PATH_STRING = config["DATA_PATH_STRING"]
```

## Core Utilities Architecture

### SparkOptimiser
- Configured Spark session with optimized settings
- Handles driver memory, encryption, authentication
- Centralized session management

### NotebookLogger
- Rich console logging with fallback to standard print
- Structured logging (info, warning, error, success)
- Graceful degradation when Rich library unavailable

### TableUtilities
- DataFrame operations (deduplication, hashing, timestamp conversion)
- `add_row_hash()`: Change detection
- `save_as_table()`: Standard table save with timestamp conversion
- `clean_date_time_columns()`: Intelligent timestamp parsing
- `drop_duplicates_simple/advanced()`: Deduplication strategies
- `filter_and_drop_column()`: Remove duplicate flags

### DAGMonitor
- Pipeline execution tracking and reporting
- Performance metrics and logging

## Configuration Management

### configuration.yaml
Central YAML configuration includes:
- **Data Sources**: FVMS, CMS, NicheRMS table lists (`*_IN_SCOPE` variables)
- **Azure Settings**: Storage accounts, Key Vault, Synapse workspace, subscription IDs
- **Spark Settings**: Driver, encryption, authentication scheme
- **Data Paths**: Local (`/workspaces/data`) vs Azure (`abfss://`)
- **Logging**: LOG_LEVEL, LOG_ROTATION, LOG_RETENTION
- **Nulls Handling**: STRING_NULL_REPLACEMENT, NUMERIC_NULL_REPLACEMENT, TIMESTAMP_NULL_REPLACEMENT

## Error Handling Strategy

- **Decorator-Based**: `@synapse_error_print_handler` for consistent error handling
- **Loguru Integration**: Structured logging with proper levels
- **Graceful Degradation**: Handle missing dependencies (Rich library fallback)
- **Context Information**: Include table/database names in all log messages

## Local Data Filtering

`TableUtilities.save_as_table()` automatically filters to last N years when `date_created` column exists, controlled by `NUMBER_OF_YEARS` global variable in `session_optimiser.py`. Prevents full dataset processing in local development.

## Testing Architecture

### Test Structure
- `python_files/testing/`: Unit and integration tests
- `medallion_testing.py`: Full pipeline validation
- `bronze_layer_validation.py`: Bronze layer tests
- `ingestion_layer_validation.py`: Ingestion tests

### Testing Strategy
- pytest integration with PySpark environments
- Quality gates: syntax validation and linting before completion
- Integration tests for full medallion flow

## DuckDB Integration

After running pipelines, build local DuckDB database for fast SQL analysis:
- **File**: `/workspaces/data/warehouse.duckdb`
- **Command**: `make build_duckdb`
- **Purpose**: Fast local queries without Azure connection
- **Contains**: All bronze, silver, gold layer tables

## Recent Architectural Changes

### Path Migration
- Standardized all paths to use `unify_2_1_dm_synapse_env_d10`
- Improved portability and environment consistency
- 12 files updated across utilities, notebooks, configurations

### Code Cleanup
- Removed unused utilities: `file_executor.py`, `file_finder.py`
- Reduced codebase complexity
- Regular cleanup pattern for maintainability
