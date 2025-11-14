"""
Multi-Agent Orchestration Framework
Spawn and coordinate specialized sub-agents for complex task decomposition.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from pathlib import Path
import asyncio
import json
import shutil
from datetime import datetime
from collections import defaultdict, deque


class AgentStatus(Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentResult:
    """Result from agent execution"""
    agent_id: str
    status: AgentStatus
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AgentTask:
    """Task definition for a sub-agent"""
    agent_id: str
    role: str
    context: Dict[str, Any]
    instructions: str
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    max_retries: int = 0


class Orchestrator:
    """Base orchestrator for managing sub-agent execution"""
    
    def __init__(self, max_concurrent: int = 5, workspace: str = "/tmp/agent_workspace"):
        self.max_concurrent = max_concurrent
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        
        self.agents: Dict[str, AgentTask] = {}
        self.results: Dict[str, AgentResult] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    def register_task(self, task: AgentTask) -> None:
        """Register a new agent task"""
        self.agents[task.agent_id] = task
        self.results[task.agent_id] = AgentResult(
            agent_id=task.agent_id,
            status=AgentStatus.PENDING
        )
        
    def get_agent_dir(self, agent_id: str) -> Path:
        """Get isolated workspace directory for agent"""
        agent_dir = self.workspace / agent_id
        agent_dir.mkdir(exist_ok=True)
        return agent_dir
    
    async def execute_agent(self, agent_id: str) -> AgentResult:
        """Execute a single agent with retry logic"""
        task = self.agents[agent_id]
        
        for attempt in range(task.max_retries + 1):
            async with self.semaphore:
                self.results[agent_id].status = AgentStatus.RUNNING
                
                try:
                    result = await asyncio.wait_for(
                        self._run_agent_task(task),
                        timeout=task.timeout
                    )
                    
                    self.results[agent_id] = AgentResult(
                        agent_id=agent_id,
                        status=AgentStatus.SUCCESS,
                        output=result,
                        metadata={"role": task.role, "attempt": attempt + 1}
                    )
                    return self.results[agent_id]
                    
                except asyncio.TimeoutError:
                    self.results[agent_id].status = AgentStatus.TIMEOUT
                    self.results[agent_id].error = f"Timeout after {task.timeout}s"
                    
                except Exception as e:
                    if attempt < task.max_retries:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    self.results[agent_id].status = AgentStatus.FAILED
                    self.results[agent_id].error = str(e)
                    
        return self.results[agent_id]
    
    async def _run_agent_task(self, task: AgentTask) -> Any:
        """
        Override this method to implement agent execution.
        Example: spawn subprocess, call API, execute Python function, etc.
        """
        raise NotImplementedError("Subclass must implement _run_agent_task")
    
    def get_dependency_order(self) -> List[List[str]]:
        """Resolve dependencies into execution batches using topological sort"""
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        
        # Build dependency graph
        for agent_id, task in self.agents.items():
            for dep in task.dependencies:
                graph[dep].append(agent_id)
                in_degree[agent_id] += 1
        
        # Topological sort by batches
        batches = []
        queue = deque([aid for aid in self.agents if in_degree[aid] == 0])
        
        while queue:
            batch = list(queue)
            batches.append(batch)
            queue.clear()
            
            for agent_id in batch:
                for dependent in graph[agent_id]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        return batches
    
    async def execute_parallel(self) -> Dict[str, AgentResult]:
        """Execute all agents in parallel"""
        tasks = [self.execute_agent(aid) for aid in self.agents]
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.results
    
    async def execute_chain(self) -> Dict[str, AgentResult]:
        """Execute agents respecting dependencies"""
        batches = self.get_dependency_order()
        
        for batch in batches:
            batch_tasks = [self.execute_agent(aid) for aid in batch]
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Check for failures
            failed = [aid for aid in batch 
                     if self.results[aid].status == AgentStatus.FAILED]
            if failed:
                print(f"Chain halted due to failures: {failed}")
                break
        
        return self.results
    
    def cleanup(self) -> None:
        """Remove workspace directory"""
        if self.workspace.exists():
            shutil.rmtree(self.workspace)


class FileBasedOrchestrator(Orchestrator):
    """Orchestrator using filesystem for agent communication"""
    
    def share_data(self, from_agent: str, to_agent: str, filename: str) -> None:
        """Copy data between agent workspaces"""
        src = self.get_agent_dir(from_agent) / filename
        dst = self.get_agent_dir(to_agent) / filename
        shutil.copy(src, dst)
    
    def write_agent_input(self, agent_id: str, data: Dict[str, Any]) -> Path:
        """Write input data for agent"""
        input_file = self.get_agent_dir(agent_id) / "input.json"
        with open(input_file, "w") as f:
            json.dump(data, f, indent=2)
        return input_file
    
    def read_agent_output(self, agent_id: str) -> Any:
        """Read output from agent"""
        output_file = self.get_agent_dir(agent_id) / "output.json"
        if output_file.exists():
            with open(output_file) as f:
                return json.load(f)
        return None


class TokenAwareOrchestrator(Orchestrator):
    """Orchestrator with token budget tracking"""
    
    def __init__(self, token_budget: int = 100000, **kwargs):
        super().__init__(**kwargs)
        self.token_budget = token_budget
        self.token_usage = {}
    
    async def execute_agent(self, agent_id: str) -> AgentResult:
        """Execute agent and track token usage"""
        result = await super().execute_agent(agent_id)
        
        tokens = result.metadata.get("tokens", 0)
        self.token_usage[agent_id] = tokens
        
        total_tokens = sum(self.token_usage.values())
        if total_tokens > self.token_budget:
            raise Exception(f"Token budget exceeded: {total_tokens}/{self.token_budget}")
        
        return result


# Example implementation for Python function execution
class FunctionOrchestrator(Orchestrator):
    """Orchestrator that executes Python functions as agents"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent_functions: Dict[str, Callable] = {}
    
    def register_function(self, agent_id: str, func: Callable) -> None:
        """Register a Python function as an agent"""
        self.agent_functions[agent_id] = func
    
    async def _run_agent_task(self, task: AgentTask) -> Any:
        """Execute the registered function"""
        if task.agent_id not in self.agent_functions:
            raise ValueError(f"No function registered for {task.agent_id}")
        
        func = self.agent_functions[task.agent_id]
        
        # Run function (handle both sync and async)
        if asyncio.iscoroutinefunction(func):
            result = await func(task.context)
        else:
            result = func(task.context)
        
        return result


# Utility for creating agent contexts
class AgentContext:
    """Minimal context container for sub-agents"""
    
    def __init__(self, role: str, task_data: Dict[str, Any], 
                 allowed_tools: List[str] = None):
        self.role = role
        self.task_data = task_data
        self.allowed_tools = allowed_tools or []
        self.output_schema = {}
    
    def to_prompt(self) -> str:
        """Generate isolated prompt for sub-agent"""
        return f"""Role: {self.role}

Task Data:
{json.dumps(self.task_data, indent=2)}

Available Tools: {', '.join(self.allowed_tools)}

Instructions:
- Complete only your assigned task
- Return results in JSON format
- Do not access data outside your task scope
- Report completion status clearly

Output Schema:
{json.dumps(self.output_schema, indent=2)}
"""
