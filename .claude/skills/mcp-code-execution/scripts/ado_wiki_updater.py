#!/usr/bin/env python3
"""Context-efficient Azure DevOps Wiki updater using MCP code execution pattern."""
import os
import sys
import json
import ast
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Azure DevOps Configuration
ORG = os.getenv('AZURE_DEVOPS_ORG', 'emstas')
PROJECT = os.getenv('AZURE_DEVOPS_PROJECT', 'Program Unify')
PAT = os.getenv('AZURE_DEVOPS_PAT')
WIKI_ID = 'Program-Unify.wiki'

BASE_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wiki/wikis/{WIKI_ID}"
AUTH = ('', PAT)
HEADERS = {'Content-Type': 'application/json'}

class WikiUpdater:
    """Context-efficient wiki page updater."""

    def __init__(self):
        self.stats = {
            'pages_checked': 0,
            'pages_updated': 0,
            'pages_created': 0,
            'pages_failed': 0,
            'errors': []
        }

    def analyze_python_file(self, file_path: str) -> Optional[Dict]:
        """Lightweight AST analysis - only return summary, not full content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            classes = []
            functions = []
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node) or f"{node.name} implementation"
                    methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'docstring': docstring[:200],  # Truncate for context efficiency
                        'method_count': len(methods),
                        'methods': methods[:5]  # Limit methods in summary
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Only count top-level functions
                    parent = getattr(node, '_parent', None)
                    if not isinstance(parent, ast.ClassDef):
                        docstring = ast.get_docstring(node) or f"{node.name} function"
                        functions.append({
                            'name': node.name,
                            'docstring': docstring[:200]
                        })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name for alias in node.names)
                    elif node.module:
                        imports.add(node.module)

            return {
                'classes': classes,
                'functions': functions,
                'imports': sorted(list(imports))[:15],  # Limit imports
                'class_count': len(classes),
                'function_count': len(functions)
            }

        except Exception as e:
            return {'error': str(e)}

    def generate_markdown(self, file_path: str, analysis: Dict, branch: str) -> str:
        """Generate well-formatted markdown with proper formatting."""
        filename = Path(file_path).stem
        repo_link = f"https://dev.azure.com/{ORG}/{PROJECT}/_git/unify_2_1_dm_synapse_env_d10?path=/{file_path}&version=GB{branch}"

        # Header with badges
        md = f"""# {filename}

> **Utility Module** | [View Source]({repo_link}) | **Branch**: `{branch}`

---

## 📋 Overview

**File Path**: `{file_path}`
**Category**: Utility Module
**Project**: Unify Data Migration (Medallion Architecture)

{filename.replace('_', ' ').title()} - Core utility module for the Unify data migration project supporting Bronze → Silver → Gold data transformations.

---

## 📦 Components Summary

| Component Type | Count |
|----------------|-------|
| Classes | {analysis.get('class_count', 0)} |
| Functions | {analysis.get('function_count', 0)} |
| Dependencies | {len(analysis.get('imports', []))} |

