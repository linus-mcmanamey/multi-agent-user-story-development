"""
Example usage patterns for multi-agent orchestration
"""

import asyncio
import json
from pathlib import Path
from orchestrator import (
    FunctionOrchestrator, FileBasedOrchestrator,
    AgentTask, AgentStatus
)


# Example 1: Data Pipeline with Parallel Extraction
async def example_data_pipeline():
    """Extract from multiple sources, transform, then analyze"""
    
    orchestrator = FunctionOrchestrator(max_concurrent=3)
    
    # Define extraction functions
    def extract_api(context):
        # Simulate API extraction
        return {"api_data": [1, 2, 3, 4, 5]}
    
    def extract_db(context):
        # Simulate DB extraction  
        return {"db_data": [10, 20, 30, 40, 50]}
    
    def transform(context):
        # Get results from dependencies
        api_result = orchestrator.results["extract_api"].output
        db_result = orchestrator.results["extract_db"].output
        
        combined = api_result["api_data"] + db_result["db_data"]
        return {"transformed": combined}
    
    def analyze(context):
        transform_result = orchestrator.results["transform"].output
        data = transform_result["transformed"]
        return {
            "count": len(data),
            "sum": sum(data),
            "avg": sum(data) / len(data)
        }
    
    # Register functions
    orchestrator.register_function("extract_api", extract_api)
    orchestrator.register_function("extract_db", extract_db)
    orchestrator.register_function("transform", transform)
    orchestrator.register_function("analyze", analyze)
    
    # Register tasks
    orchestrator.register_task(AgentTask(
        agent_id="extract_api",
        role="API Extractor",
        context={"endpoint": "api.example.com"},
        instructions="Extract data from API"
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="extract_db",
        role="Database Extractor",
        context={"query": "SELECT * FROM users"},
        instructions="Extract data from database"
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="transform",
        role="Data Transformer",
        context={},
        instructions="Transform and merge data",
        dependencies=["extract_api", "extract_db"]
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="analyze",
        role="Data Analyst",
        context={},
        instructions="Analyze transformed data",
        dependencies=["transform"]
    ))
    
    # Execute chain
    results = await orchestrator.execute_chain()
    
    print("Pipeline Results:")
    for agent_id, result in results.items():
        print(f"  {agent_id}: {result.status.value}")
        if result.status == AgentStatus.SUCCESS:
            print(f"    Output: {result.output}")
    
    return results["analyze"].output


# Example 2: Code Analysis with Parallel Checks
async def example_code_analysis():
    """Run multiple code quality checks in parallel"""
    
    orchestrator = FunctionOrchestrator(max_concurrent=5)
    
    # Define analysis functions
    def lint_check(context):
        code_file = context["code_file"]
        return {"lint_errors": 2, "warnings": 5}
    
    def security_check(context):
        code_file = context["code_file"]
        return {"vulnerabilities": 0, "severity": "none"}
    
    def performance_check(context):
        code_file = context["code_file"]
        return {"complexity": 8, "suggestions": ["Use list comprehension"]}
    
    def generate_report(context):
        lint = orchestrator.results["lint"].output
        security = orchestrator.results["security"].output
        performance = orchestrator.results["performance"].output
        
        return {
            "summary": "Code quality report",
            "lint": lint,
            "security": security,
            "performance": performance,
            "overall_score": 85
        }
    
    # Register functions
    orchestrator.register_function("lint", lint_check)
    orchestrator.register_function("security", security_check)
    orchestrator.register_function("performance", performance_check)
    orchestrator.register_function("report", generate_report)
    
    # Register parallel tasks
    code_context = {"code_file": "myapp.py"}
    
    orchestrator.register_task(AgentTask(
        agent_id="lint",
        role="Linter",
        context=code_context,
        instructions="Run linting checks"
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="security",
        role="Security Scanner",
        context=code_context,
        instructions="Scan for security issues"
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="performance",
        role="Performance Analyzer",
        context=code_context,
        instructions="Analyze performance"
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="report",
        role="Report Generator",
        context={},
        instructions="Generate comprehensive report",
        dependencies=["lint", "security", "performance"]
    ))
    
    # Execute
    results = await orchestrator.execute_chain()
    
    if results["report"].status == AgentStatus.SUCCESS:
        print(json.dumps(results["report"].output, indent=2))


# Example 3: File-Based Communication
async def example_file_based():
    """Use filesystem for agent data exchange"""
    
    orchestrator = FileBasedOrchestrator(workspace="/tmp/example_workspace")
    
    async def process_step1(task):
        # Write output to agent workspace
        output_file = orchestrator.get_agent_dir(task.agent_id) / "output.json"
        with open(output_file, "w") as f:
            json.dump({"step1_result": "processed"}, f)
        return {"status": "complete"}
    
    async def process_step2(task):
        # Read from previous agent
        orchestrator.share_data("step1", "step2", "output.json")
        
        input_file = orchestrator.get_agent_dir(task.agent_id) / "output.json"
        with open(input_file) as f:
            prev_data = json.load(f)
        
        return {"step2_result": f"used {prev_data['step1_result']}"}
    
    orchestrator.register_function = lambda aid, func: setattr(
        orchestrator, f"_func_{aid}", func
    )
    orchestrator.register_function("step1", process_step1)
    orchestrator.register_function("step2", process_step2)
    
    orchestrator.register_task(AgentTask(
        agent_id="step1",
        role="Processor 1",
        context={},
        instructions="Process data"
    ))
    
    orchestrator.register_task(AgentTask(
        agent_id="step2",
        role="Processor 2",
        context={},
        instructions="Use step1 output",
        dependencies=["step1"]
    ))
    
    async def _run_agent_task(task):
        func = getattr(orchestrator, f"_func_{task.agent_id}")
        return await func(task)
    
    orchestrator._run_agent_task = _run_agent_task
    
    results = await orchestrator.execute_chain()
    orchestrator.cleanup()
    
    print(f"Step 2 result: {results['step2'].output}")


if __name__ == "__main__":
    print("=== Example 1: Data Pipeline ===")
    asyncio.run(example_data_pipeline())
    
    print("\n=== Example 2: Code Analysis ===")
    asyncio.run(example_code_analysis())
    
    print("\n=== Example 3: File-Based Communication ===")
    asyncio.run(example_file_based())
