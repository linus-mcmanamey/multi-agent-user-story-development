"""
Azure DevOps Wiki REST API Client

Provides a Python wrapper for Azure DevOps Wiki REST API operations including:
- Creating and updating wiki pages
- Retrieving page content and metadata
- Managing wiki page hierarchy
- Handling authentication and error handling

Usage:
    from ado_wiki_client import WikiClient

    client = WikiClient.from_env()
    response = client.create_or_update_page(
        path="/project/docs/readme",
        content="# Hello World\\n\\nThis is my wiki page",
        comment="Created documentation"
    )
    print(response["remoteUrl"])

API Documentation:
    https://learn.microsoft.com/en-us/rest/api/azure/devops/wiki/pages
"""

import os
import sys
import json
import time
import base64
from typing import Dict, Optional, List, Any
from urllib.parse import quote
import requests

class WikiAPIError(Exception):
    """Raised when Azure DevOps Wiki API returns an error"""
    pass

class WikiClient:
    """Azure DevOps Wiki REST API client"""

    API_VERSION = "7.1"
    BASE_URL_TEMPLATE = "https://dev.azure.com/{organization}/{project}/_apis"
    WIKI_URL_TEMPLATE = "https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wiki_id}"
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2
    RATE_LIMIT_PER_MINUTE = 200

    def __init__(self, organization: str, project: str, wiki_id: str, pat: str):
        self.organization = organization
        self.project = project
        self.wiki_id = wiki_id
        self.pat = pat
        self.base_url = self.BASE_URL_TEMPLATE.format(organization=organization, project=project)
        self.wiki_base_url = self.WIKI_URL_TEMPLATE.format(organization=organization, project=project, wiki_id=wiki_id)
        self.session = requests.Session()
        self.session.headers.update(self._get_auth_headers())
        self.request_count = 0
        self.request_window_start = time.time()

    @classmethod
    def from_env(cls, wiki_id: str = "Program-Unify.wiki") -> "WikiClient":
        organization = os.getenv("AZURE_DEVOPS_ORGANIZATION")
        project = os.getenv("AZURE_DEVOPS_PROJECT")
        pat = os.getenv("AZURE_DEVOPS_PAT")
        if not all([organization, project, pat]):
            raise ValueError("Missing required environment variables: AZURE_DEVOPS_ORGANIZATION, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT")
        return cls(organization, project, wiki_id, pat)

    def _get_auth_headers(self) -> Dict[str, str]:
        auth_string = f":{self.pat}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}", "Content-Type": "application/json"}

    def _rate_limit_check(self) -> None:
        elapsed = time.time() - self.request_window_start
        if elapsed >= 60:
            self.request_count = 0
            self.request_window_start = time.time()
        elif self.request_count >= self.RATE_LIMIT_PER_MINUTE - 10:
            sleep_time = 60 - elapsed
            print(f"[WikiClient] Approaching rate limit ({self.request_count}/200 requests). Sleeping {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            self.request_count = 0
            self.request_window_start = time.time()

    def _make_request(self, method: str, url: str, headers: Optional[Dict] = None, json_data: Optional[Dict] = None, retry: int = 0) -> requests.Response:
        self._rate_limit_check()
        self.request_count += 1
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=json_data)
            elif method == "PATCH":
                response = self.session.patch(url, headers=headers, json=json_data)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            if response.status_code >= 400:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("message", error_detail)
                except:
                    pass
                if retry < self.MAX_RETRIES:
                    delay = self.RETRY_DELAY_SECONDS * (2 ** retry)
                    print(f"[WikiClient] Request failed with {response.status_code}. Retrying in {delay}s... (Attempt {retry + 1}/{self.MAX_RETRIES})")
                    time.sleep(delay)
                    return self._make_request(method, url, headers, json_data, retry + 1)
                raise WikiAPIError(f"API request failed with status {response.status_code}: {error_detail}")
            return response
        except requests.exceptions.RequestException as e:
            if retry < self.MAX_RETRIES:
                delay = self.RETRY_DELAY_SECONDS * (2 ** retry)
                print(f"[WikiClient] Request exception: {e}. Retrying in {delay}s... (Attempt {retry + 1}/{self.MAX_RETRIES})")
                time.sleep(delay)
                return self._make_request(method, url, headers, json_data, retry + 1)
            raise WikiAPIError(f"Request failed after {self.MAX_RETRIES} attempts: {e}")

    def create_or_update_page(self, path: str, content: str, comment: Optional[str] = None) -> Dict[str, Any]:
        if not path.startswith("/"):
            path = "/" + path
        encoded_path = quote(path, safe="/")
        url = f"{self.base_url}/wiki/wikis/{self.wiki_id}/pages?path={encoded_path}&api-version={self.API_VERSION}"
        payload = {"content": content}
        if comment:
            payload["comment"] = comment
        response = self._make_request("PUT", url, json_data=payload)
        result = response.json()
        result["eTag"] = response.headers.get("ETag", "")
        return result

    def get_page(self, path: str, include_content: bool = True) -> Dict[str, Any]:
        if not path.startswith("/"):
            path = "/" + path
        encoded_path = quote(path, safe="/")
        url = f"{self.base_url}/wiki/wikis/{self.wiki_id}/pages?path={encoded_path}&api-version={self.API_VERSION}"
        if include_content:
            url += "&includeContent=true"
        response = self._make_request("GET", url)
        result = response.json()
        result["eTag"] = response.headers.get("ETag", "")
        return result

    def update_page(self, path: str, content: str, version: str, comment: Optional[str] = None) -> Dict[str, Any]:
        if not path.startswith("/"):
            path = "/" + path
        encoded_path = quote(path, safe="/")
        url = f"{self.base_url}/wiki/wikis/{self.wiki_id}/pages?path={encoded_path}&api-version={self.API_VERSION}"
        headers = {"If-Match": version}
        payload = {"content": content}
        if comment:
            payload["comment"] = comment
        response = self._make_request("PUT", url, headers=headers, json_data=payload)
        result = response.json()
        result["eTag"] = response.headers.get("ETag", "")
        return result

    def delete_page(self, path: str, comment: Optional[str] = None) -> None:
        if not path.startswith("/"):
            path = "/" + path
        encoded_path = quote(path, safe="/")
        url = f"{self.base_url}/wiki/wikis/{self.wiki_id}/pages?path={encoded_path}&api-version={self.API_VERSION}"
        if comment:
            url += f"&comment={quote(comment)}"
        self._make_request("DELETE", url)

    def list_pages(self, path: Optional[str] = None, recursive: bool = True) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/wiki/wikis/{self.wiki_id}/pages?api-version={self.API_VERSION}"
        if path:
            if not path.startswith("/"):
                path = "/" + path
            encoded_path = quote(path, safe="/")
            url += f"&path={encoded_path}"
        url += f"&recursionLevel={'full' if recursive else 'oneLevel'}"
        response = self._make_request("GET", url)
        result = response.json()
        return result.get("value", [])

    def page_exists(self, path: str) -> bool:
        try:
            self.get_page(path, include_content=False)
            return True
        except WikiAPIError as e:
            if "404" in str(e):
                return False
            raise

    def get_wiki_url(self, path: str, page_id: Optional[int] = None) -> str:
        if page_id:
            return f"{self.wiki_base_url}/{page_id}"
        if not path.startswith("/"):
            path = "/" + path
        encoded_path = quote(path, safe="/")
        return f"{self.wiki_base_url}/{encoded_path}"

    def get_api_stats(self) -> Dict[str, Any]:
        return {"requests_made": self.request_count, "window_elapsed_seconds": time.time() - self.request_window_start, "rate_limit_per_minute": self.RATE_LIMIT_PER_MINUTE}

