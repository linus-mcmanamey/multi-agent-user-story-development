# Auto Code Review Gate Skill

## Skill Purpose
Automatically run comprehensive code reviews before any PR-related commands (`/pr-*`) and ensure all identified issues are resolved before allowing commits to be pushed. This acts as a quality gate to prevent low-quality code from entering the staging/develop branches.

## Activation
This skill is automatically triggered when any of these commands are called:
- `/pr-feature-to-staging`
- `/pr-deploy-workflow`
- `/commit-and-pr`
- `/pr-fix-pr-review`
- Any other command starting with `/pr-`

## Workflow

### Phase 1: Pre-Commit Code Review

When a `/pr-*` command is detected:

1. **Intercept the command** - Don't execute the PR command yet
2. **Display notice to user**:
   ```
   🔍 AUTO CODE REVIEW GATE ACTIVATED
   Running comprehensive code review before proceeding with PR...
   This ensures code quality standards are met before merge.
   ```

3. **Execute code review**:
   ```bash
   /code-review
   ```

4. **Analyze review results**:
   - Count total issues by severity (Critical, High, Medium, Low)
   - Create issue summary report
   - Determine if auto-fix is possible

### Phase 2: Issue Resolution

#### If NO issues found:
```
✅ CODE REVIEW PASSED
No issues detected. Proceeding with original command...
```
→ Execute the original `/pr-*` command

#### If issues found (Critical or High priority):
```
❌ CODE REVIEW FAILED - BLOCKING ISSUES FOUND
Found X critical and Y high-priority issues that must be fixed.

BLOCKING ISSUES:
- [List of critical issues with file:line]
- [List of high-priority issues with file:line]

🔧 AUTOMATIC FIX PROCESS INITIATED
Launching pyspark-data-engineer agent to resolve issues...
```

**Auto-Fix Workflow**:

1. **Create task document** (if not already exists):
   - Location: `.claude/tasks/pre_commit_code_review_fixes.md`
   - Format: Same as code review fixes task list
   - Include all critical and high-priority issues

2. **Launch pyspark-data-engineer agent**:
   ```
   Task: Fix all critical and high-priority issues before PR
   Document: .claude/tasks/pre_commit_code_review_fixes.md
   Validation: Run syntax check, linting, and formatting after each fix
   ```

3. **Wait for agent completion** and verify:
   - All critical issues resolved
   - All high-priority issues resolved
   - Syntax validation passes
   - Linting passes
   - No new issues introduced

4. **Re-run code review** to confirm all issues resolved

5. **Final decision**:
   - ✅ If all issues fixed: Proceed with original command
   - ❌ If issues remain: Block PR and display unresolved issues

#### If only Medium/Low priority issues:
```
⚠️ CODE REVIEW WARNING - NON-BLOCKING ISSUES FOUND
Found X medium and Y low-priority issues.

These won't block the PR but should be addressed soon.
```

**User Choice**:
```
Do you want to:
1. Auto-fix these issues before proceeding (recommended)
2. Proceed with PR and create tech debt ticket
3. Cancel and fix manually

Choice [1/2/3]:
```

### Phase 3: Post-Fix Validation

After auto-fix completes:

1. **Run validation suite**:
   ```bash
   python3 -m py_compile <modified_files>
   ruff check python_files/
   ruff format python_files/
   ```

2. **Run second code review**:
   - Ensure no new issues introduced
   - Verify all original issues resolved
   - Check for any regressions

3. **Generate fix summary**:
   ```
   📊 AUTO-FIX SUMMARY
   ==================
   Files Modified: 4
   Issues Fixed: 9 (3 critical, 4 high, 2 medium)
   Validation: ✅ All checks passed

   Modified Files:
   - python_files/gold/g_z_mg_occ_person_address.py
   - python_files/gold/g_xa_mg_statsclasscount.py
   - python_files/silver/silver_cms/s_cms_person.py
   - python_files/gold/g_xa_mg_cms_mo.py

   ✅ All issues resolved. Proceeding with PR...
   ```

### Phase 4: Execute Original Command

Only after ALL critical/high issues are resolved:

1. **Add fixed files to git staging**:
   ```bash
   git add <modified_files>
   ```

2. **Create enhanced commit message**:
   ```
   [Original commit message]

   🤖 Auto Code Review Fixes Applied:
   - Fixed X critical issues
   - Fixed Y high-priority issues
   - All validation checks passed
   ```

3. **Execute original `/pr-*` command**

4. **Display completion message**:
   ```
   ✅ PR CREATED WITH AUTO-FIXES
   All code quality issues have been resolved.
   PR is ready for human review.

   Code Review Report: .claude/tasks/pre_commit_code_review_fixes.md
   ```

## Configuration

### Severity Thresholds

```yaml
# .claude/config/code_review_gate.yaml
blocking_severities:
  - CRITICAL
  - HIGH

auto_fix_enabled: true
auto_fix_medium_issues: true  # Prompt user for medium issues
auto_fix_low_issues: false    # Skip low-priority auto-fix

max_auto_fix_attempts: 2
validation_required: true
```

### Bypass Options

**Emergency Override** (use with caution):
```bash
# Skip code review gate (requires explicit confirmation)
/pr-feature-to-staging --skip-review-gate --confirm-override

# This will prompt:
⚠️ DANGER: Skipping code review gate
This may introduce bugs or technical debt.
Type 'I UNDERSTAND THE RISKS' to proceed:
```

## Implementation Hooks

