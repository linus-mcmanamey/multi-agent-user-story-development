# Example Task Files

This document provides example task files for both background and orchestration commands.

## Background Task File Example

Save to: `.claude/tasks/gold_validation_fixes.md`

```markdown
# Gold Layer Validation Fixes

**Date Created**: 2025-11-07
**Priority**: HIGH
**Estimated Total Time**: 35 minutes
**Files Affected**: 7
**Layer**: Gold

## Overview
Fix validation issues identified in code review across gold layer tables.
All fixes must include proper error handling and logging.

---

## Task 1: Add null validation for statsclasscount
**File**: python_files/gold/g_xa_mg_statsclasscount.py
**Line**: 67
**Estimated Time**: 5 minutes
**Severity**: HIGH

**Current Code**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    result = df.groupBy("class_code").count()
    return result
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    if df is None or df.isEmpty():
        logger.error("Extract DataFrame is None or empty in g_xa_mg_statsclasscount.transform()")
        raise ValueError("Cannot transform empty DataFrame")
    result = df.groupBy("class_code").count()
    logger.info(f"Transformed statsclasscount: {result.count()} rows")
    return result
\```

**Reason**: Missing null/empty validation can cause pipeline failures
**Testing**: Run with empty input DataFrame, should raise ValueError with proper logging

---

## Task 2: Add column existence validation
**File**: python_files/gold/g_x_mg_incident_summary.py
**Line**: 89
**Estimated Time**: 5 minutes
**Severity**: MEDIUM

**Current Code**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    return df.select("incident_id", "incident_date", "location")
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    required_columns = ["incident_id", "incident_date", "location"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns in g_x_mg_incident_summary: {missing_columns}")
        raise ValueError(f"Required columns missing: {missing_columns}")
    logger.info(f"Column validation passed for g_x_mg_incident_summary")
    return df.select(*required_columns)
\```

**Reason**: Schema changes can cause runtime errors without validation
**Testing**: Run with DataFrame missing "location" column, should raise ValueError

---

## Task 3: Add date range validation
**File**: python_files/gold/g_xa_time_series_analysis.py
**Line**: 123
**Estimated Time**: 7 minutes
**Severity**: MEDIUM

**Current Code**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    return df.filter(col("date") >= "2020-01-01")
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    min_date = df.agg(F.min("date")).collect()[0][0]
    max_date = df.agg(F.max("date")).collect()[0][0]
    if min_date is None or max_date is None:
        logger.warning("No date values found in g_xa_time_series_analysis")
        return df.filter(F.lit(False))  # Return empty DataFrame
    logger.info(f"Date range in g_xa_time_series_analysis: {min_date} to {max_date}")
    cutoff_date = "2020-01-01"
    result = df.filter(col("date") >= cutoff_date)
    logger.info(f"Filtered to {result.count()} rows >= {cutoff_date}")
    return result
\```

**Reason**: Better observability and handles missing date data
**Testing**: Run with DataFrame where all dates are null, should return empty DataFrame with warning

---

## Task 4: Add aggregation validation
**File**: python_files/gold/g_x_mg_monthly_stats.py
**Line**: 156
**Estimated Time**: 6 minutes
**Severity**: HIGH

**Current Code**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    monthly = df.groupBy("year_month").agg(
        F.count("*").alias("total_count"),
        F.avg("value").alias("avg_value")
    )
    return monthly
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    monthly = df.groupBy("year_month").agg(
        F.count("*").alias("total_count"),
        F.avg("value").alias("avg_value")
    )
    zero_count_months = monthly.filter(col("total_count") == 0).count()
    if zero_count_months > 0:
        logger.warning(f"Found {zero_count_months} months with zero records in g_x_mg_monthly_stats")
    null_avg_months = monthly.filter(col("avg_value").isNull()).count()
    if null_avg_months > 0:
        logger.warning(f"Found {null_avg_months} months with null averages in g_x_mg_monthly_stats")
    logger.info(f"Monthly aggregation complete: {monthly.count()} months")
    return monthly
\```

**Reason**: Detect data quality issues in aggregations
**Testing**: Run with data that produces zero counts, should log warnings

---

## Task 5: Add type conversion validation
**File**: python_files/gold/g_xa_mg_numeric_conversions.py
**Line**: 78
**Estimated Time**: 6 minutes
**Severity**: MEDIUM

**Current Code**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    return df.withColumn("amount", col("amount_str").cast("double"))
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    result = df.withColumn("amount", col("amount_str").cast("double"))
    null_conversions = result.filter(col("amount").isNull()).count()
    total_rows = result.count()
    if null_conversions > 0:
        null_percentage = (null_conversions / total_rows) * 100
        logger.warning(f"Type conversion failed for {null_conversions} rows ({null_percentage:.2f}%) in g_xa_mg_numeric_conversions")
        if null_percentage > 10:
            logger.error(f"More than 10% conversion failures in g_xa_mg_numeric_conversions")
    logger.info(f"Type conversion complete: {total_rows - null_conversions} successful conversions")
    return result
\```

**Reason**: Track conversion failures and alert on high failure rates
**Testing**: Run with invalid numeric strings, should log warning with percentage

---

## Task 6: Add join validation
**File**: python_files/gold/g_x_mg_incident_person.py
**Line**: 201
**Estimated Time**: 8 minutes
**Severity**: HIGH

**Current Code**:
\```python
def transform(self) -> DataFrame:
    incidents = spark.table("silver_fvms.s_fvms_incident")
    persons = spark.table("silver_fvms.s_fvms_person")
    joined = incidents.join(persons, "person_id", "inner")
    return joined
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    incidents = spark.table("silver_fvms.s_fvms_incident")
    persons = spark.table("silver_fvms.s_fvms_person")
    incidents_count = incidents.count()
    persons_count = persons.count()
    logger.info(f"Joining {incidents_count} incidents with {persons_count} persons")
    joined = incidents.join(persons, "person_id", "inner")
    joined_count = joined.count()
    join_ratio = (joined_count / incidents_count) * 100 if incidents_count > 0 else 0
    logger.info(f"Join complete: {joined_count} rows ({join_ratio:.2f}% of incidents matched)")
    if join_ratio < 80:
        logger.warning(f"Low join ratio ({join_ratio:.2f}%) in g_x_mg_incident_person - possible data quality issue")
    return joined
\```

**Reason**: Monitor join quality and detect missing reference data
**Testing**: Run with persons table missing most person_ids, should log warning

---

## Task 7: Add deduplication validation
**File**: python_files/gold/g_xa_unique_records.py
**Line**: 134
**Estimated Time**: 5 minutes
**Severity**: MEDIUM

**Current Code**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    return df.dropDuplicates(["record_id"])
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    original_count = df.count()
    deduplicated = df.dropDuplicates(["record_id"])
    final_count = deduplicated.count()
    duplicates_removed = original_count - final_count
    if duplicates_removed > 0:
        duplicate_percentage = (duplicates_removed / original_count) * 100
        logger.warning(f"Removed {duplicates_removed} duplicates ({duplicate_percentage:.2f}%) in g_xa_unique_records")
    logger.info(f"Deduplication complete: {final_count} unique records (removed {duplicates_removed})")
    return deduplicated
\```

**Reason**: Track duplicate rates to identify data quality issues
**Testing**: Run with DataFrame containing duplicates, should log count and percentage

---

## Quality Gates

After completing all tasks, run:
```bash
# Syntax validation
python3 -m py_compile python_files/gold/g_xa_mg_statsclasscount.py
python3 -m py_compile python_files/gold/g_x_mg_incident_summary.py
python3 -m py_compile python_files/gold/g_xa_time_series_analysis.py
python3 -m py_compile python_files/gold/g_x_mg_monthly_stats.py
python3 -m py_compile python_files/gold/g_xa_mg_numeric_conversions.py
python3 -m py_compile python_files/gold/g_x_mg_incident_person.py
python3 -m py_compile python_files/gold/g_xa_unique_records.py

