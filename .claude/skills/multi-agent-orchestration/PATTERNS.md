# Multi-Agent Orchestration Patterns

This document describes common orchestration patterns for the Unify 2.1 Data Migration project.

## Pattern 1: Parallel Independent Execution

**Use Case**: Tasks with no dependencies between subtasks

```
Main Task: Fix linting across all silver databases
    ↓
Orchestrator analyzes and decomposes
    ↓
    ├─→ Agent 1: silver_cms (parallel)
    ├─→ Agent 2: silver_fvms (parallel)
    └─→ Agent 3: silver_nicherms (parallel)
    ↓
All agents execute simultaneously
    ↓
Orchestrator collects JSON responses
    ↓
Consolidated report generated
```

**Characteristics**:
- All agents launch simultaneously
- No dependencies between agents
- Fastest execution time
- Each agent works on separate files/components

**Example Command**:
```bash
/orchestrate "fix all linting errors across silver layer"
```

**Expected Agents**: 3
**Estimated Time**: 15-20 minutes (vs 45-60 sequential)

---

## Pattern 2: Layer-by-Layer Sequential

**Use Case**: Work must proceed through medallion layers in order

```
Main Task: Implement new validation framework
    ↓
Phase 1: Bronze Layer
    ↓
    ├─→ Agent 1: bronze_cms
    ├─→ Agent 2: bronze_fvms
    └─→ Agent 3: bronze_nicherms
    ↓
Wait for Phase 1 completion
    ↓
Phase 2: Silver Layer
    ↓
    ├─→ Agent 4: silver_cms
    ├─→ Agent 5: silver_fvms
    └─→ Agent 6: silver_nicherms
    ↓
Wait for Phase 2 completion
    ↓
Phase 3: Gold Layer
    ↓
    ├─→ Agent 7: gold_x_mg
    ├─→ Agent 8: gold_xa
    └─→ Agent 9: gold_xb
```

**Characteristics**:
- Multiple sequential phases
- Parallel execution within each phase
- Hybrid approach (sequential + parallel)
- Respects data flow dependencies

**Example Command**:
```bash
/orchestrate validation_framework_phased.md
# Task file specifies phased execution
```

**Expected Agents**: 9 (3 phases × 3 agents)
**Estimated Time**: 60-90 minutes

---

## Pattern 3: Design-then-Implement

**Use Case**: Need framework design before parallel implementation

```
Main Task: Add monitoring to all ETL pipelines
    ↓
Phase 1: Design (Single Agent)
    ↓
Agent 1: Design monitoring framework
    ├─→ Define monitoring schema
    ├─→ Create base monitoring classes
    ├─→ Design logging patterns
    └─→ Output: Monitoring specification (JSON)
    ↓
Phase 2: Implementation (Parallel Agents)
    ↓
Uses monitoring spec from Agent 1
    ↓
    ├─→ Agent 2: Implement in bronze layer
    ├─→ Agent 3: Implement in silver layer
    ├─→ Agent 4: Implement in gold layer
    ├─→ Agent 5: Create monitoring dashboard
    └─→ Agent 6: Write monitoring tests
    ↓
Orchestrator validates consistency with spec
```

**Characteristics**:
- Single design agent first
- Design output used by implementation agents
- Ensures consistency across implementations
- Good for new feature development

**Example Command**:
```bash
/orchestrate monitoring_framework_design_impl.md
```

**Expected Agents**: 6 (1 design + 5 implementation)
**Estimated Time**: 50-70 minutes

---

## Pattern 4: Analyze-then-Fix

**Use Case**: Need analysis before determining fixes

```
Main Task: Optimize all gold table performance
    ↓
Phase 1: Analysis (Parallel)
    ↓
    ├─→ Agent 1: Analyze g_x_mg_* tables
    ├─→ Agent 2: Analyze g_xa_* tables
    ├─→ Agent 3: Analyze g_xb_* tables
    └─→ Agent 4: Analyze cross-table joins
    ↓
Orchestrator aggregates findings
    ↓
Phase 2: Optimization (Parallel)
    ↓
Based on Phase 1 analysis
    ↓
    ├─→ Agent 5: Optimize g_x_mg_* tables
    ├─→ Agent 6: Optimize g_xa_* tables
    ├─→ Agent 7: Optimize g_xb_* tables
    └─→ Agent 8: Optimize join strategies
    ↓
Phase 3: Validation (Single Agent)
    ↓
Agent 9: Validate performance improvements
```

**Characteristics**:
- Analysis phase identifies issues
- Optimization phase fixes issues
- Validation phase confirms improvements
- Data-driven optimization

**Example Command**:
```bash
/orchestrate gold_performance_optimization.md
```

