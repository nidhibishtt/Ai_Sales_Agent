"""
Writer Agent - Handles proposal generation and writing
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from services.memory_service import MemoryService
from services.proposal_generator import FewShotProposalGenerator
from models.schemas import ProposalResponse


class WriterAgent(BaseAgent):
    """Agent responsible for generating proposals and written content"""
    
    def __init__(self, memory_service: MemoryService, proposal_generator: FewShotProposalGenerator):
        super().__init__("writer", memory_service)
        self.proposal_generator = proposal_generator
    
    def process(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process request and generate proposal"""
        self.log_interaction(session_id, "processing_proposal", {"input_length": len(user_input)})
        
        try:
            # Get conversation state
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state:
                return self._handle_missing_context(session_id, user_input)
            
            client_inquiry = conversation_state.client_inquiry
            recommended_packages = conversation_state.recommended_packages
            
            if not client_inquiry or not recommended_packages:
                return self._handle_incomplete_context(session_id, user_input)
            
            # Determine which package to create proposal for
            selected_package = self._select_package_from_input(
                user_input, recommended_packages, context
            )
            
            if not selected_package:
                return self._handle_package_selection(session_id, recommended_packages)
            
            # Generate conversation context
            conversation_history = self.get_conversation_context(session_id, message_limit=10)
            
            # Generate proposal
            proposal = self.proposal_generator.generate_proposal(
                client_inquiry, 
                selected_package,
                conversation_history
            )
            
            # Format the response
            response_text = self._format_proposal_response(proposal)
            
            # Add response to conversation history
            self.memory_service.add_message(session_id, "assistant", response_text, {
                "proposal_generated": True,
                "package_id": selected_package.package_id,
                "proposal_summary": proposal.summary
            })
            
            # Update conversation state
            next_actions = self._generate_next_actions(proposal)
            self.update_conversation_state(session_id, {
                'stage': 'proposal',
                'next_actions': next_actions
            })
            
            self.log_interaction(session_id, "proposal_generated", {
                "package_id": selected_package.package_id,
                "proposal_length": len(proposal.personalized_pitch),
                "next_steps_count": len(proposal.next_steps)
            })
            
            return {
                "response": response_text,
                "proposal": proposal.dict(),
                "stage": "proposal",
                "next_actions": next_actions,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error in proposal generation - Details: {str(e)}")
            self.logger.error(f"Session ID: {session_id}, User Input: {user_input}")
            self.logger.error(f"Context: {context}")
            # Check if we have recommendations, if not this request should go to recommender
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state.recommended_packages:
                return {"error": "No recommendations available, should route to recommender", "success": False}
            return self._generate_fallback_proposal(session_id, user_input)
    
    def _select_package_from_input(self, user_input: str, packages: list, context: Dict[str, Any] = None) -> 'ServicePackage':
        """Select package based on user input"""
        user_input_lower = user_input.lower().strip()
        
        # Check for direct package selection by number or option
        selection_patterns = {
            # Numbers
            '1': 0, '2': 1, '3': 2, '4': 3, '5': 4,
            # Options
            'option 1': 0, 'option 2': 1, 'option 3': 2, 'option 4': 3, 'option 5': 4,
            'option one': 0, 'option two': 1, 'option three': 2,
            # Ordinals
            'first': 0, 'second': 1, 'third': 2, 'fourth': 3, 'fifth': 4,
            'first option': 0, 'second option': 1, 'third option': 2,
            # Choice indicators
            'choose 1': 0, 'choose 2': 1, 'choose 3': 2,
            'select 1': 0, 'select 2': 1, 'select 3': 2,
            'go with 1': 0, 'go with 2': 1, 'go with 3': 2,
            'pick 1': 0, 'pick 2': 1, 'pick 3': 2,
            'i want 1': 0, 'i want 2': 1, 'i want 3': 2,
            'i choose 1': 0, 'i choose 2': 1, 'i choose 3': 2,
            'i select 1': 0, 'i select 2': 1, 'i select 3': 2,
            'i pick 1': 0, 'i pick 2': 1, 'i pick 3': 2,
            "i'll take 1": 0, "i'll take 2": 1, "i'll take 3": 2,
            'let me go with 1': 0, 'let me go with 2': 1, 'let me go with 3': 2,
        }
        
        # Check direct patterns first
        for pattern, index in selection_patterns.items():
            if pattern in user_input_lower and index < len(packages):
                return packages[index]
        
        # Check for package name or description keywords
        for package in packages:
            package_keywords = [
                package.name.lower(),
                package.package_id.lower()
            ]
            
            # Add specific keywords from package names
            if 'startup' in package.name.lower():
                package_keywords.extend(['startup', 'tech startup', 'small company', 'new company'])
            if 'enterprise' in package.name.lower():
                package_keywords.extend(['enterprise', 'large company', 'big company', 'corporation'])
            if 'volume' in package.name.lower():
                package_keywords.extend(['volume', 'bulk', 'multiple', 'many roles'])
            if 'executive' in package.name.lower():
                package_keywords.extend(['executive', 'leadership', 'senior', 'c-level'])
            if 'standard' in package.name.lower():
                package_keywords.extend(['standard', 'regular', 'normal', 'basic'])
            
            # Check if any keyword matches
            if any(keyword in user_input_lower for keyword in package_keywords):
                return package
        
        # Check context for previously selected package
        if context and 'selected_package_id' in context:
            for package in packages:
                if package.package_id == context['selected_package_id']:
                    return package
        
        # Check if user mentions specific package features
        if 'fast' in user_input_lower or 'quick' in user_input_lower or 'urgent' in user_input_lower:
            # Look for expedited packages
            for package in packages:
                if 'expedited' in package.name.lower() or 'fast' in package.name.lower():
                    return package
        
        # Default to first package if no clear selection
        return packages[0]
    
    def _format_proposal_response(self, proposal: ProposalResponse) -> str:
        """Format proposal response for display"""
        response_parts = []
        
        # Main proposal
        response_parts.append(proposal.personalized_pitch)
        
        # Package summary
        response_parts.append(f"\n**Package Summary:**")
        response_parts.append(f"• **{proposal.recommended_package.name}**")
        response_parts.append(f"• Timeline: {proposal.estimated_timeline}")
        response_parts.append(f"• Investment: {proposal.price_estimate or proposal.recommended_package.price_range}")
        
        # Next steps
        if proposal.next_steps:
            response_parts.append("\n**Suggested Next Steps:**")
            for i, step in enumerate(proposal.next_steps, 1):
                response_parts.append(f"{i}. {step}")
        
        return "\n".join(response_parts)
    
    def _generate_next_actions(self, proposal: ProposalResponse) -> List[str]:
        """Generate next actions after proposal"""
        return [
            "Wait for client response to proposal",
            "Answer questions about the package",
            "Schedule follow-up call if requested",
            "Prepare contract or detailed quote",
            "Connect client with account manager"
        ]
    
    def _handle_missing_context(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Handle case where conversation context is missing"""
        response = "I'd be happy to prepare a proposal for you! However, I need to understand your hiring needs first. Could you tell me what positions you're looking to fill?"
        
        self.memory_service.add_message(session_id, "assistant", response)
        self.update_conversation_state(session_id, {
            'stage': 'inquiry',
            'next_actions': ["Collect hiring requirements"]
        })
        
        return {
            "response": response,
            "stage": "inquiry",
            "success": True,
            "redirect": "inquiry"
        }
    
    def _handle_incomplete_context(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Handle case where we have incomplete context - redirect to recommender"""
        # Set the stage to recommendation so the orchestrator will route to recommender agent
        self.update_conversation_state(session_id, {
            'stage': 'recommendation',
            'next_actions': ["Generate service recommendations"]
        })
        
        return {
            "redirect_to": "recommender",
            "stage": "recommendation", 
            "success": True,
            "message": "Redirecting to show service packages"
        }
    
    def _handle_package_selection(self, session_id: str, packages: list) -> Dict[str, Any]:
        """Handle case where user needs to select a package"""
        response_parts = [
            "I have several great options for you! Which package would you like me to prepare a detailed proposal for?"
        ]
        
        for i, package in enumerate(packages, 1):
            response_parts.append(f"\n{i}. {package.name} - {package.description}")
        
        response_parts.append("\nJust let me know which one interests you most!")
        response_text = "\n".join(response_parts)
        
        self.memory_service.add_message(session_id, "assistant", response_text)
        
        return {
            "response": response_text,
            "stage": "recommendation",
            "packages": [pkg.model_dump() for pkg in packages],
            "success": True,
            "requires_selection": True
        }
    
    def _generate_fallback_proposal(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Generate fallback proposal when main system fails"""
        self.log_interaction(session_id, "fallback_proposal_used")
        
        fallback_response = """Thank you for your interest! Based on our conversation, I'm confident we can help you find excellent candidates.

        Here's what we offer:
        • Comprehensive candidate screening and evaluation
        • Fast turnaround times to meet your hiring deadlines  
        • Dedicated account management and support
        • Competitive pricing with flexible payment options
        • Strong track record of successful placements
        
        I'd love to schedule a 30-minute call to discuss your specific needs and provide you with a customized quote.
        
        When would be a good time for you to connect?"""
        
        self.memory_service.add_message(session_id, "assistant", fallback_response)
        
        self.update_conversation_state(session_id, {
            'stage': 'follow_up',
            'next_actions': ["Schedule consultation call", "Provide custom quote"]
        })
        
        return {
            "response": fallback_response,
            "stage": "follow_up",
            "success": True,
            "fallback": True
        }
    
    def generate_custom_content(self, session_id: str, content_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom content based on request"""
        self.log_interaction(session_id, "custom_content_requested", {"content_type": content_type})
        
        content_generators = {
            "case_study": self._generate_case_study,
            "pricing_breakdown": self._generate_pricing_breakdown,
            "timeline_details": self._generate_timeline_details,
            "success_stories": self._generate_success_stories
        }
        
        if content_type not in content_generators:
            return {
                "error": f"Content type '{content_type}' not supported",
                "success": False
            }
        
        try:
            content = content_generators[content_type](session_id, context)
            
            self.memory_service.add_message(session_id, "assistant", content, {
                "custom_content_type": content_type
            })
            
            return {
                "response": content,
                "content_type": content_type,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating custom content: {str(e)}")
            return {
                "error": "Failed to generate custom content",
                "success": False
            }
    
    def _generate_case_study(self, session_id: str, context: Dict[str, Any]) -> str:
        """Generate a relevant case study"""
        return """**Case Study: TechCorp's Rapid Team Expansion**

        *Challenge:* TechCorp needed to hire 5 backend engineers and 2 UI/UX designers within 6 weeks for a critical product launch.

        *Solution:* We used our Tech Startup Hiring Pack with expedited screening and our network of pre-vetted candidates.

        *Results:* 
        • All 7 positions filled in 4 weeks
        • 100% of hires passed probation period
        • Team successfully launched product on time
        • Client saved 40% compared to traditional recruiting

        This demonstrates how we can help you achieve similar success with your hiring goals!"""
    
    def _generate_pricing_breakdown(self, session_id: str, context: Dict[str, Any]) -> str:
        """Generate detailed pricing information"""
        return """**Pricing Breakdown:**

        Our pricing is transparent and value-driven:

        **What's Included:**
        • Comprehensive candidate sourcing and screening
        • Skills assessments and cultural fit evaluation  
        • Interview coordination and scheduling
        • Reference and background checks
        • Dedicated account manager
        • Replacement guarantee

        **Investment:** Based on role complexity and seniority
        • Junior roles: $5,000 - $8,000 per placement
        • Mid-level roles: $8,000 - $15,000 per placement  
        • Senior roles: $15,000 - $25,000 per placement

        **Volume Discounts:** Available for 3+ simultaneous roles
        **Payment Terms:** Flexible options available

        All pricing is discussed and agreed upon before we begin work."""
    
    def _generate_timeline_details(self, session_id: str, context: Dict[str, Any]) -> str:
        """Generate detailed timeline information"""
        return """**Detailed Timeline Breakdown:**

        **Week 1:** Kickoff & Strategy
        • Requirements gathering and role clarification
        • Sourcing strategy development
        • Initial candidate identification

        **Week 2-3:** Candidate Pipeline
        • Active sourcing and outreach
        • Initial screening interviews
        • Skills assessments

        **Week 3-4:** Client Interviews
        • Candidate presentation to client
        • Interview coordination
        • Feedback collection and next steps

        **Week 4+:** Final Steps
        • Final interviews and decision making
        • Offer negotiation support
        • Onboarding assistance

        **Typical Completion:** 3-6 weeks depending on role complexity and feedback speed.
        **Expedited Options:** Available for urgent requirements."""
    
    def _generate_success_stories(self, session_id: str, context: Dict[str, Any]) -> str:
        """Generate success stories"""
        return """**Recent Success Stories:**

        🚀 **Fintech Startup:** Helped scale engineering team from 3 to 15 developers in 3 months, enabling $10M Series A funding.

        🏥 **Healthcare Company:** Placed 8 specialized roles including Chief Medical Officer and VP of Engineering in under 2 months.

        📱 **Mobile App Company:** Found perfect Product Manager who led team to 1M+ app downloads within 6 months of hire.

        🎯 **E-commerce Platform:** Built entire data science team (5 roles) that increased conversion rates by 35%.

        These clients chose us because of our proven process, industry expertise, and commitment to finding not just candidates, but the right cultural fits who drive real business results.

        Ready to create your own success story?"""
