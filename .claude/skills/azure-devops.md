---
name: azure-devops
description: On-demand Azure DevOps operations (PRs, work items, pipelines, repos) using context-efficient patterns. Loaded only when needed to avoid polluting Claude context with 50+ MCP tools. (project, gitignored)
---

# Azure DevOps (On-Demand)

Context-efficient Azure DevOps operations without loading all MCP tools into context.

## When to Use This Skill

Load this skill when you need to:
- Query pull request details, conflicts, or discussion threads
- Check merge status or retrieve PR commits
- Add comments to Azure DevOps work items
- Query work item details or WIQL searches
- Trigger or monitor pipeline runs
- Manage repository branches or commits
- Avoid loading 50+ MCP tools into Claude's context

## Core Concept

Use REST API helpers and Python scripts to interact with Azure DevOps only when needed. Results are filtered before returning to context.

**Context Efficiency**:
- **Without this approach**: Loading ADO MCP server → 50+ tools → 10,000-25,000 tokens
- **With this approach**: Load specific helper when needed → 500-2,000 tokens

## Prerequisites

Environment variables must be set:
```bash
export AZURE_DEVOPS_PAT="your-personal-access-token"
export AZURE_DEVOPS_ORGANIZATION="emstas"
export AZURE_DEVOPS_PROJECT="Program Unify"
```

## Quick Reference

### Pull Request Operations

```python
from scripts.ado_pr_helper import ADOHelper

ado = ADOHelper()

# Get PR details
pr = ado.get_pr(5860)
print(pr["title"])
print(pr["mergeStatus"])

# Check for merge conflicts
conflicts = ado.get_pr_conflicts(5860)
if conflicts.get("value"):
    print(f"Found {len(conflicts['value'])} conflicts")

# Get PR discussion threads
threads = ado.get_pr_threads(5860)

# Get PR commits
commits = ado.get_pr_commits(5860)
```

### CLI Usage

```bash
# Get PR details and check conflicts
python3 .claude/skills/mcp-code-execution/scripts/ado_pr_helper.py 5860
```

## Common Workflows

### Review and Fix PR Conflicts

```python
# 1. Get PR details and conflicts
ado = ADOHelper()
pr = ado.get_pr(pr_id)
conflicts = ado.get_pr_conflicts(pr_id)

# 2. Filter to only conflict info (don't load full PR data)
conflict_files = [c["conflictPath"] for c in conflicts.get("value", [])]

# 3. Return summary to context
print(f"PR {pr_id}: {pr['mergeStatus']}")
print(f"Conflicts in: {', '.join(conflict_files)}")
```

### Integration with Git Commands

This skill complements the git-manager agent and slash commands:
- `/pr-feature-to-staging` - Uses ADO API to create PR and comment on work items
- `/pr-fix-pr-review [PR_ID]` - Retrieves review comments via ADO API
- `/pr-deploy-workflow` - Queries PR status during deployment
- `/branch-cleanup` - Checks remote branch merge status

## Repository Configuration

**Organization**: emstas
**Project**: Program Unify
**Repository**: unify_2_1_dm_synapse_env_d10
**Repository ID**: e030ea00-2f85-4b19-88c3-05a864d7298d

## Extending Functionality

To add more ADO operations:
1. Add methods to `ado_pr_helper.py` or create new helper files
2. Follow the pattern: fetch → filter → return summary
3. Use REST API directly for maximum efficiency
4. Document new operations in the skill directory

## REST API Reference

**Base URL**: `https://dev.azure.com/{organization}/{project}/_apis/`
**API Version**: `7.1`
**Authentication**: Basic auth with PAT
**Documentation**: https://learn.microsoft.com/en-us/rest/api/azure/devops/

## Skill Directory Structure

For detailed documentation, see:
- `azure-devops/skill.md` - Complete skill documentation
- `azure-devops/scripts/` - Helper scripts (ado_pr_helper.py)
- `azure-devops/README.md` - Quick start guide (future)
- `azure-devops/INDEX.md` - Navigation guide (future)

## Best Practices

### DO
- ✅ Use this skill to avoid loading MCP server tools
- ✅ Filter results before returning to context
- ✅ Return summaries instead of full data structures
- ✅ Use helper scripts for common operations
- ✅ Cache results when making multiple calls

### DON'T
- ❌ Load MCP server if only querying 1-2 PRs
- ❌ Return full JSON responses to context
- ❌ Make redundant API calls
- ❌ Expose PAT tokens in logs or responses

## Integration Points

### With Git Manager Agent
- PR creation and status checking
- Review comment retrieval
- Work item commenting
- Branch merge status

### With Deployment Workflows
- Pipeline trigger and monitoring
- PR validation before merge
- Work item state updates
- Commit linking

### With Documentation
- Wiki page management (future)
- Markdown documentation sync (future)
- Work item documentation links

## Performance

**API Call Timing**:
- Single PR query: ~200-500ms
- PR with conflicts: ~300-700ms
- PR threads retrieval: ~400-1000ms
- Work item query: ~100-300ms

**Rate Limits**:
- Azure DevOps API: 200 requests per minute per PAT
- Best practice: Batch operations when possible

## Troubleshooting

### Issue: Authentication Failed
```bash
# Verify PAT is set
echo $AZURE_DEVOPS_PAT

# Test connection
python3 scripts/ado_pr_helper.py [PR_ID]
```

### Issue: PR Not Found
- Verify PR ID is correct
- Check repository configuration
- Ensure PAT has read permissions

### Issue: Context Overflow
- Use helper scripts instead of MCP tools
- Filter results to essentials only
- Return summaries not raw JSON

## Future Enhancements

Planned additions:
- Work item helper functions
- Pipeline operation helpers
- Repository statistics
- Build validation queries
- Wiki management

---

**Created**: 2025-11-09
**Version**: 1.0
**Maintainer**: AI Agent Team
**Status**: Production Ready
