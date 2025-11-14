def business_analyst_prompt(user_story: str, file_name: str, read_layer: str, write_layer: str) -> str:
    """Generate efficient business analyst prompt with clear structure and actionable tasks."""
    datasource = "cms" if "cms" in file_name.lower() else "fvms" if "fvms" in file_name.lower() else "nicherms"
    return f"""# Azure DevOps User Story Analysis & Implementation Planning

@business-analyst
LOCATION: .claude/agents/business-analyst.md
## CONTEXT
- **User Story ID**: {user_story} (Project: "Program Unify")
- **Target File**: `{file_name}.py`
- **Data Flow**: {read_layer} to {write_layer}
- **Data Source**: {datasource.upper()}

## PRIMARY OBJECTIVE
Create comprehensive technical specifications for PySpark engineer to implement data pipeline transformation.

## � CRITICAL EXECUTION INSTRUCTIONS �
**AUTOMATED NON-INTERACTIVE WORKFLOW - NO USER PRESENT**

YOU MUST:
1. **IMMEDIATELY USE ALL REQUIRED TOOLS** - Do NOT ask "Should I proceed?" or "May I use these tools?"
2. **EXECUTE EVERY PHASE WITHOUT STOPPING** - This workflow has no human to approve actions
3. **NEVER WAIT FOR CONFIRMATION** - There is no user to respond to questions
4. **IF A TOOL IS NEEDED, USE IT IMMEDIATELY** - Permission is pre-granted for all MCP tools
5. **DOCUMENT EVERYTHING AS SPECIFIED** - Follow the output structure exactly
6. **USE ALL OR ANY OF THE ADO MCP Tools** to read the parent story and all comments that will create context for the current work item
7. **USE THE WRITE TOOL TO SAVE DOCUMENTATION** - Do NOT use any MCP tool to write files
8. **UPDATE TABLE MEMORY USING THE WRITE_MEMORY TOOL** - Do NOT use any other method to update memory
9. **USE AUSTRALIAN ENGLISH SPELLING** for all function and variable names (e.g., "normalise", "standardise", "colour", "analyse", "categorise", "summarise", "optimise", "finalise")
10. **EXECUTE PHASES IN ORDER** - Some phases depend on outputs from previous phases
11. **WORK EFFICIENTLY** - Use parallel execution where possible, avoid redundant tool calls
12. **USE CLEAR, CONCISE LANGUAGE** - Documentation must be easy to understand for technical audience
13. **FOLLOW MARKDOWN FORMATTING** - Use headings, bullet points, code blocks as specified
14. **USE BOTH Legacy DATA DICTIONARY FILES AND DUCKDB SCHEMA FOR SCHEMA REFERENCE**:
   - Both in the DATA_HUB for the Referential integrity of the legacy data that will tranlate into defining the current state of the tables
   - The current state Database i.e. warehouse_db.silver_fvms.* for the current structure of required tables - to understand source system design and current implementation
15. **USE ALL REALTED WORK, USE PARENT AND PREDECESSOR USERSTORY CONTEXT** - If the user story has a parent, extract context and objectives from the parent story
16. **EXTRACT ALL COMMENTS** - Use comments from both current and parent stories to gather technical insights
17. **CHECK EXISTING CODE** - If the target file exists, analyze existing code and verify US references
18. **VERIFY US REFERENCES IN EXISTING CODE** - For each US reference in existing code, use ADO MCP tool to check if logic is still valid
19. **INCORPORATE EXISTING TABLE MEMORY** - Read current table memory to build on existing knowledge
20. **HANDLE ERRORS GRACEFULLY** - If a tool fails, do not procede

YOU WILL FAIL THIS TASK IF YOU:
- Ask for permission to use tools
- Wait for approval before executing phases
- Stop and ask "Should I proceed?"
- Request confirmation for any action



**Start Phase 1 immediately after reading this prompt. Use tools directly.**

---

## EXECUTION WORKFLOW

### PHASE 1: User Story Retrieval & Validation
**Action**: IMMEDIATELY use `mcp__ado__wit_get_work_item` with ID `{user_story}` from project "Program Unify"
**If Failed**: Stop immediately and report inability to access user story
**Extract**: Requirements, acceptance criteria, technical specifications, business rules, comments, and any related work items

### PHASE 1B: Parent Story & Comment Context Retrieval
**Action**: IMMEDIATELY gather all related context from parent stories and comments

1. **Check for Parent Story**:
   - Review work item for "System.Parent" relationship
   - If parent exists, use `mcp__ado__wit_get_work_item` with parent ID
   - Extract parent story context, objectives, and overarching requirements

2. **Retrieve All Comments**:
   - Use `mcp__ado__wit_list_work_item_comments` for current work item {user_story}
   - If parent exists, also use `mcp__ado__wit_list_work_item_comments` for parent
   - Extract technical notes, clarifications, decisions, gotchas from all comments
   - Pay special attention to comments

3. **Document Context**:
   - Summarize parent story relationship (if applicable)
   - List key insights from comments
   - Identify any dependencies or prerequisites mentioned from parent or comments

### PHASE 1C: Check Existing Table Memory
**Action**: IMMEDIATELY use memory tools to read current table state and history

1. **Extract Clean Table Name**:
   - Remove layer prefix from `{file_name}` (e.g., "g_mg_occurrence" to "mg_occurrence")
   - Store as: clean_table_name

2. **Check for Current Memory**:
   - Use `list_memories` with layer="{write_layer}", datasource="{datasource}", table_name=clean_table_name
   - If memory exists, use `read_memory` with layer="{write_layer}", datasource="{datasource}", table_name=clean_table_name
   - **This returns the CURRENT consolidated state** (not per-user-story)

3. **Review Current Memory Content**:
   - **Changelog**: List of user stories that previously modified this table
   - **Summary**: Current understanding of table purpose
   - **Key Requirements**: Consolidated requirements from all previous work
   - **Data Transformations**: Current transformation logic
   - **Business Rules**: Active business rules
   - **Data Quality Rules**: Current validations
   - **Related Tables**: Cross-references
   - **Gotchas**: Cumulative warnings and special considerations

4. **Incorporate Historical Context**:
   - Build on existing knowledge (don't duplicate)
   - Identify conflicts between new requirements and existing logic
   - Reference changelog to understand evolution of requirements
   - If needed, use `list_memory_history` to review specific past user story snapshots

### PHASE 2: Existing Code Analysis
**Action**: Use `check_existing_python_file` with:
- file_name: `{file_name}`
- layer: `{write_layer}`
- datasource: `{datasource}`

**If File Exists**:
1. Review all user story references (#### US: comments)
2. For each existing US reference, use `mcp__ado__wit_get_work_item` to verify if logic is still valid
3. Document which functions need updating vs. which are obsolete
4. **CRITICAL**: Include in documentation: "The following functions have US references that should be verified before removal: [list functions with US IDs]"

**If File Not Exists**: Document as new implementation

### PHASE 3: Schema Analysis
**Execute in Parallel** (use all tools efficiently):

1. **Data Dictionary Reference** (Read source system documentation):
   - **Action**: Use Read tool to load `.claude/data_dictionary/{datasource}_<table_name>.md` for legacy system schema
   - **Action**: Use mcp-server-motherduck MCP tools to load the current schema from DuckDB
   - Extract table name from user story requirements
   - Read data dictionary files and current schema for all tables mentioned in requirements
   - Extract: column descriptions, data types, business rules, common values, NULL handling
   - **Pattern**: For table "case" from CMS to read `.claude/data_dictionary/cms_case.md`
   - **Pattern**: For table "incident" from FVMS to read `.claude/data_dictionary/fvms_incident.md`
   - If data dictionary file not found, document and proceed with DuckDB schema only

2. **DuckDB Current Schema** (Query actual implemented schemas):
   - Use `mcp__mcp-server-motherduck__query` MCP tool to query schemas directly
   - databases will be found as child of the warehouse_db database
   - Query all tables in read layer:
     ```sql
     SELECT DISTINCT database_name, schema_name, table_name, COUNT(*) as column_count
     FROM data_hub.legacy_schema
     WHERE database_name LIKE '%{read_layer}%'
     GROUP BY database_name, schema_name, table_name
     ORDER BY table_name;
     ```
   - Query all tables in write layer:
     ```sql
     SELECT DISTINCT database_name, schema_name, table_name, COUNT(*) as column_count
     FROM data_hub.legacy_schema
     WHERE database_name LIKE '%{write_layer}%'
     GROUP BY database_name, schema_name, table_name
     ORDER BY table_name;
     ```
   - Get detailed column information for specific tables:
     ```sql
     SELECT column_name, data_type, max_length, precision, scale, is_nullable,
            is_primary_key, is_unique_constraint, foreign_key_name,
            referenced_schema_name, referenced_table_name, referenced_column_name
     FROM data_hub.legacy_schema
     WHERE table_name = 'your_table_name'
     ORDER BY column_name;
     ```

3. **Schema Comparison & Analysis**:
   - **Compare**: Data dictionary (source system design) vs DuckDB schema (current implementation)
   - **Identify**: Schema drift, missing columns, data type mismatches
   - **Document**: Any discrepancies between data dictionary and actual schema
   - **Note**: Data dictionary shows NULL constraints - verify against DuckDB implementation

4. **Related Tables Discovery**:
   - Use `mcp__mcp-server-motherduck__query` to search for columns:
     ```sql
     SELECT database_name, schema_name, table_name, column_name, data_type
     FROM data_hub.legacy_schema
     WHERE column_name LIKE '%column_name%'
     ORDER BY table_name, column_name;
     ```
   - Find related tables based on naming patterns:
     ```sql
     SELECT DISTINCT database_name, schema_name, table_name
     FROM data_hub.legacy_schema
     WHERE table_name LIKE '%base_table_name%'
     ORDER BY table_name;
     ```
   - Cross-reference with data dictionary foreign key references

### PHASE 4: Implementation Plan Creation
Document the following in structured format:

#### 4.1 Requirements Summary
- User story objectives (2-3 sentences)
- Acceptance criteria (bullet points)
- Business rules and validations

#### 4.2 Data Architecture
```
Source: {read_layer}_{datasource}.<table_list>
Target: {write_layer}_<database>.<target_table>
```
Include:
- **Data Dictionary Context**: Business meaning and constraints from source system docs
- **DuckDB Schema**: Current implementation column names and types
- **Column Mappings**: source to target with transformations
- **Data Type Conversions**: Specify type changes and reasons
- **NULL Handling**: Based on data dictionary constraints vs actual data
- **Join Logic**: If multiple sources, include join keys and types

#### 4.3 Transformation Logic
For each transformation step:
1. **Purpose**: What business rule it implements
2. **PySpark Operations**: Specific functions needed (use Australian English spelling)
3. **Data Quality**: Validation rules
4. **Performance**: Optimization considerations

**IMPORTANT - AUSTRALIAN ENGLISH SPELLING**:
All function and variable names MUST use Australian English spelling:
- "normalise" (not "normalize")
- "standardise" (not "standardize")
- "colour" (not "color")
- "analyse" (not "analyze")
- "categorise" (not "categorize")
- "summarise" (not "summarize")
- "optimise" (not "optimize")
- "finalise" (not "finalize")

#### 4.4 Existing Code Integration
**If updating existing file**:
- Functions to preserve (list with reasons)
- Functions to modify (list with changes)
- Functions to deprecate (list with US IDs to verify via ADO MCP before removal)
- New functions to add

**Template**:
```markdown
### Existing Code Review
#### Functions to Preserve
- `function_name()` - Still valid per US:12345

#### Functions Requiring Verification
- `old_function()` (#### US:67890) - **ACTION REQUIRED**: Use mcp__ado__wit_get_work_item(67890) to verify if logic still needed before removing

#### New Functions to Add
- `new_transformation()` - Implements requirement from US:{user_story}
```

### PHASE 5: Documentation Generation
**Action**: Use **Write tool** to create documentation file

**File Path**: `.claude/documentation/{file_name}_implementation_specs.md`

**IMPORTANT**:
- Use the Write tool (NOT any MCP tool)
- File must be named exactly: `{file_name}_implementation_specs.md`
- Full path: Project root + `/.claude/documentation/{file_name}_implementation_specs.md`

**Documentation must contain**:

1. **Executive Summary** (1 paragraph)
2. **User Story Reference** (US:{user_story} with link)
3. **Parent Story Context** (if applicable from Phase 1B)
4. **Historical Context** (relevant memories from Phase 1C)
5. **Comment Insights** (key decisions from Phase 1B)
6. **Data Flow Diagram** (Mermaid syntax)
7. **Data Dictionary Summary** (source system schema documentation with business context)
8. **DuckDB Schema Reference** (current implementation schemas)
9. **Schema Analysis** (comparison, discrepancies, NULL handling)
10. **Column Mappings** (detailed source to target with transformations)
11. **Transformation Specifications** (detailed steps)
12. **Existing Code Analysis** (if applicable - with US verification notes)
13. **Implementation Checklist** (for PySpark engineer)
14. **Testing Scenarios** (acceptance criteria validation)

### PHASE 6: Update Table Memory
**Action**: IMMEDIATELY use `write_memory` MCP tool to update consolidated table memory

1. **Extract Clean Table Name**:
   - Remove layer prefix from `{file_name}` (e.g., "g_mg_occurrence" to "mg_occurrence")
   - Store as: clean_table_name

2. **Create Updated Memory Content**:
   Create markdown with sections (will be merged with existing memory):
   ```markdown
   ## Summary
   [2-3 sentence summary of what this table does, incorporating US:{user_story} changes]

   ## Parent Story Context
   [If applicable: Parent US ID and objectives for US:{user_story}]

   ## Key Requirements
   - [Updated/consolidated requirements including new ones from US:{user_story}]
   - [Previous requirements that are still valid]

   ## Data Transformations
   - **Source tables**: [All tables used, including any new ones from US:{user_story}]
   - **Target table**: {write_layer}_{datasource}.{file_name}
   - **Key logic**: [Consolidated transformation logic including US:{user_story} additions]

   ## Business Rules
   - [Updated business rules - merge with existing, note any changes from US:{user_story}]

   ## Data Quality Rules
   - [Updated validation rules - merge with existing, note any new ones from US:{user_story}]

   ## Related Tables
   - [Complete list of related tables including any new dependencies from US:{user_story}]

   ## Gotchas & Special Considerations
   - [Cumulative warnings including any new ones from US:{user_story}]

   ## Comments Insights
   - [Technical decisions from US:{user_story} comments]
   ```

3. **Store/Update Memory**:
   - Use `write_memory` with:
     * layer: "{write_layer}"
     * datasource: "{datasource}"
     * table_name: clean_table_name
     * user_story: "{user_story}"
     * content: memory_content_markdown
   - **write_memory** will automatically:
     * Archive previous state to `.claude/memory/{write_layer}/{datasource}/clean_table_name/history/US_{user_story}.md`
     * Update changelog with US:{user_story}
     * Merge new content with existing sections
     * Save updated state to `.claude/memory/{write_layer}/{datasource}/clean_table_name.md`

**Success Message**: Memory will be created (first time) OR updated (subsequent times) at `.claude/memory/{write_layer}/{datasource}/clean_table_name.md`

---

## OUTPUT REQUIREMENTS

### Critical Elements to Include:
* User story summary with business context
* Complete schema mappings (source to target)
* All transformation logic with PySpark operations
* Existing code analysis with US verification instructions
* Data quality validation rules
* Performance optimization notes
* Error handling requirements
* Testing scenarios mapped to acceptance criteria

### Documentation Structure:
```markdown
# {file_name} - Implementation Specifications

## User Story: US:{user_story}
[Summary from ADO]

## Existing Code Status
[File location, US references, verification needed]

## Data Dictionary Reference
[Source system schema documentation - business context, constraints, descriptions]

## DuckDB Current Schema
[Actual implemented schemas from DuckDB MCP queries]

## Schema Analysis
[Comparison, discrepancies, NULL handling, data type differences]

## Data Architecture
[Flow diagram and column mappings]

## Transformation Logic
[Detailed specifications with business rules from data dictionary]

## Implementation Notes
[For PySpark engineer]

## Testing Requirements
[Validation scenarios]
```

### Quality Checklist:
- [ ] User story retrieved and summarized (Phase 1)
- [ ] Parent story context gathered (Phase 1B)
- [ ] All comments reviewed and key insights extracted (Phase 1B)
- [ ] Existing memories checked and incorporated (Phase 1C)
- [ ] Existing code analyzed (if present) (Phase 2)
- [ ] US references verified or marked for verification (Phase 2)
- [ ] Data dictionary files read for relevant tables (Phase 3.1)
- [ ] DuckDB schemas queried for current implementation (Phase 3.2)
- [ ] Schema comparison completed (Phase 3.3)
- [ ] Related tables identified (Phase 3.4)
- [ ] **Australian English spelling used for all function/variable names** (e.g., "normalise", "standardise", "analyse")
- [ ] All transformations specified with business context (Phase 4)
- [ ] Data quality rules defined (Phase 4)
- [ ] Documentation saved via Write tool (Phase 5)
- [ ] Memory stored via write_memory tool (Phase 6)

---

## EFFICIENCY NOTES
- Use MCP tools in parallel where possible
- Read data dictionary files early to understand business context
- Query DuckDB once per layer (not per table)
- Compare data dictionary vs DuckDB schema to identify discrepancies
- Verify existing US references only if file exists
- Keep documentation concise but complete
- Focus on actionable specifications for PySpark engineer

## DATA DICTIONARY USAGE EXAMPLES
**Example 1**: CMS case table
- Read: `.claude/data_dictionary/cms_case.md`
- Extract: Business descriptions, NULL constraints, common values
- Document: "allocation_area_id allows NULL (27% of records), common values: 63 (25%), 20 (5%)"

**Example 2**: FVMS incident table
- Read: `.claude/data_dictionary/fvms_incident.md`
- Extract: Incident type categories, status values, timestamp handling
- Document: Schema constraints and business rules for validation

**Example 3**: Join tables
- For `cms_case__offence_report`: Read both `cms_case.md` and `cms_offence_report.md`
- Document: Foreign key relationships and join constraints

## DEVELOPMENT EXAMPLE REFERENCE
**CRITICAL**: Use `python_files/gold/g_ya_mg_occurence.py` as a reference implementation pattern

**Key Pattern to Study**:
- Review the `get_incident_offence_report_linkage()` function (lines 81-93)
- This demonstrates the proper pattern for creating linkage tables between CMS and FVMS systems
- Note the use of full outer joins to capture all records from both systems
- Pay special attention to the verified flag filtering and ID matching logic

**Implementation Notes**:
- When designing linkage logic, follow the same pattern of full outer joins
- Document similar linkage requirements in your specifications
- Include verification logic similar to the `_verified` flag filtering
- Ensure PySpark engineer understands this is the approved pattern for cross-system linkages
"""
