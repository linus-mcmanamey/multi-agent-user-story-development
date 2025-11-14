# Context-Efficient MCP Patterns

Common patterns for using MCP tools with minimal context pollution.

## Pattern 1: Filter Before Return

Process large datasets in execution environment, only return summaries.

```python
# ❌ Context Inefficient (10K rows in context)
all_rows = await gdrive.get_sheet("abc123")
# Model processes all 10K rows to find pending...

# ✅ Context Efficient (only summary in context)
all_rows = await gdrive.get_sheet("abc123")
pending = [r for r in all_rows if r["Status"] == "pending"]
print(f"Found {len(pending)} pending orders")
print(pending[:5])  # Show first 5 as sample
```

**Token savings**: 10,000 rows → 5 rows + summary = ~99% reduction

## Pattern 2: Aggregation Without Bloat

Compute aggregates in code, return only results.

```python
# ✅ Context Efficient
sales_data = await salesforce.query("SELECT * FROM Sales WHERE Year = 2024")
total_revenue = sum(row["Amount"] for row in sales_data)
avg_deal_size = total_revenue / len(sales_data)

print(f"2024 Revenue: ${total_revenue:,.2f}")
print(f"Avg Deal: ${avg_deal_size:,.2f}")
print(f"Total Deals: {len(sales_data)}")
# Only 3 lines in context vs 1000+ rows
```

## Pattern 3: Cross-Source Joins

Join data from multiple sources without context overhead.

```python
# ✅ Context Efficient
leads = await salesforce.query("SELECT Id, Email FROM Lead")
email_to_lead_id = {lead["Email"]: lead["Id"] for lead in leads}

contacts = await gdrive.get_sheet("contacts_sheet")
matches = [
    c for c in contacts 
    if c["email"] in email_to_lead_id
]

print(f"Found {len(matches)} contacts with leads")
# Only summary enters context, not full datasets
```

## Pattern 4: Polling Loops

Wait for conditions without repeated context pollution.

```python
# ✅ Context Efficient
import asyncio

deployment_complete = False
attempts = 0

while not deployment_complete and attempts < 20:
    messages = await slack.get_channel_history("deployments")
    deployment_complete = any(
        "deployment complete" in msg["text"].lower() 
        for msg in messages
    )
    
    if not deployment_complete:
        await asyncio.sleep(5)
        attempts += 1

print(f"Deployment {'completed' if deployment_complete else 'timed out'}")
# Only final status in context, not 20 polling attempts
```

## Pattern 5: Batch Operations

Process multiple items without flooding context.

```python
# ✅ Context Efficient
emails = await gmail.search("from:customers label:unread")

success_count = 0
error_count = 0

for email in emails:
    try:
        await salesforce.create_lead({
            "Email": email["from"],
            "Description": email["subject"]
        })
        success_count += 1
    except Exception as e:
        error_count += 1

print(f"Created {success_count} leads, {error_count} errors")
# Summary only, not 100+ email bodies
```

## Pattern 6: Progressive Disclosure

Load tool definitions only when needed.

```python
from scripts.tool_discovery import discover_tools, load_tool_definition

# Step 1: List servers (minimal context)
servers = discover_tools("./mcp_tools")  # ["gdrive", "salesforce", "slack"]

# Step 2: Load only relevant server tools (still minimal)
gdrive_tools = list_server_tools("./mcp_tools", "gdrive")  # ["get_document", "get_sheet", ...]

# Step 3: Load full definition only when about to use
if needs_document_access:
    tool_def = load_tool_definition("./mcp_tools/gdrive/get_document.py", detail="full")
    # Now execute using the tool
```

**Token savings**: 150K tokens (all tools) → 2K tokens (only used tools) = 98.7% reduction

## Pattern 7: Multi-Agent Decomposition

Split complex tasks across specialized agents with minimal context overlap.

```python
from scripts.tool_discovery import discovery_agent, execution_agent, filtering_agent

# Agent 1: Discovery (minimal context - just task + tool names)
task = "Find all high-value leads from last month and add notes"
relevant_tools = await discovery_agent("./mcp_tools", task)
# Returns: ["./mcp_tools/salesforce/query.py", "./mcp_tools/salesforce/update_record.py"]

# Agent 2: Execution (only loads needed tool definitions)
code = await execution_agent(relevant_tools, task)
result = exec(code)  # Runs in sandbox

# Agent 3: Filtering (processes results, returns summary)
summary = await filtering_agent(result, task)
# Returns: {"updated": 47, "errors": 2}
```

