"""
Greeter Agent - Handles initial greetings and conversation setup
"""
from typing import Dict, Any

from .base_agent import BaseAgent
from services.memory_service import MemoryService
from utils.helpers import clean_llm_response


class GreeterAgent(BaseAgent):
    """Agent responsible for greeting prospects and initiating conversations"""
    
    def __init__(self, memory_service: MemoryService, llm_service):
        super().__init__("greeter", memory_service)
        self.llm_service = llm_service

    def _build_prompt(self, user_input: str, history_text: str) -> str:
        """Enhanced greeting prompt optimized for Groq and recruiting scenarios"""
        # Import our specialized prompts
        from utils.groq_prompts import GREETING_PROMPT
        
        # If this is an initial greeting, use the specialized prompt
        if not history_text or len(history_text.strip()) < 50:
            return GREETING_PROMPT
        
        # For follow-up interactions, use contextual response
        return f"""You are an expert recruiting assistant. 

CRITICAL: Only respond based on what the user ACTUALLY said. Do NOT hallucinate or assume information.

Previous conversation context:
{history_text}

User's current message: "{user_input}"

Respond professionally by:
1. Acknowledging ONLY what they explicitly mentioned
2. Showing understanding of their stated needs
3. Asking clarifying questions for missing information
4. NEVER assume details like company names, locations, or specific requirements not mentioned

Keep it professional, specific, and solution-focused. Max 2-3 sentences. Base response ONLY on facts provided."""
    
    def process(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process greeting and initial interaction"""
        self.log_interaction(session_id, "processing_greeting", {"input_length": len(user_input)})
        
        try:
            # Get conversation context
            conversation_history = self.get_conversation_context(session_id, message_limit=5)
            history_text = self._format_conversation_history(conversation_history)
            
            # Generate greeting response
            prompt = self._build_prompt(user_input, history_text)
            greeting_text = clean_llm_response(self.llm_service.generate(prompt))
            
            # Add response to conversation history
            self.memory_service.add_message(session_id, "assistant", greeting_text)
            
            # Update conversation state
            next_stage = self._determine_next_stage(user_input, conversation_history)
            next_actions = self._generate_next_actions(user_input, next_stage)
            
            self.update_conversation_state(session_id, {
                'stage': next_stage,
                'next_actions': next_actions
            })
            
            self.log_interaction(session_id, "greeting_completed", {
                "next_stage": next_stage,
                "response_length": len(greeting_text)
            })
            
            return {
                "response": greeting_text,
                "stage": next_stage,
                "next_actions": next_actions,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error in greeting process: {str(e)}")
            return self._generate_fallback_greeting(session_id, user_input)
    
    def _format_conversation_history(self, history: list) -> str:
        """Format conversation history for prompt"""
        if not history:
            return "This is the start of the conversation."
        
        formatted = []
        for msg in history[-5:]:  # Only use last 5 messages
            role = "Agent" if msg['role'] == "assistant" else "Client"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def _determine_next_stage(self, user_input: str, conversation_history: list) -> str:
        """Determine the next stage based on user input and conversation state"""
        user_input_lower = user_input.lower()
        
        # Check if user is already providing hiring details
        hiring_keywords = [
            'need', 'hire', 'looking for', 'want', 'positions', 'roles',
            'engineers', 'developers', 'designers', 'managers', 'analysts'
        ]
        
        if any(keyword in user_input_lower for keyword in hiring_keywords):
            return "inquiry"  # Skip to inquiry stage
        
        # Check if this is a follow-up message
        if len(conversation_history) > 2:
            return "inquiry"
        
        # Default to greeting for initial interactions
        return "greeting"
    
    def _generate_next_actions(self, user_input: str, next_stage: str) -> list:
        """Generate appropriate next actions"""
        if next_stage == "inquiry":
            return [
                "Extract hiring requirements from user input",
                "Ask clarifying questions about roles and timeline",
                "Understand budget and location preferences"
            ]
        else:
            return [
                "Wait for user to describe their hiring needs",
                "Build rapport and trust",
                "Guide conversation toward understanding requirements"
            ]
    
    def _generate_fallback_greeting(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Generate fallback greeting when LLM fails"""
        self.log_interaction(session_id, "fallback_greeting_used")
        
        # Simple rule-based greeting
        if any(word in user_input.lower() for word in ['hello', 'hi', 'hey']):
            greeting = "Hello! I'm excited to help you with your hiring needs. What positions are you looking to fill?"
        elif any(word in user_input.lower() for word in ['need', 'hire', 'looking']):
            greeting = "Great! I'd love to help you find the right candidates. Could you tell me more about the roles you need to fill?"
        else:
            greeting = "Hi there! Thanks for reaching out. I'm here to help you with your recruitment needs. What can I assist you with today?"
        
        # Add to conversation history
        self.memory_service.add_message(session_id, "assistant", greeting)
        
        # Update state
        self.update_conversation_state(session_id, {
            'stage': 'greeting',
            'next_actions': ["Wait for hiring requirements", "Build rapport"]
        })
        
        return {
            "response": greeting,
            "stage": "greeting",
            "next_actions": ["Wait for hiring requirements", "Build rapport"],
            "success": True,
            "fallback": True
        }
    
    def generate_follow_up_greeting(self, session_id: str) -> Dict[str, Any]:
        """Generate a follow-up greeting for returning users"""
        self.log_interaction(session_id, "follow_up_greeting")
        
        greetings = [
            "Welcome back! How can I help you with your hiring needs today?",
            "Good to see you again! Are you ready to continue discussing your recruitment requirements?",
            "Hello again! Let's pick up where we left off with your hiring plans."
        ]
        
        import random
        greeting = random.choice(greetings)
        
        # Add to conversation history
        self.memory_service.add_message(session_id, "assistant", greeting)
        
        return {
            "response": greeting,
            "stage": "greeting",
            "success": True
        }
