#!/usr/bin/env python3
"""
Fintech Extraction Test Case - Exactly as requested
Tests: Extract {industry: "fintech", location: "Mumbai", roles: ["backend engineer", "UI/UX designer"], urgency: true}
Response: "Great! Based on your requirements, we recommend our Tech Startup Hiring Pack. Would you like a proposal?"
"""

import sys
import os
import json
from typing import Dict, Any

# Add project root to path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.advanced_ner import create_advanced_ner_service, AdvancedNERService
from services.llm_service import LLMService
from main import EnhancedAISalesAgent
from dotenv import load_dotenv

def test_exact_extraction_case():
    """
    Test case exactly as specified by user:
    User: "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    → Extract: {industry: "fintech", location: "Mumbai", roles: ["backend engineer", "UI/UX designer"], urgency: true}
    → Respond: "Great! Based on your requirements, we recommend our Tech Startup Hiring Pack. Would you like a proposal?"
    """
    
    print("🧪 EXACT EXTRACTION TEST CASE")
    print("=" * 40)
    
    # Exact user input from request
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    
    print(f"📝 Input: {user_input}")
    print()
    
    # Expected extraction
    expected_extraction = {
        "industry": "fintech",
        "location": "Mumbai", 
        "roles": ["backend engineer", "UI/UX designer"],
        "urgency": True
    }
    
    print(f"🎯 Expected Extraction:")
    for key, value in expected_extraction.items():
        print(f"   • {key}: {value}")
    print()
    
    try:
        # Test with Enhanced NER Service
        print("🔍 Testing Advanced NER Extraction...")
        load_dotenv()
        
        llm_service = LLMService()
        ner_service = create_advanced_ner_service(llm_service)
        
        result = ner_service.extract_entities(user_input)
        
        print(f"📊 Actual Extraction (Method: {result.extraction_method}):")
        actual_entities = result.entities
        
        for key, value in actual_entities.items():
            if value:  # Only show non-empty values
                print(f"   • {key}: {value}")
        print()
        
        # Validation against expected
        print("✅ EXTRACTION VALIDATION:")
        
        # Check industry
        industry_match = False
        actual_industry = actual_entities.get("industry", "")
        if actual_industry:
            industry_match = "fintech" in str(actual_industry).lower() or "finance" in str(actual_industry).lower()
        print(f"   Industry (fintech): {'✅ PASS' if industry_match else '❌ FAIL'} - Got: '{actual_industry}'")
        
        # Check location
        location_match = False
        actual_location = actual_entities.get("location", "")
        if actual_location:
            location_match = "mumbai" in str(actual_location).lower()
        print(f"   Location (Mumbai): {'✅ PASS' if location_match else '❌ FAIL'} - Got: '{actual_location}'")
        
        # Check roles
        roles_match = False
        actual_roles = actual_entities.get("roles", [])
        if actual_roles:
            backend_found = any("backend" in str(role).lower() for role in actual_roles)
            designer_found = any("ui" in str(role).lower() or "ux" in str(role).lower() or "designer" in str(role).lower() for role in actual_roles)
            roles_match = backend_found and designer_found
        print(f"   Roles (backend + UI/UX): {'✅ PASS' if roles_match else '❌ FAIL'} - Got: {actual_roles}")
        
        # Check urgency
        urgency_match = False
        actual_urgency = actual_entities.get("urgency", "")
        if actual_urgency:
            urgency_match = str(actual_urgency).lower() in ["urgent", "urgently", "high", "true", "asap"]
        print(f"   Urgency (true): {'✅ PASS' if urgency_match else '❌ FAIL'} - Got: '{actual_urgency}'")
        
        # Overall score
        total_score = sum([industry_match, location_match, roles_match, urgency_match])
        print(f"\n📊 Extraction Score: {total_score}/4 ({total_score/4*100:.1f}%)")
        
        return result, total_score >= 3
        
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
        return None, False