**Key insight**: Each agent sees only its slice of context, enabling parallelization and reducing total tokens.

## Pattern 8: Skill Persistence

Save proven workflows as reusable functions.

```python
# In ./skills/enrich_leads.py
"""Enrich Salesforce leads from Google Sheets data."""

import mcp_tools.salesforce as sf
import mcp_tools.google_drive as gdrive


async def enrich_leads_from_sheet(sheet_id: str):
    """Load contacts from sheet and update matching leads."""
    contacts = await gdrive.get_sheet(sheet_id)
    leads = await sf.query("SELECT Id, Email FROM Lead WHERE Status = 'New'")
    
    email_to_lead = {lead["Email"]: lead["Id"] for lead in leads}
    
    updated = 0
    for contact in contacts:
        if lead_id := email_to_lead.get(contact["email"]):
            await sf.update_record("Lead", lead_id, {
                "Phone": contact.get("phone"),
                "Company": contact.get("company"),
            })
            updated += 1
    
    return {"updated": updated, "total_contacts": len(contacts)}


# Later, in any agent execution:
from skills.enrich_leads import enrich_leads_from_sheet

result = await enrich_leads_from_sheet("abc123")
print(f"Enriched {result['updated']} leads")
```

## Pattern 9: Privacy-Preserving Operations

Keep sensitive data in execution environment.

```python
# ✅ PII never enters model context
customer_data = await gdrive.get_sheet("customer_pii")

for row in customer_data:
    # PII flows directly from gdrive to salesforce
    # Never logged or returned to model context
    await salesforce.update_record("Contact", row["salesforce_id"], {
        "Email": row["email"],
        "Phone": row["phone"],
        "SSN": row["ssn"]  # Stays in execution environment
    })

print(f"Updated {len(customer_data)} contacts")
# Only count enters context, not actual PII
```

## Pattern 10: Error Handling Without Noise

Handle errors in code, only report summary.

```python
# ✅ Context Efficient
results = {"success": [], "errors": []}

for doc_id in document_ids:
    try:
        doc = await gdrive.get_document(doc_id)
        await salesforce.attach_file(lead_id, doc["content"])
        results["success"].append(doc_id)
    except Exception as e:
        results["errors"].append({"id": doc_id, "error": str(e)[:50]})

print(f"Attached {len(results['success'])} docs")
if results["errors"]:
    print(f"{len(results['errors'])} errors:")
    for err in results["errors"][:3]:  # Show first 3 only
        print(f"  - {err['id']}: {err['error']}")
```

## Choosing the Right Pattern

| Use Case | Pattern | Token Reduction |
|----------|---------|-----------------|
| Large datasets | Filter Before Return | 90-99% |
| Analytics | Aggregation | 95-99% |
| Multi-source data | Cross-Source Joins | 90-95% |
| Waiting for events | Polling Loops | 95-99% |
| Bulk operations | Batch Operations | 90-98% |
| Tool discovery | Progressive Disclosure | 98% |
| Complex workflows | Multi-Agent | 85-95% |
| Proven workflows | Skill Persistence | N/A (reusability) |
| Sensitive data | Privacy-Preserving | 99% (PII) |
| Reliability | Error Handling | 80-90% |

## Anti-Patterns to Avoid

### ❌ Loading All Tools Upfront
```python
# Bad: 150K tokens
from mcp_tools import *  # Loads everything
```

### ❌ Passing Large Results Through Model
```python
# Bad: Transcript flows through context twice
transcript = await gdrive.get_document("abc123")
# Model sees full transcript in context
await salesforce.update(lead_id, {"Notes": transcript})
# Model writes full transcript again in tool call
```

### ❌ Logging Everything
```python
# Bad: Every iteration enters context
for i in range(1000):
    result = await process_item(items[i])
    print(f"Processed item {i}: {result}")  # 1000 lines in context
```
