#!/usr/bin/env python3
"""
Example: Context-efficient MCP workflow
Demonstrates 98.7% token reduction vs traditional approach
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.tool_discovery import (
    discover_tools,
    search_tools,
    load_tool_definition,
    discovery_agent,
)


async def example_1_progressive_discovery():
    """Example 1: Progressive tool discovery"""
    print("=" * 60)
    print("Example 1: Progressive Tool Discovery")
    print("=" * 60)
    
    # Step 1: Discover available servers (minimal context)
    print("\n1. Discovering servers...")
    servers = discover_tools("./mcp_tools")
    print(f"   Found servers: {servers}")
    print(f"   Context cost: ~50 tokens")
    
    # Step 2: Search for relevant tools (still minimal)
    print("\n2. Searching for 'lead' tools...")
    tools = search_tools("./mcp_tools", "lead", detail="name_only")
    print(f"   Found {len(tools)} tools")
    for tool in tools:
        print(f"   - {tool['name']}")
    print(f"   Context cost: ~200 tokens")
    
    # Step 3: Load full definition only when needed
    print("\n3. Loading full definition for selected tool...")
    if tools:
        full_def = load_tool_definition(tools[0]["path"], detail="full")
        print(f"   Loaded: {full_def['signature']}")
        print(f"   Context cost: ~500 tokens")
    
    print(f"\n✓ Total context: ~750 tokens")
    print(f"  vs ~150,000 tokens loading all tools upfront")
    print(f"  Reduction: 99.5%")


async def example_2_context_efficient_workflow():
    """Example 2: Context-efficient data processing"""
    print("\n" + "=" * 60)
    print("Example 2: Context-Efficient Data Processing")
    print("=" * 60)
    
    # Simulated: Process large dataset
    print("\n❌ Traditional approach (context inefficient):")
    print("   1. Load 10,000 row spreadsheet → 50K tokens in context")
    print("   2. Model filters for 'pending' status")
    print("   3. Model copies filtered data to tool call")
    print("   Total context: ~100K tokens")
    
    print("\n✅ Code execution approach (context efficient):")
    print("   1. Load 10,000 rows in execution environment (0 tokens)")
    print("   2. Filter in code: pending = [r for r in rows if r['Status'] == 'pending']")
    print("   3. Return only: 'Found 47 pending orders' + 5 sample rows")
    print("   Total context: ~500 tokens")
    
    print(f"\n✓ Token reduction: 99.5%")


async def example_3_multi_agent():
    """Example 3: Multi-agent workflow"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Agent Workflow")
    print("=" * 60)
    
    task = "Export pending leads to spreadsheet"
    
    print(f"\nTask: {task}")
    print("\nAgent 1 (Discovery): Identifying relevant tools...")
    relevant_tools = await discovery_agent("./mcp_tools", task)
    print(f"   Found {len(relevant_tools)} relevant tools")
    print(f"   Context: Task description + tool names (~100 tokens)")
    
    print("\nAgent 2 (Execution): Writing context-efficient code...")
    print("   Loading only required tool definitions")
    print("   Generating code that filters data before returning")
    print(f"   Context: Task + {len(relevant_tools)} tool definitions (~1K tokens)")
    
    print("\nAgent 3 (Filtering): Processing results...")
    print("   Raw results: 1,234 leads (would be 50K tokens)")
    print("   Filtered output: 'Exported 1,234 leads to sheet_abc123'")
    print("   Context: Summary only (~20 tokens)")
    
    print(f"\n✓ Total context across all agents: ~1,200 tokens")
    print(f"  vs ~150K+ tokens in traditional approach")
    print(f"  Reduction: 99.2%")


async def example_4_skill_persistence():
    """Example 4: Saving reusable skills"""
    print("\n" + "=" * 60)
    print("Example 4: Skill Persistence")
    print("=" * 60)
    
    print("\n1. Agent develops working code for 'enrich leads from sheet'")
    print("2. Code is tested and proven effective")
    print("3. Agent saves as reusable skill:")
    
    skill_code = '''
# ./skills/enrich_leads.py
async def enrich_leads_from_sheet(sheet_id: str):
    """Enrich Salesforce leads from Google Sheets data."""
    contacts = await gdrive.get_sheet(sheet_id)
    leads = await sf.query("SELECT Id, Email FROM Lead")
    
    email_to_lead = {lead["Email"]: lead["Id"] for lead in leads}
    
    updated = 0
    for contact in contacts:
        if lead_id := email_to_lead.get(contact["email"]):
            await sf.update_record("Lead", lead_id, {
                "Phone": contact.get("phone"),
                "Company": contact.get("company"),
            })
            updated += 1
    
    return {"updated": updated}
'''
    print(skill_code)
    
    print("\n4. Future executions import and reuse:")
    print("   from skills.enrich_leads import enrich_leads_from_sheet")
    print("   result = await enrich_leads_from_sheet('abc123')")
    
    print("\n✓ Builds library of proven, context-efficient workflows")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MCP Code Execution: Context Efficiency Examples")
    print("=" * 60)
    
    await example_1_progressive_discovery()
    await example_2_context_efficient_workflow()
    await example_3_multi_agent()
    await example_4_skill_persistence()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("\nKey Benefits:")
    print("  • 98-99% reduction in token usage")
    print("  • Faster response times")
    print("  • Handle 1000+ tools efficiently")
    print("  • Privacy-preserving (data stays in execution env)")
    print("  • Reusable skill library")
    print("\nLearn more: references/patterns.md")


if __name__ == "__main__":
    asyncio.run(main())
