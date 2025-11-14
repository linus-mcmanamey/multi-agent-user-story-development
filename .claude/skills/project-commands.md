---
name: project-commands
description: Complete reference for all make commands, development workflows, Azure operations, and database operations. Use when you need to know how to run specific operations.
---

# Project Commands Reference

Complete command reference for the Unify data migration project.

## Build & Test Commands

### Syntax Validation
```bash
python3 -m py_compile <file_path>
python3 -m py_compile python_files/utilities/session_optimiser.py
```

### Code Quality
```bash
ruff check python_files/          # Linting (must pass)
ruff format python_files/         # Auto-format code
```

### Testing
```bash
python -m pytest python_files/testing/                    # All tests
python -m pytest python_files/testing/medallion_testing.py  # Integration
```

## Pipeline Commands

### Complete Pipeline
```bash
make run_all  # Executes: choice_list_mapper → bronze → silver → gold → build_duckdb
```

### Layer-Specific (WARNING: Deletes existing layer data)
```bash
make bronze       # Bronze layer pipeline (deletes /workspaces/data/bronze_*)
make run_silver   # Silver layer (includes choice_list_mapper, deletes /workspaces/data/silver_*)
make gold         # Gold layer (includes DuckDB build, deletes /workspaces/data/gold_*)
```

### Specific Table Execution
```bash
# Run specific silver table
make silver_table FILE_READ_LAYER=silver PATH_DATABASE=silver_fvms RUN_FILE_NAME=s_fvms_incident

# Run specific gold table
make gold_table G_RUN_FILE_NAME=g_x_mg_statsclasscount

# Run currently open file (auto-detects layer and database)
make current_table  # Requires: make install_file_tracker (run once, then reload VSCode)
```

## Development Workflow

### Interactive UI
```bash
make ui  # Interactive menu for all commands
```

### Data Generation
```bash
make generate_data  # Generate synthetic test data
```

## Spark Thrift Server

Enables JDBC/ODBC connections to local Spark data on port 10000:

```bash
make thrift-start   # Start server
make thrift-status  # Check if running
make thrift-stop    # Stop server

# Connect via spark-sql CLI
spark-sql -e "SHOW DATABASES; SHOW TABLES;"
spark-sql -e "SELECT * FROM gold_data_model.g_x_mg_statsclasscount LIMIT 10;"
```

## Database Operations

### Database Inspection
```bash
make database-check  # Check Hive databases and tables

# View schemas
spark-sql -e "SHOW DATABASES; SHOW TABLES;"
```

### DuckDB Operations
```bash
make build_duckdb  # Build local DuckDB database (/workspaces/data/warehouse.duckdb)
make harly         # Open Harlequin TUI for interactive DuckDB queries
```

**DuckDB Benefits**:
- Fast local queries without Azure connection
- Data exploration and validation
- Report prototyping
- Testing query logic before deploying to Synapse

## Azure Operations

### Authentication
```bash
make azure_login  # Azure CLI login
```

### SharePoint Integration
```bash
# Download SharePoint files
make download_sharepoint SHAREPOINT_FILE_ID=<file-id>

# Convert Excel to JSON
make convert_excel_to_json

# Upload to Azure Storage
make upload_to_storage UPLOAD_FILE=<file-path>
```

### Complete Pipelines
```bash
# Offence mapping pipeline
make offence_mapping_build  # download_sharepoint → convert_excel_to_json → upload_to_storage

# Table list management
make table_lists_pipeline    # download_ors_table_mapping → generate_table_lists → upload_all_table_lists
make update_pipeline_variables  # Update Azure Synapse pipeline variables
```

## AI Agent Integration

### User Story Processing
Automate ETL file generation from Azure DevOps user stories:

```bash
make user_story_build \
  A_USER_STORY=44687 \
  A_FILE_NAME=g_x_mg_statsclasscount \
  A_READ_LAYER=silver \
  A_WRITE_LAYER=gold
```

**What it does**:
- Reads user story requirements from Azure DevOps
- Generates ETL transformation code
- Creates appropriate tests
- Follows project coding standards

### Agent Session
```bash
make session  # Start persistent Claude Code session with dangerously-skip-permissions
```

## Git Operations

### Branch Merging
```bash
make merge_staging   # Merge from staging (adds all changes, commits, pulls with --no-ff)
make rebase_staging  # Rebase from staging (adds all changes, commits, rebases)
```

## Environment Variables

### Required for Azure DevOps MCP
```bash
export AZURE_DEVOPS_PAT="<your-personal-access-token>"
export AZURE_DEVOPS_ORGANIZATION="emstas"
export AZURE_DEVOPS_PROJECT="Program Unify"
```

### Required for Azure Operations
See `configuration.yaml` for complete list of Azure environment variables.

## Common Workflows

### Complete Development Cycle
```bash
# 1. Generate test data
make generate_data

# 2. Run full pipeline
make run_all

# 3. Explore results
make harly

# 4. Run tests
python -m pytest python_files/testing/

# 5. Quality checks
ruff check python_files/
ruff format python_files/
```

### Quick Table Development
```bash
# 1. Open file in VSCode
# 2. Run current file
make current_table

# 3. Check output in DuckDB
make harly
```

### Quality Gates Before Commit
```bash
# Must run these before committing
python3 -m py_compile <file>  # 1. Syntax check
ruff check python_files/       # 2. Linting (must pass)
ruff format python_files/      # 3. Format code
```

## Troubleshooting Commands

### Check Spark Session
```bash
spark-sql -e "SHOW DATABASES;"
```

### Verify Azure Connection
```bash
make azure_login
az account show
```

### Check Data Paths
```bash
ls -la /workspaces/data/
```

## File Tracker Setup

One-time setup for `make current_table`:
```bash
make install_file_tracker
# Then reload VSCode
```

## Notes

- **Data Deletion**: Layer-specific commands delete existing data before running
- **Thrift Server**: Port 10000 for JDBC/ODBC connections
- **DuckDB**: Local analysis without Azure connection required
- **Quality Gates**: Always run before committing code
