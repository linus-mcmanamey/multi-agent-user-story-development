# Implementation Guide

Advanced patterns and implementation details for multi-agent orchestration.

## Claude Code Integration

### Subprocess-Based Agent Execution

Execute each agent as a separate Claude Code subprocess:

```python
import subprocess
import json
from pathlib import Path

class ClaudeCodeOrchestrator(FileBasedOrchestrator):
    async def _run_agent_task(self, task: AgentTask) -> Any:
        # Prepare agent workspace
        agent_dir = self.get_agent_dir(task.agent_id)
        
        # Write agent prompt
        prompt = self._create_agent_prompt(task)
        prompt_file = agent_dir / "prompt.txt"
        with open(prompt_file, "w") as f:
            f.write(prompt)
        
        # Write context data
        context_file = agent_dir / "context.json"
        with open(context_file, "w") as f:
            json.dump(task.context, f, indent=2)
        
        # Execute Claude Code subprocess
        output_file = agent_dir / "output.json"
        process = await asyncio.create_subprocess_exec(
            "claude",
            "--prompt-file", str(prompt_file),
            "--output", str(output_file),
            cwd=str(agent_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Agent failed: {stderr.decode()}")
        
        # Read result
        with open(output_file) as f:
            return json.load(f)
    
    def _create_agent_prompt(self, task: AgentTask) -> str:
        return f"""You are a specialized sub-agent in a multi-agent system.

Role: {task.role}

Task: {task.instructions}

Context:
{json.dumps(task.context, indent=2)}

IMPORTANT:
- Complete ONLY the assigned task
- Use files in the current directory for input/output
- Save your final result to output.json
- Format: {{"status": "success", "result": <your_result>}}
- Do not attempt to access other agents' data
- Focus solely on your specific responsibility

Begin your task now.
"""
```

## Hierarchical Delegation

Sub-agents can spawn their own specialized agents:

```python
class HierarchicalOrchestrator(Orchestrator):
    def __init__(self, max_depth: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.max_depth = max_depth
        self.current_depth = 0
    
    async def _run_agent_task(self, task: AgentTask) -> Any:
        # Check if agent needs sub-delegation
        if self._should_delegate(task) and self.current_depth < self.max_depth:
            return await self._delegate_to_subagents(task)
        else:
            return await self._execute_directly(task)
    
    def _should_delegate(self, task: AgentTask) -> bool:
        # Logic to determine if task should be further decomposed
        complexity_indicators = task.context.get("complexity_score", 0)
        return complexity_indicators > 7
    
    async def _delegate_to_subagents(self, task: AgentTask) -> Any:
        # Create child orchestrator
        child_orchestrator = HierarchicalOrchestrator(
            max_depth=self.max_depth,
            max_concurrent=2
        )
        child_orchestrator.current_depth = self.current_depth + 1
        
        # Decompose task into subtasks
        subtasks = self._decompose_task(task)
        for subtask in subtasks:
            child_orchestrator.register_task(subtask)
        
        # Execute child orchestration
        results = await child_orchestrator.execute_chain()
        
        # Aggregate child results
        return self._aggregate_results(results)
```

## Message Bus for Inter-Agent Communication

Advanced communication when agents need to exchange messages:

```python
from dataclasses import dataclass
from typing import Callable, List
from datetime import datetime

@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    message_type: str  # "progress", "completion", "error", "request"
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class MessageBus:
    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.subscribers: Dict[str, List[Callable]] = {}
        self.lock = asyncio.Lock()
    
    async def publish(self, message: AgentMessage) -> None:
        async with self.lock:
            self.messages.append(message)
            
            # Notify subscribers
            for callback in self.subscribers.get(message.to_agent, []):
                await callback(message)
    
    def subscribe(self, agent_id: str, callback: Callable) -> None:
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)
    
    def get_messages_for(self, agent_id: str) -> List[AgentMessage]:
        return [m for m in self.messages if m.to_agent == agent_id]

class MessageBusOrchestrator(Orchestrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_bus = MessageBus()
    
    async def _run_agent_task(self, task: AgentTask) -> Any:
        # Agent can publish progress updates
        await self.message_bus.publish(AgentMessage(
            from_agent=task.agent_id,
            to_agent="orchestrator",
            message_type="progress",
            payload={"status": "started"}
        ))
        
        # Execute task
        result = await self._execute_task_logic(task)
        
        # Publish completion
        await self.message_bus.publish(AgentMessage(
            from_agent=task.agent_id,
            to_agent="orchestrator",
            message_type="completion",
            payload={"result": result}
        ))
        
        return result
```

## Adaptive Resource Allocation

Dynamically adjust resources based on agent performance:

```python
class AdaptiveOrchestrator(Orchestrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.performance_history = defaultdict(list)
    
    async def execute_agent(self, agent_id: str) -> AgentResult:
        start_time = asyncio.get_event_loop().time()
        result = await super().execute_agent(agent_id)
        duration = asyncio.get_event_loop().time() - start_time
        
        # Record performance
        self.performance_history[self.agents[agent_id].role].append(duration)
        
        # Adjust timeout for future similar agents
        avg_duration = sum(self.performance_history[self.agents[agent_id].role]) / \
                      len(self.performance_history[self.agents[agent_id].role])
        
        # Update timeout with buffer
        self.agents[agent_id].timeout = int(avg_duration * 2)
        
        return result
```

## Monitoring and Observability

Comprehensive logging and metrics:

