# Business Logic Patterns

This document describes common business logic patterns found in the medallion architecture transformations, with a focus on how to extract and implement business rules from data dictionaries.

## Extracting Business Logic from Data Dictionaries

Data dictionary files (`.claude/data_dictionary/{table}.md`) contain critical business logic in column descriptions. Look for these patterns:

### 1. Relationship Indicators

**Pattern**: "linked to", "link to", "references"

**Example**:
```
allocation_area_id | Optional allocation area, linked to "work_group"
```

**Implementation**:
```python
# Join with related table
case_df = case_df.join(
    work_group_df,
    case_df.allocation_area_id == work_group_df.s_cms_work_group_id,
    "left"  # Left join because it's optional
)
```

### 2. Default Values and Common Patterns

**Pattern**: "default is", "by default", "common values are"

**Example**:
```
status_id | Case status (by default, "Active") linked to "case_status". Cases can only be "Active" or "Non Active".
```

**Implementation**:
```python
# Handle default values
case_df = case_df.withColumn(
    "status_id",
    F.when(F.col("status_id").isNull(), F.lit(1))  # 1 = Active (default)
     .otherwise(F.col("status_id"))
)
```

### 3. Data Quality Rules

**Pattern**: "should be treated as NULL", "inactive", "valid values"

**Example**:
```
allocation_area_id | Common values are NULL (27%), 63 "Launceston CIB" (25%), 1 (inactive default work group, should be treated as NULL; around 4%).
```

**Implementation**:
```python
# Apply data quality rules
case_df = case_df.withColumn(
    "allocation_area_id",
    F.when(F.col("allocation_area_id") == 1, F.lit(None))  # Treat 1 as NULL
     .otherwise(F.col("allocation_area_id"))
)
```

### 4. Data Type Constraints

**Pattern**: "Data type changed from", "else data is truncated"

**Example**:
```
description | Optional free-text description. Data type changed from VARCHAR(200) to VARCHAR(500), else data is truncated.
```

**Implementation**:
```python
# Ensure proper data type and length
case_df = case_df.withColumn(
    "description",
    F.substring(F.col("description"), 1, 500)  # Truncate to 500 chars
)
```

### 5. Nullable Constraints

**Pattern**: "Allow NULLs" column in data dictionary

**Implementation**:
```python
# For required fields (Allow NULLs = N), filter out nulls or apply defaults
case_df = case_df.filter(F.col("cms_case_id").isNotNull())

# For optional fields (Allow NULLs = Y), preserve nulls or apply null replacement
case_df = case_df.withColumn(
    "description",
    F.coalesce(F.col("description"), F.lit("NOT RECORDED"))
)
```

## Common Transformation Patterns

### Pattern 1: Choice List Mapping

**When**: Column values are enumeration codes that need descriptive text

**Example**:
```python
# Map status_id to status description
case_df = case_df.join(
    choice_list_df.filter(F.col("list_name") == "case_status"),
    case_df.status_id == choice_list_df.code_value,
    "left"
).withColumn(
    "status_description",
    F.coalesce(F.col("code_description"), F.lit("Unknown"))
)
```

### Pattern 2: Primary Key Transformation

**When**: Moving from bronze to silver

**Example**:
```python
# Rename primary key with layer prefix
silver_df = bronze_df.withColumnRenamed(
    "cms_case_id",
    "s_cms_case_id"
)
```

### Pattern 3: Timestamp Standardization

**When**: Working with date/time columns

**Example**:
```python
# Use TableUtilities for intelligent timestamp conversion
silver_df = TableUtilities.clean_date_time_columns(bronze_df)
```

### Pattern 4: Deduplication

**When**: Source data may contain duplicates

**Example**:
```python
# Simple deduplication on primary key
deduplicated_df = TableUtilities.drop_duplicates_simple(
    df=silver_df,
    primary_key="s_cms_case_id"
)

# Advanced deduplication with timestamp ordering
deduplicated_df = TableUtilities.drop_duplicates_advanced(
    df=silver_df,
    partition_columns=["s_cms_case_id"],
    order_column="last_updated",
    ascending=False  # Keep most recent
)
```

### Pattern 5: Cross-Source Joins

**When**: Creating gold layer tables that combine data from multiple sources

**Example**:
```python
# Join CMS and FVMS data on common identifiers
cms_df = spark.table("silver_cms.s_cms_case")
fvms_df = spark.table("silver_fvms.s_fvms_incident")

joined_df = cms_df.join(
    fvms_df,
    cms_df.incident_link_id == fvms_df.s_fvms_incident_id,
    "inner"
)
```

### Pattern 6: Conditional Logic

**When**: Applying business rules based on column values

**Example**:
```python
# Categorize cases by age
case_df = case_df.withColumn(
    "case_age_category",
    F.when(F.datediff(F.current_date(), F.col("date_created")) < 30, "Recent")
     .when(F.datediff(F.current_date(), F.col("date_created")) < 90, "Medium")
     .otherwise("Old")
)
```

### Pattern 7: Aggregation with Business Logic

**When**: Creating summary tables in gold layer

