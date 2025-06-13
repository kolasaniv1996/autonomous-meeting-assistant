"""
Autonomous Agent Framework

A modular framework for creating autonomous agents that can attend meetings,
communicate on behalf of employees, and handle post-meeting actions.
"""

__version__ = "0.1.0"
__author__ = "Autonomous Agent Framework Team"

from .config.config_manager import ConfigManager, AgentConfig, EmployeeConfig
from .agents.base_agent import (
    BaseAgent, 
    AgentOrchestrator, 
    AgentFactory,
    WorkItem,
    ContextSummary,
    MeetingMessage,
    MeetingContext,
    ActionItem,
    MeetingSummary
)

__all__ = [
    "ConfigManager",
    "AgentConfig", 
    "EmployeeConfig",
    "BaseAgent",
    "AgentOrchestrator",
    "AgentFactory",
    "WorkItem",
    "ContextSummary", 
    "MeetingMessage",
    "MeetingContext",
    "ActionItem",
    "MeetingSummary"
]

