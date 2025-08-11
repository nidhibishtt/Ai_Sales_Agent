"""
Few-Shot Proposal Generation System
Advanced proposal creation using template-based few-shot prompting
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from models.schemas import ClientInquiry, UrgencyLevel, ServicePackage, ProposalResponse
from utils.helpers import format_list_for_display


class ProposalTemplate:
    """Template for different types of proposals"""
    
    def __init__(self, template_type: str, template_content: str, metadata: Dict[str, Any]):
        self.template_type = template_type
        self.template_content = template_content
        self.metadata = metadata


class FewShotProposalGenerator:
    """Advanced proposal generator with few-shot learning capabilities"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.proposal_templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, ProposalTemplate]:
        """Initialize few-shot proposal templates"""
        
        templates = {}
        
        # Technical roles template
        templates['technical'] = ProposalTemplate(
            template_type='technical',
            template_content="""
EXAMPLE 1:
Input: Need 2 senior React developers urgently in NYC, fintech company
Output:
Subject: Urgent: 2 Senior React Developers for Fintech - Premium Talent Available

Dear Hiring Manager,

I understand you need 2 senior React developers urgently for your fintech company in NYC. This is exactly the type of critical technical hiring we excel at.

**Our Approach:**
• Immediate access to pre-vetted senior React developers with fintech experience
• Fast-track interview process optimized for urgent needs
• Specialized screening for financial services compliance and technical depth

**What We Deliver:**
✓ 2 senior React developers (5+ years experience)
✓ Fintech domain expertise with regulatory knowledge
✓ NYC-based or willing to relocate
✓ Available for immediate start

**Timeline:**
- Initial candidates: 24-48 hours
- First interviews: Within 3-5 business days  
- Final selection: 1-2 weeks

**Our Fee Structure:**
20% of first year salary (standard rate for senior technical roles)
Guarantee: 90-day replacement warranty

I have 3 qualified candidates ready for immediate review. Can we schedule a brief call today to discuss your specific technical requirements?

Best regards,
[Recruiter Name]
""",
            metadata={'roles': ['developer', 'engineer'], 'urgency': 'urgent', 'industry': 'fintech'}
        )
        
        # Management roles template
        templates['management'] = ProposalTemplate(
            template_type='management',
            template_content="""
EXAMPLE 2:
Input: Looking for an experienced product manager for our SaaS startup, remote OK
Output:
Subject: Senior Product Manager for SaaS Startup - Remote Leadership Talent

Hello,

I specialize in placing senior product managers with SaaS startups, and I'm excited about your remote product management opportunity.

**Our Expertise:**
• Deep network in SaaS product management community
• Understanding of startup dynamics and scale challenges
• Remote work assessment and cultural fit evaluation

**Candidate Profile We'll Deliver:**
✓ 5+ years product management experience
✓ SaaS platform development background
✓ Remote work proficiency with distributed teams
✓ Startup experience with scale-up mindset

**Our Process:**
1. Comprehensive product strategy assessment
2. Technical collaboration skills evaluation  
3. Startup culture fit analysis
4. Reference checks with previous SaaS teams

**Investment:**
18% of first year salary
90-day guarantee period

I have 2 strong product managers from successful SaaS companies interested in remote opportunities. Both have experience scaling products from startup to enterprise.

Available for a discovery call this week?

Best regards,
[Recruiter Name]
""",
            metadata={'roles': ['manager'], 'level': 'senior', 'work_type': 'remote'}
        )
        
        return templates
    
    def generate_proposal(
        self, 
        client_inquiry: ClientInquiry, 
        recommended_package: ServicePackage,
        conversation_context: List[Dict[str, str]] = None
    ) -> ProposalResponse:
        """Generate a personalized proposal response using few-shot prompting"""
        
        try:
            # Prepare the prompt variables
            roles_display = format_list_for_display(client_inquiry.roles) if client_inquiry.roles else "Various positions"
            
            role_counts_display = ""
            if client_inquiry.role_counts:
                counts = [f"{count} {role}(s)" for role, count in client_inquiry.role_counts.items()]
                role_counts_display = ", ".join(counts)
            
            # Generate the main proposal using few-shot template
            template = self._select_template(client_inquiry)
            prompt = self._create_few_shot_prompt_for_package(client_inquiry, recommended_package, template, roles_display, role_counts_display)
            personalized_pitch = self.llm_service.generate(prompt)
            
            # Generate follow-up steps
            followup_prompt = self._build_followup_prompt(personalized_pitch, client_inquiry.urgency.value if client_inquiry.urgency else "medium")
            next_steps = self._parse_next_steps(self.llm_service.generate(followup_prompt))
            
            # Generate summary
            summary = self._generate_summary(client_inquiry, recommended_package)
            
            # Estimate timeline and price
            estimated_timeline = self._estimate_timeline(client_inquiry, recommended_package)
            price_estimate = self._generate_price_estimate(client_inquiry, recommended_package)
            
            return ProposalResponse(
                summary=summary,
                recommended_package=recommended_package,
                personalized_pitch=personalized_pitch,
                next_steps=next_steps,
                estimated_timeline=estimated_timeline,
                price_estimate=price_estimate
            )
            
        except Exception as e:
            print(f"Error generating proposal: {str(e)}")
            return self._generate_fallback_proposal(client_inquiry, recommended_package)
    
    def _select_template(self, inquiry: ClientInquiry) -> ProposalTemplate:
        """Select most appropriate template based on inquiry characteristics"""
        
        # Check for management roles
        management_keywords = ['manager', 'director', 'lead', 'head', 'vp', 'chief']
        if inquiry.roles:
            for role in inquiry.roles:
                if any(keyword in role.lower() for keyword in management_keywords):
                    return self.proposal_templates['management']
        
        # Default to technical template
        return self.proposal_templates['technical']
    
    def _create_few_shot_prompt_for_package(self, inquiry: ClientInquiry, package: ServicePackage, template: ProposalTemplate, roles_display: str, role_counts_display: str) -> str:
        """Create few-shot prompt with package-specific information"""
        
        # Calculate timeline based on urgency and package
        timeline = self._calculate_timeline(inquiry.urgency)
        
        prompt = f"""
You are a senior recruitment consultant creating a professional proposal. Use these examples to understand the style and structure:

{template.template_content}

Now create a similar proposal for this new inquiry:

**Client Inquiry Details:**
- Company: {inquiry.company_name or 'Not specified'}
- Industry: {inquiry.industry or 'Not specified'}
- Location: {inquiry.location or 'Not specified'}
- Roles: {roles_display}
- Role Counts: {role_counts_display}
- Experience Level: {inquiry.experience_level or 'Not specified'}
- Urgency: {inquiry.urgency.value if inquiry.urgency else 'medium'}
- Budget: {inquiry.budget_range or 'Not specified'}
- Requirements: {inquiry.additional_requirements or 'Standard requirements'}

**Recommended Service Package:**
- Package Name: {package.name}
- Description: {package.description}
- Key Features: {', '.join(package.features[:4]) if package.features else 'Comprehensive recruitment services'}
- Timeline: {package.typical_timeline}
- Success Rate: {package.success_rate}%
- Investment: {package.price_range}

**Guidelines:**
1. Write a compelling 3-paragraph proposal
2. Paragraph 1: Acknowledge their specific needs and timeline urgency
3. Paragraph 2: Explain why this {package.name} package is perfect (mention 2-3 key benefits)
4. Paragraph 3: Include success rate/timeline and clear next step
5. Tone: Professional, confident, results-focused
6. Length: 2-3 sentences per paragraph maximum
7. Use specific details from their requirements

Generate the proposal:
"""
        
        return prompt

    def _create_few_shot_prompt(self, inquiry: ClientInquiry, template: ProposalTemplate, user_input: str) -> str:
        """Create few-shot prompt with examples and current inquiry"""
        
        # Calculate timeline based on urgency
        timeline = self._calculate_timeline(inquiry.urgency)
        
        # Determine fee structure
        fee_structure = self._calculate_fee_structure(inquiry)
        
        prompt = f"""
You are a senior recruitment consultant creating a professional proposal. Use these examples to understand the style and structure:

{template.template_content}

Now create a similar proposal for this new inquiry:

**Client Inquiry:**
Input: {user_input}

**Extracted Details:**
- Company: {inquiry.company_name or 'Not specified'}
- Industry: {inquiry.industry or 'Not specified'}
- Location: {inquiry.location or 'Not specified'}
- Roles: {', '.join(inquiry.roles) if inquiry.roles else 'Not specified'}
- Role Counts: {inquiry.role_counts if inquiry.role_counts else 'Not specified'}
- Experience Level: {inquiry.experience_level or 'Not specified'}
- Urgency: {inquiry.urgency.value if inquiry.urgency else 'medium'}
- Budget: {inquiry.budget_range or 'Not specified'}
- Requirements: {inquiry.additional_requirements or 'Standard requirements'}

**Guidelines:**
1. Match the professional tone and structure from the examples
2. Customize the timeline based on urgency: {timeline}
3. Use appropriate fee structure: {fee_structure}
4. Include specific value propositions relevant to their industry/roles
5. End with a clear call-to-action
6. Keep the proposal concise but comprehensive
7. Use bullet points and formatting for readability

Generate the proposal:
"""
        
        return prompt
    
    def _calculate_timeline(self, urgency: Optional[UrgencyLevel]) -> str:
        """Calculate timeline based on urgency level"""
        
        if not urgency:
            return "1 week for initial candidates, 2 weeks for full process"
            
        timelines = {
            UrgencyLevel.URGENT: "24-48 hours for initial candidates, 3-5 days for interviews",
            UrgencyLevel.HIGH: "2-3 days for initial candidates, 1 week for interviews", 
            UrgencyLevel.MEDIUM: "1 week for initial candidates, 2 weeks for full process",
            UrgencyLevel.LOW: "1-2 weeks for comprehensive search, 3-4 weeks for completion"
        }
        
        return timelines.get(urgency, timelines[UrgencyLevel.MEDIUM])
    
    def _calculate_fee_structure(self, inquiry: ClientInquiry) -> str:
        """Calculate appropriate fee structure"""
        
        # Base rates by role type and level
        if inquiry.experience_level:
            if 'junior' in inquiry.experience_level.lower():
                return "12% of first year salary (junior rate)"
            elif 'senior' in inquiry.experience_level.lower():
                return "20% of first year salary (senior rate)"
            elif 'lead' in inquiry.experience_level.lower():
                return "22% of first year salary (leadership rate)"
        
        # Default rate
        return "18% of first year salary (standard rate)"
    
    def _enhance_proposal(self, proposal: str, inquiry: ClientInquiry) -> str:
        """Post-process and enhance the generated proposal"""
        
        # Add timestamp and reference
        current_time = datetime.now()
        reference_id = f"PROP-{current_time.strftime('%Y%m%d')}-{hash(str(inquiry)) % 10000:04d}"
        
        # Add header with reference
        enhanced = f"Proposal Reference: {reference_id}\n"
        enhanced += f"Generated: {current_time.strftime('%B %d, %Y')}\n"
        enhanced += "=" * 50 + "\n\n"
        enhanced += proposal
        
        # Add footer with next steps
        enhanced += "\n\n" + "=" * 50
        enhanced += "\n**Next Steps:**"
        enhanced += "\n1. Review and provide feedback on this proposal"
        enhanced += "\n2. Schedule discovery call to discuss specific requirements"
        enhanced += "\n3. Begin candidate sourcing immediately upon agreement"
        enhanced += "\n4. Provide regular updates throughout the search process"
        
        enhanced += f"\n\nReference ID: {reference_id}"
        enhanced += f"\nValid until: {(current_time + timedelta(days=7)).strftime('%B %d, %Y')}"
        
        return enhanced
    
    def _build_followup_prompt(self, proposal_text: str, urgency: str) -> str:
        """Generate follow-up prompt for next steps"""
        return f"""
Provide 4 bullet next steps (no numbering) after the following proposal.
Urgency level: {urgency}
Proposal:
---
{proposal_text}
---
Bullets ONLY.
"""
    
    def _parse_next_steps(self, next_steps_text: str) -> List[str]:
        """Parse next steps from LLM response"""
        import re
        
        # Split by lines and clean up
        lines = next_steps_text.strip().split('\n')
        next_steps = []
        
        for line in lines:
            # Remove bullet points, numbers, and extra spaces
            cleaned_line = re.sub(r'^[-•*\d.]+\s*', '', line.strip())
            if cleaned_line and len(cleaned_line) > 5:  # Filter out very short lines
                next_steps.append(cleaned_line)
        
        # If parsing failed, provide default next steps
        if not next_steps:
            next_steps = [
                "Schedule a 30-minute discovery call to discuss your specific needs",
                "Send detailed information about our recruitment process",
                "Provide case studies from similar successful placements",
                "Prepare a customized proposal with timeline and pricing"
            ]
        
        return next_steps[:5]  # Limit to 5 steps
    
    def _generate_summary(self, inquiry: ClientInquiry, package: ServicePackage) -> str:
        """Generate a brief summary of the proposal"""
        role_count = len(inquiry.roles) if inquiry.roles else 0
        role_text = f"{role_count} role{'s' if role_count != 1 else ''}" if role_count > 0 else "multiple roles"
        
        company_text = f" for {inquiry.company_name}" if inquiry.company_name else ""
        industry_text = f" in the {inquiry.industry} industry" if inquiry.industry else ""
        location_text = f" in {inquiry.location}" if inquiry.location else ""
        
        summary = f"Recommended {package.name} to help hire {role_text}{company_text}{industry_text}{location_text}."
        
        if inquiry.urgency and inquiry.urgency.value in ['urgent', 'high']:
            summary += f" Fast-track solution to meet {inquiry.urgency.value} timeline requirements."
        
        return summary
    
    def _estimate_timeline(self, inquiry: ClientInquiry, package: ServicePackage) -> str:
        """Estimate timeline based on inquiry and package"""
        base_timeline = package.typical_timeline
        
        # Adjust based on urgency
        if inquiry.urgency:
            if inquiry.urgency.value == 'urgent':
                return f"Expedited: {base_timeline} (prioritized processing)"
            elif inquiry.urgency.value == 'high':
                return f"Fast-track: {base_timeline}"
        
        # Adjust based on number of roles
        role_count = len(inquiry.roles) if inquiry.roles else 1
        if role_count > 3:
            import re
            # Extract weeks from timeline and add buffer
            weeks_match = re.search(r'(\d+)-(\d+)\s*weeks', base_timeline)
            if weeks_match:
                min_weeks = int(weeks_match.group(1))
                max_weeks = int(weeks_match.group(2))
                # Add 1-2 weeks for multiple roles
                return f"{min_weeks + 1}-{max_weeks + 2} weeks (multiple roles)"
        
        return base_timeline
    
    def _generate_price_estimate(self, inquiry: ClientInquiry, package: ServicePackage) -> str:
        """Generate price estimate based on inquiry"""
        base_price = package.price_range
        
        # If we have specific role counts, we can be more specific
        if inquiry.role_counts:
            total_roles = sum(inquiry.role_counts.values())
            if total_roles > 1:
                return f"{base_price} per role (estimated total for {total_roles} roles)"
        elif inquiry.roles and len(inquiry.roles) > 1:
            role_count = len(inquiry.roles)
            return f"{base_price} per role (estimated total for {role_count} roles)"
        
        return base_price
    
    def _generate_fallback_proposal(self, inquiry: ClientInquiry, package: ServicePackage) -> ProposalResponse:
        """Generate a fallback proposal when LLM fails"""
        
        roles_text = format_list_for_display(inquiry.roles) if inquiry.roles else "the positions"
        company_text = f" at {inquiry.company_name}" if inquiry.company_name else ""
        
        fallback_pitch = f"""
Thank you for your interest in our recruitment services. Based on your requirements for {roles_text}{company_text}, 
I recommend our {package.name}. 

This package is specifically designed for companies like yours and includes {', '.join(package.features[:3])}. 
With our {package.success_rate or 'high'} success rate and typical timeline of {package.typical_timeline}, 
we're confident we can help you find the right candidates.

I'd love to schedule a call to discuss how we can specifically help with your hiring needs. 
When would be a good time to connect?
        """.strip()
        
        default_next_steps = [
            "Schedule a discovery call to discuss your specific requirements",
            "Send detailed package information and case studies",
            "Provide client references from similar industries",
            "Prepare a customized proposal with pricing"
        ]
        
        return ProposalResponse(
            summary=self._generate_summary(inquiry, package),
            recommended_package=package,
            personalized_pitch=fallback_pitch,
            next_steps=default_next_steps,
            estimated_timeline=self._estimate_timeline(inquiry, package),
            price_estimate=self._generate_price_estimate(inquiry, package)
        )