"""

        # Classes section with better formatting
        if analysis.get('classes'):
            md += "\n---\n\n## 🏛️ Classes\n\n"
            for i, cls in enumerate(analysis['classes'], 1):
                md += f"### {i}. `{cls['name']}`\n\n"
                md += f"> {cls['docstring']}\n\n"

                if cls['method_count'] > 0:
                    md += f"**Methods** ({cls['method_count']} total):\n\n"
                    md += "```python\n"
                    for method in cls['methods']:
                        md += f"{method}()\n"
                    md += "```\n\n"

        # Functions section with code blocks
        if analysis.get('functions'):
            md += "\n---\n\n## ⚙️ Functions\n\n"
            for i, func in enumerate(analysis['functions'], 1):
                md += f"### {i}. `{func['name']}()`\n\n"
                md += "**Description:**\n\n"
                md += f"> {func['docstring']}\n\n"
                md += "**Usage:**\n\n"
                md += "```python\n"
                md += f"from {file_path.replace('/', '.').replace('.py', '')} import {func['name']}\n\n"
                md += f"result = {func['name']}(...)\n"
                md += "```\n\n"

        # Dependencies with categorization
        if analysis.get('imports'):
            md += "\n---\n\n## 📚 Dependencies\n\n"

            # Categorize imports
            external_imports = []
            internal_imports = []

            for imp in analysis['imports']:
                if any(x in imp for x in ['pyspark', 'pandas', 'numpy', 'requests', 'azure', 'yaml', 'json', 'os', 'sys', 'pathlib', 'typing', 'dataclasses', 'enum', 'duckdb', 'loguru', 'rich', 'textual']):
                    external_imports.append(imp)
                else:
                    internal_imports.append(imp)

            if external_imports:
                md += "### External Libraries\n\n"
                md += "| Package | Purpose |\n"
                md += "|---------|----------|\n"
                for imp in external_imports:
                    purpose = self._guess_package_purpose(imp)
                    md += f"| `{imp}` | {purpose} |\n"
                md += "\n"

            if internal_imports:
                md += "### Internal Modules\n\n"
                md += "| Module | Type |\n"
                md += "|--------|------|\n"
                for imp in internal_imports:
                    md += f"| `{imp}` | Project Utility |\n"
                md += "\n"

        # Usage examples section
        md += "\n---\n\n## 💡 Usage\n\n"

        if analysis.get('classes'):
            first_class = analysis['classes'][0]['name']
            md += f"### Basic Usage Example\n\n"
            md += "```python\n"
            md += f"from {file_path.replace('/', '.').replace('.py', '')} import {first_class}\n\n"
            md += f"# Initialize and use the {first_class}\n"
            md += f"instance = {first_class}(...)\n"
            md += "```\n\n"

        md += "> 💡 **Note**: For detailed implementation and advanced usage, refer to the source code.\n\n"

        # Footer
        md += f"""---

## 📄 Documentation Metadata

- **Last Updated**: 2025-11-13
- **Generated By**: wiki-auto-documenter skill
- **Documentation Type**: Auto-generated from source code
- **Source Branch**: `{branch}`

### Quick Links

