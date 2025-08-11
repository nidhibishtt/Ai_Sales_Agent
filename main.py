"""
Enhanced AI Sales Agent for Recruiting Agency
With premium LLM providers, advanced NER, and few-shot proposal generation
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Enhanced service imports
from services.llm_service import LLMService
from services.advanced_ner import create_advanced_ner_service, AdvancedNERService
from services.proposal_generator import FewShotProposalGenerator
from services.memory_service import create_enhanced_memory_service, EnhancedMemoryService

from agents import (
    AgentOrchestrator, GreeterAgent, ExtractorAgent, 
    RecommenderAgent, WriterAgent, FollowUpAgent
)
from services import (
    MemoryService, ServiceRecommendationEngine
)
from models.schemas import ClientInquiry
from utils.helpers import setup_logging, generate_session_id


class EnhancedAISalesAgent:
    """
    Enhanced AI Sales Agent with premium LLM providers and advanced capabilities
    """
    
    def __init__(self, db_path: str = "enhanced_sales_agent.db"):
        # Load environment variables
        load_dotenv()

        # Setup logging
        self.logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))
        self.logger.info("Initializing Enhanced AI Sales Agent")

        # Initialize enhanced LLM service with premium providers (GPT-4o, Gemini, Claude)
        self.llm_service = LLMService()
        provider_info = self.llm_service.info()
        self.logger.info(f"Active LLM provider: {provider_info['active']} (available: {provider_info['available']})")

        # Initialize enhanced services
        self.advanced_ner = create_advanced_ner_service(self.llm_service)
        self.few_shot_generator = FewShotProposalGenerator(self.llm_service)
        self.enhanced_memory = create_enhanced_memory_service(self.llm_service)
        
        # Initialize base services
        self.memory_service = MemoryService(db_path)
        self.recommendation_engine = ServiceRecommendationEngine()
        
        # Initialize orchestrator and agents
        self.orchestrator = AgentOrchestrator(self.memory_service)
        self._setup_enhanced_agents()
        
        self.logger.info("Enhanced AI Sales Agent initialized successfully")
    
    def _setup_enhanced_agents(self):
        """Setup enhanced agents with new capabilities"""
        # Create enhanced agents
        greeter_agent = GreeterAgent(self.memory_service, self.llm_service)
        
        # Enhanced extractor with advanced NER
        extractor_agent = ExtractorAgent(self.memory_service, self.advanced_ner)
        
        recommender_agent = RecommenderAgent(self.memory_service, self.recommendation_engine)
        
        # Enhanced writer with few-shot generation
        writer_agent = WriterAgent(self.memory_service, self.few_shot_generator)
        
        follow_up_agent = FollowUpAgent(self.memory_service)

        # Register agents
        self.orchestrator.register_agent(greeter_agent)
        self.orchestrator.register_agent(extractor_agent)
        self.orchestrator.register_agent(recommender_agent)
        self.orchestrator.register_agent(writer_agent)
        self.orchestrator.register_agent(follow_up_agent)

        self.logger.info(f"Registered {len(self.orchestrator.get_available_agents())} agents")
    
    def start_conversation(self, initial_message: str = None) -> Dict[str, Any]:
        """Start a new conversation session"""
        try:
            session_id = self.memory_service.create_session(initial_message)
            
            if initial_message:
                # Process the initial message
                response = self.orchestrator.route_request(session_id, initial_message)
                response['session_id'] = session_id
                response['new_session'] = True
                
                self.logger.info(f"Started conversation {session_id} with initial message")
                return response
            else:
                # Just return greeting for empty session
                greeting_response = {
                    'response': "Hello! I'm here to help you with your recruitment needs. What positions are you looking to fill?",
                    'session_id': session_id,
                    'stage': 'greeting',
                    'new_session': True,
                    'success': True
                }
                
                # Add greeting to conversation history
                self.memory_service.add_message(session_id, "assistant", greeting_response['response'])
                
                self.logger.info(f"Started conversation {session_id} with default greeting")
                return greeting_response
                
        except Exception as e:
            self.logger.error(f"Error starting conversation: {str(e)}")
            return {
                'error': 'Failed to start conversation',
                'success': False
            }
    
    def process_message(self, session_id: str, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user message in an existing conversation"""
        try:
            # Validate session
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state:
                return {
                    'error': 'Session not found. Please start a new conversation.',
                    'success': False
                }
            
            # Add user message to history
            self.memory_service.add_message(session_id, "user", user_message)
            
            # Route to appropriate agent
            response = self.orchestrator.route_request(session_id, user_message, context)
            
            self.logger.info(f"Processed message in session {session_id}, routed to {response.get('agent', 'unknown')}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return {
                'error': 'Failed to process message',
                'success': False,
                'session_id': session_id
            }
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> Dict[str, Any]:
        """Get conversation history for a session"""
        try:
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state:
                return {
                    'error': 'Session not found',
                    'success': False
                }
            
            history = self.memory_service.get_conversation_history(session_id, limit)
            
            return {
                'session_id': session_id,
                'history': history,
                'current_stage': conversation_state.current_stage,
                'client_inquiry': conversation_state.client_inquiry.dict() if conversation_state.client_inquiry else None,
                'recommended_packages': [pkg.model_dump() for pkg in conversation_state.recommended_packages],
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {str(e)}")
            return {
                'error': 'Failed to get conversation history',
                'success': False
            }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation session"""
        try:
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state:
                return {
                    'error': 'Session not found',
                    'success': False
                }
            
            client_inquiry = conversation_state.client_inquiry
            
            summary = {
                'session_id': session_id,
                'current_stage': conversation_state.current_stage,
                'created_at': conversation_state.created_at.isoformat(),
                'updated_at': conversation_state.updated_at.isoformat(),
                'message_count': len(conversation_state.conversation_history),
                'client_info': {
                    'company_name': client_inquiry.company_name,
                    'industry': client_inquiry.industry,
                    'location': client_inquiry.location,
                    'roles': client_inquiry.roles,
                    'role_counts': client_inquiry.role_counts,
                    'urgency': client_inquiry.urgency.value if client_inquiry.urgency else None,
                    'has_contact_info': bool(client_inquiry.contact_info)
                } if client_inquiry else {},
                'recommended_packages': len(conversation_state.recommended_packages),
                'next_actions': conversation_state.next_actions,
                'success': True
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting session summary: {str(e)}")
            return {
                'error': 'Failed to get session summary',
                'success': False
            }
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            analytics = self.memory_service.get_analytics_summary(days=days)
            
            # Add agent status
            analytics['agent_status'] = self.orchestrator.get_agent_status()
            analytics['available_agents'] = self.orchestrator.get_available_agents()
            
            return {
                'analytics': analytics,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analytics: {str(e)}")
            return {
                'error': 'Failed to get analytics',
                'success': False
            }
    
    def reset_conversation(self, session_id: str) -> Dict[str, Any]:
        """Reset a conversation to initial state"""
        try:
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state:
                return {
                    'error': 'Session not found',
                    'success': False
                }
            
            # Reset the conversation state
            conversation_state.current_stage = "greeting"
            conversation_state.client_inquiry = ClientInquiry()
            conversation_state.recommended_packages = []
            conversation_state.next_actions = []
            
            # Save updated state
            self.memory_service.save_conversation_state(conversation_state)
            
            # Add reset message
            self.memory_service.add_message(session_id, "system", "Conversation reset")
            
            self.logger.info(f"Reset conversation {session_id}")
            
            return {
                'session_id': session_id,
                'message': 'Conversation reset successfully',
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error resetting conversation: {str(e)}")
            return {
                'error': 'Failed to reset conversation',
                'success': False
            }
    
    def cleanup_old_sessions(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old session data"""
        try:
            deleted_count = self.memory_service.cleanup_old_sessions(days)
            
            self.logger.info(f"Cleaned up {deleted_count} old sessions")
            
            return {
                'deleted_sessions': deleted_count,
                'days': days,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {str(e)}")
            return {
                'error': 'Failed to clean up sessions',
                'success': False
            }
    
    def get_service_packages(self) -> Dict[str, Any]:
        """Get all available service packages"""
        try:
            packages = self.recommendation_engine.get_all_packages()
            
            return {
                'packages': [pkg.model_dump() for pkg in packages],
                'count': len(packages),
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting service packages: {str(e)}")
            return {
                'error': 'Failed to get service packages',
                'success': False
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        try:
            health_status = {
                'system': 'operational',
                'services': {
                    'memory': self._check_memory_service(),
                    'ner': self._check_ner_service(),
                    'recommendations': self._check_recommendation_engine(),
                    'proposals': self._check_proposal_generator()
                },
                'agents': {
                    'total': len(self.orchestrator.get_available_agents()),
                    'available': self.orchestrator.get_available_agents()
                },
                'database': self._check_database(),
                'success': True
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error in health check: {str(e)}")
            return {
                'system': 'error',
                'error': str(e),
                'success': False
            }
    
    def _check_memory_service(self) -> str:
        """Check memory service health"""
        try:
            # Try to get recent sessions
            self.memory_service.get_recent_sessions(days=1, limit=1)
            return "operational"
        except Exception:
            return "error"
    
    def _check_ner_service(self) -> str:
        """Check NER service health"""
        try:
            # Try a simple extraction
            result = self.ner_service.extract_entities("test message")
            return "operational" if result else "error"
        except Exception:
            return "error"
    
    def _check_recommendation_engine(self) -> str:
        """Check recommendation engine health"""
        try:
            packages = self.recommendation_engine.get_all_packages()
            return "operational" if packages else "error"
        except Exception:
            return "error"
    
    def _check_proposal_generator(self) -> str:
        """Check proposal generator health"""
        try:
            # This would require a full test, so just check if it's initialized
            return "operational" if self.proposal_generator else "error"
        except Exception:
            return "error"
    
    def _check_database(self) -> str:
        """Check database health"""
        try:
            with self.memory_service.get_db_connection() as conn:
                conn.execute("SELECT 1")
            return "operational"
        except Exception:
            return "error"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including performance metrics"""
        try:
            # Get basic health check
            health = self.health_check()
            
            # Add performance metrics
            analytics = self.get_analytics(days=1)
            
            # LLM provider info
            llm_info = {
                'provider': self.llm_service.active,
                'available_providers': list(self.llm_service.providers.keys()),
                'status': 'operational' if self.llm_service.is_available() else 'degraded'
            }
            
            status = {
                **health,
                'llm': llm_info,
                'performance': analytics.get('analytics', {}),
                'uptime': 'operational',
                'version': '2.0.0-enhanced'
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                'system': 'error',
                'error': str(e),
                'success': False
            }


# Convenience function for enhanced agent setup
def create_sales_agent(db_path: str = "enhanced_sales_agent.db", **_: Any) -> EnhancedAISalesAgent:
    """Create and return an enhanced AI Sales Agent with premium capabilities.

    Features: GPT-4o/Gemini/Claude integration, advanced NER, few-shot proposals.
    """
    return EnhancedAISalesAgent(db_path=db_path)


if __name__ == "__main__":
    # Example usage of Enhanced AI Sales Agent
    agent = EnhancedAISalesAgent()
    
    # Start conversation
    conversation_start = agent.start_conversation("Hello, I need help with hiring software engineers")
    session_id = conversation_start.get('session_id')
    print(f"Session started: {conversation_start}")
    
    # Process some messages
    if session_id:
        response = agent.process_message(session_id, "We need 3 senior Python developers for our fintech startup")
        print(f"Agent: {response}")
    
    # Show system status
    status = agent.get_system_status()
    print(f"System Status: {status}")
