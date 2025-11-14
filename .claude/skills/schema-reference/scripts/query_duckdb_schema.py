#!/usr/bin/env python3
"""Query DuckDB warehouse for table schema information."""
import argparse
import sys
from pathlib import Path
try:
    import duckdb
except ImportError:
    print("Error: duckdb package not installed. Install with: pip install duckdb")
    sys.exit(1)


def query_table_schema(db_path: str, database: str, table: str) -> dict:
    """Query DuckDB for table schema information.
    Args:
        db_path: Path to DuckDB database file
        database: Database name (e.g., 'bronze_cms', 'silver_cms', 'gold_data_model')
        table: Table name (e.g., 'b_cms_case', 's_cms_case', 'g_x_mg_statsclasscount')
    Returns:
        Dictionary containing schema information including columns, types, and constraints
    """
    conn = duckdb.connect(db_path, read_only=True)
    try:
        qualified_table = f"{database}.{table}"
        schema_query = f"DESCRIBE {qualified_table};"
        result = conn.execute(schema_query).fetchall()
        columns = []
        for row in result:
            columns.append({"name": row[0], "type": row[1], "null": row[2], "key": row[3] if len(row) > 3 else None, "default": row[4] if len(row) > 4 else None})
        count_query = f"SELECT COUNT(*) FROM {qualified_table};"
        row_count = conn.execute(count_query).fetchone()[0]
        return {"database": database, "table": table, "columns": columns, "row_count": row_count, "qualified_name": qualified_table}
    except Exception as e:
        return {"error": str(e), "database": database, "table": table}
    finally:
        conn.close()


def list_tables(db_path: str, database: str = None) -> list:
    """List all tables in DuckDB database.
    Args:
        db_path: Path to DuckDB database file
        database: Optional database name to filter results
    Returns:
        List of dictionaries with database and table information
    """
    conn = duckdb.connect(db_path, read_only=True)
    try:
        if database:
            query = f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = '{database}' ORDER BY table_name;"
        else:
            query = "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name;"
        result = conn.execute(query).fetchall()
        return [{"database": row[0], "table": row[1]} for row in result]
    finally:
        conn.close()


def format_schema_output(schema_info: dict) -> str:
    """Format schema information for display.
    Args:
        schema_info: Dictionary containing schema information
    Returns:
        Formatted string representation of schema
    """
    if "error" in schema_info:
        return f"Error querying {schema_info.get('database')}.{schema_info.get('table')}: {schema_info['error']}"
    output = []
    output.append(f"\n{'=' * 80}")
    output.append(f"Table: {schema_info['qualified_name']}")
    output.append(f"Row Count: {schema_info['row_count']:,}")
    output.append(f"{'=' * 80}")
    output.append(f"\n{'Column Name':<40} {'Data Type':<20} {'Nullable':<10}")
    output.append(f"{'-' * 40} {'-' * 20} {'-' * 10}")
    for col in schema_info['columns']:
        null_str = "YES" if col['null'] == "YES" else "NO"
        output.append(f"{col['name']:<40} {col['type']:<20} {null_str:<10}")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Query DuckDB warehouse for table schema information")
    parser.add_argument("--db-path", default="/workspaces/data/warehouse.duckdb", help="Path to DuckDB database file")
    parser.add_argument("--list", action="store_true", help="List all tables in database")
    parser.add_argument("--database", help="Database name (e.g., bronze_cms, silver_cms, gold_data_model)")
    parser.add_argument("--table", help="Table name (e.g., b_cms_case, s_cms_case)")
    args = parser.parse_args()
    if not Path(args.db_path).exists():
        print(f"Error: DuckDB database not found at {args.db_path}")
        print("Run 'make build_duckdb' to create the database")
        sys.exit(1)
    if args.list:
        tables = list_tables(args.db_path, args.database)
        if args.database:
            print(f"\nTables in database: {args.database}")
        else:
            print("\nAll tables in warehouse:")
        print(f"{'Database':<30} {'Table':<50}")
        print(f"{'-' * 30} {'-' * 50}")
        for t in tables:
            print(f"{t['database']:<30} {t['table']:<50}")
        print(f"\nTotal tables: {len(tables)}")
    elif args.database and args.table:
        schema_info = query_table_schema(args.db_path, args.database, args.table)
        print(format_schema_output(schema_info))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
