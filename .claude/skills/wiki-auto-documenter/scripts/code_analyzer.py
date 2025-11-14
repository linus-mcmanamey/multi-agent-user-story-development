"""
Python Code Analyzer using AST (Abstract Syntax Tree)

Analyzes Python source files to extract:
- Classes and their methods
- Standalone functions
- Import statements (external and internal)
- Decorators
- ETL pattern detection (Extract/Transform/Load methods)
- Documentation strings

Usage:
    from code_analyzer import analyze_file, generate_markdown

    analysis = analyze_file("path/to/file.py")
    markdown_doc = generate_markdown(analysis, repo_url="https://...")

API:
    analyze_file(file_path) -> dict
    generate_markdown(analysis, repo_url, branch) -> str
"""

import ast
import os
import sys
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

class CodeAnalyzer:
    """Analyzes Python code using AST"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            tree = ast.parse(source_code, filename=str(file_path))
            relative_path = file_path.relative_to(self.repo_root) if file_path.is_relative_to(self.repo_root) else file_path
            analysis = {"file_path": str(relative_path), "absolute_path": str(file_path), "file_name": file_path.name, "module_name": file_path.stem, "line_count": source_code.count("\n") + 1, "classes": self._extract_classes(tree), "functions": self._extract_functions(tree), "imports": self._extract_imports(tree), "has_etl_pattern": False, "decorators": self._extract_decorators(tree), "module_docstring": ast.get_docstring(tree), "analysis_timestamp": datetime.now().isoformat()}
            analysis["has_etl_pattern"] = self._detect_etl_pattern(analysis["classes"])
            analysis["layer"] = self._detect_layer(str(relative_path))
            analysis["related_files"] = self._find_related_files(analysis)
            return analysis
        except SyntaxError as e:
            return {"file_path": str(file_path), "error": f"Syntax error: {e}", "analysis_timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"file_path": str(file_path), "error": f"Analysis error: {e}", "analysis_timestamp": datetime.now().isoformat()}

    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {"name": node.name, "docstring": ast.get_docstring(node), "methods": [], "attributes": [], "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list], "base_classes": [self._get_name(base) for base in node.bases], "lineno": node.lineno}
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {"name": item.name, "docstring": ast.get_docstring(item), "args": [arg.arg for arg in item.args.args], "decorators": [self._get_decorator_name(dec) for dec in item.decorator_list], "returns": self._get_annotation(item.returns), "lineno": item.lineno, "is_property": any("property" in str(dec) for dec in item.decorator_list)}
                        class_info["methods"].append(method_info)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info["attributes"].append(target.id)
                classes.append(class_info)
        return classes

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_method(node):
                    func_info = {"name": node.name, "docstring": ast.get_docstring(node), "args": [arg.arg for arg in node.args.args], "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list], "returns": self._get_annotation(node.returns), "lineno": node.lineno}
                    functions.append(func_info)
        return functions

    def _extract_imports(self, tree: ast.AST) -> Dict[str, List[str]]:
        external_imports = []
        internal_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_internal_import(alias.name):
                        internal_imports.append(alias.name)
                    else:
                        external_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if self._is_internal_import(module):
                    for alias in node.names:
                        internal_imports.append(f"{module}.{alias.name}" if module else alias.name)
                else:
                    for alias in node.names:
                        external_imports.append(f"{module}.{alias.name}" if module else alias.name)
        return {"external": list(set(external_imports)), "internal": list(set(internal_imports))}

    def _extract_decorators(self, tree: ast.AST) -> List[str]:
        decorators = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    decorators.add(self._get_decorator_name(dec))
        return list(decorators)

    def _detect_etl_pattern(self, classes: List[Dict]) -> bool:
        for cls in classes:
            method_names = {m["name"] for m in cls["methods"]}
            if {"extract", "transform", "load"}.issubset(method_names):
                return True
        return False

    def _detect_layer(self, file_path: str) -> str:
        file_path_lower = file_path.lower()
        if "gold" in file_path_lower:
            return "gold"
        elif "silver" in file_path_lower:
            return "silver"
        elif "bronze" in file_path_lower:
            return "bronze"
        elif "utilities" in file_path_lower or "util" in file_path_lower:
            return "utility"
        elif "test" in file_path_lower:
            return "testing"
        elif "pipeline" in file_path_lower:
            return "pipeline"
        else:
            return "other"

    def _find_related_files(self, analysis: Dict) -> List[Dict[str, str]]:
        related = []
        file_name = analysis["module_name"]
        layer = analysis["layer"]
        if layer == "gold" and file_name.startswith("g_"):
            silver_name = file_name.replace("g_", "s_", 1)
            for db in ["cms", "fvms", "nicherms"]:
                if db in file_name:
                    related.append({"file_name": f"{silver_name}.py", "relationship": "silver_input", "wiki_path": f"/silver/silver_{db}/{silver_name}", "layer": "silver"})
                    break
        elif layer == "silver" and file_name.startswith("s_"):
            gold_name = file_name.replace("s_", "g_", 1)
            related.append({"file_name": f"{gold_name}.py", "relationship": "gold_output", "wiki_path": f"/gold/{gold_name}", "layer": "gold"})
            bronze_name = file_name.replace("s_", "b_", 1)
            related.append({"file_name": f"{bronze_name}.parquet", "relationship": "bronze_input", "wiki_path": f"/bronze/{bronze_name}", "layer": "bronze"})
        for internal_import in analysis.get("imports", {}).get("internal", []):
            import_parts = internal_import.split(".")
            if len(import_parts) >= 2:
                import_file = import_parts[-1] if import_parts[-1] not in ["py", "pyspark", "spark"] else import_parts[-2]
                related.append({"file_name": f"{import_file}.py", "relationship": "dependency", "wiki_path": f"/{import_parts[0]}/{import_file}", "layer": "utility"})
        return related

    def _is_internal_import(self, module_name: str) -> bool:
        internal_prefixes = ["python_files", "utilities", "pipeline_operations", "gold", "silver", "bronze", "testing"]
        return any(module_name.startswith(prefix) for prefix in internal_prefixes)

    def _is_method(self, node: ast.FunctionDef) -> bool:
        parent_stack = []
        def check_parent(n):
            parent_stack.append(n)
            for child in ast.iter_child_nodes(n):
                if child == node:
                    return any(isinstance(p, ast.ClassDef) for p in parent_stack)
                if check_parent(child):
                    return True
            parent_stack.pop()
            return False
        return False

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name(decorator.value)}.{decorator.attr}"
        return str(decorator)

    def _get_name(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def _get_annotation(self, node: Optional[ast.expr]) -> Optional[str]:
        if node is None:
            return None
        return self._get_name(node)

def generate_markdown(analysis: Dict, repo_url: str, branch: str = "main", wiki_base: Optional[str] = None, repo_root: str = None) -> str:
    if repo_root is None:
        repo_root = os.getcwd()
    if wiki_base is None:
        repo_name = Path(repo_root).resolve().name
        wiki_base = f"/Unify-2.1-Data-Migration-Technical-Documentation/Data-Migration-Pipeline/{repo_name}"
    if "error" in analysis:
        return f"# {analysis.get('file_name', 'Error')}\n\n**Error analyzing file**: {analysis['error']}\n"
    file_path = analysis["file_path"]
    file_name = analysis["file_name"]
    module_name = analysis["module_name"]
    layer = analysis["layer"]
    line_count = analysis["line_count"]
    classes = analysis["classes"]
    functions = analysis["functions"]
    imports = analysis["imports"]
    has_etl = analysis["has_etl_pattern"]
    decorators = analysis["decorators"]
    module_doc = analysis.get("module_docstring", "")
    related_files = analysis.get("related_files", [])
    encoded_repo_url = repo_url.replace(" ", "%20")
    repo_file_url = f"{encoded_repo_url}?path=/{file_path}&version=GB{branch}"
    md = [f"# {module_name}", "", f"**File Path**: `{file_path}`", f"**Repository Link**: [View Source]({repo_file_url})", f"**Layer**: {layer.capitalize()}", f"**Lines of Code**: {line_count}", ""]
    if module_doc:
        md.extend(["## Module Description", "", module_doc, ""])
    else:
        md.extend(["## Overview", "", f"Python module for {layer} layer processing.", ""])
    if classes:
        md.extend(["## Classes", ""])
        for cls in classes:
            md.append(f"### `{cls['name']}`")
            if cls.get("base_classes"):
                md.append(f"**Inherits from**: {', '.join(cls['base_classes'])}")
            if cls.get("decorators"):
                md.append(f"**Decorators**: {', '.join(cls['decorators'])}")
            md.append("")
            if cls.get("docstring"):
                md.append(f"**Purpose**: {cls['docstring']}")
            elif has_etl:
                md.append(f"**Purpose**: ETL class for {layer} layer transformation")
            else:
                md.append(f"**Purpose**: {cls['name']} implementation")
            md.append("")
            if cls.get("attributes"):
                md.append("**Attributes**:")
                for attr in cls["attributes"]:
                    md.append(f"- `{attr}`")
                md.append("")
            if cls.get("methods"):
                md.append("**Methods**:")
                for method in cls["methods"]:
                    args_str = ", ".join(method["args"])
                    returns_str = f" -> {method['returns']}" if method.get("returns") else ""
                    decorators_str = f" [{', '.join(method['decorators'])}]" if method.get("decorators") else ""
                    md.append(f"- `{method['name']}({args_str}){returns_str}`{decorators_str}")
                    if method.get("docstring"):
                        md.append(f"  - {method['docstring']}")
                md.append("")
    if functions:
        md.extend(["## Functions", ""])
        for func in functions:
            args_str = ", ".join(func["args"])
            returns_str = f" -> {func['returns']}" if func.get("returns") else ""
            decorators_str = f" [{', '.join(func['decorators'])}]" if func.get("decorators") else ""
            md.append(f"### `{func['name']}({args_str}){returns_str}`{decorators_str}")
            if func.get("docstring"):
                md.append(f"**Purpose**: {func['docstring']}")
            md.append("")
    md.extend(["## Dependencies", ""])
    if imports["external"]:
        md.append("### External Libraries")
        for imp in sorted(imports["external"]):
            md.append(f"- `{imp}`")
        md.append("")
    if imports["internal"]:
        md.append("### Internal Modules")
        for imp in sorted(imports["internal"]):
            md.append(f"- `{imp}`")
        md.append("")
    if related_files:
        md.extend(["## Related Files", ""])
        for related in related_files:
            relationship = related["relationship"].replace("_", " ").title()
            md.append(f"- [{related['file_name']}]({wiki_base}{related['wiki_path']}) - {relationship}")
        md.append("")
    if has_etl:
        md.extend(["## ETL Pattern", "", "This file implements the Extract-Transform-Load (ETL) pattern with dedicated methods for each phase.", ""])
    if decorators:
        md.extend(["## Decorators Used", ""])
        for dec in sorted(decorators):
            if dec == "synapse_error_print_handler":
                md.append(f"- `@{dec}` - Error handling and logging for Synapse operations")
            else:
                md.append(f"- `@{dec}`")
        md.append("")
    md.extend(["---", f"*Auto-generated documentation*", f"*Last updated: {analysis['analysis_timestamp']}*", f"*Generated by: wiki-auto-documenter skill*"])
    return "\n".join(md)

def analyze_file(file_path: str, repo_root: str = None) -> Dict[str, Any]:
    if repo_root is None:
        repo_root = os.getcwd()
    analyzer = CodeAnalyzer(repo_root)
    return analyzer.analyze_file(file_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python code_analyzer.py <file_path> [repo_root]")
        print("\nExample:")
        print("  python code_analyzer.py python_files/gold/g_cms_address.py")
        sys.exit(1)
    file_path = sys.argv[1]
    repo_root = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    try:
        analysis = analyze_file(file_path, repo_root)
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            sys.exit(1)
        print(f"✅ Analysis complete for: {analysis['file_path']}")
        print(f"\n📊 Summary:")
        print(f"   Classes: {len(analysis['classes'])}")
        print(f"   Functions: {len(analysis['functions'])}")
        print(f"   External imports: {len(analysis['imports']['external'])}")
        print(f"   Internal imports: {len(analysis['imports']['internal'])}")
        print(f"   ETL pattern: {'Yes' if analysis['has_etl_pattern'] else 'No'}")
        print(f"   Layer: {analysis['layer']}")
        print(f"   Lines: {analysis['line_count']}")
        print(f"\n📝 Markdown documentation:")
        print("=" * 80)
        repo_url = "https://dev.azure.com/emstas/Program%20Unify/_git/unify_2_1_dm_synapse_env_d10"
        markdown = generate_markdown(analysis, repo_url, branch="main", repo_root=repo_root)
        print(markdown)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
