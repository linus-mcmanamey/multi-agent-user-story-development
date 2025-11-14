"""
Wiki Hierarchy Builder

Builds Azure DevOps wiki page hierarchy from repository directory structure.
Maps repository directory tree to wiki page paths and generates index pages.

Usage:
    from wiki_hierarchy_builder import WikiHierarchyBuilder

    builder = WikiHierarchyBuilder(
        repo_root=os.getcwd(),
        wiki_base=f"/{os.path.basename(os.getcwd())}"
    )
    hierarchy = builder.build_hierarchy("python_files/gold/")

Output:
    {
        "wiki_path": "/unify_2_1_dm_synapse_env_d10/gold",
        "repo_path": "python_files/gold",
        "files": [list of .py files],
        "subdirs": [list of subdirectories],
        "parent_path": "/unify_2_1_dm_synapse_env_d10",
        "file_count": 50
    }
"""

import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class WikiHierarchyBuilder:
    """Builds wiki hierarchy from repository directory structure"""

    def __init__(self, repo_root: str, wiki_base: Optional[str] = None):
        self.repo_root = Path(repo_root).resolve()
        if wiki_base is None:
            repo_name = self.repo_root.name
            wiki_base = f"/Unify-2.1-Data-Migration-Technical-Documentation/Data-Migration-Pipeline/{repo_name}"
        self.wiki_base = wiki_base.rstrip("/")

    def build_hierarchy(self, path: str, recursive: bool = True) -> Dict[str, Any]:
        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = self.repo_root / target_path
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")
        if target_path.is_file():
            return self._build_file_info(target_path)
        elif target_path.is_dir():
            return self._build_directory_info(target_path, recursive)
        else:
            raise ValueError(f"Invalid path type: {target_path}")

    def _build_file_info(self, file_path: Path) -> Dict[str, Any]:
        relative_path = file_path.relative_to(self.repo_root)
        wiki_path = self.map_repo_to_wiki(str(relative_path))
        return {"type": "file", "repo_path": str(relative_path), "absolute_path": str(file_path), "wiki_path": wiki_path, "file_name": file_path.name, "parent_path": str(file_path.parent.relative_to(self.repo_root))}

    def _build_directory_info(self, dir_path: Path, recursive: bool) -> Dict[str, Any]:
        relative_path = dir_path.relative_to(self.repo_root) if dir_path != self.repo_root else Path(".")
        wiki_path = self.map_repo_to_wiki(str(relative_path))
        files = []
        subdirs = []
        total_files = 0
        for item in sorted(dir_path.iterdir()):
            if item.is_file() and item.suffix == ".py" and not item.name.startswith("__"):
                file_info = {"file_name": item.name, "module_name": item.stem, "repo_path": str(item.relative_to(self.repo_root)), "wiki_path": self.map_repo_to_wiki(str(item.relative_to(self.repo_root))).replace(".py", "")}
                files.append(file_info)
                total_files += 1
            elif item.is_dir() and not item.name.startswith(".") and not item.name == "__pycache__":
                subdir_info = {"dir_name": item.name, "repo_path": str(item.relative_to(self.repo_root)), "wiki_path": self.map_repo_to_wiki(str(item.relative_to(self.repo_root)))}
                if recursive:
                    subdir_hierarchy = self._build_directory_info(item, recursive)
                    subdir_info["file_count"] = subdir_hierarchy["total_files"]
                    subdir_info["subdirs"] = subdir_hierarchy["subdirs"]
                subdirs.append(subdir_info)
                if recursive:
                    total_files += subdir_info.get("file_count", 0)
        parent_path = self.map_repo_to_wiki(str(relative_path.parent)) if relative_path != Path(".") else None
        return {"type": "directory", "repo_path": str(relative_path), "absolute_path": str(dir_path), "wiki_path": wiki_path, "parent_path": parent_path, "files": files, "subdirs": subdirs, "total_files": total_files, "direct_files": len(files)}

    def map_repo_to_wiki(self, repo_path: str) -> str:
        repo_path = repo_path.replace("\\", "/")
        if repo_path == ".":
            return self.wiki_base
        wiki_path = f"{self.wiki_base}/{repo_path}".replace(".py", "")
        return wiki_path

    def generate_index_content(self, directory_info: Dict[str, Any], analysis_summaries: Optional[List[Dict]] = None) -> str:
        dir_name = Path(directory_info["repo_path"]).name
        repo_path = directory_info["repo_path"]
        wiki_path = directory_info["wiki_path"]
        files = directory_info["files"]
        subdirs = directory_info["subdirs"]
        total_files = directory_info["total_files"]
        direct_files = directory_info["direct_files"]
        md = [f"# {dir_name if dir_name != '.' else 'Python Files'}", "", f"**Repository Path**: `{repo_path}`", f"**Total Python Files**: {total_files} ({direct_files} in this directory)", f"**Subdirectories**: {len(subdirs)}", ""]
        layer_description = self._get_layer_description(dir_name)
        if layer_description:
            md.extend(["## Overview", "", layer_description, ""])
        if files:
            md.extend(["## Files in This Directory", ""])
            file_summaries = {f["module_name"]: f for f in files}
            if analysis_summaries:
                for summary in analysis_summaries:
                    if summary["module_name"] in file_summaries:
                        file_info = file_summaries[summary["module_name"]]
                        class_count = len(summary.get("classes", []))
                        func_count = len(summary.get("functions", []))
                        has_etl = summary.get("has_etl_pattern", False)
                        etl_badge = " `[ETL]`" if has_etl else ""
                        description = summary.get("module_docstring", "").split("\n")[0] if summary.get("module_docstring") else f"{summary['layer'].capitalize()} layer processing"
                        md.append(f"- [{file_info['module_name']}]({file_info['wiki_path']}){etl_badge}")
                        md.append(f"  - {description}")
                        md.append(f"  - {class_count} classes, {func_count} functions")
            else:
                for file_info in files:
                    md.append(f"- [{file_info['module_name']}]({file_info['wiki_path']})")
            md.append("")
        if subdirs:
            md.extend(["## Subdirectories", ""])
            for subdir in subdirs:
                file_count_str = f" ({subdir.get('file_count', '?')} files)" if subdir.get("file_count") else ""
                md.append(f"- [{subdir['dir_name']}]({subdir['wiki_path']}){file_count_str}")
            md.append("")
        if directory_info.get("parent_path"):
            md.extend(["## Navigation", "", f"- [⬆️ Parent Directory]({directory_info['parent_path']})", ""])
        md.extend(["---", f"*Auto-generated directory index*", f"*Last updated: {datetime.now().isoformat()}*", f"*Generated by: wiki-auto-documenter skill*"])
        return "\n".join(md)

    def _get_layer_description(self, dir_name: str) -> Optional[str]:
        descriptions = {"gold": "**Gold Layer**: Business-ready analytics tables optimized for reporting and data consumption. Final transformation layer containing aggregated, denormalized, and enriched data.", "silver": "**Silver Layer**: Validated and standardized data with cleansed values, type conversions, and business logic applied. Intermediate transformation layer.", "bronze": "**Bronze Layer**: Raw ingested data from source systems stored in Parquet format. Minimal transformation applied.", "utilities": "**Utilities**: Shared helper functions, common patterns, and reusable components used across all layers. Includes SparkOptimiser, TableUtilities, and NotebookLogger.", "testing": "**Testing**: Test suites for validating pipeline operations, data quality, and ETL transformations across all medallion layers.", "pipeline_operations": "**Pipeline Operations**: Orchestration and deployment scripts for managing bronze, silver, and gold layer processing workflows.", "silver_cms": "**Silver CMS**: Case Management System data transformations - validated and standardized CMS source data.", "silver_fvms": "**Silver FVMS**: Family Violence Management System transformations - validated FVMS incident and safety audit data.", "silver_nicheRMS": "**Silver NicheRMS**: Record Management System transformations - validated person, address, and identification data."}
        return descriptions.get(dir_name)

    def get_decomposition_strategy(self, hierarchy: Dict[str, Any], max_agents: int = 8, target_files_per_agent: int = 30) -> Dict[str, Any]:
        total_files = hierarchy["total_files"]
        if total_files <= target_files_per_agent:
            return {"strategy": "single_agent", "agent_count": 1, "assignments": [{"agent_id": "code-documenter-1", "path": hierarchy["repo_path"], "file_count": total_files}]}
        subdirs = hierarchy.get("subdirs", [])
        if subdirs and len(subdirs) <= max_agents:
            balanced = all(subdir.get("file_count", 0) > 5 for subdir in subdirs)
            if balanced:
                assignments = []
                for i, subdir in enumerate(subdirs, 1):
                    assignments.append({"agent_id": f"code-documenter-{i}", "path": subdir["repo_path"], "file_count": subdir.get("file_count", 0)})
                return {"strategy": "by_directory", "agent_count": len(subdirs), "assignments": assignments}
        optimal_agents = min(max_agents, (total_files + target_files_per_agent - 1) // target_files_per_agent)
        files_per_agent = (total_files + optimal_agents - 1) // optimal_agents
        all_files = self._collect_all_files(hierarchy)
        assignments = []
        for i in range(optimal_agents):
            start_idx = i * files_per_agent
            end_idx = min((i + 1) * files_per_agent, total_files)
            agent_files = all_files[start_idx:end_idx]
            assignments.append({"agent_id": f"code-documenter-{i+1}", "files": agent_files, "file_count": len(agent_files)})
        return {"strategy": "by_file_chunks", "agent_count": optimal_agents, "files_per_agent": files_per_agent, "assignments": assignments}

    def _collect_all_files(self, hierarchy: Dict[str, Any]) -> List[str]:
        files = []
        for file_info in hierarchy.get("files", []):
            files.append(file_info["repo_path"])
        for subdir in hierarchy.get("subdirs", []):
            if "subdirs" in subdir:
                files.extend(self._collect_all_files(subdir))
        return files

def main():
    if len(sys.argv) < 2:
        print("Usage: python wiki_hierarchy_builder.py <path> [repo_root] [wiki_base]")
        print("\nExamples:")
        print("  python wiki_hierarchy_builder.py python_files/gold/")
        print("  python wiki_hierarchy_builder.py python_files/ /workspaces/your_project /docs")
        sys.exit(1)
    path = sys.argv[1]
    repo_root = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    wiki_base = sys.argv[3] if len(sys.argv) > 3 else None
    try:
        builder = WikiHierarchyBuilder(repo_root, wiki_base)
        hierarchy = builder.build_hierarchy(path)
        print(f"✅ Hierarchy built for: {hierarchy['repo_path']}")
        print(f"\n📊 Summary:")
        print(f"   Type: {hierarchy['type']}")
        print(f"   Wiki path: {hierarchy['wiki_path']}")
        if hierarchy['type'] == 'directory':
            print(f"   Total files: {hierarchy['total_files']}")
            print(f"   Direct files: {hierarchy['direct_files']}")
            print(f"   Subdirectories: {len(hierarchy['subdirs'])}")
            print(f"\n🔧 Decomposition strategy:")
            strategy = builder.get_decomposition_strategy(hierarchy)
            print(f"   Strategy: {strategy['strategy']}")
            print(f"   Agent count: {strategy['agent_count']}")
            if strategy['strategy'] != 'single_agent':
                print(f"   Assignments:")
                for assignment in strategy['assignments']:
                    if 'path' in assignment:
                        print(f"      - {assignment['agent_id']}: {assignment['path']} ({assignment['file_count']} files)")
                    else:
                        print(f"      - {assignment['agent_id']}: {assignment['file_count']} files")
            print(f"\n📄 Index page content:")
            print("=" * 80)
            index_content = builder.generate_index_content(hierarchy)
            print(index_content)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
