"""
Utility functions for the AI Sales Agent
"""
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('sales_agent.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def normalize_text(text: str) -> str:
    """Normalize text for better matching"""
    if not text:
        return ""
    # Convert to lowercase and remove extra spaces
    text = re.sub(r'\s+', ' ', text.lower().strip())
    return text


def extract_numbers_from_text(text: str) -> List[int]:
    """Extract numbers from text"""
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]


def find_role_counts(text: str, roles: List[str]) -> Dict[str, int]:
    """Find role counts from text"""
    role_counts = {}
    text_lower = text.lower()
    
    for role in roles:
        role_lower = role.lower()
        # Look for patterns like "2 backend engineers", "3 designers", etc.
        patterns = [
            rf'(\d+)\s+{re.escape(role_lower)}',
            rf'{re.escape(role_lower)}.*?(\d+)',
            rf'(\d+).*?{re.escape(role_lower)}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                # Take the first number found
                try:
                    role_counts[role] = int(matches[0])
                    break
                except (ValueError, IndexError):
                    continue
    
    return role_counts


def calculate_similarity(text1: str, text2: str) -> float:
    """Simple similarity calculation based on common words"""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(normalize_text(text1).split())
    words2 = set(normalize_text(text2).split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def format_currency(amount: str) -> str:
    """Format currency string"""
    if not amount:
        return "Contact for pricing"
    return amount


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits) <= 15


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from text"""
    contact_info = {}
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]
    
    # Phone extraction
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
        r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
        r'\b\+\d{1,3}[-.\s]?\d{10,14}\b'  # International
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
            break
    
    return contact_info


def format_list_for_display(items: List[str], max_items: int = 5) -> str:
    """Format a list for display with proper grammar"""
    if not items:
        return "None specified"
    
    if len(items) > max_items:
        displayed_items = items[:max_items]
        return f"{', '.join(displayed_items[:-1])}, {displayed_items[-1]}, and {len(items) - max_items} others"
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return f"{', '.join(items[:-1])}, and {items[-1]}"


def safe_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().isoformat()


def clean_llm_response(response: str) -> str:
    """Clean LLM response by removing unwanted formatting"""
    if not response:
        return ""
    
    # Remove potential JSON formatting
    response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
    
    # Remove excessive newlines
    response = re.sub(r'\n{3,}', '\n\n', response)
    
    return response.strip()
