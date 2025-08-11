"""
Extractor Agent - Handles data extraction from client inquiries
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from services.memory_service import MemoryService
from services.advanced_ner import AdvancedNERService
from models.schemas import ClientInquiry


class ExtractorAgent(BaseAgent):
    """Agent responsible for extracting structured data from client inquiries"""
    
    def __init__(self, memory_service: MemoryService, ner_service: AdvancedNERService):
        super().__init__("extractor", memory_service)
        self.ner_service = ner_service
    
    def process(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and extract hiring requirements"""
        self.log_interaction(session_id, "processing_extraction", {"input_length": len(user_input)})
        
        try:
            # Extract entities from user input
            extraction_result = self.ner_service.extract_entities(user_input)
            
            # Get existing conversation state
            conversation_state = self.memory_service.get_conversation_state(session_id)
            
            # Merge with existing client inquiry if available
            if conversation_state and conversation_state.client_inquiry:
                merged_inquiry = self._merge_client_inquiries(
                    conversation_state.client_inquiry,
                    extraction_result.extracted_inquiry
                )
            else:
                merged_inquiry = extraction_result.extracted_inquiry
            
            # Update conversation state
            self.memory_service.update_client_inquiry(session_id, merged_inquiry)
            
            # Generate clarifying questions if needed
            clarifying_questions = self._generate_clarifying_questions(merged_inquiry, extraction_result.confidence_scores)
            
            # Determine next stage
            next_stage = "recommendation" if self._is_extraction_complete(merged_inquiry) else "inquiry"
            
            # Generate response
            response_text = self._generate_response(merged_inquiry, clarifying_questions, extraction_result.confidence_scores)
            
            # Add response to conversation history
            self.memory_service.add_message(session_id, "assistant", response_text)
            
            # Update conversation state
            self.update_conversation_state(session_id, {
                'stage': next_stage,
                'client_inquiry': merged_inquiry,
                'next_actions': self._generate_next_actions(merged_inquiry, clarifying_questions)
            })
            
            self.log_interaction(session_id, "extraction_completed", {
                "entities_extracted": len(extraction_result.entities),
                "roles_count": len(merged_inquiry.roles),
                "has_location": bool(merged_inquiry.location),
                "has_industry": bool(merged_inquiry.industry),
                "next_stage": next_stage
            })
            
            return {
                "response": response_text,
                "extracted_inquiry": merged_inquiry.dict(),
                "confidence_scores": extraction_result.confidence_scores,
                "clarifying_questions": clarifying_questions,
                "stage": next_stage,
                "extraction_complete": self._is_extraction_complete(merged_inquiry),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error in extraction process: {str(e)}")
            return self._generate_fallback_response(session_id, user_input)
    
    def _merge_client_inquiries(self, existing: ClientInquiry, new: ClientInquiry) -> ClientInquiry:
        """Merge existing client inquiry with newly extracted data"""
        # Create a new inquiry with merged data
        merged_data = existing.dict()
        new_data = new.dict()
        
        for key, value in new_data.items():
            if value is not None:
                if key == 'roles' and isinstance(value, list):
                    # Merge roles lists, avoiding duplicates
                    existing_roles = merged_data.get('roles', [])
                    merged_roles = list(set(existing_roles + value))
                    merged_data['roles'] = merged_roles
                elif key == 'role_counts' and isinstance(value, dict):
                    # Merge role counts
                    existing_counts = merged_data.get('role_counts', {})
                    existing_counts.update(value)
                    merged_data['role_counts'] = existing_counts
                elif key == 'contact_info' and isinstance(value, dict):
                    # Merge contact info
                    existing_contact = merged_data.get('contact_info', {})
                    existing_contact.update(value)
                    merged_data['contact_info'] = existing_contact
                else:
                    # For other fields, use new value if it exists
                    merged_data[key] = value
        
        return ClientInquiry(**merged_data)
    
    def _is_extraction_complete(self, inquiry: ClientInquiry) -> bool:
        """Check if we have enough information to proceed"""
        # Must have: roles
        if not inquiry.roles:
            return False
        
        # Must have: location 
        if not inquiry.location:
            return False
            
        # Must have: experience level
        if not inquiry.experience_level:
            return False
        
        # Good to have industry (but "it" is too generic)
        if not inquiry.industry or inquiry.industry.lower() in ['it', 'technology']:
            return False
            
        # If we have all the above, we can proceed
        return True
    
    def _generate_clarifying_questions(self, inquiry: ClientInquiry, confidence_scores: Dict[str, float]) -> list:
        """Generate questions to clarify missing or low-confidence information"""
        questions = []
        
        # Only ask about missing critical information
        if not inquiry.roles:
            questions.append("What specific roles or positions are you looking to fill?")
        
        # Ask about quantities only if we have multiple roles but no counts
        if inquiry.roles and len(inquiry.roles) > 1 and not inquiry.role_counts:
            questions.append("How many of each position do you need?")
        elif inquiry.roles and not inquiry.role_counts and len(inquiry.roles) == 1:
            questions.append(f"How many {inquiry.roles[0]}s do you need to hire?")
        
        # Only ask missing info (not already provided)
        if not inquiry.location:
            questions.append("What location should these candidates be based in?")
        
        if not inquiry.industry or inquiry.industry == "it":  # "IT" is too generic
            questions.append("What specific industry or business sector is your company in?")
        
        if not inquiry.experience_level:
            questions.append("What experience level are you looking for (junior, mid-level, senior)?")
            
        # Only ask about timeline if urgency is unclear
        if not inquiry.urgency or inquiry.urgency.value == 'medium':
            questions.append("What's your ideal timeline for these hires?")
        
        # Ask about additional requirements only if we have basic info
        if inquiry.roles and inquiry.location and not inquiry.additional_requirements:
            questions.append("Are there any specific technical skills or requirements for these roles?")
        
        return questions[:2]  # Limit to 2 questions maximum
    
    def _generate_response(self, inquiry: ClientInquiry, clarifying_questions: list, confidence_scores: Dict[str, float]) -> str:
        """Generate a response based on extracted information"""
        response_parts = []
        
        # Acknowledge what we understood
        if inquiry.roles:
            roles_text = ", ".join(inquiry.roles)
            response_parts.append(f"Perfect! I understand you need {roles_text}.")
            
            if inquiry.role_counts:
                counts_text = ", ".join([f"{count} {role}(s)" for role, count in inquiry.role_counts.items()])
                response_parts.append(f"Specifically, {counts_text}.")
        
        # Build acknowledgment of known details
        details = []
        if inquiry.location:
            details.append(f"in {inquiry.location}")
        if inquiry.industry and inquiry.industry != "it":  # Don't repeat "IT company"
            details.append(f"for your {inquiry.industry} company")
        if inquiry.experience_level:
            details.append(f"at {inquiry.experience_level} level")
        
        if details:
            response_parts.append(f"Based {', '.join(details)}.")
        
        # Mention urgency if specified
        if inquiry.urgency and inquiry.urgency.value != 'medium':
            urgency_text = {
                'urgent': 'I understand this is urgent',
                'high': 'I see you need them quickly',
                'low': 'I understand you can be flexible with timing'
            }.get(inquiry.urgency.value, '')
            if urgency_text:
                response_parts.append(f"{urgency_text}.")
        
        # Add clarifying questions only if needed and not already answered
        if clarifying_questions and len(clarifying_questions) > 0:
            response_parts.append("To finalize the best recommendations, I just need:")
            for i, question in enumerate(clarifying_questions, 1):
                response_parts.append(f"{i}. {question}")
        else:
            # Ready to move to next stage
            response_parts.append("Excellent! I have all the information needed to recommend the perfect service package for you.")
        
        return " ".join(response_parts)
    
    def _generate_next_actions(self, inquiry: ClientInquiry, clarifying_questions: list) -> list:
        """Generate next actions based on extraction results"""
        if clarifying_questions:
            return [
                "Wait for answers to clarifying questions",
                "Continue extracting missing information",
                "Build complete client profile"
            ]
        else:
            return [
                "Proceed to service recommendations",
                "Match client needs with service packages",
                "Prepare personalized proposals"
            ]
    
    def _generate_fallback_response(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Generate fallback response when extraction fails"""
        self.log_interaction(session_id, "fallback_extraction_used")
        
        fallback_response = """I'd love to help you find the right candidates! To get started, could you tell me:
        • What positions are you looking to fill?
        • How many of each role do you need?
        • What's your timeline for these hires?"""
        
        # Add to conversation history
        self.memory_service.add_message(session_id, "assistant", fallback_response)
        
        # Update state
        self.update_conversation_state(session_id, {
            'stage': 'inquiry',
            'next_actions': ["Collect basic hiring requirements", "Clarify role details"]
        })
        
        return {
            "response": fallback_response,
            "stage": "inquiry",
            "success": True,
            "fallback": True,
            "extraction_complete": False
        }