# Linting
ruff check python_files/gold/

# Formatting
ruff format python_files/gold/
```

## Expected Final Report

Agent should provide:
1. Summary of all 7 validation fixes applied
2. List of files modified with line numbers
3. Quality gate results (all passing)
4. Testing recommendations for each fix
5. Any issues encountered during implementation
6. Recommendations for additional validation improvements

## Usage

```bash
/background gold_validation_fixes.md
```
```

---

## Orchestration Task File Example

Save to: `.claude/tasks/silver_layer_optimization.md`

```markdown
# Silver Layer Performance Optimization

**Date Created**: 2025-11-07
**Priority**: HIGH
**Estimated Total Time**: 75 minutes
**Complexity**: High
**Recommended Worker Agents**: 6

## Main Objective

Improve performance of all silver layer ETL transformations by analyzing bottlenecks, optimizing queries, and implementing caching strategies.

## Success Criteria

- [ ] All silver tables profiled for performance
- [ ] Bottlenecks identified in each database
- [ ] Query optimizations implemented
- [ ] Caching strategies applied where beneficial
- [ ] Performance improvements validated (>20% faster)
- [ ] All quality gates passed

---

## Suggested Subtask Decomposition

### Subtask 1: Profile silver_cms performance
**Scope**: All tables in python_files/silver/silver_cms/
**Estimated Time**: 12 minutes
**Dependencies**: None
**Agent**: agent_1

**Description**:
Analyze performance of all CMS silver tables:
- Measure transformation execution time
- Identify slow joins and aggregations
- Check for inefficient column operations
- Analyze DataFrame lineage complexity

**Expected Outputs**:
- Performance profile for each table (JSON format)
- List of bottlenecks with severity ranking
- Recommended optimizations
- Baseline execution times

**JSON Response Fields**:
```json
{
  "tables_analyzed": ["s_cms_case", "s_cms_person", ...],
  "slow_operations": [
    {"table": "s_cms_case", "operation": "join", "time_ms": 5000},
    ...
  ],
  "recommendations": ["Add broadcast hint to person join", ...]
}
```

---

### Subtask 2: Profile silver_fvms performance
**Scope**: All tables in python_files/silver/silver_fvms/
**Estimated Time**: 12 minutes
**Dependencies**: None
**Agent**: agent_2

**Description**:
Analyze performance of all FVMS silver tables:
- Measure transformation execution time
- Identify slow joins and aggregations
- Check for inefficient column operations
- Analyze DataFrame lineage complexity

**Expected Outputs**:
- Performance profile for each table (JSON format)
- List of bottlenecks with severity ranking
- Recommended optimizations
- Baseline execution times

**JSON Response Fields**:
```json
{
  "tables_analyzed": ["s_fvms_incident", "s_fvms_person", ...],
  "slow_operations": [...],
  "recommendations": [...]
}
```

---

### Subtask 3: Profile silver_nicherms performance
**Scope**: All tables in python_files/silver/silver_nicherms/
**Estimated Time**: 12 minutes
**Dependencies**: None
**Agent**: agent_3

**Description**:
Analyze performance of all NicheRMS silver tables:
- Measure transformation execution time
- Identify slow joins and aggregations
- Check for inefficient column operations
- Analyze DataFrame lineage complexity

**Expected Outputs**:
- Performance profile for each table (JSON format)
- List of bottlenecks with severity ranking
- Recommended optimizations
- Baseline execution times

**JSON Response Fields**:
```json
{
  "tables_analyzed": ["s_nicherms_tbl_case", ...],
  "slow_operations": [...],
  "recommendations": [...]
}
```

---

### Subtask 4: Optimize silver_cms tables
**Scope**: Implement optimizations for silver_cms
**Estimated Time**: 15 minutes
**Dependencies**: Subtask 1 analysis results
**Agent**: agent_4

**Description**:
Based on agent_1 analysis, implement optimizations:
- Add broadcast hints for small dimension tables
- Optimize join orders
- Cache frequently reused DataFrames
- Add partition pruning hints
- Replace expensive operations with efficient alternatives

**Expected Outputs**:
- Modified files with optimizations
- Performance improvement metrics
- Quality gate validation results

**Optimizations to Apply**:
- Broadcast joins for reference data (<10MB)
- Filter pushdown optimization
- Column pruning (select only needed columns)
- Cache intermediate results used multiple times

---

### Subtask 5: Optimize silver_fvms tables
**Scope**: Implement optimizations for silver_fvms
**Estimated Time**: 15 minutes
**Dependencies**: Subtask 2 analysis results
**Agent**: agent_5

**Description**:
Based on agent_2 analysis, implement optimizations:
- Add broadcast hints for small dimension tables
- Optimize join orders
- Cache frequently reused DataFrames
- Add partition pruning hints
- Replace expensive operations with efficient alternatives

**Expected Outputs**:
- Modified files with optimizations
- Performance improvement metrics
- Quality gate validation results

---

### Subtask 6: Optimize silver_nicherms tables
**Scope**: Implement optimizations for silver_nicherms
**Estimated Time**: 15 minutes
**Dependencies**: Subtask 3 analysis results
**Agent**: agent_6

**Description**:
Based on agent_3 analysis, implement optimizations:
- Add broadcast hints for small dimension tables
- Optimize join orders
- Cache frequently reused DataFrames
- Add partition pruning hints
- Replace expensive operations with efficient alternatives

**Expected Outputs**:
- Modified files with optimizations
- Performance improvement metrics
- Quality gate validation results

---

## Quality Requirements

All agents must:
1. Run syntax validation: `python3 -m py_compile <modified_files>`
2. Run linting: `ruff check python_files/silver/`
3. Run formatting: `ruff format python_files/silver/`
4. Include quality gate results in JSON response

## Aggregation Requirements

Orchestrator must:
1. Collect JSON responses from all 6 agents
2. Aggregate performance metrics across all databases
3. Calculate total performance improvement percentage
4. Consolidate all recommendations
5. Validate all quality checks passed
6. Produce comprehensive optimization report

## Consolidated Report Format

```json
{
  "orchestration_summary": {
    "main_task": "Silver layer performance optimization",
    "total_agents_launched": 6,
    "successful_agents": 6,
    "failed_agents": 0,
    "total_execution_time_seconds": 4500
  },
  "performance_analysis": {
    "total_tables_analyzed": 58,
    "bottlenecks_identified": 23,
    "optimizations_applied": 35
  },
  "performance_improvements": {
    "silver_cms_improvement_pct": 28.5,
    "silver_fvms_improvement_pct": 31.2,
    "silver_nicherms_improvement_pct": 25.8,
    "overall_improvement_pct": 28.5
  },
  "consolidated_metrics": {
    "total_files_modified": 35,
    "broadcast_joins_added": 12,
    "caching_strategies_applied": 8,
    "query_reorderings": 15
  },
  "quality_validation": {
    "all_syntax_checks_passed": true,
    "all_linting_passed": true,
    "all_formatting_passed": true
  },
  "next_steps": [
    "Run silver layer pipeline: make run_silver",
    "Validate output data quality",
    "Monitor performance in production",
    "Document optimization patterns for future use"
  ]
}
```

## Execution Pattern

**Pattern**: Analyze-then-Fix (Hybrid Sequential-Parallel)

```
Phase 1: Analysis (Parallel)
├─→ Agent 1: Profile silver_cms
├─→ Agent 2: Profile silver_fvms
└─→ Agent 3: Profile silver_nicherms