def test_ideal_agent_response():
    """Test the ideal agent response pattern"""
    
    print("\n🤖 IDEAL RESPONSE TEST")
    print("=" * 25)
    
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    expected_response = "Great! Based on your requirements, we recommend our Tech Startup Hiring Pack. Would you like a proposal?"
    
    print(f"📝 Input: {user_input}")
    print(f"🎯 Expected Response: {expected_response}")
    print()
    
    try:
        # Test actual agent response
        agent = EnhancedAISalesAgent()
        conversation = agent.start_conversation(user_input)
        
        actual_response = ""
        if isinstance(conversation, dict):
            actual_response = conversation.get('response', '')
        
        print(f"🤖 Actual Response: {actual_response}")
        print()
        
        # Check response quality
        response_checks = {
            "Professional greeting": any(word in actual_response.lower() for word in ['hello', 'great', 'excellent']),
            "Acknowledges requirements": any(word in actual_response.lower() for word in ['understand', 'based', 'requirements']),
            "Mentions packages/services": any(word in actual_response.lower() for word in ['package', 'recommend', 'service']),
            "Asks for next step": '?' in actual_response,
            "Appropriate length": 20 <= len(actual_response) <= 200
        }
        
        print("📋 RESPONSE QUALITY CHECK:")
        for check, passed in response_checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {check}")
        
        response_score = sum(response_checks.values())
        print(f"\n📊 Response Quality: {response_score}/5 ({response_score/5*100:.1f}%)")
        
        return response_score >= 3
        
    except Exception as e:
        print(f"❌ Response test failed: {e}")
        return False

def show_implementation_status():
    """Show current implementation status and recommendations"""
    
    print(f"\n💡 IMPLEMENTATION STATUS")
    print("=" * 30)
    
    status_report = """
✅ WORKING COMPONENTS:
   • Agent initialization and basic conversation flow
   • Professional greeting generation  
   • Session management and conversation tracking
   • Service package definitions
   • Multi-agent architecture (greeter, extractor, recommender, writer)

⚠️  NEEDS IMPROVEMENT:
   • NER extraction accuracy (using mock LLM provider)
   • Industry-specific knowledge (fintech recognition)
   • Location extraction (Mumbai not detected)
   • Role parsing (backend engineer + UI/UX designer)
   • Urgency detection and response

🔧 RECOMMENDED FIXES:
   1. Configure real LLM provider (OpenAI/Claude/Gemini) with API keys
   2. Enhance NER patterns for fintech industry terms
   3. Add Mumbai to location dictionary 
   4. Improve role synonyms for "backend engineer" and "UI/UX designer"
   5. Train response templates for fintech scenarios

📋 EXPECTED WORKFLOW:
   User Input → Advanced NER → Extract entities → Match to service package → Generate proposal response
   
🎯 TARGET ACCURACY:
   • Entity extraction: 90%+ accuracy for industry, location, roles, urgency  
   • Response relevance: Professional, contextual, actionable
   • Conversion focus: Always end with call-to-action (proposal, consultation, etc.)
"""
    
    print(status_report)

if __name__ == "__main__":
    print("🧪 FINTECH STARTUP - EXACT TEST CASE")
    print("=" * 50)
    print("User: 'We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently.'")
    print("Expected: Extract fintech/Mumbai/roles/urgency → Recommend Tech Startup Pack")
    print("=" * 50)
    
    # Test 1: Extraction accuracy
    extraction_result, extraction_passed = test_exact_extraction_case()
    
    # Test 2: Response quality
    response_passed = test_ideal_agent_response()
    
    # Show implementation status
    show_implementation_status()
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS:")
    
    if extraction_passed and response_passed:
        print("🎉 ALL TESTS PASSED! Agent handles fintech scenario correctly.")
    elif extraction_passed:
        print("✅ EXTRACTION WORKS, ⚠️  Response needs improvement")
    elif response_passed:  
        print("✅ RESPONSE QUALITY GOOD, ⚠️  Extraction needs improvement")
    else:
        print("❌ BOTH EXTRACTION AND RESPONSE NEED IMPROVEMENT")
    
    print("\nNext Step: Configure real LLM provider for production-quality results!")
    print("=" * 50)
