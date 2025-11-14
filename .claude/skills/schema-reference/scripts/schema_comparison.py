#!/usr/bin/env python3
"""Compare schemas across medallion architecture layers."""
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set
try:
    import duckdb
except ImportError:
    print("Error: duckdb package not installed. Install with: pip install duckdb")
    sys.exit(1)


def get_table_columns(db_path: str, database: str, table: str) -> Set[str]:
    """Get set of column names from a table.
    Args:
        db_path: Path to DuckDB database file
        database: Database name
        table: Table name
    Returns:
        Set of column names
    """
    conn = duckdb.connect(db_path, read_only=True)
    try:
        qualified_table = f"{database}.{table}"
        schema_query = f"DESCRIBE {qualified_table};"
        result = conn.execute(schema_query).fetchall()
        return {row[0] for row in result}
    except Exception:
        return set()
    finally:
        conn.close()


def compare_schemas(db_path: str, source_db: str, source_table: str, target_db: str, target_table: str) -> Dict:
    """Compare schemas between source and target tables.
    Args:
        db_path: Path to DuckDB database file
        source_db: Source database name
        source_table: Source table name
        target_db: Target database name
        target_table: Target table name
    Returns:
        Dictionary containing comparison results
    """
    source_cols = get_table_columns(db_path, source_db, source_table)
    target_cols = get_table_columns(db_path, target_db, target_table)
    if not source_cols:
        return {"error": f"Source table {source_db}.{source_table} not found"}
    if not target_cols:
        return {"error": f"Target table {target_db}.{target_table} not found"}
    return {"source": f"{source_db}.{source_table}", "target": f"{target_db}.{target_table}", "source_columns": sorted(source_cols), "target_columns": sorted(target_cols), "common_columns": sorted(source_cols & target_cols), "source_only": sorted(source_cols - target_cols), "target_only": sorted(target_cols - source_cols), "column_mapping": infer_column_mapping(source_cols, target_cols)}


def infer_column_mapping(source_cols: Set[str], target_cols: Set[str]) -> List[Dict]:
    """Infer potential column mappings between layers based on naming conventions.
    Args:
        source_cols: Set of source column names
        target_cols: Set of target column names
    Returns:
        List of potential column mappings
    """
    mappings = []
    for source_col in sorted(source_cols):
        clean_source = source_col.replace("b_", "").replace("s_", "").replace("g_", "")
        for target_col in sorted(target_cols):
            clean_target = target_col.replace("b_", "").replace("s_", "").replace("g_", "")
            if clean_source == clean_target and source_col != target_col:
                mappings.append({"source": source_col, "target": target_col, "type": "renamed"})
            elif source_col in clean_target or clean_target in source_col:
                mappings.append({"source": source_col, "target": target_col, "type": "possible_match"})
    return mappings


def format_comparison_output(comparison: Dict) -> str:
    """Format comparison results for display.
    Args:
        comparison: Comparison results dictionary
    Returns:
        Formatted string representation
    """
    if "error" in comparison:
        return f"Error: {comparison['error']}"
    output = []
    output.append(f"\n{'=' * 80}")
    output.append(f"Schema Comparison")
    output.append(f"Source: {comparison['source']}")
    output.append(f"Target: {comparison['target']}")
    output.append(f"{'=' * 80}")
    output.append(f"\nCommon Columns ({len(comparison['common_columns'])}):")
    for col in comparison['common_columns']:
        output.append(f"  ✓ {col}")
    if comparison['source_only']:
        output.append(f"\nColumns Only in Source ({len(comparison['source_only'])}):")
        for col in comparison['source_only']:
            output.append(f"  - {col}")
    if comparison['target_only']:
        output.append(f"\nColumns Only in Target ({len(comparison['target_only'])}):")
        for col in comparison['target_only']:
            output.append(f"  + {col}")
    if comparison['column_mapping']:
        output.append(f"\nInferred Column Mappings:")
        for mapping in comparison['column_mapping']:
            if mapping['type'] == "renamed":
                output.append(f"  {mapping['source']} → {mapping['target']} (renamed)")
            else:
                output.append(f"  {mapping['source']} ≈ {mapping['target']} (possible match)")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Compare schemas across medallion architecture layers")
    parser.add_argument("--db-path", default="/workspaces/data/warehouse.duckdb", help="Path to DuckDB database file")
    parser.add_argument("--source-db", required=True, help="Source database (e.g., bronze_cms)")
    parser.add_argument("--source-table", required=True, help="Source table (e.g., b_cms_case)")
    parser.add_argument("--target-db", required=True, help="Target database (e.g., silver_cms)")
    parser.add_argument("--target-table", required=True, help="Target table (e.g., s_cms_case)")
    args = parser.parse_args()
    if not Path(args.db_path).exists():
        print(f"Error: DuckDB database not found at {args.db_path}")
        print("Run 'make build_duckdb' to create the database")
        sys.exit(1)
    comparison = compare_schemas(args.db_path, args.source_db, args.source_table, args.target_db, args.target_table)
    print(format_comparison_output(comparison))


if __name__ == "__main__":
    main()
