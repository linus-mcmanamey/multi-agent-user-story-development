#!/usr/bin/env python3
"""Azure DevOps PR helper using REST API."""
import os
import json
import base64
import requests
from typing import Any


class ADOHelper:
    """Azure DevOps helper for PR operations."""

    def __init__(self):
        self.pat = os.getenv("AZURE_DEVOPS_PAT")
        self.org = os.getenv("AZURE_DEVOPS_ORGANIZATION", "emstas")
        self.project = os.getenv("AZURE_DEVOPS_PROJECT", "Program Unify")
        if not self.pat:
            raise ValueError("AZURE_DEVOPS_PAT environment variable not set")
        auth_str = f":{self.pat}"
        self.auth_header = f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        self.base_url = f"https://dev.azure.com/{self.org}/{self.project}/_apis"

    def _get(self, endpoint: str, api_version: str = "7.1") -> dict[str, Any]:
        """Make GET request to Azure DevOps API."""
        url = f"{self.base_url}/{endpoint}?api-version={api_version}"
        headers = {"Authorization": self.auth_header, "Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict[str, Any], api_version: str = "7.1") -> dict[str, Any]:
        """Make POST request to Azure DevOps API."""
        url = f"{self.base_url}/{endpoint}?api-version={api_version}"
        headers = {"Authorization": self.auth_header, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_pr(self, pr_id: int) -> dict[str, Any]:
        """Get pull request details."""
        return self._get(f"git/pullrequests/{pr_id}")

    def get_pr_conflicts(self, pr_id: int) -> dict[str, Any]:
        """Get pull request merge conflicts."""
        pr = self.get_pr(pr_id)
        repo_id = pr["repository"]["id"]
        return self._get(f"git/repositories/{repo_id}/pullRequests/{pr_id}/conflicts")

    def get_pr_threads(self, pr_id: int) -> dict[str, Any]:
        """Get pull request discussion threads."""
        pr = self.get_pr(pr_id)
        repo_id = pr["repository"]["id"]
        return self._get(f"git/repositories/{repo_id}/pullRequests/{pr_id}/threads")

    def get_pr_commits(self, pr_id: int) -> dict[str, Any]:
        """Get pull request commits."""
        pr = self.get_pr(pr_id)
        repo_id = pr["repository"]["id"]
        return self._get(f"git/repositories/{repo_id}/pullRequests/{pr_id}/commits")

    def get_repository(self, repo_name: str) -> dict[str, Any]:
        """Get repository details by name."""
        return self._get(f"git/repositories/{repo_name}")

    def create_pr(self, repo_name: str, source_branch: str, target_branch: str, title: str, description: str = "") -> dict[str, Any]:
        """Create a pull request."""
        repo = self.get_repository(repo_name)
        repo_id = repo["id"]
        pr_data = {
            "sourceRefName": f"refs/heads/{source_branch}" if not source_branch.startswith("refs/") else source_branch,
            "targetRefName": f"refs/heads/{target_branch}" if not target_branch.startswith("refs/") else target_branch,
            "title": title,
            "description": description
        }
        return self._post(f"git/repositories/{repo_id}/pullrequests", pr_data)


def main():
    """Main entry point."""
    import sys
    if len(sys.argv) < 2:
        print("Usage: ado_pr_helper.py <pr_id>")
        sys.exit(1)
    pr_id = int(sys.argv[1])
    ado = ADOHelper()
    pr = ado.get_pr(pr_id)
    print(json.dumps({
        "title": pr["title"],
        "description": pr.get("description", ""),
        "source_branch": pr["sourceRefName"],
        "target_branch": pr["targetRefName"],
        "status": pr["status"],
        "merge_status": pr["mergeStatus"],
        "created_by": pr["createdBy"]["displayName"],
        "creation_date": pr["creationDate"],
        "url": pr["url"]
    }, indent=2))
    conflicts = ado.get_pr_conflicts(pr_id)
    if conflicts.get("value"):
        print(f"\n⚠️  Merge Conflicts Found: {len(conflicts['value'])} conflicts")
        for conflict in conflicts["value"]:
            print(f"  - {conflict['conflictPath']}: {conflict['conflictType']}")
    else:
        print("\n✓ No merge conflicts detected")


if __name__ == "__main__":
    main()
