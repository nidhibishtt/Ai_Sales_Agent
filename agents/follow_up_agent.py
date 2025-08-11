"""
Follow-up Agent - Handles scheduling and follow-up actions
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from services.memory_service import MemoryService
from utils.helpers import validate_email, validate_phone, extract_contact_info


class FollowUpAgent(BaseAgent):
    """Agent responsible for follow-up actions and scheduling"""
    
    def __init__(self, memory_service: MemoryService):
        super().__init__("follow_up", memory_service)
    
    def process(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process follow-up requests and scheduling"""
        self.log_interaction(session_id, "processing_follow_up", {"input_length": len(user_input)})
        
        try:
            # Analyze the type of follow-up request
            follow_up_type = self._analyze_follow_up_type(user_input)
            
            # Process based on type
            if follow_up_type == "schedule_call":
                return self._handle_call_scheduling(session_id, user_input, context)
            elif follow_up_type == "contact_info":
                return self._handle_contact_collection(session_id, user_input, context)
            elif follow_up_type == "send_materials":
                return self._handle_material_request(session_id, user_input, context)
            elif follow_up_type == "pricing_inquiry":
                return self._handle_pricing_inquiry(session_id, user_input, context)
            elif follow_up_type == "next_steps":
                return self._handle_next_steps(session_id, user_input, context)
            else:
                return self._handle_general_follow_up(session_id, user_input, context)
                
        except Exception as e:
            self.logger.error(f"Error in follow-up process: {str(e)}")
            return self._generate_fallback_follow_up(session_id, user_input)
    
    def _analyze_follow_up_type(self, user_input: str) -> str:
        """Analyze what type of follow-up is being requested"""
        user_input_lower = user_input.lower()
        
        # Call scheduling keywords
        call_keywords = ['call', 'phone', 'meeting', 'schedule', 'talk', 'discuss', 'consultation']
        if any(keyword in user_input_lower for keyword in call_keywords):
            return "schedule_call"
        
        # Contact info keywords
        contact_keywords = ['email', 'phone number', 'contact', 'reach me', 'send me']
        if any(keyword in user_input_lower for keyword in contact_keywords):
            return "contact_info"
        
        # Material request keywords
        material_keywords = ['send', 'brochure', 'information', 'details', 'proposal', 'case study']
        if any(keyword in user_input_lower for keyword in material_keywords):
            return "send_materials"
        
        # Pricing keywords
        pricing_keywords = ['price', 'cost', 'pricing', 'quote', 'budget', 'fee']
        if any(keyword in user_input_lower for keyword in pricing_keywords):
            return "pricing_inquiry"
        
        # Next steps keywords
        next_keywords = ['next', 'what now', 'proceed', 'move forward', 'continue']
        if any(keyword in user_input_lower for keyword in next_keywords):
            return "next_steps"
        
        return "general"
    
    def _handle_call_scheduling(self, session_id: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle call scheduling requests"""
        self.log_interaction(session_id, "call_scheduling_requested")
        
        # Extract potential time preferences from input
        time_preferences = self._extract_time_preferences(user_input)
        
        # Get conversation state to understand client context
        conversation_state = self.memory_service.get_conversation_state(session_id)
        client_inquiry = conversation_state.client_inquiry if conversation_state else None
        
        response_parts = []
        
        if time_preferences:
            response_parts.append(f"Perfect! I see you mentioned {time_preferences}.")
        
        response_parts.extend([
            "I'd love to schedule a 30-minute discovery call to discuss your hiring needs in detail.",
            "\nTo book your consultation, I'll need:",
            "• Your preferred day and time",
            "• Your phone number or preferred meeting method",
            "• Your email address for the calendar invite"
        ])
        
        # Add context-specific information
        if client_inquiry and client_inquiry.roles:
            response_parts.append(f"\nDuring our call, we'll dive deeper into your requirements for {', '.join(client_inquiry.roles)} and create a customized recruitment strategy.")
        
        response_parts.extend([
            "\nAvailable time slots:",
            "• Monday-Friday, 9 AM - 5 PM (your local time)", 
            "• Same-day appointments available for urgent needs",
            "\nHow would you prefer to connect? Phone call, video meeting, or in-person (if local)?"
        ])
        
        response_text = "\n".join(response_parts)
        
        # Add to conversation history
        self.memory_service.add_message(session_id, "assistant", response_text, {
            "follow_up_type": "call_scheduling",
            "time_preferences": time_preferences
        })
        
        # Update conversation state
        next_actions = [
            "Collect preferred meeting time",
            "Gather contact information",
            "Send calendar invite",
            "Prepare for discovery call"
        ]
        
        self.update_conversation_state(session_id, {
            'stage': 'follow_up',
            'next_actions': next_actions
        })
        
        return {
            "response": response_text,
            "stage": "follow_up",
            "follow_up_type": "call_scheduling",
            "next_actions": next_actions,
            "success": True
        }
    
    def _handle_contact_collection(self, session_id: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle contact information collection"""
        self.log_interaction(session_id, "contact_collection_requested")
        
        # Extract contact info from input
        contact_info = extract_contact_info(user_input)
        
        # Update client inquiry with contact info
        if contact_info:
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if conversation_state and conversation_state.client_inquiry:
                existing_contact = conversation_state.client_inquiry.contact_info or {}
                existing_contact.update(contact_info)
                conversation_state.client_inquiry.contact_info = existing_contact
                self.memory_service.update_client_inquiry(session_id, conversation_state.client_inquiry)
        
        response_parts = ["Great! I have your contact information."]
        
        if contact_info.get('email'):
            if validate_email(contact_info['email']):
                response_parts.append(f"I'll send our detailed information packet to {contact_info['email']}.")
            else:
                response_parts.append("The email address seems to have a formatting issue. Could you double-check it?")
        
        if contact_info.get('phone'):
            if validate_phone(contact_info['phone']):
                response_parts.append(f"I have your phone number as {contact_info['phone']}.")
            else:
                response_parts.append("Could you please provide a valid phone number for follow-up calls?")
        
        # If missing info, ask for it
        if not contact_info.get('email'):
            response_parts.append("What's the best email address to send you information?")
        
        if not contact_info.get('phone'):
            response_parts.append("What's a good phone number to reach you at?")
        
        response_parts.extend([
            "\nI'll follow up with:",
            "• Detailed service information and pricing",
            "• Relevant case studies from your industry",
            "• Next steps to get started",
            "\nIs there anything specific you'd like me to include?"
        ])
        
        response_text = "\n".join(response_parts)
        
        self.memory_service.add_message(session_id, "assistant", response_text, {
            "contact_info_collected": contact_info
        })
        
        return {
            "response": response_text,
            "contact_info": contact_info,
            "success": True
        }
    
    def _handle_material_request(self, session_id: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for materials and information"""
        self.log_interaction(session_id, "materials_requested")
        
        # Determine what materials are being requested
        materials = self._identify_requested_materials(user_input)
        
        response_parts = ["Absolutely! I'll prepare the following materials for you:"]
        
        available_materials = {
            "company_overview": "Company overview and service catalog",
            "pricing_guide": "Detailed pricing guide",
            "case_studies": "Relevant case studies from your industry",
            "process_overview": "Our recruitment process overview",
            "success_metrics": "Success rates and performance metrics",
            "testimonials": "Client testimonials and references"
        }
        
        if materials:
            for material in materials:
                if material in available_materials:
                    response_parts.append(f"• {available_materials[material]}")
        else:
            # Default materials package
            response_parts.extend([
                "• Company overview and service catalog",
                "• Pricing guide for your specific requirements",
                "• Case studies from similar companies",
                "• Our step-by-step recruitment process"
            ])
        
        response_parts.extend([
            "\nTo send these materials, I'll need your email address.",
            "What's the best email to send the information package to?",
            "\nI can have everything sent within the next hour!"
        ])
        
        response_text = "\n".join(response_parts)
        
        self.memory_service.add_message(session_id, "assistant", response_text, {
            "materials_requested": materials or list(available_materials.keys())
        })
        
        return {
            "response": response_text,
            "materials": materials,
            "success": True
        }
    
    def _handle_pricing_inquiry(self, session_id: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pricing and cost inquiries"""
        self.log_interaction(session_id, "pricing_inquiry")
        
        conversation_state = self.memory_service.get_conversation_state(session_id)
        client_inquiry = conversation_state.client_inquiry if conversation_state else None
        
        response_parts = ["I'd be happy to provide pricing information!"]
        
        # Provide general pricing context
        response_parts.extend([
            "\n**Our Pricing Structure:**",
            "• Based on role complexity and seniority level",
            "• Transparent, no hidden fees",
            "• Volume discounts for multiple roles",
            "• Flexible payment terms available"
        ])
        
        # Provide specific estimates if we have role information
        if client_inquiry and client_inquiry.roles:
            response_parts.append(f"\n**For your {', '.join(client_inquiry.roles)} requirements:**")
            response_parts.append("• I can provide a detailed quote based on your specific needs")
            response_parts.append("• Pricing includes all services from sourcing to placement")
            response_parts.append("• Replacement guarantee included at no extra cost")
        
        response_parts.extend([
            "\n**What's Included in Our Fee:**",
            "• Comprehensive candidate sourcing",
            "• Skills and cultural fit assessments", 
            "• Interview coordination and feedback",
            "• Reference and background checks",
            "• Offer negotiation support",
            "• 30-90 day replacement guarantee",
            "\nWould you like me to prepare a detailed quote for your specific requirements?"
        ])
        
        response_text = "\n".join(response_parts)
        
        self.memory_service.add_message(session_id, "assistant", response_text)
        
        return {
            "response": response_text,
            "success": True
        }
    
    def _handle_next_steps(self, session_id: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle next steps inquiries"""
        self.log_interaction(session_id, "next_steps_inquiry")
        
        conversation_state = self.memory_service.get_conversation_state(session_id)
        
        response_parts = ["Great question! Here's what happens next:"]
        
        # Provide next steps based on conversation stage
        current_stage = conversation_state.current_stage if conversation_state else "initial"
        
        if current_stage in ["greeting", "inquiry"]:
            response_parts.extend([
                "\n1. **Requirements Finalization** - We'll clarify any remaining details about your hiring needs",
                "2. **Service Recommendation** - I'll recommend the best package for your requirements",
                "3. **Proposal & Pricing** - You'll receive a detailed proposal with timeline and pricing",
                "4. **Agreement & Kickoff** - Once approved, we begin sourcing immediately"
            ])
        elif current_stage == "recommendation":
            response_parts.extend([
                "\n1. **Package Selection** - Choose the service package that best fits your needs",
                "2. **Detailed Proposal** - Receive customized proposal with specific timeline and pricing",
                "3. **Contract & Kickoff** - Sign agreement and we start sourcing candidates",
                "4. **Regular Updates** - Weekly progress reports and candidate presentations"
            ])
        elif current_stage == "proposal":
            response_parts.extend([
                "\n1. **Review Proposal** - Take time to review our recommended solution",
                "2. **Q&A Session** - Schedule call to address any questions",
                "3. **Contract Signing** - Finalize agreement and payment terms",
                "4. **Project Kickoff** - Meet your dedicated recruiter and begin sourcing"
            ])
        else:
            response_parts.extend([
                "\n1. **Discovery Call** - 30-minute consultation to understand your needs",
                "2. **Custom Proposal** - Tailored solution with pricing and timeline",
                "3. **Agreement** - Review and sign service agreement",
                "4. **Recruitment Launch** - Begin active candidate sourcing"
            ])
        
        response_parts.extend([
            "\n**Timeline:** Most clients move from initial contact to active recruitment within 1-2 weeks.",
            "\nWhat would you like to focus on first? I can schedule a call, send more information, or answer any specific questions you have."
        ])
        
        response_text = "\n".join(response_parts)
        
        self.memory_service.add_message(session_id, "assistant", response_text)
        
        return {
            "response": response_text,
            "current_stage": current_stage,
            "success": True
        }
    
    def _handle_general_follow_up(self, session_id: str, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general follow-up requests"""
        self.log_interaction(session_id, "general_follow_up")
        
        response = """Thank you for your continued interest! I'm here to help you move forward with your hiring needs.

        Here's how I can assist you right now:
        
        📞 **Schedule a Call** - Let's discuss your requirements in detail
        📧 **Send Information** - Receive detailed service information and case studies  
        💰 **Get Pricing** - Receive a customized quote for your specific needs
        📋 **Review Options** - Go over our service packages again
        ⏭️ **Next Steps** - Understand the process to get started
        
        What would be most helpful for you right now?"""
        
        self.memory_service.add_message(session_id, "assistant", response)
        
        return {
            "response": response,
            "success": True
        }
    
    def _generate_fallback_follow_up(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Generate fallback follow-up response"""
        self.log_interaction(session_id, "fallback_follow_up_used")
        
        response = """I'd love to help you with the next steps! 

        Would you like to:
        • Schedule a consultation call to discuss your needs?
        • Receive detailed information about our services?
        • Get a customized quote for your hiring requirements?
        
        Let me know what would be most valuable for you, and I'll make it happen!"""
        
        self.memory_service.add_message(session_id, "assistant", response)
        
        return {
            "response": response,
            "success": True,
            "fallback": True
        }
    
    def _extract_time_preferences(self, text: str) -> str:
        """Extract time preferences from user input"""
        import re
        
        time_patterns = [
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(this week|next week|tomorrow|today)',
            r'(\d{1,2}:\d{2}|\d{1,2} (am|pm))',
            r'(morning|afternoon|evening)',
            r'(asap|urgent|soon)'
        ]
        
        found_times = []
        text_lower = text.lower()
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    found_times.extend([m for m in match if m])
                else:
                    found_times.append(match)
        
        return ", ".join(found_times) if found_times else None
    
    def _identify_requested_materials(self, text: str) -> List[str]:
        """Identify what materials are being requested"""
        text_lower = text.lower()
        materials = []
        
        material_keywords = {
            "company_overview": ["company", "overview", "about"],
            "pricing_guide": ["pricing", "price", "cost", "fee"],
            "case_studies": ["case study", "examples", "success stories"],
            "process_overview": ["process", "how it works", "methodology"],
            "success_metrics": ["success rate", "metrics", "performance"],
            "testimonials": ["testimonials", "reviews", "references"]
        }
        
        for material, keywords in material_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                materials.append(material)
        
        return materials