def main():
    if len(sys.argv) < 3:
        print("Usage: python ado_wiki_client.py <command> <args>")
        print("\nCommands:")
        print("  create <path> <content> [comment]  - Create or update wiki page")
        print("  get <path>                          - Get wiki page content")
        print("  delete <path> [comment]             - Delete wiki page")
        print("  list [path]                         - List wiki pages")
        print("  exists <path>                       - Check if page exists")
        print("\nEnvironment variables required:")
        print("  AZURE_DEVOPS_ORGANIZATION")
        print("  AZURE_DEVOPS_PROJECT")
        print("  AZURE_DEVOPS_PAT")
        sys.exit(1)
    command = sys.argv[1]
    try:
        client = WikiClient.from_env()
        if command == "create":
            path = sys.argv[2]
            content = sys.argv[3]
            comment = sys.argv[4] if len(sys.argv) > 4 else "Created via ado_wiki_client"
            result = client.create_or_update_page(path, content, comment)
            print(f"✅ Page created/updated: {result['remoteUrl']}")
            print(f"   Page ID: {result['id']}")
            print(f"   Version: {result['eTag']}")
        elif command == "get":
            path = sys.argv[2]
            result = client.get_page(path)
            print(f"📄 Page: {result['path']}")
            print(f"   URL: {result['remoteUrl']}")
            print(f"   Version: {result['eTag']}")
            print(f"\nContent:\n{result.get('content', '(no content)')}")
        elif command == "delete":
            path = sys.argv[2]
            comment = sys.argv[3] if len(sys.argv) > 3 else "Deleted via ado_wiki_client"
            client.delete_page(path, comment)
            print(f"✅ Page deleted: {path}")
        elif command == "list":
            path = sys.argv[2] if len(sys.argv) > 2 else None
            pages = client.list_pages(path)
            print(f"📚 Found {len(pages)} pages:")
            for page in pages:
                print(f"   - {page['path']} (ID: {page['id']})")
        elif command == "exists":
            path = sys.argv[2]
            exists = client.page_exists(path)
            if exists:
                print(f"✅ Page exists: {path}")
            else:
                print(f"❌ Page does not exist: {path}")
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except WikiAPIError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
