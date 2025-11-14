# Azure DevOps Wiki REST API Reference

Complete reference for Azure DevOps Wiki REST API operations used in wiki-auto-documenter skill.

## Base Configuration

**API Version**: 7.1
**Base URL**: `https://dev.azure.com/{organization}/{project}/_apis`
**Wiki URL**: `https://dev.azure.com/{organization}/{project}/_wiki/wikis/{wikiId}`

**Authentication**: Basic Auth with Personal Access Token (PAT)
- Header: `Authorization: Basic {base64(':'+PAT)}`
- Required Scope: `vso.wiki_write`

## Create or Update Page

Creates a new wiki page or updates an existing one.

**Endpoint**: `PUT /wiki/wikis/{wikiIdentifier}/pages`

**URL Parameters**:
- `path` (required): Wiki page path (e.g., `/folder/page`)
- `api-version` (required): `7.1`

**Headers**:
- `Authorization`: Basic auth with PAT
- `Content-Type`: `application/json`
- `If-Match`: ETag version (required for updates, omit for creates)

**Request Body**:
```json
{
  "content": "# Page Title\n\nMarkdown content here..."
}
```

**Response**: 201 Created or 200 OK
```json
{
  "id": 123,
  "path": "/folder/page",
  "remoteUrl": "https://dev.azure.com/org/project/_wiki/wikis/wiki/123/page",
  "content": "# Page Title...",
  "gitItemPath": "/.attachments/page.md",
  "isParentPage": false,
  "order": 0
}
```

**Response Headers**:
- `ETag`: Version identifier (needed for subsequent updates)

## Get Page

Retrieves a wiki page and its content.

**Endpoint**: `GET /wiki/wikis/{wikiIdentifier}/pages`

**URL Parameters**:
- `path` (required): Wiki page path
- `includeContent` (optional): `true` to include content (default: false)
- `api-version` (required): `7.1`

**Response**: 200 OK
```json
{
  "id": 123,
  "path": "/folder/page",
  "remoteUrl": "https://...",
  "content": "...",
  "gitItemPath": "..."
}
```

**Response Headers**:
- `ETag`: Current version identifier

## Update Existing Page

Updates an existing page with version check.

**Process**:
1. GET page to obtain current ETag
2. PUT with `If-Match: {ETag}` header

**Conflict Handling**:
If ETag doesn't match (someone else edited), API returns 412 Precondition Failed.
- Fetch latest version
- Retry with new ETag

## Delete Page

Removes a wiki page.

**Endpoint**: `DELETE /wiki/wikis/{wikiIdentifier}/pages`

**URL Parameters**:
- `path` (required): Wiki page path
- `comment` (optional): Deletion comment
- `api-version` (required): `7.1`

**Response**: 200 OK

## List Pages

Lists all pages in a wiki or under a specific path.

**Endpoint**: `GET /wiki/wikis/{wikiIdentifier}/pages`

**URL Parameters**:
- `path` (optional): Parent path to list from
- `recursionLevel` (optional): `oneLevel` or `full` (default: oneLevel)
- `api-version` (required): `7.1`

**Response**: 200 OK
```json
{
  "value": [
    {
      "id": 123,
      "path": "/folder/page1"
    },
    {
      "id": 124,
      "path": "/folder/page2"
    }
  ]
}
```

## Page Hierarchy Rules

### Path Requirements
- Must start with `/`
- Use forward slashes for hierarchy: `/parent/child/page`
- No file extensions (`.md` added automatically)
- URL encode special characters

### Parent-Child Relationships
- Parent pages must exist before creating children
- Creating `/parent/child/page` requires `/parent` and `/parent/child` to exist
- Use nested PUT calls to create hierarchy

### Page Ordering
Pages within a directory are ordered by `order` field (0-based).

## Rate Limiting

**Limits**:
- 200 requests per minute per PAT
- Exceeding limit: 429 Too Many Requests

