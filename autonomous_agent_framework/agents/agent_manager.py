"""
Agent manager for initializing and managing multiple employee agents.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from ..agents.base_agent import BaseAgent, AgentOrchestrator
from ..agents.employee_agent import EmployeeAgent
from ..config.config_manager import ConfigManager, AgentConfig, EmployeeConfig


class AgentManager:
    """Manages multiple employee agents and their lifecycle."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config: Optional[AgentConfig] = None
        self.agents: Dict[str, EmployeeAgent] = {}
        self.orchestrator = AgentOrchestrator()
        self.logger = logging.getLogger("agent_manager")
        
    async def initialize(self) -> None:
        """Initialize the agent manager and load configuration."""
        self.logger.info("Initializing Agent Manager")
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Initialize agents for all configured employees
        for employee_id, employee_config in self.config.employees.items():
            try:
                await self.create_agent(employee_id, employee_config)
            except Exception as e:
                self.logger.error(f"Failed to create agent for {employee_id}: {e}")
        
        self.logger.info(f"Agent Manager initialized with {len(self.agents)} agents")
    
    async def create_agent(self, employee_id: str, employee_config: EmployeeConfig) -> EmployeeAgent:
        """Create and initialize an agent for an employee."""
        self.logger.info(f"Creating agent for {employee_id}")
        
        # Prepare agent configuration
        agent_config = {
            'employee_config': employee_config,
            'api_credentials': self.config.api_credentials.dict(),
            'meeting_config': self.config.meeting_config.dict(),
            'llm_model': self.config.llm_model,
            'embedding_model': self.config.embedding_model
        }
        
        # Create and initialize the agent
        agent = EmployeeAgent(employee_id, agent_config)
        await agent.initialize()
        
        # Register with orchestrator
        self.orchestrator.register_agent(agent)
        
        # Store in our registry
        self.agents[employee_id] = agent
        
        self.logger.info(f"Agent created and registered for {employee_id}")
        return agent
    
    async def get_agent(self, employee_id: str) -> Optional[EmployeeAgent]:
        """Get an agent by employee ID."""
        return self.agents.get(employee_id)
    
    async def remove_agent(self, employee_id: str) -> bool:
        """Remove an agent."""
        if employee_id in self.agents:
            del self.agents[employee_id]
            self.logger.info(f"Agent removed for {employee_id}")
            return True
        return False
    
    async def update_agent_context(self, employee_id: str) -> bool:
        """Update context for a specific agent."""
        agent = self.agents.get(employee_id)
        if agent:
            try:
                await agent.update_context()
                self.logger.info(f"Context updated for {employee_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to update context for {employee_id}: {e}")
        return False
    
    async def update_all_contexts(self) -> Dict[str, bool]:
        """Update context for all agents."""
        self.logger.info("Updating context for all agents")
        results = {}
        
        for employee_id, agent in self.agents.items():
            try:
                await agent.update_context()
                results[employee_id] = True
                self.logger.info(f"Context updated for {employee_id}")
            except Exception as e:
                self.logger.error(f"Failed to update context for {employee_id}: {e}")
                results[employee_id] = False
        
        return results
    
    async def get_agent_status(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for an agent."""
        agent = self.agents.get(employee_id)
        if not agent:
            return None
        
        status = {
            'employee_id': employee_id,
            'employee_name': agent.employee_config.name if agent.employee_config else 'Unknown',
            'initialized': agent.context is not None,
            'last_context_update': agent.last_context_update.isoformat() if agent.last_context_update else None,
            'context_age_minutes': None,
            'active_tasks_count': 0,
            'blockers_count': 0,
            'availability': 'Unknown'
        }
        
        if agent.last_context_update:
            age = datetime.now() - agent.last_context_update
            status['context_age_minutes'] = int(age.total_seconds() / 60)
        
        if agent.context:
            status['active_tasks_count'] = len(agent.context.active_tasks)
            status['blockers_count'] = len(agent.context.blockers)
            status['availability'] = agent.context.availability_status
            status['current_focus'] = agent.context.current_focus
        
        return status
    
    async def get_all_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all agents."""
        status_dict = {}
        for employee_id in self.agents:
            status_dict[employee_id] = await self.get_agent_status(employee_id)
        return status_dict
    
    async def prepare_agents_for_meeting(self, meeting_participants: List[str]) -> Dict[str, Dict[str, Any]]:
        """Prepare agents for a meeting by updating their context."""
        self.logger.info(f"Preparing agents for meeting with participants: {meeting_participants}")
        
        preparation_results = {}
        
        for participant in meeting_participants:
            if participant in self.agents:
                agent = self.agents[participant]
                try:
                    # Update context if needed
                    if agent.should_update_context():
                        await agent.update_context()
                    
                    # Get meeting preparation summary
                    preparation_results[participant] = {
                        'status': 'ready',
                        'context_updated': True,
                        'summary': agent.get_meeting_preparation_summary(None)  # Will be updated with actual meeting context
                    }
                    
                except Exception as e:
                    self.logger.error(f"Failed to prepare agent {participant}: {e}")
                    preparation_results[participant] = {
                        'status': 'error',
                        'error': str(e),
                        'context_updated': False
                    }
            else:
                self.logger.warning(f"No agent found for participant: {participant}")
                preparation_results[participant] = {
                    'status': 'not_found',
                    'context_updated': False
                }
        
        return preparation_results
    
    async def get_team_summary(self, team_name: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of team status."""
        team_agents = []
        
        if team_name:
            # Filter agents by team
            for agent in self.agents.values():
                if agent.employee_config and team_name in agent.employee_config.teams:
                    team_agents.append(agent)
        else:
            # All agents
            team_agents = list(self.agents.values())
        
        if not team_agents:
            return {'error': f'No agents found for team: {team_name}'}
        
        summary = {
            'team_name': team_name or 'All Employees',
            'member_count': len(team_agents),
            'members': [],
            'total_active_tasks': 0,
            'total_blockers': 0,
            'availability_breakdown': {},
            'generated_at': datetime.now().isoformat()
        }
        
        for agent in team_agents:
            member_info = {
                'employee_id': agent.employee_id,
                'name': agent.employee_config.name if agent.employee_config else 'Unknown',
                'availability': 'Unknown',
                'active_tasks': 0,
                'blockers': 0,
                'current_focus': 'Unknown'
            }
            
            if agent.context:
                member_info['availability'] = agent.context.availability_status
                member_info['active_tasks'] = len(agent.context.active_tasks)
                member_info['blockers'] = len(agent.context.blockers)
                member_info['current_focus'] = agent.context.current_focus
                
                summary['total_active_tasks'] += member_info['active_tasks']
                summary['total_blockers'] += member_info['blockers']
                
                # Count availability statuses
                availability = member_info['availability']
                summary['availability_breakdown'][availability] = summary['availability_breakdown'].get(availability, 0) + 1
            
            summary['members'].append(member_info)
        
        return summary
    
    def get_orchestrator(self) -> AgentOrchestrator:
        """Get the agent orchestrator."""
        return self.orchestrator
    
    async def shutdown(self) -> None:
        """Shutdown all agents and cleanup resources."""
        self.logger.info("Shutting down Agent Manager")
        
        # Clear all agents
        self.agents.clear()
        
        self.logger.info("Agent Manager shutdown complete")