### Hook 1: Command Interceptor
```python
# Intercepts all /pr-* commands
if command.startswith("/pr-"):
    # Trigger auto-code-review-gate skill
    execute_skill("auto-code-review-gate")
```

### Hook 2: Issue Detection
```python
# Parse code review output
issues = parse_code_review_output(review_result)
critical_count = count_by_severity(issues, "CRITICAL")
high_count = count_by_severity(issues, "HIGH")

if critical_count > 0 or high_count > 0:
    block_pr = True
    attempt_auto_fix = True
```

### Hook 3: Auto-Fix Delegation
```python
# Create task document and delegate to pyspark-data-engineer
task_doc = create_task_document(issues)
agent_result = launch_agent("pyspark-data-engineer", task_doc)

# Validate fixes
validation_passed = run_validation_suite()
issues_resolved = verify_issues_fixed(issues, agent_result)

if validation_passed and issues_resolved:
    allow_pr = True
```

## Example Execution Flow

### Scenario: User runs `/pr-feature-to-staging`

```
USER: /pr-feature-to-staging "feat: add new statsclasscount table"

SYSTEM:
🔍 AUTO CODE REVIEW GATE ACTIVATED
Running comprehensive code review before proceeding with PR...

[Code review executes...]

SYSTEM:
❌ CODE REVIEW FAILED - 3 CRITICAL ISSUES FOUND

CRITICAL ISSUES:
1. python_files/gold/g_z_mg_occ_person_address.py:43
   - Redundant Spark session initialization (memory leak risk)

2. python_files/gold/g_xa_mg_statsclasscount.py:100
   - Validation methods defined but never called (data quality risk)

3. python_files/gold/g_z_mg_occ_person_address.py:32
   - Unused constructor parameter (confusing API)

🔧 AUTOMATIC FIX PROCESS INITIATED
Launching pyspark-data-engineer agent...

[Agent fixes all issues...]

SYSTEM:
📊 AUTO-FIX SUMMARY
==================
Files Modified: 2
Issues Fixed: 3 (3 critical)
Validation: ✅ All checks passed

✅ All critical issues resolved.

Adding fixed files to commit:
  M python_files/gold/g_z_mg_occ_person_address.py
  M python_files/gold/g_xa_mg_statsclasscount.py

Proceeding with PR creation...

[Original /pr-feature-to-staging command executes]

SYSTEM:
✅ PR CREATED SUCCESSFULLY
Branch: feature/statsclasscount → staging
PR #: 5830
Status: Ready for review

All code quality gates passed! 🎉
```

## Error Handling

### If auto-fix fails:
```
❌ AUTO-FIX FAILED
The pyspark-data-engineer agent was unable to resolve all issues.

Remaining Issues:
- [List of unresolved issues]

NEXT STEPS:
1. Review the task document: .claude/tasks/pre_commit_code_review_fixes.md
2. Fix issues manually
3. Re-run /pr-feature-to-staging when ready

OR

Use emergency override (not recommended):
/pr-feature-to-staging --skip-review-gate --confirm-override
```

### If validation fails after fix:
```
❌ VALIDATION FAILED AFTER AUTO-FIX
The fixes introduced new issues or broke existing functionality.

Validation Errors:
- [List of validation errors]

Rolling back auto-fixes...
Original code restored.

NEXT STEPS:
1. Review the code review report
2. Fix issues manually with more care
3. Test thoroughly before re-running PR command
```

## Benefits

1. **Prevents bugs before merge**: Catches issues at commit time, not in production
2. **Automated quality gates**: No manual intervention needed for common issues
3. **Consistent code quality**: All PRs meet minimum quality standards
4. **Faster review cycles**: Human reviewers see clean code
5. **Learning tool**: Developers see fixes and learn patterns
6. **Tech debt prevention**: Issues fixed immediately, not deferred

## Metrics Tracked

The skill automatically logs:
- Number of PRs with code review issues
- Issues caught per severity level
- Auto-fix success rate
- Time saved by automated fixes
- Common issue patterns

Stored in: `.claude/metrics/code_review_gate_stats.json`

## Integration with Existing Workflows

This skill works seamlessly with:
- `/pr-feature-to-staging` - Adds quality gate before PR creation
- `/pr-deploy-workflow` - Ensures clean code through entire deployment pipeline
- `/commit-and-pr` - Quick commits still get quality checks
- `/pr-fix-pr-review` - Prevents re-introducing issues when fixing review feedback

## Testing the Skill

To test the auto code review gate:

```bash
# 1. Make some intentional code quality issues
echo "import os\nimport os" >> test_file.py  # Duplicate import

# 2. Try to create PR
/pr-feature-to-staging "test auto review gate"

# 3. Verify gate catches issues and auto-fixes them

# 4. Confirm PR only proceeds after fixes applied
```

## Maintenance

Update the skill when:
- New code quality rules are added
- Project standards change
- New file types need review
- Additional validation checks needed

## Future Enhancements

Potential improvements:
1. **AI-powered issue prioritization**: Use ML to determine which issues are most critical
2. **Team notification**: Slack/Teams alerts when auto-fixes are applied
3. **Fix explanation**: Include detailed explanations of each fix for learning
4. **Custom rule sets**: Project-specific or team-specific quality gates
5. **Performance metrics**: Track build times and code quality trends

---

**Status**: Active
**Version**: 1.0
**Last Updated**: 2025-11-04
**Owner**: DevOps/Quality Team