# Legacy compatibility - ProposalGeneratorService remains for backward compatibility
class ProposalGeneratorService:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.few_shot_generator = FewShotProposalGenerator(llm_service)

    def _build_proposal_prompt(self, inquiry: ClientInquiry, package: ServicePackage, roles_display: str, role_counts_display: str) -> str:
        return f"""
You are a professional sales representative for a recruiting agency.
Create a personalized recruiting proposal for this client.

CLIENT DETAILS:
- Company: {inquiry.company_name or 'Client'}
- Industry: {inquiry.industry or 'Not specified'}
- Location: {inquiry.location or 'Not specified'}
- Roles needed: {roles_display}
- Quantities: {role_counts_display or 'Multiple positions'}
- Urgency: {(inquiry.urgency.value if inquiry.urgency else 'medium')}
- Budget: {inquiry.budget_range or 'To be discussed'}

RECOMMENDED PACKAGE:
- Name: {package.name}
- Description: {package.description}
- Key features: {', '.join(package.features[:4])}
- Timeline: {package.typical_timeline}
- Success rate: {package.success_rate}%
- Investment: {package.price_range}

Write a compelling 3-paragraph proposal:

Paragraph 1: Acknowledge their specific needs and show understanding
Paragraph 2: Explain why this package is perfect (mention 2-3 key benefits)
Paragraph 3: Include success rate/timeline and clear next step

Tone: Professional, confident, results-focused.
Length: 2-3 sentences per paragraph maximum.
"""

    def _build_followup_prompt(self, proposal_text: str, urgency: str) -> str:
        return f"""
Provide 4 bullet next steps (no numbering) after the following proposal.
Urgency level: {urgency}
Proposal:
---
{proposal_text}
---
Bullets ONLY.
"""
    
    def generate_proposal(
        self, 
        client_inquiry: ClientInquiry, 
        recommended_package: ServicePackage,
        conversation_context: List[Dict[str, str]] = None
    ) -> ProposalResponse:
        """Generate a personalized proposal response"""
        
        try:
            # Prepare the prompt variables
            roles_display = format_list_for_display(client_inquiry.roles) if client_inquiry.roles else "Various positions"
            
            role_counts_display = ""
            if client_inquiry.role_counts:
                counts = [f"{count} {role}(s)" for role, count in client_inquiry.role_counts.items()]
                role_counts_display = ", ".join(counts)
            
            # Generate the main proposal
            prompt = self._build_proposal_prompt(client_inquiry, recommended_package, roles_display, role_counts_display)
            personalized_pitch = self.llm_service.generate(prompt)
            followup_prompt = self._build_followup_prompt(personalized_pitch, client_inquiry.urgency.value if client_inquiry.urgency else "medium")
            next_steps = self._parse_next_steps(self.llm_service.generate(followup_prompt))
            
            # Generate summary
            summary = self._generate_summary(client_inquiry, recommended_package)
            
            # Estimate timeline and price
            estimated_timeline = self._estimate_timeline(client_inquiry, recommended_package)
            price_estimate = self._generate_price_estimate(client_inquiry, recommended_package)
            
            return ProposalResponse(
                summary=summary,
                recommended_package=recommended_package,
                personalized_pitch=personalized_pitch,
                next_steps=next_steps,
                estimated_timeline=estimated_timeline,
                price_estimate=price_estimate
            )
            
        except Exception as e:
            print(f"Error generating proposal: {str(e)}")
            return self._generate_fallback_proposal(client_inquiry, recommended_package)
    
    def _parse_next_steps(self, next_steps_text: str) -> List[str]:
        """Parse next steps from LLM response"""
        import re
        
        # Split by lines and clean up
        lines = next_steps_text.strip().split('\n')
        next_steps = []
        
        for line in lines:
            # Remove bullet points, numbers, and extra spaces
            cleaned_line = re.sub(r'^[-•*\d.]+\s*', '', line.strip())
            if cleaned_line and len(cleaned_line) > 5:  # Filter out very short lines
                next_steps.append(cleaned_line)
        
        # If parsing failed, provide default next steps
        if not next_steps:
            next_steps = [
                "Schedule a 30-minute discovery call to discuss your specific needs",
                "Send detailed information about our recruitment process",
                "Provide case studies from similar successful placements",
                "Prepare a customized proposal with timeline and pricing"
            ]
        
        return next_steps[:5]  # Limit to 5 steps
    
    def _generate_summary(self, inquiry: ClientInquiry, package: ServicePackage) -> str:
        """Generate a brief summary of the proposal"""
        role_count = len(inquiry.roles) if inquiry.roles else 0
        role_text = f"{role_count} role{'s' if role_count != 1 else ''}" if role_count > 0 else "multiple roles"
        
        company_text = f" for {inquiry.company_name}" if inquiry.company_name else ""
        industry_text = f" in the {inquiry.industry} industry" if inquiry.industry else ""
        location_text = f" in {inquiry.location}" if inquiry.location else ""
        
        summary = f"Recommended {package.name} to help hire {role_text}{company_text}{industry_text}{location_text}."
        
        if inquiry.urgency and inquiry.urgency.value in ['urgent', 'high']:
            summary += f" Fast-track solution to meet {inquiry.urgency.value} timeline requirements."
        
        return summary
    
    def _estimate_timeline(self, inquiry: ClientInquiry, package: ServicePackage) -> str:
        """Estimate timeline based on inquiry and package"""
        base_timeline = package.typical_timeline
        
        # Adjust based on urgency
        if inquiry.urgency:
            if inquiry.urgency.value == 'urgent':
                return f"Expedited: {base_timeline} (prioritized processing)"
            elif inquiry.urgency.value == 'high':
                return f"Fast-track: {base_timeline}"
        
        # Adjust based on number of roles
        role_count = len(inquiry.roles) if inquiry.roles else 1
        if role_count > 3:
            import re
            # Extract weeks from timeline and add buffer
            weeks_match = re.search(r'(\d+)-(\d+)\s*weeks', base_timeline)
            if weeks_match:
                min_weeks = int(weeks_match.group(1))
                max_weeks = int(weeks_match.group(2))
                # Add 1-2 weeks for multiple roles
                return f"{min_weeks + 1}-{max_weeks + 2} weeks (multiple roles)"
        
        return base_timeline
    
    def _generate_price_estimate(self, inquiry: ClientInquiry, package: ServicePackage) -> str:
        """Generate price estimate based on inquiry"""
        base_price = package.price_range
        
        # If we have specific role counts, we can be more specific
        if inquiry.role_counts:
            total_roles = sum(inquiry.role_counts.values())
            if total_roles > 1:
                return f"{base_price} per role (estimated total for {total_roles} roles)"
        elif inquiry.roles and len(inquiry.roles) > 1:
            role_count = len(inquiry.roles)
            return f"{base_price} per role (estimated total for {role_count} roles)"
        
        return base_price
    
    def _generate_fallback_proposal(self, inquiry: ClientInquiry, package: ServicePackage) -> ProposalResponse:
        """Generate a fallback proposal when LLM fails"""
        
        roles_text = format_list_for_display(inquiry.roles) if inquiry.roles else "the positions"
        company_text = f" at {inquiry.company_name}" if inquiry.company_name else ""
        
        fallback_pitch = f"""
Thank you for your interest in our recruitment services. Based on your requirements for {roles_text}{company_text}, 
I recommend our {package.name}. 

This package is specifically designed for companies like yours and includes {', '.join(package.features[:3])}. 
With our {package.success_rate or 'high'} success rate and typical timeline of {package.typical_timeline}, 
we're confident we can help you find the right candidates.

I'd love to schedule a call to discuss how we can specifically help with your hiring needs. 
When would be a good time to connect?
        """.strip()
        
        default_next_steps = [
            "Schedule a discovery call to discuss your specific requirements",
            "Send detailed package information and case studies",
            "Provide client references from similar industries",
            "Prepare a customized proposal with pricing"
        ]
        
        return ProposalResponse(
            summary=self._generate_summary(inquiry, package),
            recommended_package=package,
            personalized_pitch=fallback_pitch,
            next_steps=default_next_steps,
            estimated_timeline=self._estimate_timeline(inquiry, package),
            price_estimate=self._generate_price_estimate(inquiry, package)
        )