**Example**:
```python
# Count active cases by allocation area
summary_df = case_df.filter(F.col("status") == "Active").groupBy(
    "allocation_area_id"
).agg(
    F.count("*").alias("active_case_count"),
    F.countDistinct("primary_investigating_officer_id").alias("unique_officers"),
    F.min("date_created").alias("oldest_case_date"),
    F.max("last_updated").alias("most_recent_update")
)
```

## ETL Class Pattern Implementation

All silver and gold transformations follow the standard ETL class pattern with business logic embedded in each method:

```python
class TableName:
    def __init__(self, bronze_table_name: str):
        self.bronze_table_name = bronze_table_name
        # Automatically derive database and table names
        self.silver_database_name = f"silver_{self.bronze_table_name.split('.')[0].split('_')[-1]}"
        self.silver_table_name = self.bronze_table_name.split(".")[-1].replace("b_", "s_")
        # Execute ETL pipeline
        self.extract_sdf = self.extract()
        self.transform_sdf = self.transform()
        self.load()

    @synapse_error_print_handler
    def extract(self):
        """Extract data from bronze layer."""
        logger.info(f"Extracting {self.bronze_table_name}")
        return spark.table(self.bronze_table_name)

    @synapse_error_print_handler
    def transform(self):
        """Apply business logic and transformations."""
        logger.info(f"Transforming {self.silver_table_name}")
        sdf = self.extract_sdf
        # 1. Rename primary key
        sdf = sdf.withColumnRenamed("cms_case_id", "s_cms_case_id")
        # 2. Apply data quality rules (from data dictionary)
        sdf = sdf.withColumn(
            "allocation_area_id",
            F.when(F.col("allocation_area_id") == 1, F.lit(None))
             .otherwise(F.col("allocation_area_id"))
        )
        # 3. Standardize timestamps
        sdf = TableUtilities.clean_date_time_columns(sdf)
        # 4. Deduplicate
        sdf = TableUtilities.drop_duplicates_advanced(
            sdf,
            partition_columns=["s_cms_case_id"],
            order_column="last_updated",
            ascending=False
        )
        # 5. Add row hash for change detection
        sdf = TableUtilities.add_row_hash(sdf)
        return sdf

    @synapse_error_print_handler
    def load(self):
        """Save transformed data to silver layer."""
        logger.info(f"Loading {self.silver_database_name}.{self.silver_table_name}")
        TableUtilities.save_as_table(
            sdf=self.transform_sdf,
            table_name=self.silver_table_name,
            database_name=self.silver_database_name
        )
        logger.success(f"Successfully loaded {self.silver_database_name}.{self.silver_table_name}")
```

## Workflow for Implementing Business Logic

When creating a new transformation, follow this workflow:

1. **Read Data Dictionary**: Use `extract_data_dictionary.py` to view schema and business logic
   ```bash
   python scripts/extract_data_dictionary.py cms_case
   ```

2. **Query Source Schema**: Use `query_duckdb_schema.py` to see actual column names and types
   ```bash
   python scripts/query_duckdb_schema.py --database bronze_cms --table b_cms_case
   ```

3. **Compare Schemas**: Use `schema_comparison.py` to identify transformations needed
   ```bash
   python scripts/schema_comparison.py \
     --source-db bronze_cms --source-table b_cms_case \
     --target-db silver_cms --target-table s_cms_case
   ```

4. **Extract Business Logic**: Review data dictionary for:
   - Foreign key relationships
   - Default values and common patterns
   - Data quality rules
   - Data type constraints
   - Nullable constraints

5. **Implement Transformation**: Write PySpark code following the ETL class pattern

6. **Validate**: Test transformation with sample data and verify business logic is applied correctly

## Logging Best Practices

Use `NotebookLogger` for all logging (not print statements):

```python
logger = NotebookLogger()

# Info for normal operations
logger.info(f"Processing {table_name} with {df.count()} records")

# Success for completed operations
logger.success(f"Successfully loaded {database}.{table}")

# Error for failures
logger.error(f"Failed to load {table}: {str(error)}")

# Always include table/database names in log messages
logger.info(f"Joining {source_table} with {target_table}")
```

## Error Handling

Always use the `@synapse_error_print_handler` decorator for error handling:

```python
@synapse_error_print_handler
def transform(self):
    # Transformation code here
    # Errors will be caught and logged automatically
    pass
```

## Testing Business Logic

Before deploying transformations, test business logic:

1. **Unit Tests**: Test individual business rules
2. **Integration Tests**: Test full ETL pipeline
3. **Data Validation**: Verify business logic produces expected results
4. **Schema Validation**: Confirm output schema matches expectations

Example test:
```python
def test_inactive_allocation_area_treated_as_null():
    # Test that allocation_area_id = 1 is treated as NULL
    input_data = [(1, 1), (2, 63)]
    input_df = spark.createDataFrame(input_data, ["case_id", "allocation_area_id"])
    result_df = apply_data_quality_rules(input_df)
    assert result_df.filter(F.col("case_id") == 1).select("allocation_area_id").first()[0] is None
```