**Expected Agents**: 9 (4 analyze + 4 optimize + 1 validate)
**Estimated Time**: 70-90 minutes

---

## Pattern 5: Quality Gate Sweep

**Use Case**: Comprehensive code quality validation and fixes

```
Main Task: Complete code quality sweep
    ↓
Phase 1: Assessment (Parallel)
    ↓
    ├─→ Agent 1: Syntax validation all files
    ├─→ Agent 2: Linting check all files
    ├─→ Agent 3: Type hint coverage check
    └─→ Agent 4: Test coverage check
    ↓
Orchestrator identifies issues
    ↓
Phase 2: Fixes (Parallel by Layer)
    ↓
    ├─→ Agent 5: Fix bronze layer issues
    ├─→ Agent 6: Fix silver layer issues
    ├─→ Agent 7: Fix gold layer issues
    └─→ Agent 8: Fix utilities issues
    ↓
Phase 3: Verification (Parallel)
    ↓
    ├─→ Agent 9: Re-run syntax validation
    ├─→ Agent 10: Re-run linting
    ├─→ Agent 11: Verify type hints
    └─→ Agent 12: Verify test coverage
```

**Characteristics**:
- Assess → Fix → Verify workflow
- Comprehensive quality validation
- Multiple quality dimensions
- Ensures all gates pass

**Example Command**:
```bash
/orchestrate code_quality_sweep.md
```

**Expected Agents**: 12 (4 assess + 4 fix + 4 verify)
**Estimated Time**: 80-100 minutes

---

## Pattern 6: Feature Rollout

**Use Case**: Implement new feature across entire codebase

```
Main Task: Add data lineage tracking
    ↓
Phase 1: Foundation (Sequential)
    ↓
Agent 1: Design lineage schema
    ↓
Agent 2: Create base lineage classes
    ↓
Agent 3: Update configuration
    ↓
Phase 2: Layer Implementation (Parallel)
    ↓
    ├─→ Agent 4: Bronze layer lineage
    ├─→ Agent 5: Silver layer lineage
    └─→ Agent 6: Gold layer lineage
    ↓
Phase 3: Infrastructure (Parallel)
    ↓
    ├─→ Agent 7: Create lineage tests
    ├─→ Agent 8: Add lineage dashboard
    ├─→ Agent 9: Update documentation
    └─→ Agent 10: Add lineage validation
```

**Characteristics**:
- Foundation built first
- Layer implementation in parallel
- Infrastructure added last
- Complete feature rollout

**Example Command**:
```bash
/orchestrate data_lineage_feature.md
```

**Expected Agents**: 10 (3 foundation + 3 layers + 4 infrastructure)
**Estimated Time**: 90-120 minutes

---

## Pattern 7: Database-Specific Work

**Use Case**: Work required for specific source databases

```
Main Task: Update all CMS table transformations
    ↓
Scope: Only CMS database (not FVMS or NicheRMS)
    ↓
Orchestrator identifies CMS files
    ↓
    ├─→ Agent 1: bronze_cms tables (all)
    ├─→ Agent 2: silver_cms tables (subset 1)
    ├─→ Agent 3: silver_cms tables (subset 2)
    └─→ Agent 4: gold tables using CMS data
```

**Characteristics**:
- Scoped to specific database
- May split large layers into subsets
- Focused, domain-specific work
- Faster than full pipeline updates

**Example Command**:
```bash
/orchestrate "update all CMS transformations to use new schema"
```

**Expected Agents**: 4
**Estimated Time**: 30-45 minutes

---

## Pattern 8: Refactoring Campaign

**Use Case**: Large-scale code refactoring

```
Main Task: Refactor all ETL classes to new pattern
    ↓
Phase 1: Template Creation (Single Agent)
    ↓
Agent 1: Create new ETL base class template
    ├─→ Define new class structure
    ├─→ Create migration guide
    └─→ Build example implementation
    ↓
Phase 2: Migration (Parallel by Count)
    ↓
Distribute files evenly across agents
    ↓
    ├─→ Agent 2: Migrate files 1-20
    ├─→ Agent 3: Migrate files 21-40
    ├─→ Agent 4: Migrate files 41-60
    └─→ Agent 5: Migrate files 61-80
    ↓
Phase 3: Validation (Parallel)
    ↓
    ├─→ Agent 6: Validate bronze migrations
    ├─→ Agent 7: Validate silver migrations
    └─→ Agent 8: Validate gold migrations
```

**Characteristics**:
- Template/pattern defined first
- Work distributed evenly
- Validation by layer
- Consistency ensured

**Example Command**:
```bash
/orchestrate etl_class_refactoring.md
```

