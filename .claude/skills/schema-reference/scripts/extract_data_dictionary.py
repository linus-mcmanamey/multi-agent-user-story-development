#!/usr/bin/env python3
"""Extract schema and business logic from data dictionary markdown files."""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def find_data_dictionary_file(table_name: str, data_dict_paths: List[str]) -> Optional[Path]:
    """Find data dictionary file for a given table name.
    Args:
        table_name: Table name (can include layer prefix like b_, s_, or without)
        data_dict_paths: List of paths to search for data dictionary files
    Returns:
        Path to data dictionary file if found, None otherwise
    """
    clean_name = table_name.replace("b_", "").replace("s_", "").replace("g_", "")
    for base_path in data_dict_paths:
        dict_path = Path(base_path)
        if not dict_path.exists():
            continue
        dict_file = dict_path / f"{clean_name}.md"
        if dict_file.exists():
            return dict_file
    return None


def parse_data_dictionary(file_path: Path) -> Dict:
    """Parse data dictionary markdown file to extract schema and business logic.
    Args:
        file_path: Path to data dictionary markdown file
    Returns:
        Dictionary containing parsed information
    """
    content = file_path.read_text()
    parsed = {"file": file_path.name, "table_name": file_path.stem, "source": None, "page": None, "columns": [], "primary_key": None, "foreign_keys": [], "business_logic": []}
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("**Source**:"):
            parsed["source"] = line.split(":", 1)[1].strip()
        elif line.startswith("**Page**:"):
            parsed["page"] = line.split(":", 1)[1].strip()
        elif "| Column name |" in line and i + 2 < len(lines):
            column_start = i + 2
            for j in range(column_start, len(lines)):
                if not lines[j].strip() or not lines[j].startswith("|"):
                    break
                parts = [p.strip() for p in lines[j].split("|") if p.strip()]
                if len(parts) >= 4:
                    col_name = parts[0]
                    description = parts[1]
                    data_type = parts[2]
                    allow_nulls = parts[3]
                    parsed["columns"].append({"name": col_name, "description": description, "data_type": data_type, "allow_nulls": allow_nulls})
                    if "linked to" in description.lower() or "link to" in description.lower():
                        parsed["business_logic"].append(f"{col_name}: {description}")
                    if "common values" in description.lower() or "default" in description.lower():
                        parsed["business_logic"].append(f"{col_name}: {description}")
        elif line.startswith("### Primary Key"):
            if i + 1 < len(lines):
                pk_line = lines[i + 1]
                parsed["primary_key"] = pk_line.strip().lstrip("- ").lstrip("**").rstrip("**")
        elif line.startswith("### Foreign Keys") or line.startswith("### Composite Primary Key"):
            fk_start = i + 1
            for j in range(fk_start, len(lines)):
                if not lines[j].strip() or lines[j].startswith("#"):
                    break
                if lines[j].strip().startswith("-"):
                    fk_info = lines[j].strip().lstrip("- ")
                    parsed["foreign_keys"].append(fk_info)
    return parsed


def format_data_dictionary_output(parsed: Dict, include_business_logic: bool = True) -> str:
    """Format parsed data dictionary information for display.
    Args:
        parsed: Parsed data dictionary dictionary
        include_business_logic: Whether to include business logic section
    Returns:
        Formatted string representation
    """
    output = []
    output.append(f"\n{'=' * 80}")
    output.append(f"Data Dictionary: {parsed['table_name']}")
    if parsed['source']:
        output.append(f"Source: {parsed['source']} (Page {parsed['page']})")
    output.append(f"{'=' * 80}")
    if parsed['primary_key']:
        output.append(f"\nPrimary Key: {parsed['primary_key']}")
    if parsed['foreign_keys']:
        output.append(f"\nForeign Keys:")
        for fk in parsed['foreign_keys']:
            output.append(f"  - {fk}")
    output.append(f"\nColumns ({len(parsed['columns'])}):")
    output.append(f"{'Column Name':<40} {'Data Type':<20} {'Nullable':<10}")
    output.append(f"{'-' * 40} {'-' * 20} {'-' * 10}")
    for col in parsed['columns']:
        output.append(f"{col['name']:<40} {col['data_type']:<20} {col['allow_nulls']:<10}")
    if include_business_logic and parsed['business_logic']:
        output.append(f"\n{'Business Logic & Constraints:'}")
        output.append(f"{'-' * 80}")
        for logic in parsed['business_logic']:
            wrapped = logic.replace("\n", " ")
            if len(wrapped) > 76:
                output.append(f"  {wrapped[:76]}...")
            else:
                output.append(f"  {wrapped}")
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Extract schema and business logic from data dictionary files")
    parser.add_argument("table", help="Table name (with or without layer prefix)")
    parser.add_argument("--data-dict-paths", nargs="+", default=[os.path.join(os.getcwd(), ".claude/data_dictionary"), "/home/vscode/.claude/data_dictionary"], help="Paths to data dictionary directories")
    parser.add_argument("--no-business-logic", action="store_true", help="Exclude business logic section")
    args = parser.parse_args()
    dict_file = find_data_dictionary_file(args.table, args.data_dict_paths)
    if not dict_file:
        print(f"Error: Data dictionary file not found for table '{args.table}'")
        print(f"Searched in: {', '.join(args.data_dict_paths)}")
        sys.exit(1)
    parsed = parse_data_dictionary(dict_file)
    print(format_data_dictionary_output(parsed, include_business_logic=not args.no_business_logic))


if __name__ == "__main__":
    main()