Wait for Phase 1 completion

Phase 2: Optimization (Parallel)
├─→ Agent 4: Optimize silver_cms (uses Agent 1 results)
├─→ Agent 5: Optimize silver_fvms (uses Agent 2 results)
└─→ Agent 6: Optimize silver_nicherms (uses Agent 3 results)
```

## Usage

```bash
/orchestrate silver_layer_optimization.md
```

## Expected Timeline

- Phase 1 (Analysis): 12 minutes (parallel)
- Phase 2 (Optimization): 15 minutes (parallel)
- Orchestrator aggregation: 3 minutes
- **Total**: ~30 minutes (vs 75 minutes sequential)
```

---

## Additional Example: Simple Background Task

Save to: `.claude/tasks/fix_single_table.md`

```markdown
# Fix g_xa_mg_statsclasscount Table

**Date Created**: 2025-11-07
**Priority**: MEDIUM
**Estimated Total Time**: 15 minutes
**Files Affected**: 1
**Layer**: Gold

## Overview
Fix validation and performance issues in the statsclasscount gold table.

---

## Task 1: Add input validation
**File**: python_files/gold/g_xa_mg_statsclasscount.py
**Line**: 45
**Estimated Time**: 5 minutes
**Severity**: HIGH

**Current Code**:
\```python
def extract(self) -> DataFrame:
    return spark.table("silver_fvms.s_fvms_incident")
\```

**Required Fix**:
\```python
def extract(self) -> DataFrame:
    df = spark.table("silver_fvms.s_fvms_incident")
    if df.isEmpty():
        logger.warning("No data in silver_fvms.s_fvms_incident for g_xa_mg_statsclasscount")
    logger.info(f"Extracted {df.count()} rows from silver_fvms.s_fvms_incident")
    return df
\```

**Reason**: Better observability and empty data handling
**Testing**: Check logs show row count

---

## Task 2: Optimize aggregation
**File**: python_files/gold/g_xa_mg_statsclasscount.py
**Line**: 67
**Estimated Time**: 7 minutes
**Severity**: MEDIUM

**Current Code**:
\```python
def transform(self) -> DataFrame:
    return self.extract_sdf.groupBy("stats_class_code").count()
\```

**Required Fix**:
\```python
def transform(self) -> DataFrame:
    df = self.extract_sdf
    # Filter out nulls before aggregation for better performance
    filtered = df.filter(col("stats_class_code").isNotNull())
    result = filtered.groupBy("stats_class_code").count()
    logger.info(f"Aggregated to {result.count()} unique stats class codes")
    return result
\```

**Reason**: Performance optimization and null handling
**Testing**: Verify nulls are excluded, check performance improvement

---

## Task 3: Add load validation
**File**: python_files/gold/g_xa_mg_statsclasscount.py
**Line**: 89
**Estimated Time**: 3 minutes
**Severity**: LOW

**Current Code**:
\```python
def load(self) -> None:
    TableUtilities.save_as_table(self.transform_sdf, "gold_data_model", "g_xa_mg_statsclasscount")
\```

**Required Fix**:
\```python
def load(self) -> None:
    row_count = self.transform_sdf.count()
    if row_count == 0:
        logger.error("Transform produced zero rows for g_xa_mg_statsclasscount - check source data")
    TableUtilities.save_as_table(self.transform_sdf, "gold_data_model", "g_xa_mg_statsclasscount")
    logger.success(f"Saved {row_count} rows to gold_data_model.g_xa_mg_statsclasscount")
\```

**Reason**: Validate output before saving
**Testing**: Verify error logged if transform produces empty DataFrame

---

## Quality Gates

```bash
python3 -m py_compile python_files/gold/g_xa_mg_statsclasscount.py
ruff check python_files/gold/g_xa_mg_statsclasscount.py
ruff format python_files/gold/g_xa_mg_statsclasscount.py
```

## Usage

```bash
/background fix_single_table.md
```
```

---

**Created**: 2025-11-07
**Related**: multi-agent-orchestration.md, README.md, PATTERNS.md
