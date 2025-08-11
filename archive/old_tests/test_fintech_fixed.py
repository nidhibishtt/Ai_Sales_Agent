#!/usr/bin/env python3
"""
Fixed Agent Response Test for Fintech Startup Scenario
Handles the correct return format from start_conversation
"""

import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import EnhancedAISalesAgent

def test_fintech_startup_conversation():
    """Test the fintech startup conversation with proper handling"""
    
    print("🏦 FINTECH STARTUP CONVERSATION TEST")
    print("=" * 45)
    
    # Test input from user request
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    print(f"👤 User Input: {user_input}")
    print()
    
    try:
        # Initialize agent
        load_dotenv()
        agent = EnhancedAISalesAgent()
        print("✅ Agent initialized successfully")
        print()
        
        # Start conversation - this returns a dict with session info
        print("🚀 Starting conversation...")
        conversation_start = agent.start_conversation(user_input)
        
        # Extract session ID from the response
        if isinstance(conversation_start, dict):
            session_id = conversation_start.get('session_id')
            greeting_response = conversation_start.get('response', 'No greeting')
            print(f"📝 Session ID: {session_id}")
            print(f"🤖 Initial Greeting: {greeting_response}")
        else:
            session_id = conversation_start
            print(f"📝 Session ID: {session_id}")
        print()
        
        if not session_id:
            print("❌ Failed to get session ID")
            return False
        
        # Now test the main processing - since start_conversation already processed the initial message,
        # let's test with a follow-up question
        print("🔄 Testing follow-up interaction...")
        follow_up = "What packages do you recommend for our hiring needs?"
        response = agent.process_message(session_id, follow_up)
        
        print(f"👤 Follow-up: {follow_up}")
        if isinstance(response, dict):
            if response.get('error'):
                print(f"❌ Error: {response['error']}")
            else:
                agent_response = response.get('response', 'No response')
                print(f"🤖 Agent Response: {agent_response}")
        else:
            print(f"🤖 Agent Response: {response}")
        print()
        
        # Test service packages
        print("📦 Testing Service Packages...")
        try:
            packages = agent.get_service_packages()
            print(f"Available packages: {list(packages.keys())}")
            
            # Look for relevant packages for fintech/startup
            relevant_packages = []
            for pkg_name, pkg_info in packages.items():
                if any(keyword in pkg_name.lower() for keyword in ['tech', 'startup', 'fintech']):
                    relevant_packages.append(pkg_name)
            
            print(f"📊 Relevant packages for fintech startup: {relevant_packages}")
            
        except Exception as e:
            print(f"⚠️  Package test failed: {e}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_expected_response_pattern():
    """Test if the greeting response matches expected sales patterns"""
    
    print("🎯 RESPONSE PATTERN ANALYSIS")
    print("=" * 35)
    
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    
    try:
        agent = EnhancedAISalesAgent()
        result = agent.start_conversation(user_input)
        
        # Get the greeting response
        greeting = result.get('response', '') if isinstance(result, dict) else str(result)
        print(f"🤖 Agent Greeting: '{greeting}'")
        print()
        
        # Analyze the greeting for expected sales behavior
        greeting_lower = greeting.lower() if greeting else ""
        
        # Expected patterns for a good sales response
        patterns = {
            "Professional greeting": any(word in greeting_lower for word in ['hello', 'hi', 'welcome', 'greetings']),
            "Shows helpfulness": any(phrase in greeting_lower for phrase in ['help', 'assist', 'support']),
            "Industry awareness": any(word in greeting_lower for word in ['recruiting', 'hiring', 'positions', 'talent']),
            "Asks for details": '?' in greeting,
            "Reasonable length": 20 <= len(greeting) <= 200 if greeting else False
        }
        
        print("📋 GREETING ANALYSIS:")
        for pattern, found in patterns.items():
            status = "✅" if found else "❌"
            print(f"   {status} {pattern}")
        
        # Overall score
        score = sum(patterns.values())
        total = len(patterns)
        print(f"\n📊 Greeting Quality: {score}/{total} ({score/total*100:.1f}%)")
        
        # Test ideal response
        print(f"\n💡 EXPECTED PATTERN:")
        print(f"   User: 'We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently.'")
        print(f"   Expected: Acknowledge fintech industry, mention Mumbai location, recognize urgency")
        print(f"   Expected: Ask about budget/timeline, offer relevant packages")
        print(f"   Expected: 'Great! For fintech startups in Mumbai, we have specialized packages...'")
        
        return score >= total * 0.6  # 60% threshold for basic functionality
        
    except Exception as e:
        print(f"❌ Response pattern test failed: {e}")
        return False

def simulate_ideal_response():
    """Show what the ideal response should look like"""
    
    print("\n💯 IDEAL SALES AGENT RESPONSE")
    print("=" * 35)
    
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    
    ideal_response = """
🎯 IDEAL EXTRACTION:
   • Industry: fintech ✅
   • Location: Mumbai ✅  
   • Roles: [backend engineer, UI/UX designer] ✅
   • Count: 2 backend engineers + 1 designer ✅
   • Urgency: high ✅

🤖 IDEAL AGENT RESPONSE:
"Great! I understand you're a fintech startup in Mumbai looking to hire 2 backend engineers and a UI/UX designer urgently. 

For fintech companies with urgent hiring needs, I'd recommend our **Tech Startup Hiring Pack** which includes:
- Pre-vetted senior backend engineers with fintech experience
- UI/UX designers specialized in financial applications  
- Fast-track recruitment (2-3 weeks vs standard 4-6 weeks)
- Mumbai-based talent pool with competitive packages

Given your urgency, would you like me to prepare a detailed proposal with timelines and pricing for these 3 positions?"

🔄 EXPECTED FOLLOW-UP:
   • Ask about tech stack (React, Node.js, Python, etc.)
   • Inquire about budget range for each role
   • Discuss timeline expectations
   • Offer to schedule a consultation call
"""
    
    print(ideal_response)

if __name__ == "__main__":
    print("🧪 ENHANCED FINTECH STARTUP TEST")
    print("=" * 50)
    print("Scenario: Fintech startup in Mumbai needs urgent hiring")
    print("Testing: Agent response quality and sales behavior")
    print("=" * 50)
    
    # Test 1: Conversation flow
    conversation_success = test_fintech_startup_conversation()
    
    # Test 2: Response pattern analysis  
    pattern_success = test_expected_response_pattern()
    
    # Show ideal response
    simulate_ideal_response()
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    if conversation_success and pattern_success:
        print("🎉 TESTS PASSED - Agent handles fintech scenario adequately")
    elif conversation_success or pattern_success:
        print("⚠️  PARTIAL SUCCESS - Some functionality works")  
    else:
        print("❌ TESTS FAILED - Agent needs improvement")
    
    print("\n🔧 RECOMMENDATIONS:")
    print("   • Ensure real LLM provider (OpenAI/Claude/Gemini) for better extraction")
    print("   • Add fintech-specific industry knowledge")
    print("   • Improve location recognition (Mumbai)")
    print("   • Enhance urgency detection and response")
    print("=" * 50)
