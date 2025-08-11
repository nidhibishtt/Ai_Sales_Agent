"""
Service recommendation engine for matching client inquiries to service packages
"""
from typing import List, Dict, Any, Tuple
from models.schemas import ClientInquiry, ServicePackage
from data.service_packages import SERVICE_PACKAGES, ROLE_SYNONYMS, INDUSTRY_SYNONYMS
from utils.helpers import calculate_similarity, normalize_text


class ServiceRecommendationEngine:
    """Engine for recommending appropriate service packages"""
    
    def __init__(self):
        self.service_packages = [ServicePackage(**package) for package in SERVICE_PACKAGES]
    
    def recommend_packages(self, client_inquiry: ClientInquiry, max_recommendations: int = 3) -> List[ServicePackage]:
        """Recommend service packages based on client inquiry"""
        
        # Calculate match scores for each package
        package_scores = []
        
        for package in self.service_packages:
            score = self._calculate_match_score(client_inquiry, package)
            package_scores.append((package, score))
        
        # Sort by score (descending) and return top recommendations
        package_scores.sort(key=lambda x: x[1], reverse=True)
        
        recommended_packages = []
        for package, score in package_scores[:max_recommendations]:
            if score > 0.1:  # Minimum threshold
                recommended_packages.append(package)
        
        return recommended_packages
    
    def _calculate_match_score(self, inquiry: ClientInquiry, package: ServicePackage) -> float:
        """Calculate match score between inquiry and package"""
        total_score = 0.0
        weight_sum = 0.0
        
        # Industry match (weight: 0.3)
        if inquiry.industry:
            industry_score = self._calculate_industry_match(inquiry.industry, package.target_industries)
            total_score += industry_score * 0.3
            weight_sum += 0.3
        
        # Role match (weight: 0.4)
        if inquiry.roles:
            role_score = self._calculate_role_match(inquiry.roles, package.target_roles)
            total_score += role_score * 0.4
            weight_sum += 0.4
        
        # Urgency match (weight: 0.1)
        if inquiry.urgency:
            urgency_score = self._calculate_urgency_match(inquiry.urgency.value, package)
            total_score += urgency_score * 0.1
            weight_sum += 0.1
        
        # Budget compatibility (weight: 0.2)
        if inquiry.budget_range:
            budget_score = self._calculate_budget_match(inquiry.budget_range, package.price_range)
            total_score += budget_score * 0.2
            weight_sum += 0.2
        
        # Return normalized score
        return total_score / weight_sum if weight_sum > 0 else 0.0
    
    def _calculate_industry_match(self, client_industry: str, package_industries: List[str]) -> float:
        """Calculate industry match score"""
        client_industry_normalized = normalize_text(client_industry)
        
        # Direct match
        for package_industry in package_industries:
            if client_industry_normalized == normalize_text(package_industry):
                return 1.0
        
        # Synonym match
        for standard_industry, synonyms in INDUSTRY_SYNONYMS.items():
            if client_industry_normalized in synonyms or client_industry_normalized == standard_industry:
                if standard_industry in [normalize_text(pi) for pi in package_industries]:
                    return 0.9
        
        # Similarity match
        max_similarity = 0.0
        for package_industry in package_industries:
            similarity = calculate_similarity(client_industry, package_industry)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_role_match(self, client_roles: List[str], package_roles: List[str]) -> float:
        """Calculate role match score"""
        if not client_roles or not package_roles:
            return 0.0
        
        total_score = 0.0
        
        for client_role in client_roles:
            best_match = 0.0
            
            # Direct match
            for package_role in package_roles:
                if normalize_text(client_role) == normalize_text(package_role):
                    best_match = 1.0
                    break
            
            # Synonym match
            if best_match < 1.0:
                for standard_role, synonyms in ROLE_SYNONYMS.items():
                    client_role_normalized = normalize_text(client_role)
                    if client_role_normalized in synonyms or client_role_normalized == standard_role:
                        if standard_role in [normalize_text(pr) for pr in package_roles]:
                            best_match = 0.9
                            break
            
            # Similarity match
            if best_match < 0.9:
                for package_role in package_roles:
                    similarity = calculate_similarity(client_role, package_role)
                    best_match = max(best_match, similarity)
            
            total_score += best_match
        
        return total_score / len(client_roles)
    
    def _calculate_urgency_match(self, client_urgency: str, package: ServicePackage) -> float:
        """Calculate urgency match score based on package timeline"""
        # Extract typical timeline weeks
        timeline_weeks = self._extract_timeline_weeks(package.typical_timeline)
        
        urgency_timeline_preference = {
            'urgent': 2,    # Need within 2 weeks
            'high': 4,      # Need within 4 weeks  
            'medium': 8,    # Need within 8 weeks
            'low': 12       # Flexible timeline
        }
        
        client_preferred_weeks = urgency_timeline_preference.get(client_urgency, 8)
        
        # Calculate match based on timeline compatibility
        if timeline_weeks <= client_preferred_weeks:
            return 1.0
        elif timeline_weeks <= client_preferred_weeks * 1.5:
            return 0.7
        elif timeline_weeks <= client_preferred_weeks * 2:
            return 0.4
        else:
            return 0.1
    
    def _extract_timeline_weeks(self, timeline_str: str) -> int:
        """Extract timeline in weeks from timeline string"""
        import re
        
        # Look for week patterns
        week_match = re.search(r'(\d+)[-–]?(\d+)?\s*weeks?', timeline_str.lower())
        if week_match:
            start_weeks = int(week_match.group(1))
            end_weeks = int(week_match.group(2)) if week_match.group(2) else start_weeks
            return (start_weeks + end_weeks) // 2
        
        # Look for month patterns and convert to weeks
        month_match = re.search(r'(\d+)[-–]?(\d+)?\s*months?', timeline_str.lower())
        if month_match:
            start_months = int(month_match.group(1))
            end_months = int(month_match.group(2)) if month_match.group(2) else start_months
            avg_months = (start_months + end_months) // 2
            return avg_months * 4  # Convert months to weeks
        
        # Default to 4 weeks if no pattern found
        return 4
    
    def _calculate_budget_match(self, client_budget: str, package_price: str) -> float:
        """Calculate budget compatibility score"""
        try:
            # Extract numeric values from budget strings
            client_range = self._extract_budget_range(client_budget)
            package_range = self._extract_budget_range(package_price)
            
            if not client_range or not package_range:
                return 0.5  # Neutral score if can't parse
            
            client_max = client_range[1] if len(client_range) > 1 else client_range[0]
            package_min = package_range[0]
            package_max = package_range[1] if len(package_range) > 1 else package_range[0]
            
            # Check if client budget can cover package minimum
            if client_max >= package_min:
                # Perfect match if client budget is within package range
                if client_max <= package_max:
                    return 1.0
                # Good match if client budget is higher than package range
                elif client_max <= package_max * 1.5:
                    return 0.8
                else:
                    return 0.6
            else:
                # Poor match if client budget is below package minimum
                budget_ratio = client_max / package_min
                return max(0.1, budget_ratio)
        
        except Exception:
            return 0.5  # Neutral score if calculation fails
    
    def _extract_budget_range(self, budget_str: str) -> List[int]:
        """Extract numeric budget values from budget string"""
        import re
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,]', '', budget_str)
        
        # Look for patterns like "80k-120k", "5000-15000", "10000"
        range_pattern = r'(\d+(?:\.\d+)?)\s*k?[-–]\s*(\d+(?:\.\d+)?)\s*k?'
        single_pattern = r'(\d+(?:\.\d+)?)\s*k?'
        
        range_match = re.search(range_pattern, cleaned, re.IGNORECASE)
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            
            # Convert k values to thousands
            if 'k' in budget_str.lower():
                min_val *= 1000
                max_val *= 1000
            
            return [int(min_val), int(max_val)]
        
        single_match = re.search(single_pattern, cleaned, re.IGNORECASE)
        if single_match:
            val = float(single_match.group(1))
            
            # Convert k values to thousands
            if 'k' in budget_str.lower():
                val *= 1000
            
            return [int(val)]
        
        return []
    
    def get_package_by_id(self, package_id: str) -> ServicePackage:
        """Get service package by ID"""
        for package in self.service_packages:
            if package.package_id == package_id:
                return package
        return None
    
    def get_all_packages(self) -> List[ServicePackage]:
        """Get all service packages"""
        return self.service_packages
