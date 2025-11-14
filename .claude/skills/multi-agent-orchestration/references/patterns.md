# Common Orchestration Patterns

Quick reference for typical multi-agent scenarios.

## Pattern 1: ETL Pipeline

Extract → Transform → Load pattern with parallel extraction.

```python
# Parallel extraction
agents = [
    AgentTask("extract_source1", "Extractor", {...}),
    AgentTask("extract_source2", "Extractor", {...}),
    AgentTask("extract_source3", "Extractor", {...}),
]

# Sequential transform and load
agents.extend([
    AgentTask("transform", "Transformer", {...}, 
              dependencies=["extract_source1", "extract_source2", "extract_source3"]),
    AgentTask("load", "Loader", {...}, 
              dependencies=["transform"])
])
```

**Use when:** Processing data from multiple sources that can be extracted in parallel.

## Pattern 2: Fan-Out/Fan-In

One agent produces work for multiple parallel agents, then results aggregate.

```python
agents = [
    AgentTask("splitter", "Data Splitter", {...}),
    AgentTask("process1", "Processor", {...}, dependencies=["splitter"]),
    AgentTask("process2", "Processor", {...}, dependencies=["splitter"]),
    AgentTask("process3", "Processor", {...}, dependencies=["splitter"]),
    AgentTask("aggregator", "Aggregator", {...}, 
              dependencies=["process1", "process2", "process3"])
]
```

**Use when:** Large dataset needs parallel processing with combined results.

## Pattern 3: Quality Gate

Multiple parallel quality checks gate progression to next stage.

```python
agents = [
    # Parallel quality checks
    AgentTask("lint", "Linter", {...}),
    AgentTask("test", "Tester", {...}),
    AgentTask("security", "Security Scanner", {...}),
    
    # Only proceed if all pass
    AgentTask("deploy", "Deployer", {...}, 
              dependencies=["lint", "test", "security"])
]
```

**Use when:** Multiple validation steps must pass before proceeding.

## Pattern 4: Research → Create → Review

Sequential workflow with parallel creation step.

```python
agents = [
    AgentTask("research", "Researcher", {...}),
    
    # Parallel content creation
    AgentTask("write_intro", "Writer", {...}, dependencies=["research"]),
    AgentTask("write_body", "Writer", {...}, dependencies=["research"]),
    AgentTask("write_conclusion", "Writer", {...}, dependencies=["research"]),
    
    # Sequential review
    AgentTask("edit", "Editor", {...}, 
              dependencies=["write_intro", "write_body", "write_conclusion"])
]
```

**Use when:** Creating multi-section content from research.

## Pattern 5: Retry with Fallback

Primary approach with fallback on failure.

```python
# Try primary method
orchestrator.register_task(AgentTask(
    agent_id="primary",
    role="Primary Processor",
    context={"method": "advanced"},
    instructions="Process using advanced method"
))

# Check if primary succeeded
results = await orchestrator.execute_parallel()

if results["primary"].status == AgentStatus.FAILED:
    # Use fallback
    orchestrator.register_task(AgentTask(
        agent_id="fallback",
        role="Fallback Processor",
        context={"method": "basic"},
        instructions="Process using basic method"
    ))
    results = await orchestrator.execute_parallel()
```

**Use when:** Primary approach might fail and simpler alternative exists.

## Pattern 6: Streaming Pipeline

Process data in stages as it arrives.

```python
# Stage 1: Ingest
for i in range(num_batches):
    orchestrator.register_task(AgentTask(
        agent_id=f"ingest_{i}",
        role="Ingestor",
        context={"batch": i},
        instructions="Ingest batch"
    ))

# Stage 2: Process (depends on corresponding ingest)
for i in range(num_batches):
    orchestrator.register_task(AgentTask(
        agent_id=f"process_{i}",
        role="Processor",
        context={"batch": i},
        instructions="Process batch",
        dependencies=[f"ingest_{i}"]
    ))
```

**Use when:** Processing large datasets in batches.

## Pattern 7: Map-Reduce

Distributed computation pattern.

```python
# Map phase (parallel)
items = ["item1", "item2", "item3", "item4"]
for i, item in enumerate(items):
    orchestrator.register_task(AgentTask(
        agent_id=f"map_{i}",
        role="Mapper",
        context={"item": item},
        instructions="Map operation"
    ))

# Reduce phase (sequential)
orchestrator.register_task(AgentTask(
    agent_id="reduce",
    role="Reducer",
    context={},
    instructions="Reduce all mapped results",
    dependencies=[f"map_{i}" for i in range(len(items))]
))
```

**Use when:** Aggregating results from parallel computations.

## Pattern 8: Conditional Execution

Execute different paths based on conditions.

```python
# Initial analysis
orchestrator.register_task(AgentTask(
    agent_id="analyze",
    role="Analyzer",
    context={"data": "..."},
    instructions="Analyze data complexity"
))

results = await orchestrator.execute_parallel()

# Branch based on analysis
if results["analyze"].output["complexity"] > 5:
    # Complex path
    orchestrator.register_task(AgentTask(
        agent_id="process_complex",
        role="Complex Processor",
        context={},
        instructions="Use advanced processing"
    ))
else:
    # Simple path
    orchestrator.register_task(AgentTask(
        agent_id="process_simple",
        role="Simple Processor",
        context={},
        instructions="Use basic processing"
    ))

results = await orchestrator.execute_parallel()
```

**Use when:** Processing strategy depends on runtime conditions.

## Pattern Selection Guide

| Pattern | Parallelism | Use Case |
|---------|-------------|----------|
| ETL Pipeline | Partial | Multi-source data processing |
| Fan-Out/Fan-In | High | Large dataset partition processing |
| Quality Gate | High | Multi-criteria validation |
| Research → Create → Review | Partial | Content generation |
| Retry with Fallback | Low | Fault-tolerant processing |
| Streaming Pipeline | Batched | Continuous data ingestion |
| Map-Reduce | High | Distributed aggregation |
| Conditional Execution | Variable | Dynamic workflow routing |

## Anti-Patterns to Avoid

### ❌ Sequential When Parallel Possible
```python
# Bad: Sequential independent tasks
dependencies=["step1"]  # But step2 doesn't actually need step1!

# Good: Parallel independent tasks
dependencies=[]
```

### ❌ Too Many Dependencies
```python
# Bad: Everything depends on everything
dependencies=["a", "b", "c", "d", "e", "f"]

# Good: Only actual dependencies
dependencies=["a", "c"]
```

### ❌ God Agent
```python
# Bad: One agent does everything
AgentTask("do_all", "Master Agent", {...})

# Good: Specialized agents
AgentTask("extract", "Extractor", {...})
AgentTask("transform", "Transformer", {...})
AgentTask("load", "Loader", {...})
```
