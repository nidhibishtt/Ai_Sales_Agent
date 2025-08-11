"""
Recommender Agent - Handles service package recommendations
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from services.memory_service import MemoryService
from services.recommendation_engine import ServiceRecommendationEngine
from models.schemas import ServicePackage
from utils.helpers import format_list_for_display


class RecommenderAgent(BaseAgent):
    """Agent responsible for recommending appropriate service packages"""
    
    def __init__(self, memory_service: MemoryService, recommendation_engine: ServiceRecommendationEngine):
        super().__init__("recommender", memory_service)
        self.recommendation_engine = recommendation_engine
    
    def process(self, session_id: str, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process request and recommend appropriate service packages"""
        self.log_interaction(session_id, "processing_recommendation", {"input_length": len(user_input)})
        
        try:
            # Get conversation state
            conversation_state = self.memory_service.get_conversation_state(session_id)
            if not conversation_state or not conversation_state.client_inquiry:
                return self._handle_missing_inquiry(session_id, user_input)
            
            client_inquiry = conversation_state.client_inquiry
            
            # Get recommendations
            recommended_packages = self.recommendation_engine.recommend_packages(
                client_inquiry, 
                max_recommendations=3
            )
            
            if not recommended_packages:
                return self._handle_no_recommendations(session_id, client_inquiry)
            
            # Generate recommendation response
            response_text = self._generate_recommendation_response(client_inquiry, recommended_packages)
            
            # Add response to conversation history
            self.memory_service.add_message(session_id, "assistant", response_text, {
                "recommended_packages": [pkg.package_id for pkg in recommended_packages]
            })
            
            # Update conversation state
            self.memory_service.set_recommended_packages(session_id, recommended_packages)
            
            next_actions = self._generate_next_actions(recommended_packages)
            self.update_conversation_state(session_id, {
                'stage': 'recommendation',
                'recommended_packages': recommended_packages,
                'next_actions': next_actions
            })
            
            self.log_interaction(session_id, "recommendation_completed", {
                "packages_count": len(recommended_packages),
                "package_ids": [pkg.package_id for pkg in recommended_packages]
            })
            
            return {
                "response": response_text,
                "recommended_packages": [pkg.model_dump() for pkg in recommended_packages],
                "stage": "recommendation",
                "next_actions": next_actions,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error in recommendation process: {str(e)}")
            return self._generate_fallback_recommendation(session_id, user_input)
    
    def _generate_recommendation_response(self, client_inquiry, recommended_packages: List[ServicePackage]) -> str:
        """Generate recommendation response text without hallucinating details"""
        response_parts = []
        
        # Only mention explicitly provided information
        roles = getattr(client_inquiry, 'roles', []) or []
        industry = getattr(client_inquiry, 'industry', None)
        location = getattr(client_inquiry, 'location', None)
        urgency = getattr(client_inquiry, 'urgency', None)
        
        # Opening that reflects actual requirements
        if roles:
            roles_text = ', '.join(roles)
            response_parts.append(f"Based on your need for {roles_text}, I have the perfect solution!")
        else:
            response_parts.append("Based on your hiring requirements, I have great options for you!")
        
        # Add context only if explicitly provided
        context_parts = []
        if industry and industry.lower() != 'not specified':
            context_parts.append(f"industry: {industry}")
        if location and location.lower() != 'not specified':
            context_parts.append(f"location: {location}")
        if urgency and urgency.lower() not in ['not specified', 'flexible']:
            context_parts.append(f"timeline: {urgency}")
        
        if context_parts:
            response_parts.append(f"Given your {', '.join(context_parts)}, here's what I recommend:")
        
        # Present packages without assumptions
        for i, package in enumerate(recommended_packages, 1):
            if len(recommended_packages) > 1:
                response_parts.append(f"\n{i}. **{package.name}**")
            else:
                response_parts.append(f"\n**{package.name}**")
            
            response_parts.append(f"   {package.description}")
            
            # Highlight key features (top 3)
            key_features = package.features[:3]
            if key_features:
                features_text = format_list_for_display(key_features)
                response_parts.append(f"   Key features: {features_text}")
            
            # Add timeline and success rate
            response_parts.append(f"   Timeline: {package.typical_timeline}")
            if package.success_rate:
                response_parts.append(f"   Success rate: {package.success_rate}")
            
            response_parts.append(f"   Investment: {package.price_range}")
        
        # Call to action
        if len(recommended_packages) == 1:
            response_parts.append(f"\nWould you like me to prepare a detailed proposal for the {recommended_packages[0].name}?")
        else:
            response_parts.append("\nWhich option interests you most? I can prepare a detailed proposal for any of these packages.")
        
        return "\n".join(response_parts)
    
    def _generate_next_actions(self, recommended_packages: List[ServicePackage]) -> List[str]:
        """Generate next actions after recommendations"""
        return [
            "Wait for client to choose a package",
            "Answer questions about recommended packages",
            "Prepare detailed proposal for selected package",
            "Explain package features and benefits"
        ]
    
    def _handle_missing_inquiry(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Handle case where client inquiry is missing"""
        response = "I'd love to recommend the best solution for you! Could you first tell me about your hiring needs? What positions are you looking to fill?"
        
        self.memory_service.add_message(session_id, "assistant", response)
        self.update_conversation_state(session_id, {
            'stage': 'inquiry',
            'next_actions': ["Collect hiring requirements", "Extract client needs"]
        })
        
        return {
            "response": response,
            "stage": "inquiry",
            "success": True,
            "redirect": "inquiry"
        }
    
    def _handle_no_recommendations(self, session_id: str, client_inquiry) -> Dict[str, Any]:
        """Handle case where no suitable packages are found"""
        response = f"""I understand you're looking for {format_list_for_display(client_inquiry.roles) if client_inquiry.roles else 'talent'}. 
        While I don't have a perfect package match in our standard offerings, we absolutely can create a custom solution for your needs.
        
        Let me connect you with one of our senior consultants who can design a tailored recruitment strategy for your specific requirements. 
        Would you like me to schedule a call to discuss your custom hiring solution?"""
        
        self.memory_service.add_message(session_id, "assistant", response)
        self.update_conversation_state(session_id, {
            'stage': 'follow_up',
            'next_actions': ["Schedule custom consultation", "Connect with senior consultant"]
        })
        
        return {
            "response": response,
            "stage": "follow_up",
            "custom_solution_needed": True,
            "success": True
        }
    
    def _generate_fallback_recommendation(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Generate fallback recommendation when system fails"""
        self.log_interaction(session_id, "fallback_recommendation_used")
        
        fallback_response = """We have several excellent recruitment packages that could work for your needs:

        **Tech Startup Hiring Pack** - Perfect for technology roles with fast turnaround
        **Enterprise Hiring Solution** - Comprehensive solution for senior positions  
        **Volume Hiring Package** - Cost-effective for multiple similar roles

        Which type of hiring challenge are you facing? I can provide more details on the best option for you."""
        
        self.memory_service.add_message(session_id, "assistant", fallback_response)
        
        self.update_conversation_state(session_id, {
            'stage': 'recommendation',
            'next_actions': ["Clarify client needs", "Provide package details"]
        })
        
        return {
            "response": fallback_response,
            "stage": "recommendation",
            "success": True,
            "fallback": True
        }
    
    def get_package_details(self, session_id: str, package_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific package"""
        self.log_interaction(session_id, "package_details_requested", {"package_id": package_id})
        
        package = self.recommendation_engine.get_package_by_id(package_id)
        if not package:
            return {
                "error": "Package not found",
                "success": False
            }
        
        # Generate detailed description
        response_parts = [
            f"**{package.name}** - Detailed Information:",
            f"\n{package.description}",
            f"\n**Key Features:**"
        ]
        
        for feature in package.features:
            response_parts.append(f"• {feature}")
        
        response_parts.extend([
            f"\n**Timeline:** {package.typical_timeline}",
            f"**Investment:** {package.price_range}",
            f"**Success Rate:** {package.success_rate or 'High'}"
        ])
        
        if package.target_industries:
            response_parts.append(f"**Best for industries:** {', '.join(package.target_industries[:5])}")
        
        response_parts.append("\nWould you like me to prepare a personalized proposal for this package?")
        
        response_text = "\n".join(response_parts)
        
        # Add to conversation history
        self.memory_service.add_message(session_id, "assistant", response_text, {
            "package_details": package_id
        })
        
        return {
            "response": response_text,
            "package": package.dict(),
            "success": True
        }
    
    def compare_packages(self, session_id: str, package_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple packages side by side"""
        self.log_interaction(session_id, "package_comparison_requested", {"package_ids": package_ids})
        
        packages = []
        for package_id in package_ids:
            package = self.recommendation_engine.get_package_by_id(package_id)
            if package:
                packages.append(package)
        
        if not packages:
            return {"error": "No valid packages found for comparison", "success": False}
        
        # Generate comparison
        response_parts = ["Here's a comparison of your selected packages:\n"]
        
        for package in packages:
            response_parts.extend([
                f"**{package.name}:**",
                f"• Timeline: {package.typical_timeline}",
                f"• Investment: {package.price_range}",
                f"• Success Rate: {package.success_rate or 'High'}",
                f"• Best for: {', '.join(package.target_roles[:3])}",
                ""
            ])
        
        response_parts.append("Which package would you like to move forward with?")
        
        response_text = "\n".join(response_parts)
        
        # Add to conversation history
        self.memory_service.add_message(session_id, "assistant", response_text, {
            "package_comparison": package_ids
        })
        
        return {
            "response": response_text,
            "packages": [pkg.model_dump() for pkg in packages],
            "success": True
        }