```python
import logging
from datetime import datetime

class InstrumentedOrchestrator(Orchestrator):
    def __init__(self, log_file: str = "orchestration.log", **kwargs):
        super().__init__(**kwargs)
        
        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("orchestrator")
        
        self.metrics = {
            "agents_started": 0,
            "agents_completed": 0,
            "agents_failed": 0,
            "total_duration": 0
        }
    
    async def execute_agent(self, agent_id: str) -> AgentResult:
        self.metrics["agents_started"] += 1
        self.logger.info(f"Starting agent: {agent_id}")
        
        start = datetime.utcnow()
        result = await super().execute_agent(agent_id)
        duration = (datetime.utcnow() - start).total_seconds()
        
        self.metrics["total_duration"] += duration
        
        if result.status == AgentStatus.SUCCESS:
            self.metrics["agents_completed"] += 1
            self.logger.info(f"Agent {agent_id} completed in {duration:.2f}s")
        else:
            self.metrics["agents_failed"] += 1
            self.logger.error(f"Agent {agent_id} failed: {result.error}")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.metrics,
            "success_rate": self.metrics["agents_completed"] / 
                          max(self.metrics["agents_started"], 1),
            "avg_duration": self.metrics["total_duration"] / 
                          max(self.metrics["agents_completed"], 1)
        }
```

## Checkpoint and Recovery

Save orchestration state for recovery:

```python
class CheckpointOrchestrator(Orchestrator):
    def __init__(self, checkpoint_dir: str = "/tmp/checkpoints", **kwargs):
        super().__init__(**kwargs)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def save_checkpoint(self) -> None:
        checkpoint = {
            "agents": {
                aid: {
                    "role": task.role,
                    "context": task.context,
                    "dependencies": task.dependencies
                }
                for aid, task in self.agents.items()
            },
            "results": {
                aid: {
                    "status": result.status.value,
                    "output": result.output,
                    "error": result.error
                }
                for aid, result in self.results.items()
            }
        }
        
        checkpoint_file = self.checkpoint_dir / "state.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint, f, indent=2)
    
    def load_checkpoint(self) -> bool:
        checkpoint_file = self.checkpoint_dir / "state.json"
        if not checkpoint_file.exists():
            return False
        
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)
        
        # Restore state
        for aid, task_data in checkpoint["agents"].items():
            self.register_task(AgentTask(
                agent_id=aid,
                role=task_data["role"],
                context=task_data["context"],
                instructions="",  # Not saved in checkpoint
                dependencies=task_data["dependencies"]
            ))
        
        for aid, result_data in checkpoint["results"].items():
            self.results[aid] = AgentResult(
                agent_id=aid,
                status=AgentStatus(result_data["status"]),
                output=result_data["output"],
                error=result_data["error"]
            )
        
        return True
    
    async def execute_chain(self) -> Dict[str, AgentResult]:
        try:
            results = await super().execute_chain()
        finally:
            self.save_checkpoint()
        return results
```

## Testing Strategies

Unit test individual agents and integration test workflows:

```python
import pytest

class TestOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return FunctionOrchestrator(max_concurrent=2)
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, orchestrator):
        # Define simple test functions
        async def agent1(ctx):
            await asyncio.sleep(0.1)
            return "result1"
        
        async def agent2(ctx):
            await asyncio.sleep(0.1)
            return "result2"
        
        orchestrator.register_function("agent1", agent1)
        orchestrator.register_function("agent2", agent2)
        
        orchestrator.register_task(AgentTask(
            agent_id="agent1",
            role="Test Agent 1",
            context={},
            instructions="Test"
        ))
        
        orchestrator.register_task(AgentTask(
            agent_id="agent2",
            role="Test Agent 2",
            context={},
            instructions="Test"
        ))
        
        results = await orchestrator.execute_parallel()
        
        assert results["agent1"].status == AgentStatus.SUCCESS
        assert results["agent2"].status == AgentStatus.SUCCESS
        assert results["agent1"].output == "result1"
        assert results["agent2"].output == "result2"
    
    @pytest.mark.asyncio
    async def test_dependency_chain(self, orchestrator):
        async def step1(ctx):
            return {"value": 10}
        
        async def step2(ctx):
            prev = orchestrator.results["step1"].output
            return {"value": prev["value"] * 2}
        
        orchestrator.register_function("step1", step1)
        orchestrator.register_function("step2", step2)
        
        orchestrator.register_task(AgentTask(
            agent_id="step1",
            role="Step 1",
            context={},
            instructions="Test"
        ))
        
        orchestrator.register_task(AgentTask(
            agent_id="step2",
            role="Step 2",
            context={},
            instructions="Test",
            dependencies=["step1"]
        ))
        
        results = await orchestrator.execute_chain()
        
        assert results["step2"].output["value"] == 20
```

## Performance Optimization Tips

1. **Batch Size Tuning**: Experiment with different `max_concurrent` values
2. **Timeout Calibration**: Set timeouts based on empirical data
3. **Context Minimization**: Pass only essential data to sub-agents
4. **Early Termination**: Stop execution on critical failures
5. **Result Caching**: Cache expensive computations between runs

## Common Pitfalls

### ❌ Over-sharing Context
```python
# Bad: Passing entire state
context = {"all_data": entire_dataset, "history": full_history}

# Good: Minimal context
context = {"input_file": "data.csv", "columns": ["name", "age"]}
```

### ❌ Ignoring Dependencies
```python
# Bad: Assuming execution order
results["step2"].output  # May not exist yet!

# Good: Declare dependencies
dependencies=["step1", "step2"]
```

### ❌ Infinite Recursion
```python
# Bad: No depth limit
async def recursive_delegate(task):
    return await self._delegate_to_subagents(task)

# Good: Enforce max depth
if self.current_depth < self.max_depth:
    return await self._delegate_to_subagents(task)
```
