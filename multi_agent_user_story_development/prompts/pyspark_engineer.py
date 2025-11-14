from pathlib import Path


def generate_implementation_prompt(user_story: str, file_name: str, read_layer: str, write_layer: str, doc_path: Path) -> str:
    """Generate efficient PySpark implementation prompt with clear structure and actionable tasks."""
    datasource = "cms" if "cms" in file_name.lower() else "fvms" if "fvms" in file_name.lower() else "nicherms"
    layer_class_name = f"{write_layer.capitalize()}Loader"
    return f"""# PySpark Data Pipeline Implementation

@pyspark-engineer
LOCATION: .claude/agents/spark-developer.md

## CONTEXT
- **User Story ID**: {user_story}
- **Target File**: `python_files/{write_layer}/{write_layer}_{datasource}/{file_name}.py`
- **Data Flow**: {read_layer} to {write_layer}
- **Class Name**: `{layer_class_name}`
- **Business Analysis**: `{doc_path}`

## PRIMARY OBJECTIVE
Implement production-ready PySpark data transformation based on business analyst specifications.

## � CRITICAL EXECUTION INSTRUCTIONS �
**AUTOMATED NON-INTERACTIVE WORKFLOW - NO USER PRESENT**

YOU MUST:
1. **IMMEDIATELY USE ALL REQUIRED TOOLS** - Do NOT ask "Should I proceed?" or "May I use these tools?"
2. **EXECUTE EVERY PHASE WITHOUT STOPPING** - This workflow has no human to approve actions
3. **NEVER WAIT FOR CONFIRMATION** - There is no user to respond to questions
4. **IF A TOOL IS NEEDED, USE IT IMMEDIATELY** - Permission is pre-granted for Read, Write, Edit tools

YOU WILL FAIL THIS TASK IF YOU:
- Ask for permission to use tools
- Wait for approval before executing phases
- Stop and ask "Should I proceed?"
- Request confirmation for any action

**Start Phase 1 immediately after reading this prompt. Use tools directly.**

---

## EXECUTION WORKFLOW

### PHASE 1: Read Project Guidelines
**Action**: IMMEDIATELY Read `.claude/CLAUDE.md` for critical coding standards
**Key Points to Remember**:
- Maximum line length: 240 characters
- No blank lines inside functions
- Single line between functions, double between classes
- All imports at top of file
- Type hints for all parameters and return values
- Use `@synapse_error_print_handler` decorator on all functions
- DataFrame variables end with `_sdf` suffix

### PHASE 2: Read Table Memory (If Available)
**Action**: Check for existing table memory to understand historical context

1. **Extract Clean Table Name**:
   - Remove layer prefix from `{file_name}` (e.g., "g_mg_occurrence" to "mg_occurrence")
   - Store as: clean_table_name

2. **Check Memory**:
   - Use `list_memories` with layer="{write_layer}", datasource="{datasource}", table_name=clean_table_name
   - If memory exists, use `read_memory` with layer="{write_layer}", datasource="{datasource}", table_name=clean_table_name

3. **Extract Memory Context** (if available):
   - **Changelog**: Previous user stories that modified this table
   - **Existing transformations**: Current transformation logic already implemented
   - **Business rules**: Established business rules to maintain
   - **Data quality rules**: Existing validations to preserve
   - **Gotchas**: Known issues or special considerations
   - **Related tables**: Dependencies to be aware of

4. **Use Memory to Guide Implementation**:
   - Understand what logic already exists (avoid duplication)
   - Identify what needs to be added vs modified
   - Maintain consistency with previous work

### PHASE 3: Read Business Analysis & Schema Documentation
**Action**: IMMEDIATELY Read `{doc_path}`
**Extract**:
- Requirements summary
- Data dictionary references (source system documentation)
- DuckDB schema references (current implementation)
- Schema comparison notes (discrepancies, NULL handling)
- Source/target column mappings
- Transformation specifications with business context
- Existing code analysis (if applicable)
- Data quality rules
- Testing scenarios

### PHASE 4: Check Existing Implementation
**Action**: Use **Read tool** to check if Python file exists

**File Path to Check**: `python_files/{write_layer}/{file_name}.py`

**Method**:
1. Try to Read the file at: Project root + `/python_files/{write_layer}/{file_name}.py`
2. If Read succeeds to File exists, use **Edit tool** to modify
3. If Read fails to File doesn't exist, use **Write tool** to create new file

**If File Exists** (Read succeeded):
1. Review existing class structure and functions
2. Check all user story references (#### US: comments)
3. **PRESERVE** all existing functions unless business analysis explicitly marks for deprecation
4. **ADD** new functions to existing class using **Edit tool** (don't replace entire file)
5. **MAINTAIN** existing US comments - do not remove without BA approval
6. Example: Add new transformation function after existing functions

**If File Not Exists** (Read failed): Create new file with complete class structure using **Write tool**

### PHASE 5: Verify Schemas & Cross-Reference Documentation
**Use DuckDB MCP and data dictionary files to confirm schemas**:

1. **Read Data Dictionary Files** (if referenced in BA doc):
   - BA doc will reference `.claude/data_dictionary/{datasource}_<table>.md` files
   - Read referenced data dictionary files to understand:
     * Business column descriptions
     * NULL constraints and common values
     * Data type expectations from source system
     * Foreign key relationships

2. **Query DuckDB Current Schema** (verify actual implementation):
   - Use `mcp__mcp-server-motherduck__query` MCP tool to query table schemas
   - Get source table schema:
     ```sql
     SELECT column_name, data_type, max_length, precision, scale, is_nullable,
            is_primary_key, foreign_key_name, referenced_table_name
     FROM data_hub.legacy_schema
     WHERE table_name = 'source_table_name'
     ORDER BY column_name;
     ```
   - Get target table schema (if exists):
     ```sql
     SELECT column_name, data_type, max_length, precision, scale, is_nullable
     FROM data_hub.legacy_schema
     WHERE table_name = 'target_table_name'
     ORDER BY column_name;
     ```
   - Verify column names and types match BA specifications

3. **Cross-Reference & Validate**:
   - **Data Dictionary** to Expected schema from source system
   - **DuckDB Schema** to Current implementation
   - **BA Documentation** to Required transformations
   - Note any discrepancies or special handling needed

### PHASE 6: Implementation

#### 5.1 File Structure (for NEW files)
```python
from pyspark.sql import DataFrame
from pyspark.sql.functions import [required_functions]
from datetime import datetime
import sys
from pathlib import Path
import os

env_vars = dict(os.environ)

if "/home/trusted-service-user" == env_vars["HOME"]:
    import notebookutils.mssparkutils as mssparkutils
    spark = SparkOptimiser.get_optimised_spark_session()
    table_utilities = TableUtilities()
    logger = NotebookLogger()
    DATA_PATH_STRING = "abfss://{read_layer}-layer@auedatamigdevlake.dfs.core.windows.net"
else:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from utilities.local_spark_connection import sparkConnector, UtilityFunctions
    from utilities.session_optimiser import TableUtilities, NotebookLogger, synapse_error_print_handler
    config = UtilityFunctions.get_settings_from_yaml("configuration.yaml")
    connector = sparkConnector(server_address=config["ZERO_TWO_SERVER_ADDRESS"], database_name=config["DATABASES_IN_SCOPE"][0], config=config)
    spark = connector.spark
    table_utilities = TableUtilities()
    logger = NotebookLogger()
    DATA_PATH_STRING = config["DATA_PATH_STRING"]


class {layer_class_name}:
    def __init__(self, {read_layer}_table_name: str):
        self.{read_layer}_table_name = {read_layer}_table_name
        self.{write_layer}_database_name = f"{write_layer}_{{self.{read_layer}_table_name.split('.')[0].split('_')[-1]}}"
        self.{write_layer}_table_name = self.{read_layer}_table_name.split(".")[-1].replace("{read_layer[0]}_", "{write_layer[0]}_")
        self.extract_sdf = self.extract()
        self.transform_sdf = self.transform()
        self.load()

    @synapse_error_print_handler
    def extract(self) -> DataFrame:
        return spark.read.table(self.{read_layer}_table_name)

    @synapse_error_print_handler
    def transform(self) -> DataFrame:
        #### US: {user_story}
        transform_sdf = self.extract_sdf
        # Add transformation function calls here
        return transform_sdf

    @synapse_error_print_handler
    def load(self) -> None:
        table_utilities.save_as_table(self.transform_sdf, f"{{self.{write_layer}_database_name}}.{{self.{write_layer}_table_name}}")


# Execution
{layer_class_name}("{read_layer}_{datasource}.{read_layer[0]}_{datasource}_<table_name>")
```

#### 5.2 Adding Functions to Existing Class
**If updating existing file**:
1. DO NOT remove existing functions
2. DO NOT modify existing functions unless BA explicitly requires it
3. ADD new transformation functions to the class
4. UPDATE `transform()` method to call new functions
5. ADD `#### US: {user_story}` comment above each NEW function

**Pattern for new functions**:
```python
@synapse_error_print_handler
def new_transformation_function(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Transformation logic here
    return transform_sdf
```

#### 5.3 Implement Transformations
**For each transformation in BA spec**:
1. Create dedicated function with descriptive name **using Australian English spelling**
2. Add US comment: `#### US: {user_story}`
3. Use type hints: `def function_name(self, transform_sdf: DataFrame) -> DataFrame:`
4. Apply PySpark operations based on BA specifications
5. Implement business rules from data dictionary context
6. Add validation logic respecting NULL constraints
7. Return transformed DataFrame

**IMPORTANT - AUSTRALIAN ENGLISH SPELLING**:
All function and variable names MUST use Australian English spelling:
- `normalise_data()` not `normalize_data()`
- `standardise_column()` not `standardize_column()`
- `analyse_values()` not `analyze_values()`
- `categorise_records()` not `categorize_records()`
- `summarise_results()` not `summarize_results()`
- `optimise_query()` not `optimize_query()`
- `finalise_output()` not `finalize_output()`

**Example transformations with data dictionary context**:
```python
@synapse_error_print_handler
def add_business_logic_column(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Data dictionary: source_col VARCHAR(100), allows NULL
    # Business rule: Convert to string, preserve NULLs
    return transform_sdf.withColumn("new_column", col("source_col").cast("string"))

@synapse_error_print_handler
def apply_data_quality_rules(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Data dictionary: important_field does NOT allow NULL in source system
    # Validation: Filter out NULL values (data quality issue)
    return transform_sdf.filter(col("important_field").isNotNull())

@synapse_error_print_handler
def handle_allocation_area_nulls(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Data dictionary: allocation_area_id allows NULL (27% of records)
    # Common values: 63 "Launceston CIB" (25%), 20 "Burnie CIB" (5%), 1 (inactive, treat as NULL)
    # Business rule: Replace 1 with NULL for consistency
    return transform_sdf.withColumn("allocation_area_id", when(col("allocation_area_id") == 1, lit(None)).otherwise(col("allocation_area_id")))

@synapse_error_print_handler
def join_reference_data(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Data dictionary: foreign key to reference table via id column
    ref_sdf = spark.read.table("reference.table")
    return transform_sdf.join(ref_sdf, "join_key", "left")
```

#### 5.4 Update Transform Method
**Chain all transformations in `transform()` method**:
```python
@synapse_error_print_handler
def transform(self) -> DataFrame:
    transform_sdf = self.extract_sdf
    transform_sdf = self.existing_function(transform_sdf)  # Preserve existing
    transform_sdf = self.new_transformation_function(transform_sdf)  # Add new
    transform_sdf = self.add_business_logic_column(transform_sdf)  # Add new
    transform_sdf = self.apply_data_quality_rules(transform_sdf)  # Add new
    return transform_sdf
```

### PHASE 7: Code Quality Validation
**Before saving**:

* All functions have `@synapse_error_print_handler` decorator
* All NEW functions have `#### US: {user_story}` comment
* All functions have type hints
* DataFrame variables use `_sdf` suffix
* No blank lines inside functions
* Line length d 240 characters
* Imports at top of file
* Existing functions preserved (unless BA marked for removal)
* Class properly instantiated at bottom with correct table name

### PHASE 8: Save Implementation
**IMPORTANT**: Gold layer files go directly in `python_files/gold/`, NOT in subdirectories!

**File Path**:
- For gold layer: `python_files/gold/{file_name}.py`
- For silver/bronze: `python_files/{write_layer}/{write_layer}_{datasource}/{file_name}.py`

**Full Path for this task**: Project root + `/python_files/{write_layer}/{file_name}.py`

**Method**:
- **If NEW file**: Use **Write tool** with full file content
- **If UPDATING existing**: Use **Edit tool** to add/modify specific functions only

**DO NOT**:
- Create or save .ipynb notebooks (Python .py files only)
- Use any MCP tools for saving
- Save to wrong directory

---

## CRITICAL REMINDERS

### DO NOT:
L Remove existing functions without BA approval
L Modify existing US comments
L Change existing function logic unless BA explicitly requires it
L Add blank lines inside functions
L Use print statements (use logger instead)
L Create docstrings (unless explicitly requested)
L Save as notebook (.ipynb) - save as Python (.py)

### MUST DO:
 Add `#### US: {user_story}` to ALL new functions
 Preserve all existing functions and their US comments
 Use `@synapse_error_print_handler` on all functions
 Use type hints: `def func(self, transform_sdf: DataFrame) -> DataFrame:`
 Use `_sdf` suffix for DataFrame variables
 Use `table_utilities.save_as_table()` for saving tables
 Use `logger` for logging (not print)
 Chain transformations in `transform()` method
 Follow ETL pattern: extract to transform to load
 **Use Australian English spelling for ALL function and variable names** (e.g., "normalise", "standardise", "analyse")

---

## EXAMPLE: Updating Existing File

**Scenario**: File exists with 3 functions, need to add 2 new transformations

**Existing functions** (preserve these):
```python
def extract(self) -> DataFrame:
    return spark.read.table(self.bronze_table_name)

def transform(self) -> DataFrame:
    transform_sdf = self.extract_sdf
    transform_sdf = self.old_logic(transform_sdf)  # Keep this
    return transform_sdf

def old_logic(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: 12345  # Keep this US reference
    return transform_sdf.withColumn("old_col", lit("value"))
```

**Add these NEW functions**:
```python
def new_validation(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    return transform_sdf.filter(col("key_field").isNotNull())

def new_enrichment(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    return transform_sdf.withColumn("enriched_col", upper(col("source_col")))
```

**Update transform() method**:
```python
def transform(self) -> DataFrame:
    transform_sdf = self.extract_sdf
    transform_sdf = self.old_logic(transform_sdf)  # Existing
    transform_sdf = self.new_validation(transform_sdf)  # NEW
    transform_sdf = self.new_enrichment(transform_sdf)  # NEW
    return transform_sdf
```

---

## OUTPUT REQUIREMENTS

### File Location
`python_files/{write_layer}/{write_layer}_{datasource}/{file_name}.py`

### Structure
1. Imports (all at top)
2. Environment detection
3. Class definition with ETL methods
4. Transformation functions (existing + new)
5. Class instantiation

### Quality Checklist
- [ ] All coding standards from CLAUDE.md followed
- [ ] BA documentation read and understood (Phase 2)
- [ ] Data dictionary files reviewed (Phase 4.1)
- [ ] DuckDB schemas verified (Phase 4.2)
- [ ] **Australian English spelling used for all function and variable names**
- [ ] Schema discrepancies addressed (Phase 4.3)
- [ ] All new functions have US:{user_story} comments
- [ ] All functions have @synapse_error_print_handler
- [ ] All functions have type hints
- [ ] Existing code preserved
- [ ] Transformations match BA specifications
- [ ] Business rules from data dictionary implemented
- [ ] NULL handling respects source system constraints
- [ ] Data quality rules implemented
- [ ] File saved to correct location

---

## EFFICIENCY NOTES
- Read BA documentation once, extract all requirements
- Read data dictionary files referenced in BA doc for business context
- Query DuckDB schemas once per table (not repeatedly)
- Cross-reference data dictionary, DuckDB schema, and BA specs
- Preserve existing code - only add/modify what's needed
- Use Edit tool for updates (not Write which replaces entire file)
- Follow existing code patterns in file
- Implement business rules and NULL handling from data dictionary

## DATA DICTIONARY INTEGRATION EXAMPLES

**Example 1: Understanding NULL Constraints**
```python
# BA doc references: .claude/data_dictionary/cms_case.md
# Data dictionary shows: allocation_area_id allows NULL (27% of records)
# Common value: 1 (inactive, should be treated as NULL)

@synapse_error_print_handler
def normalize_allocation_area(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Replace inactive allocation_area_id=1 with NULL per data dictionary
    return transform_sdf.withColumn("allocation_area_id", when(col("allocation_area_id") == 1, lit(None)).otherwise(col("allocation_area_id")))
```

**Example 2: Respecting Data Type Constraints**
```python
# BA doc references: .claude/data_dictionary/cms_case.md
# Data dictionary shows: description VARCHAR(200), but changed to VARCHAR(500)
# BA spec: Preserve existing truncation behavior

@synapse_error_print_handler
def validate_description_length(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Data dictionary: description changed from VARCHAR(200) to VARCHAR(500)
    # Apply length validation based on target schema
    return transform_sdf.withColumn("description", substring(col("description"), 1, 500))
```

**Example 3: Using Foreign Key Information**
```python
# BA doc references: .claude/data_dictionary/cms_case.md
# Data dictionary shows: status_id linked to "case_status" table

@synapse_error_print_handler
def enrich_with_status(self, transform_sdf: DataFrame) -> DataFrame:
    #### US: {user_story}
    # Data dictionary: status_id is foreign key to case_status table
    status_sdf = spark.read.table("silver_cms.s_cms_case_status")
    return transform_sdf.join(status_sdf, transform_sdf.status_id == status_sdf.id, "left")
```

---

## DEVELOPMENT EXAMPLE REFERENCE
**CRITICAL**: MUST review and follow the implementation pattern from `python_files/gold/g_ya_mg_occurence.py`

### PHASE 0: Study Reference Implementation (DO THIS FIRST!)
**Action**: IMMEDIATELY read `python_files/gold/g_ya_mg_occurence.py` to understand the approved implementation pattern

**Key Function to Study**: `get_incident_offence_report_linkage()` (lines 81-93)

**What to Learn from This Function**:
1. **Full Outer Join Pattern**: Creates linkage between CMS and FVMS systems
   - Joins `incident_to_or` with `cms_offence_report_df` using full_outer
   - Then joins with `incident_df` using full_outer
   - This ensures ALL records from both systems are captured

2. **Verification Logic**:
   - Filters `incident_to_or_df` by `_verified == 1` before joining
   - Demonstrates proper use of verification flags

3. **ID Matching**:
   - Links `or_number` from incident_to_or to `cms_offence_report_id`
   - Links `incident_id` from incident_to_or to `fvms_incident_id`
   - Returns comprehensive linkage table with all ID combinations

4. **Result Selection**:
   - Returns: `or_number`, `incident_id`, `cms_offence_report_id`, `fvms_incident_id`
   - Provides complete cross-reference between systems

**Implementation Requirements**:
 **MUST** use this exact pattern if your user story involves creating linkage between CMS and FVMS
 **MUST** use full outer joins to capture all records from both systems
 **MUST** include verification/filtering logic before joins where applicable
 **MUST** return comprehensive ID mappings for downstream use
 Study the entire file to understand the broader context of using linkage tables

**Example Implementation Pattern** (based on reference):
```python
@synapse_error_print_handler
def get_incident_offence_report_linkage(self) -> DataFrame:
    #### US: {user_story}
    logger.info("Starting incident-offence report linkage query")
    # Filter verified records first
    io_temp_df = self.incident_to_or_df.filter(
        self.incident_to_or_df["_verified"] == 1
    ).select(
        self.incident_to_or_df["or_number"],
        self.incident_to_or_df["incident_id"],
        self.incident_to_or_df["_verified"]
    )
    logger.info(f"Filtered verified records: {{io_temp_df.count()}} rows")

    # Select required columns from offence report
    offence_report_df = self.cms_offence_report_df.select(
        self.cms_offence_report_df["cms_offence_report_id"]
    )

    # Select required columns from incident
    incident_df = self.incident_df.select(
        self.incident_df["fvms_incident_id"]
    )

    # Full outer join to capture all records
    result_df = offence_report_df.join(
        io_temp_df,
        offence_report_df["cms_offence_report_id"] == io_temp_df["or_number"],
        "full_outer"
    )
    result_df = result_df.join(
        incident_df,
        result_df["incident_id"] == incident_df["fvms_incident_id"],
        "full_outer"
    )

    # Return comprehensive linkage
    result_df = result_df.select(
        io_temp_df["or_number"],
        io_temp_df["incident_id"],
        offence_report_df["cms_offence_report_id"],
        incident_df["fvms_incident_id"]
    )

    logger.success(f"Linkage query completed: {{result_df.count()}} rows")
    return result_df
```

**How This Pattern is Used** (see full file for context):
- The linkage result is stored as `self.offence_report_linkage_sdf`
- It's used in multiple extract methods to identify:
  - FIR occurrences WITHOUT CMS linkage (FVMS-only)
  - CMS occurrences WITHOUT FVMS linkage (CMS-only)
  - Linked occurrences (both CMS and FVMS)

**When to Apply This Pattern**:
 Creating cross-system linkage tables
 Implementing logic that needs to identify matched vs unmatched records
 Building occurrence or event tables that combine multiple data sources
 Any scenario requiring full visibility of records from both systems
"""
