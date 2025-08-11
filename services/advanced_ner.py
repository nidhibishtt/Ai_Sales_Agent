"""
Advanced NER Extraction with Hybrid LLM + Rule-Based Approach
Implements sophisticated entity extraction for recruiting inquiries
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from models.schemas import ClientInquiry, UrgencyLevel
from utils.helpers import normalize_text, find_role_counts, extract_contact_info


@dataclass
class EntityExtractionResult:
    """Result of entity extraction with confidence and metadata"""
    entities: Dict[str, Any]
    confidence_scores: Dict[str, float]
    extraction_method: str  # 'llm', 'rule_based', 'hybrid'
    extracted_inquiry: ClientInquiry
    metadata: Dict[str, Any]


class AdvancedNERService:
    """Enhanced NER service with multiple extraction strategies"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        
        # Enhanced role patterns
        self.role_patterns = {
            # Technical roles
            r'(\d+)?\s*(backend|back-end|back end)\s*(engineer|developer)s?': 'backend engineer',
            r'(\d+)?\s*(frontend|front-end|front end)\s*(engineer|developer)s?': 'frontend engineer', 
            r'(\d+)?\s*(fullstack|full-stack|full stack)\s*(engineer|developer)s?': 'fullstack engineer',
            r'(\d+)?\s*(software|dev)\s*(engineer|developer)s?': 'software engineer',
            r'(\d+)?\s*(web)\s*(developer|engineer)s?': 'web developer',
            r'(\d+)?\s*(mobile|ios|android)\s*(developer|engineer)s?': 'mobile developer',
            r'(\d+)?\s*(devops|dev ops)\s*(engineer)s?': 'devops engineer',
            r'(\d+)?\s*(data)\s*(scientist|engineer)s?': 'data scientist',
            r'(\d+)?\s*(ml|machine learning)\s*(engineer)s?': 'ml engineer',
            r'(\d+)?\s*(qa|quality assurance)\s*(engineer|tester)s?': 'qa engineer',
            
            # Design roles
            r'(\d+)?\s*(ui|ux|ui/ux|user experience|user interface)\s*(designer)s?': 'ux designer',
            r'(\d+)?\s*(product)\s*(designer)s?': 'product designer',
            r'(\d+)?\s*(graphic)\s*(designer)s?': 'graphic designer',
            
            # Management roles
            r'(\d+)?\s*(project)\s*(manager)s?': 'project manager',
            r'(\d+)?\s*(product)\s*(manager)s?': 'product manager',
            r'(\d+)?\s*(engineering)\s*(manager)s?': 'engineering manager',
            r'(\d+)?\s*(tech|technical)\s*(lead)s?': 'tech lead',
            
            # Business roles
            r'(\d+)?\s*(business)\s*(analyst)s?': 'business analyst',
            r'(\d+)?\s*(data)\s*(analyst)s?': 'data analyst',
            r'(\d+)?\s*(marketing)\s*(specialist|manager)s?': 'marketing specialist',
            r'(\d+)?\s*(sales)\s*(representative|manager)s?': 'sales representative',
        }
        
        # Location patterns
        self.location_patterns = {
            r'\b(nyc|new york city|new york|ny)\b': 'New York City',
            r'\b(sf|san francisco|san fran)\b': 'San Francisco', 
            r'\b(la|los angeles)\b': 'Los Angeles',
            r'\b(boston|bos)\b': 'Boston',
            r'\b(seattle|sea)\b': 'Seattle',
            r'\b(chicago|chi)\b': 'Chicago',
            r'\b(austin|atx)\b': 'Austin',
            r'\b(denver|den)\b': 'Denver',
            r'\b(remote|remotely|work from home|wfh)\b': 'Remote',
            r'\b(mumbai|bangalore|delhi|hyderabad)\b': lambda m: m.group(1).title(),
            r'\b(london|toronto|vancouver)\b': lambda m: m.group(1).title(),
        }
        
        # Industry patterns
        self.industry_patterns = {
            r'\b(fintech|financial technology)\b': 'fintech',
            r'\b(finance|financial services|banking)\b': 'finance',
            r'\b(tech|technology|software)\b': 'technology',
            r'\b(healthcare|medical|pharma|pharmaceutical)\b': 'healthcare',
            r'\b(ecommerce|e-commerce|retail)\b': 'ecommerce',
            r'\b(consulting|consultancy)\b': 'consulting',
            r'\b(startup|start-up)\b': 'startup',
            r'\b(saas|software as a service)\b': 'saas',
            r'\b(ai|artificial intelligence|ml|machine learning)\b': 'ai/ml',
            r'\b(blockchain|crypto|cryptocurrency)\b': 'blockchain',
        }
        
        # Experience patterns
        self.experience_patterns = {
            r'\b(junior|entry|entry-level|entry level|fresher|0-2 years?)\b': 'junior',
            r'\b(mid|mid-level|mid level|middle|intermediate|2-5 years?|3-6 years?)\b': 'mid-level',
            r'\b(senior|sr|experienced|5\+ years?|6\+ years?|7\+ years?)\b': 'senior',
            r'\b(lead|principal|staff|10\+ years?|expert)\b': 'lead',
        }
        
        # Urgency patterns  
        self.urgency_patterns = {
            r'\b(urgent|asap|immediately|emergency|critical)\b': 'urgent',
            r'\b(quickly|soon|fast|high priority|rush)\b': 'high',
            r'\b(flexible|no rush|low priority|when possible|eventually)\b': 'low',
            r'\b(standard|normal|regular|medium priority)\b': 'medium',
        }
        
        # Budget patterns
        self.budget_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:k|000)?)\s*-?\s*\$?(\d{1,3}(?:,\d{3})*(?:k|000)?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:k|000)?)\s*(?:per|/)\s*(?:year|annum)',
            r'(\d{1,3}(?:,\d{3})*(?:k|000)?)\s*-\s*(\d{1,3}(?:,\d{3})*(?:k|000)?)\s*(?:range|budget)',
        ]
    
    def extract_entities(self, user_input: str) -> EntityExtractionResult:
        """Extract entities using hybrid LLM + rule-based approach"""
        
        # Try LLM extraction first
        try:
            llm_result = self._llm_extraction(user_input)
            if llm_result and self._validate_extraction(llm_result):
                return self._create_result(llm_result, user_input, 'llm')
        except Exception as e:
            print(f"LLM extraction failed: {e}")
        
        # Fallback to rule-based extraction
        try:
            rule_result = self._rule_based_extraction(user_input)
            return self._create_result(rule_result, user_input, 'rule_based')
        except Exception as e:
            print(f"Rule-based extraction failed: {e}")
            
        # Ultimate fallback - empty extraction
        return self._create_empty_result(user_input)
    
    def _llm_extraction(self, user_input: str) -> Dict[str, Any]:
        """Enhanced LLM-based entity extraction optimized for Groq"""
        # Import our optimized prompts
        from utils.groq_prompts import ENTITY_EXTRACTION_PROMPT
        
        # Use the specialized Groq-optimized prompt
        prompt = ENTITY_EXTRACTION_PROMPT.format(user_message=user_input)
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Clean the response to ensure it's valid JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            elif response.startswith('```'):
                response = response.replace('```', '').strip()
            
            # Parse JSON response
            result = json.loads(response)
            
            # Normalize and validate the extracted data
            normalized_result = self._normalize_entities(result)
            
            return normalized_result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}, Response: {response[:200]}...")
            return {}
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return {}
    
    def _normalize_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize extracted entities for consistency"""
        normalized = {}
        
        # Industry normalization
        industry = entities.get('industry', '').lower() if entities.get('industry') else None
        if industry:
            if 'fintech' in industry or 'financial tech' in industry:
                normalized['industry'] = 'fintech'
            elif 'finance' in industry or 'banking' in industry:
                normalized['industry'] = 'finance'
            elif 'tech' in industry or 'software' in industry:
                normalized['industry'] = 'technology'
            elif 'health' in industry or 'medical' in industry:
                normalized['industry'] = 'healthcare'
            elif 'ai' in industry or 'machine learning' in industry or 'ml' in industry:
                normalized['industry'] = 'ai/ml'
            else:
                normalized['industry'] = industry
        else:
            normalized['industry'] = None
            
        # Location normalization
        location = entities.get('location')
        if location and location.lower() != 'null':
            # Normalize common location names
            location_lower = location.lower()
            if 'mumbai' in location_lower or 'bombay' in location_lower:
                normalized['location'] = 'Mumbai'
            elif 'bangalore' in location_lower or 'bengaluru' in location_lower:
                normalized['location'] = 'Bangalore'
            elif 'delhi' in location_lower or 'new delhi' in location_lower:
                normalized['location'] = 'Delhi'
            elif 'remote' in location_lower:
                normalized['location'] = 'Remote'
            else:
                normalized['location'] = location.title()
        else:
            normalized['location'] = None
            
        # Roles normalization
        roles = entities.get('roles', [])
        if roles:
            normalized_roles = []
            for role in roles:
                if isinstance(role, str):
                    # Normalize role names
                    role_lower = role.lower()
                    if 'backend' in role_lower and ('engineer' in role_lower or 'developer' in role_lower):
                        normalized_roles.append('backend engineer')
                    elif 'frontend' in role_lower and ('engineer' in role_lower or 'developer' in role_lower):
                        normalized_roles.append('frontend engineer')
                    elif 'fullstack' in role_lower or 'full stack' in role_lower:
                        normalized_roles.append('fullstack developer')
                    elif 'ui' in role_lower and 'ux' in role_lower:
                        normalized_roles.append('ui/ux designer')
                    elif 'ux' in role_lower and ('designer' in role_lower or 'design' in role_lower):
                        normalized_roles.append('ux designer')
                    elif 'ui' in role_lower and ('designer' in role_lower or 'design' in role_lower):
                        normalized_roles.append('ui designer')
                    else:
                        normalized_roles.append(role.lower())
            normalized['roles'] = normalized_roles
        else:
            normalized['roles'] = []
            
        # Urgency normalization
        urgency = entities.get('urgency', '').lower() if entities.get('urgency') else 'medium'
        if 'urgent' in urgency or 'asap' in urgency or 'immediately' in urgency:
            normalized['urgency'] = 'urgent'
        elif 'high' in urgency:
            normalized['urgency'] = 'high' 
        elif 'low' in urgency:
            normalized['urgency'] = 'low'
        else:
            normalized['urgency'] = 'medium'
            
        # Copy other fields
        for field in ['company_size', 'budget', 'skills', 'count']:
            value = entities.get(field)
            if value and str(value).lower() != 'null':
                normalized[field] = value
            else:
                normalized[field] = None
                
        return normalized
        
        response = self.llm_service.generate(prompt)
        return self._parse_llm_response(response)
    
    def _rule_based_extraction(self, user_input: str) -> Dict[str, Any]:
        """Rule-based extraction using regex patterns"""
        text_lower = user_input.lower()
        
        # Extract roles with counts
        roles, role_counts = self._extract_roles_with_counts(text_lower)
        
        # Extract other entities
        location = self._extract_with_patterns(text_lower, self.location_patterns)
        industry = self._extract_with_patterns(text_lower, self.industry_patterns) 
        experience = self._extract_with_patterns(text_lower, self.experience_patterns)
        urgency = self._extract_with_patterns(text_lower, self.urgency_patterns) or 'medium'
        budget = self._extract_budget(text_lower)
        
        # Extract additional requirements
        tech_keywords = ['react', 'node', 'python', 'java', 'javascript', 'typescript', 
                        'aws', 'docker', 'kubernetes', 'sql', 'mongodb', 'postgresql']
        additional_reqs = []
        for tech in tech_keywords:
            if tech in text_lower:
                additional_reqs.append(tech)
        
        return {
            'company_name': self._extract_company_name(user_input),
            'industry': industry,
            'location': location,
            'roles': roles,
            'role_counts': role_counts,
            'urgency': urgency,
            'budget_range': budget,
            'experience_level': experience,
            'additional_requirements': ', '.join(additional_reqs) if additional_reqs else None
        }
    
    def _extract_roles_with_counts(self, text: str) -> Tuple[List[str], Dict[str, int]]:
        """Extract roles and their counts using regex patterns"""
        roles = []
        role_counts = {}
        
        for pattern, standard_role in self.role_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                count_str = match.group(1) if match.group(1) else None
                count = int(count_str) if count_str and count_str.isdigit() else 1
                
                if standard_role not in roles:
                    roles.append(standard_role)
                    role_counts[standard_role] = count
                else:
                    role_counts[standard_role] += count
        
        return roles, role_counts
    
    def _extract_with_patterns(self, text: str, patterns: Dict[str, str]) -> Optional[str]:
        """Extract entity using regex patterns"""
        for pattern, value in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if callable(value):
                    return value(match)
                return value
        return None
    
    def _extract_budget(self, text: str) -> Optional[str]:
        """Extract budget information"""
        for pattern in self.budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name using simple heuristics"""
        # Look for patterns like "at CompanyName" or "CompanyName is looking"
        patterns = [
            r'\bat\s+([A-Z][a-zA-Z\s]+?)(?:\s+(?:is|needs?|wants?|looking))',
            r'^([A-Z][a-zA-Z\s]+?)(?:\s+(?:is|needs?|wants?|looking))',
            r'(?:company|startup)\s+([A-Z][a-zA-Z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response with error handling"""
        try:
            # Clean the response
            response = response.strip()
            
            # Find JSON content
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Ensure required fields have proper defaults
                data.setdefault('roles', [])
                data.setdefault('role_counts', {})
                data.setdefault('urgency', 'medium')
                
                return data
            else:
                return self._get_empty_extraction()
                
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON")
            return self._get_empty_extraction()
    
    def _get_empty_extraction(self) -> Dict[str, Any]:
        """Return empty extraction with proper defaults"""
        return {
            'company_name': None,
            'industry': None,
            'location': None,
            'roles': [],
            'role_counts': {},
            'urgency': 'medium',
            'budget_range': None,
            'experience_level': None,
            'additional_requirements': None
        }
    
    def _validate_extraction(self, extraction: Dict[str, Any]) -> bool:
        """Validate extraction quality"""
        if not extraction:
            return False
        
        # Check if we have at least one role or some meaningful information
        has_roles = extraction.get('roles') and len(extraction['roles']) > 0
        has_location = extraction.get('location') is not None
        has_industry = extraction.get('industry') is not None
        
        return has_roles or has_location or has_industry
    
    def _create_result(self, extraction: Dict[str, Any], original_text: str, method: str) -> EntityExtractionResult:
        """Create extraction result with confidence scores"""
        
        # Calculate confidence scores
        confidence_scores = {}
        for key, value in extraction.items():
            if value is None:
                confidence_scores[key] = 0.0
            elif isinstance(value, str) and value.lower() in original_text.lower():
                confidence_scores[key] = 0.9
            elif isinstance(value, list) and value:
                confidence_scores[key] = 0.8
            else:
                confidence_scores[key] = 0.6 if method == 'llm' else 0.4
        
        # Create ClientInquiry
        try:
            urgency_value = extraction.get('urgency', 'medium')
            if urgency_value not in ['low', 'medium', 'high', 'urgent']:
                urgency_value = 'medium'
            
            client_inquiry = ClientInquiry(
                company_name=extraction.get('company_name'),
                industry=extraction.get('industry'),
                location=extraction.get('location'),
                roles=extraction.get('roles', []),
                role_counts=extraction.get('role_counts', {}),
                urgency=UrgencyLevel(urgency_value),
                budget_range=extraction.get('budget_range'),
                experience_level=extraction.get('experience_level'),
                additional_requirements=extraction.get('additional_requirements')
            )
        except Exception as e:
            print(f"Error creating ClientInquiry: {e}")
            client_inquiry = ClientInquiry()  # Empty inquiry with defaults
        
        return EntityExtractionResult(
            entities=extraction,
            confidence_scores=confidence_scores,
            extraction_method=method,
            extracted_inquiry=client_inquiry,
            metadata={
                'timestamp': datetime.utcnow().isoformat(),
                'original_text_length': len(original_text),
                'extraction_method': method
            }
        )
    
    def _create_empty_result(self, original_text: str) -> EntityExtractionResult:
        """Create empty result as ultimate fallback"""
        empty_extraction = self._get_empty_extraction()
        return self._create_result(empty_extraction, original_text, 'fallback')


# Factory function for backward compatibility
def create_advanced_ner_service(llm_service) -> AdvancedNERService:
    """Create advanced NER service with hybrid extraction"""
    return AdvancedNERService(llm_service)