**Expected Agents**: 8 (1 template + 4 migration + 3 validation)
**Estimated Time**: 90-120 minutes

---

## Pattern Selection Guide

| Pattern | Best For | Agent Count | Phases | Time |
|---------|----------|-------------|--------|------|
| Parallel Independent | Code quality, linting | 2-4 | 1 | 15-30 min |
| Layer-by-Layer | Data flow changes | 6-9 | 3 | 60-90 min |
| Design-then-Implement | New features | 5-8 | 2 | 50-70 min |
| Analyze-then-Fix | Performance optimization | 8-10 | 3 | 70-90 min |
| Quality Gate Sweep | Complete validation | 10-12 | 3 | 80-100 min |
| Feature Rollout | Major features | 8-12 | 3 | 90-120 min |
| Database-Specific | Scoped updates | 3-5 | 1-2 | 30-45 min |
| Refactoring Campaign | Large refactors | 6-10 | 3 | 90-120 min |

---

## Choosing the Right Pattern

### Questions to Ask

1. **Are there dependencies between subtasks?**
   - NO → Parallel Independent
   - YES → Sequential or Hybrid patterns

2. **Does work follow data flow (bronze → silver → gold)?**
   - YES → Layer-by-Layer
   - NO → Other patterns

3. **Do you need design/analysis before implementation?**
   - YES → Design-then-Implement or Analyze-then-Fix
   - NO → Parallel Independent

4. **Is this a new feature or refactoring?**
   - New Feature → Feature Rollout or Design-then-Implement
   - Refactoring → Refactoring Campaign

5. **How many quality gates needed?**
   - Multiple validation phases → Quality Gate Sweep
   - Standard gates only → Parallel Independent

6. **Is work scoped to specific database?**
   - YES → Database-Specific
   - NO → Layer-based patterns

---

## Combining Patterns

Patterns can be combined for complex tasks:

### Example: Feature with Quality Sweep
```
1. Use Design-then-Implement for feature development
2. Use Quality Gate Sweep for final validation
3. Use Parallel Independent for documentation updates
```

### Example: Optimization Campaign
```
1. Use Analyze-then-Fix for performance optimization
2. Use Database-Specific for CMS-only fixes
3. Use Layer-by-Layer for validation
```

---

## Anti-Patterns to Avoid

### ❌ Too Many Agents
```
Main Task: Fix one file
    ↓
Agent 1: Read file
Agent 2: Analyze file
Agent 3: Fix issue 1
Agent 4: Fix issue 2
Agent 5: Validate
```
**Problem**: Overkill for simple task
**Solution**: Use `/background` instead

### ❌ Circular Dependencies
```
Agent 1 needs output from Agent 2
Agent 2 needs output from Agent 1
```
**Problem**: Deadlock
**Solution**: Break into sequential phases

### ❌ Unbalanced Workload
```
Agent 1: Process 80 files (90 min)
Agent 2: Process 5 files (6 min)
Agent 3: Process 3 files (3 min)
```
**Problem**: Inefficient parallelization
**Solution**: Distribute work evenly

### ❌ Missing Quality Gates
```
Agents complete work without validation
```
**Problem**: May introduce issues
**Solution**: Always include quality gate validation

---

## Pattern Templates

### Template: Parallel Independent
```markdown
# Task: [Description]

**Recommended Agents**: 2-4
**Pattern**: Parallel Independent

## Subtasks
- Subtask 1: [Independent work 1]
- Subtask 2: [Independent work 2]
- Subtask 3: [Independent work 3]

Dependencies: None
Execution: Fully parallel
```

### Template: Design-then-Implement
```markdown
# Task: [Description]

**Recommended Agents**: 5-8
**Pattern**: Design-then-Implement

## Phase 1: Design (1 agent)
- Design framework/schema
- Create specification document

## Phase 2: Implementation (4-6 agents)
- Implement based on spec from Phase 1
- Each agent handles different component

Dependencies: Phase 2 depends on Phase 1
Execution: Sequential phases, parallel within phase
```

### Template: Analyze-then-Fix
```markdown
# Task: [Description]

**Recommended Agents**: 6-10
**Pattern**: Analyze-then-Fix

## Phase 1: Analysis (3-5 agents)
- Analyze different components in parallel
- Identify issues and bottlenecks

## Phase 2: Fixes (3-5 agents)
- Fix issues identified in Phase 1
- Each agent handles different component

## Phase 3: Validation (1 agent)
- Validate all fixes successful

Dependencies: Phase 2 depends on Phase 1, Phase 3 depends on Phase 2
Execution: Sequential phases, parallel within phases
```

---

**Created**: 2025-11-07
**Version**: 1.0
**Related**: multi-agent-orchestration.md, README.md