- [🔗 View Source Code]({repo_link})
- [📖 Project Documentation](https://dev.azure.com/{ORG}/{PROJECT}/_wiki)
- [🏠 Utilities Index](/unify_2_1_dm_synapse_env_d10/utilities)

---

*This documentation is automatically generated from the source code. For the most up-to-date information, please refer to the source file.*
"""

        return md

    def _guess_package_purpose(self, package: str) -> str:
        """Guess package purpose for documentation."""
        purposes = {
            'pyspark': 'Distributed data processing',
            'pandas': 'Data manipulation',
            'numpy': 'Numerical computing',
            'requests': 'HTTP client',
            'azure': 'Azure cloud services',
            'yaml': 'YAML configuration',
            'json': 'JSON processing',
            'os': 'Operating system interface',
            'sys': 'System-specific parameters',
            'pathlib': 'Object-oriented filesystem paths',
            'typing': 'Type hints support',
            'dataclasses': 'Data class support',
            'enum': 'Enumeration support',
            'duckdb': 'Embedded analytical database',
            'loguru': 'Advanced logging',
            'rich': 'Rich text and formatting',
            'textual': 'Terminal UI framework'
        }

        for key, purpose in purposes.items():
            if key in package.lower():
                return purpose

        return 'Utility module'

    def get_page(self, wiki_path: str) -> Optional[Dict]:
        """Get wiki page metadata (for eTag)."""
        url = f"{BASE_URL}/pages?path={wiki_path}&includeContent=false&api-version=7.1"
        try:
            response = requests.get(url, auth=AUTH, timeout=10)
            if response.status_code == 200:
                # ETag is in response headers, not body
                page_data = response.json()
                page_data['eTag'] = response.headers.get('ETag', '').strip('"')
                return page_data
            return None
        except Exception as e:
            self.stats['errors'].append(f"GET {wiki_path}: {str(e)}")
            return None

    def create_or_update_page(self, wiki_path: str, content: str) -> bool:
        """Create or update wiki page - context-efficient (only return success/failure)."""
        self.stats['pages_checked'] += 1

        # Check if page exists
        page = self.get_page(wiki_path)

        if page:
            # UPDATE existing page (use PUT with If-Match)
            etag = page.get('eTag')
            if not etag:
                self.stats['pages_failed'] += 1
                self.stats['errors'].append(f"No eTag for {wiki_path}")
                return False

            url = f"{BASE_URL}/pages?path={wiki_path}&api-version=7.1"
            headers = {**HEADERS, 'If-Match': etag}
            payload = {'content': content}

            try:
                response = requests.put(url, auth=AUTH, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    self.stats['pages_updated'] += 1
                    return True
                else:
                    self.stats['pages_failed'] += 1
                    self.stats['errors'].append(f"UPDATE {wiki_path}: HTTP {response.status_code}")
                    return False
            except Exception as e:
                self.stats['pages_failed'] += 1
                self.stats['errors'].append(f"UPDATE {wiki_path}: {str(e)}")
                return False

        else:
            # CREATE new page
            url = f"{BASE_URL}/pages?path={wiki_path}&api-version=7.1"
            payload = {'content': content}

            try:
                response = requests.put(url, auth=AUTH, headers=HEADERS, json=payload, timeout=30)
                if response.status_code in [200, 201]:
                    self.stats['pages_created'] += 1
                    return True
                else:
                    self.stats['pages_failed'] += 1
                    error_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
                    self.stats['errors'].append(f"CREATE {wiki_path}: {error_msg}")
                    return False
            except Exception as e:
                self.stats['pages_failed'] += 1
                self.stats['errors'].append(f"CREATE {wiki_path}: {str(e)}")
                return False

    def update_utilities_wiki(self, utilities_dir: str = "python_files/utilities",
                              wiki_base: str = "/unify_2_1_dm_synapse_env_d10/utilities",
                              branch: str = "feature/uat_fixes_linus") -> Dict:
        """
        Update all utility files wiki pages.

        Returns only summary statistics - keeps context efficient.
        """
        utility_files = sorted(Path(utilities_dir).glob("*.py"))

        print(f"Processing {len(utility_files)} utility files...")

        for i, file_path in enumerate(utility_files, 1):
            filename = file_path.stem
            wiki_path = f"{wiki_base}/{filename}"

            print(f"[{i}/{len(utility_files)}] {filename}...", end=' ')

            # Analyze file (lightweight, filtered)
            analysis = self.analyze_python_file(str(file_path))

            if 'error' in analysis:
                print(f"❌ Analysis error: {analysis['error']}")
                self.stats['pages_failed'] += 1
                continue

            # Generate markdown (happens in subprocess, not in Claude context)
            markdown = self.generate_markdown(f"python_files/utilities/{file_path.name}",
                                             analysis, branch)

            # Update wiki page
            if self.create_or_update_page(wiki_path, markdown):
                action = "✅ Updated" if wiki_path in str(self.stats) else "✅ Created"
                print(f"{action}")
            else:
                print("❌ Failed")

        return self.get_summary()

    def get_summary(self) -> Dict:
        """Return minimal summary for Claude context."""
        return {
            'pages_checked': self.stats['pages_checked'],
            'pages_updated': self.stats['pages_updated'],
            'pages_created': self.stats['pages_created'],
            'pages_failed': self.stats['pages_failed'],
            'error_count': len(self.stats['errors']),
            'errors': self.stats['errors'][:5]  # Only first 5 errors
        }


def main():
    """CLI entry point."""
    updater = WikiUpdater()

    # Update utilities wiki
    summary = updater.update_utilities_wiki()

    # Print context-efficient summary (not full details)
    print("\n" + "=" * 80)
    print("📊 Wiki Update Summary")
    print("=" * 80)
    print(f"✅ Pages updated: {summary['pages_updated']}")
    print(f"➕ Pages created: {summary['pages_created']}")
    print(f"❌ Pages failed: {summary['pages_failed']}")
    print(f"📄 Total checked: {summary['pages_checked']}")

    if summary['errors']:
        print(f"\n⚠️  Errors ({summary['error_count']} total, showing first 5):")
        for error in summary['errors']:
            print(f"  - {error}")

    print(f"\n🔗 Wiki URL: https://dev.azure.com/{ORG}/{PROJECT}/_wiki/wikis/{WIKI_ID}/274/unify_2_1_dm_synapse_env_d10/utilities")
    print("=" * 80)

    # Return summary as JSON for programmatic use
    return json.dumps(summary, indent=2)


if __name__ == "__main__":
    main()