**Best Practices**:
- Track request count per minute
- Implement exponential backoff
- Batch operations when possible

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | OK - Page updated | Success |
| 201 | Created - New page | Success |
| 400 | Bad Request | Check path format and content |
| 401 | Unauthorized | Verify PAT and authentication |
| 403 | Forbidden | Check wiki write permissions |
| 404 | Not Found | Page or wiki doesn't exist |
| 409 | Conflict | Path already exists (for creates) |
| 412 | Precondition Failed | ETag mismatch, refetch and retry |
| 429 | Too Many Requests | Rate limit hit, wait 60s |
| 500 | Internal Server Error | Retry with exponential backoff |

## Example Workflows

### Create Hierarchical Structure

```python
# 1. Create parent directory index
wiki.create_or_update_page("/project", "# Project\n...")

# 2. Create subdirectory index
wiki.create_or_update_page("/project/docs", "# Documentation\n...")

# 3. Create file page
wiki.create_or_update_page("/project/docs/readme", "# README\n...")
```

### Update Existing Page

```python
# 1. Get current version
page = wiki.get_page("/project/docs/readme")
current_etag = page["eTag"]

# 2. Update with version check
wiki.update_page(
    "/project/docs/readme",
    new_content,
    version=current_etag,
    comment="Updated documentation"
)
```

### Bulk Page Creation with Rate Limiting

```python
request_count = 0
request_window_start = time.time()

for page_path, content in pages.items():
    # Rate limiting
    if request_count >= 190:
        elapsed = time.time() - request_window_start
        if elapsed < 60:
            time.sleep(60 - elapsed)
        request_count = 0
        request_window_start = time.time()

    # Create page
    wiki.create_or_update_page(page_path, content)
    request_count += 1
```

## Wiki URL Structure

**Page URL Format**:
```
https://dev.azure.com/{org}/{project}/_wiki/wikis/{wikiId}/{pageId}/{pageName}
```

**Example**:
```
https://dev.azure.com/emstas/Program%20Unify/_wiki/wikis/Program-Unify.wiki/274/unify_2_1_dm_synapse_env_d10
```

Components:
- Organization: `emstas`
- Project: `Program Unify`
- Wiki ID: `Program-Unify.wiki`
- Page ID: `274`
- Page Name: `unify_2_1_dm_synapse_env_d10`

## Markdown Support

Azure DevOps Wiki supports GitHub Flavored Markdown (GFM) with extensions:

**Supported Elements**:
- Headers (H1-H6)
- Bold, italic, strikethrough
- Lists (ordered, unordered, checkboxes)
- Code blocks with syntax highlighting
- Tables
- Links (absolute and relative)
- Images
- Blockquotes
- Horizontal rules

**Relative Links**:
- Same directory: `[Link](./page)`
- Parent directory: `[Link](../page)`
- Absolute wiki path: `[Link](/folder/page)`

**Code Syntax Highlighting**:
```python
def example():
    return "hello"
```

Supported languages: python, javascript, bash, sql, csharp, java, etc.

## Best Practices

### 1. Content Organization
- Use clear hierarchical structure
- Create index pages for directories
- Add breadcrumb navigation
- Include cross-references

### 2. Error Handling
- Implement retry logic (3 attempts)
- Use exponential backoff
- Catch and log specific error codes
- Provide detailed error messages

### 3. Performance
- Create pages in dependency order (parent → child)
- Use batch operations when available
- Monitor rate limits
- Cache ETag values for updates

### 4. Documentation Quality
- Use descriptive page titles
- Include metadata (date, author, version)
- Add table of contents for long pages
- Link to source code

## Troubleshooting

### Issue: 412 Precondition Failed
**Cause**: ETag mismatch (page was modified)
**Solution**: Fetch page again to get new ETag, then retry

### Issue: 404 Not Found on Child Page
**Cause**: Parent page doesn't exist
**Solution**: Create parent pages first

### Issue: 429 Rate Limit
**Cause**: Exceeded 200 requests/minute
**Solution**: Wait 60 seconds, then continue

### Issue: Special Characters in Path
**Cause**: Unencoded special characters
**Solution**: URL encode path components

---

**API Documentation**: https://learn.microsoft.com/en-us/rest/api/azure/devops/wiki/
**Last Updated**: 2025-11-12
