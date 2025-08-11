"""
Base agent class for the AI Sales Agent system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from models.schemas import ConversationState, ClientInquiry
from services.memory_service import MemoryService


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, memory_service: MemoryService):
        self.name = name
        self.memory_service = memory_service
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    def process(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and return response"""
        pass
    
    def log_interaction(self, session_id: str, action: str, details: Dict[str, Any] = None):
        """Log agent interaction"""
        self.logger.info(f"Agent {self.name} - Action: {action} - Session: {session_id}")
        if details:
            self.logger.debug(f"Details: {details}")
        
        # Track in memory service
        self.memory_service.track_event(session_id, f"agent_{self.name}_{action}", details)
    
    def get_conversation_context(self, session_id: str, message_limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return self.memory_service.get_conversation_history(session_id, limit=message_limit)
    
    def update_conversation_state(self, session_id: str, updates: Dict[str, Any]):
        """Update conversation state with new information"""
        conversation_state = self.memory_service.get_conversation_state(session_id)
        if conversation_state:
            # Update stage if provided
            if 'stage' in updates:
                conversation_state.current_stage = updates['stage']
            
            # Update next actions if provided
            if 'next_actions' in updates:
                conversation_state.next_actions = updates['next_actions']
            
            # Update client inquiry if provided
            if 'client_inquiry' in updates:
                conversation_state.client_inquiry = updates['client_inquiry']
            
            # Update recommended packages if provided
            if 'recommended_packages' in updates:
                conversation_state.recommended_packages = updates['recommended_packages']
            
            self.memory_service.save_conversation_state(conversation_state)


class AgentOrchestrator:
    """Orchestrates communication between different agents"""
    
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service
        self.agents = {}
        self.logger = logging.getLogger("orchestrator")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def route_request(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route request to appropriate agent based on conversation state"""
        conversation_state = self.memory_service.get_conversation_state(session_id)
        
        if not conversation_state:
            self.logger.error(f"No conversation state found for session: {session_id}")
            return {"error": "Session not found"}
        
        # Determine which agent should handle this request
        current_stage = conversation_state.current_stage
        selected_agent = self._select_agent(current_stage, user_input, conversation_state)
        
        if selected_agent not in self.agents:
            self.logger.error(f"Agent not found: {selected_agent}")
            return {"error": f"Agent {selected_agent} not available"}
        
        # Process the request
        self.logger.info(f"Routing to agent: {selected_agent} for session: {session_id}")
        response = self.agents[selected_agent].process(session_id, user_input, context)
        
        # Add agent info to response
        response['agent'] = selected_agent
        response['session_id'] = session_id
        
        return response
    
    def _select_agent(self, current_stage: str, user_input: str, conversation_state: ConversationState) -> str:
        """Select the appropriate agent based on conversation state and input"""
        user_input_lower = user_input.lower()
        
        # Check for specific package selection (numbered options like "1", "2", "3", "option 1", etc.)
        package_selection_keywords = ['1', '2', '3', 'option 1', 'option 2', 'option 3', 'tech startup', 'enterprise', 'specialized']
        if any(keyword in user_input_lower for keyword in package_selection_keywords):
            if current_stage in ["recommendation"]:
                return "writer"  # Move to proposal generation
        
        # Check for explicit goodbye/ending keywords
        end_keywords = ['goodbye', 'bye', 'thanks', 'thank you', 'that\'s all', 'end chat', 'finish', 'done']
        if any(keyword in user_input_lower for keyword in end_keywords):
            return "follow_up"
        
        # Intent-based routing (high priority overrides)
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'start', 'good morning', 'good afternoon']):
            return "greeter"
        
        # Package/service requests - route to recommender to show packages
        if any(word in user_input_lower for word in ['package', 'packages', 'service', 'services', 'options', 'recommend', 'show me', 'what do you offer', 'available']):
            return "recommender"
        
        # Proposal/pricing requests - but check if we have recommendations first
        if any(word in user_input_lower for word in ['proposal', 'quote', 'pricing', 'cost', 'price', 'how much', 'budget', 'investment', 'detailed']):
            if conversation_state.recommended_packages and len(conversation_state.recommended_packages) > 0:
                return "writer"  # Have packages, can write proposal
            else:
                return "recommender"  # Need to show packages first
        
        # Hiring needs extraction (initial requirements)
        if any(word in user_input_lower for word in ['need', 'hire', 'looking for', 'want', 'positions', 'roles', 'developers', 'engineers']):
            if current_stage == "greeting" or not conversation_state.client_inquiry or not conversation_state.client_inquiry.roles:
                return "extractor"  # Extract requirements first
            else:
                return "recommender"  # Already have requirements, show packages
        
        # Follow-up questions (after recommendations made)
        if current_stage == "recommendation" and conversation_state.recommended_packages:
            # If they're asking questions or providing clarifications, stay in follow_up
            if any(word in user_input_lower for word in ['call', 'meeting', 'schedule', 'contact', 'when', 'how', 'what', 'why']):
                return "follow_up"
            # If they made a selection, go to writer
            else:
                return "writer"
        
        # Stage-based routing with improved logic
        if current_stage == "greeting":
            if len(user_input.split()) > 5:  # Detailed message after greeting
                return "extractor"
            else:
                return "greeter"
        
        elif current_stage == "inquiry":
            if conversation_state.client_inquiry and conversation_state.client_inquiry.roles:
                return "recommender"  # Have requirements, show packages
            else:
                return "extractor"  # Still need more info
        
        elif current_stage == "recommendation":
            if conversation_state.recommended_packages and len(conversation_state.recommended_packages) > 0:
                return "writer"  # Ready for proposal
            else:
                return "recommender"  # Show recommendations
        
        elif current_stage == "proposal":
            return "follow_up"  # Handle questions about proposal
        
        # Default fallback
        return "greeter"
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return list(self.agents.keys())
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "name": agent.name,
                "class": agent.__class__.__name__,
                "active": True
            }
        return status
