# Schema Mapping Conventions

This document explains how schemas map between the medallion architecture layers (bronze, silver, gold) and the legacy warehouse.

## Layer Structure

The project implements a three-layer medallion architecture:

```
Bronze Layer → Silver Layer → Gold Layer
     ↓              ↓              ↓
Raw Data    Validated Data   Business Data
```

### Bronze Layer

- **Purpose**: Raw data ingestion from parquet files
- **Database Naming**: `bronze_{source}` (e.g., `bronze_cms`, `bronze_fvms`, `bronze_nicherms`)
- **Table Naming**: `b_{source}_{table}` (e.g., `b_cms_case`, `b_fvms_incident`)
- **Characteristics**:
  - Minimal transformation
  - Preserves source column names
  - Adds metadata columns: `data_source`, `load_date`, `row_hash`

### Silver Layer

- **Purpose**: Validated, standardized data organized by source
- **Database Naming**: `silver_{source}` (e.g., `silver_cms`, `silver_fvms`, `silver_nicherms`)
- **Table Naming**: `s_{source}_{table}` (e.g., `s_cms_case`, `s_fvms_incident`)
- **Characteristics**:
  - Data quality validation
  - Standardized data types
  - Primary keys renamed with `s_` prefix (e.g., `cms_case_id` → `s_cms_case_id`)
  - Timestamp columns converted to proper format
  - Deduplication applied
  - Choice list mappings applied (enumerations resolved to descriptive values)

### Gold Layer

- **Purpose**: Business-ready, aggregated analytical datasets
- **Database Naming**: `gold_data_model`
- **Table Naming**: `g_{source}_mg_{report_name}` or `g_x_mg_{report_name}`
  - `g_` prefix indicates gold layer
  - `{source}` indicates primary source (e.g., `fvms`, `cms`, `nicherms`)
  - `x` indicates cross-source (joins multiple sources)
  - `mg` indicates "management" or analytical report
  - Examples: `g_fvms_mg_incident_summary`, `g_x_mg_statsclasscount`
- **Characteristics**:
  - Business logic applied
  - Aggregations and calculations
  - Cross-source joins
  - Optimized for reporting and analysis

## Naming Convention Translation

### Primary Keys

| Layer | Convention | Example |
|-------|-----------|---------|
| **Data Dictionary** | `{source}_{table}_id` | `cms_case_id` |
| **Bronze** | Same as source | `cms_case_id` |
| **Silver** | `s_{source}_{table}_id` | `s_cms_case_id` |
| **Legacy Warehouse** | `id` | `id` |

### Foreign Keys

Foreign keys remain consistent across all layers and are named as `{referenced_table}_id` (e.g., `allocation_area_id`, `status_id`).

### Junction Tables

Junction tables (many-to-many relationships) use double underscore separator:
- Pattern: `{table1}__{table2}`
- Example: `cms_case__officer` (links cases to officers)
- Primary Key: Composite of both foreign keys

## Legacy Warehouse Mapping

The legacy warehouse (DuckDB) has a different schema structure:

```
cms_case (data dictionary) → s_cms_case (silver) → case_file (legacy)
fvms_incident (data dictionary) → s_fvms_incident (silver) → incident (legacy)
```

### Key Differences

1. **Table Names**: Legacy tables often have simplified names
   - `cms_case` → `case_file`
   - `cms_person` → `person`
   - `fvms_incident` → `incident`

2. **Primary Keys**: Legacy always uses `id`
   - Silver: `s_cms_case_id`
   - Legacy: `id`

3. **Database Structure**: Legacy uses `{source}_legacy` schema
   - `cms_legacy.case_file`
   - `fvms_legacy.incident`
   - `nicherms_legacy.TBL_INCIDENT`

## Common Transformations

### Bronze → Silver

Typical transformations when moving from bronze to silver:

1. **Primary Key Renaming**:
   ```python
   # Bronze: cms_case_id
   # Silver: s_cms_case_id
   .withColumnRenamed("cms_case_id", "s_cms_case_id")
   ```

2. **Timestamp Conversion**:
   ```python
   # Convert string timestamps to proper timestamp type
   TableUtilities.clean_date_time_columns(df)
   ```

3. **Deduplication**:
   ```python
   # Remove duplicates based on primary key
   TableUtilities.drop_duplicates_advanced(df, ["s_cms_case_id"])
   ```

4. **Choice List Mapping**:
   ```python
   # Map enumeration values to descriptive text
   # Example: status_id (1) → "Active"
   df.join(choice_list_df, "status_id", "left")
   ```

### Silver → Gold

Typical transformations when moving from silver to gold:

1. **Cross-Source Joins**:
   ```python
   # Join CMS and FVMS data
   cms_case = spark.table("silver_cms.s_cms_case")
   fvms_incident = spark.table("silver_fvms.s_fvms_incident")
   joined = cms_case.join(fvms_incident, ...)
   ```

2. **Aggregations**:
   ```python
   # Count cases by status
   df.groupBy("status").count()
   ```

3. **Business Logic**:
   ```python
   # Apply business rules
   # Example: Calculate case age
   .withColumn("case_age_days",
               F.datediff(F.current_date(), F.col("date_created")))
   ```

## Column Conventions

### Standard Columns

All bronze and silver tables include these metadata columns:

- `data_source`: Source system identifier
- `load_date`: Timestamp when data was loaded
- `row_hash`: Hash of row values for change detection
- `date_created`: Original record creation date
- `last_updated`: Original record update date

### Timestamp Columns

Timestamp columns are standardized in silver layer:
- Type: `TIMESTAMP`
- Format: `yyyy-MM-dd HH:mm:ss`
- Null handling: Replaced with configured null value

### String Columns

String columns are cleaned in silver layer:
- Trimmed of leading/trailing whitespace
- Null values replaced with configured null value
- Maximum length enforced

## Identifying Column Mappings

When writing transformations, use these strategies to identify column mappings:

1. **Use Data Dictionary**: Reference `.claude/data_dictionary/{table}.md` for column descriptions and relationships

2. **Check Foreign Keys**: Data dictionary shows which columns link to other tables

3. **Query DuckDB**: Use `query_duckdb_schema.py` to see actual column names and types

4. **Compare Layers**: Use `schema_comparison.py` to see differences between bronze and silver

5. **Look for Business Logic**: Check data dictionary for "linked to", "common values", "default" patterns
