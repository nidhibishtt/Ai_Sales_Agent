#!/usr/bin/env python3
"""
Quick Test: Diagnose Fintech Scenario Issues
Tests NER extraction and routing without starting Flask server
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import only what we need without starting Flask
from services.advanced_ner import create_advanced_ner_service
from services.llm_service import LLMService
from dotenv import load_dotenv

def test_ner_extraction():
    """Test NER extraction for fintech scenario"""
    print("🔍 TESTING NER EXTRACTION")
    print("=" * 40)
    
    load_dotenv()
    
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    print(f"📝 Input: {user_input}")
    print()
    
    try:
        # Test NER extraction
        llm_service = LLMService()
        print(f"✅ LLM Service initialized: {llm_service.provider}")
        
        advanced_ner = create_advanced_ner_service(llm_service)
        print("✅ Advanced NER service created")
        
        # Extract entities
        result = advanced_ner.extract_entities(user_input)
        print(f"📊 Extraction Method: {result.extraction_method}")
        print(f"🎯 Extracted Entities:")
        for key, value in result.entities.items():
            print(f"   • {key}: {value}")
        
        print(f"🔥 Confidence Scores:")
        for key, score in result.confidence_scores.items():
            print(f"   • {key}: {score}")
        
        # Validate expected extractions
        entities = result.entities
        checks = {
            "Industry detected": bool(entities.get("industry")),
            "Location detected": bool(entities.get("location")),
            "Roles detected": bool(entities.get("roles")),
            "Urgency detected": bool(entities.get("urgency"))
        }
        
        print(f"\n✅ VALIDATION RESULTS:")
        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check}: {status}")
        
        return result
        
    except Exception as e:
        print(f"❌ NER Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_agent_routing():
    """Test agent routing logic"""
    print("\n🎯 TESTING AGENT ROUTING")
    print("=" * 40)
    
    try:
        # Load services
        load_dotenv()
        llm_service = LLMService()
        
        # Test different inputs for routing
        test_inputs = [
            "We are a fintech startup hiring engineers",
            "show me your packages", 
            "what services do you offer",
            "can you recommend something",
            "prepare a proposal for tech startup pack"
        ]
        
        from agents.base_agent import BaseAgent
        
        # Create a simple routing test
        base_agent = BaseAgent("test", llm_service)
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n{i}. Input: '{test_input}'")
            
            # Test routing decision (simplified)
            if any(word in test_input.lower() for word in ['package', 'service', 'recommend', 'options']):
                route = 'recommender'
            elif any(word in test_input.lower() for word in ['proposal', 'prepare', 'write']):
                route = 'writer'  
            else:
                route = 'extractor'
            
            print(f"   → Would route to: {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Routing Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_response():
    """Test basic LLM response"""
    print("\n🤖 TESTING LLM RESPONSE")
    print("=" * 40)
    
    try:
        load_dotenv()
        llm_service = LLMService()
        
        test_prompt = """
You are a helpful recruiting assistant. A user said:
"We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."

Respond professionally and ask relevant follow-up questions about their hiring needs.
"""
        
        print("🔄 Generating response...")
        response = llm_service.generate(test_prompt)
        print(f"🤖 LLM Response: {response}")
        
        # Check response quality
        response_lower = response.lower()
        quality_checks = {
            "Mentions fintech": "fintech" in response_lower,
            "Mentions Mumbai": "mumbai" in response_lower,
            "Mentions backend": "backend" in response_lower,
            "Mentions urgency": any(word in response_lower for word in ["urgent", "quickly", "asap", "timeline"]),
            "Asks questions": "?" in response
        }
        
        print(f"\n📝 RESPONSE QUALITY:")
        for check, passed in quality_checks.items():
            status = "✅ GOOD" if passed else "⚠️  MISSING"
            print(f"   {check}: {status}")
        
        return response
        
    except Exception as e:
        print(f"❌ LLM Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧪 QUICK DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Run all tests
    ner_result = test_ner_extraction()
    routing_result = test_agent_routing()
    llm_result = test_llm_response()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    print(f"🔍 NER Extraction: {'✅ WORKING' if ner_result else '❌ FAILED'}")
    print(f"🎯 Agent Routing: {'✅ WORKING' if routing_result else '❌ FAILED'}")
    print(f"🤖 LLM Response: {'✅ WORKING' if llm_result else '❌ FAILED'}")
    
    if ner_result and routing_result and llm_result:
        print("\n🎉 ALL CORE COMPONENTS WORKING!")
        print("💡 Issue might be in conversation flow or UI integration")
    else:
        print("\n⚠️  FOUND ISSUES - Check failed components above")
    
    print("=" * 50)
