#!/usr/bin/env python3
"""
Simple Agent Response Test for Fintech Startup Scenario
Tests the actual conversation flow and agent responses
"""

import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import EnhancedAISalesAgent

def test_agent_conversation():
    """Test the complete agent conversation flow"""
    
    print("🤖 AGENT CONVERSATION TEST")
    print("=" * 40)
    
    # Test input
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    print(f"👤 User: {user_input}")
    print()
    
    try:
        # Initialize agent
        load_dotenv()
        agent = EnhancedAISalesAgent()
        
        # Start conversation
        print("🚀 Starting conversation...")
        session_id = agent.start_conversation(user_input)
        print(f"📝 Session ID: {session_id}")
        print()
        
        # Get the greeting response
        print("💬 Agent Greeting:")
        history = agent.get_conversation_history(session_id, limit=2)
        if history.get('messages'):
            for msg in history['messages'][-2:]:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                if role == 'assistant':
                    print(f"🤖 Agent: {content}")
        print()
        
        # Process the hiring request
        print("🔄 Processing hiring request...")
        response = agent.process_message(session_id, user_input)
        print(f"🤖 Agent Response: {response}")
        print()
        
        # Test follow-up questions
        follow_ups = [
            "What's your budget range?",
            "Tell me more about your tech stack",
            "Yes, I'd like to see a proposal"
        ]
        
        for follow_up in follow_ups:
            print(f"👤 User: {follow_up}")
            response = agent.process_message(session_id, follow_up)
            print(f"🤖 Agent: {response}")
            print()
        
        # Get conversation summary
        print("📊 Conversation Summary:")
        try:
            summary = agent.get_session_summary(session_id)
            print(f"   • Stage: {summary.get('stage', 'Unknown')}")
            print(f"   • Messages: {summary.get('message_count', 0)}")
            if summary.get('extracted_requirements'):
                print(f"   • Requirements: {summary['extracted_requirements']}")
        except Exception as e:
            print(f"   ⚠️  Summary not available: {e}")
        
        # Test service packages
        print("\n📦 Available Service Packages:")
        packages = agent.get_service_packages()
        for pkg_name, pkg_info in packages.items():
            print(f"   • {pkg_name}: {pkg_info.get('description', 'No description')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_expected_behavior():
    """Test if the agent exhibits expected sales behavior"""
    
    print("\n🎯 EXPECTED BEHAVIOR VERIFICATION")
    print("=" * 40)
    
    user_input = "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently."
    
    try:
        agent = EnhancedAISalesAgent()
        session_id = agent.start_conversation(user_input)
        response = agent.process_message(session_id, user_input)
        
        # Check for expected patterns in response
        response_lower = response.lower() if response else ""
        
        expected_patterns = {
            "Acknowledges fintech": any(word in response_lower for word in ["fintech", "financial", "finance"]),
            "Mentions location": "mumbai" in response_lower,
            "Recognizes roles": any(word in response_lower for word in ["backend", "engineer", "designer", "ui", "ux"]),
            "Shows urgency awareness": any(word in response_lower for word in ["urgent", "quickly", "asap", "immediately"]),
            "Offers services": any(phrase in response_lower for phrase in ["recommend", "package", "proposal", "help"]),
            "Professional tone": len(response) > 50 if response else False  # Reasonable response length
        }
        
        print("✅ BEHAVIORAL CHECKS:")
        for check, passed in expected_patterns.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check}: {status}")
        
        print(f"\n📝 Full Response: '{response}'")
        
        # Score the response
        score = sum(expected_patterns.values())
        total = len(expected_patterns)
        percentage = (score / total) * 100
        
        print(f"\n📊 Response Quality Score: {score}/{total} ({percentage:.1f}%)")
        
        if percentage >= 70:
            print("🎉 GOOD: Agent response meets expectations!")
        elif percentage >= 50:
            print("⚠️  FAIR: Agent response partially meets expectations")
        else:
            print("❌ POOR: Agent response needs improvement")
        
        return score >= total * 0.7  # 70% threshold
        
    except Exception as e:
        print(f"❌ Behavior test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 FINTECH STARTUP - AGENT RESPONSE TEST")
    print("=" * 50)
    print("Testing: 'We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently.'")
    print("Expected: Extract fintech/Mumbai/roles, recommend Tech Startup pack, professional response")
    print("=" * 50)
    
    # Run conversation test
    conversation_success = test_agent_conversation()
    
    # Run behavior verification
    behavior_success = test_expected_behavior()
    
    print("\n" + "=" * 50)
    if conversation_success and behavior_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Agent successfully handles fintech startup scenario")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("🔧 Agent may need tuning for optimal responses")
    print("=" * 50)
