"""Multi-Agent User Story Development Plugin. Automated workflow orchestrator for Business Analyst and PySpark Engineer agents."""

from multi_agent_user_story_development.config import AgentConfig
from multi_agent_user_story_development.orchestrator import run_orchestrator

__version__ = "1.0.0"
__author__ = "Program Unify"
__email__ = "unify@emstas.com"
__all__ = ["AgentConfig", "run_orchestrator"]
