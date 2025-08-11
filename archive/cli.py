"""
Command Line Interface for the AI Sales Agent
"""
import argparse
import json
import os
from main import EnhancedAISalesAgent
from dotenv import load_dotenv

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    AI Sales Agent                            ║
║                 Recruiting Agency Assistant                  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_response(response):
    """Print formatted response"""
    print("\n" + "="*60)
    print("🤖 AI Sales Agent:")
    print("="*60)
    print(response.get('response', 'No response available'))
    
    if response.get('stage'):
        print(f"\n📋 Stage: {response['stage']}")
    
    if response.get('next_actions'):
        print(f"\n⏭️  Next Actions:")
        for action in response['next_actions']:
            print(f"   • {action}")
    
    if not response.get('success'):
        print(f"\n❌ Error: {response.get('error', 'Unknown error')}")
    
    print("="*60)

def interactive_mode(agent):
    """Run in interactive conversation mode"""
    print("\n🚀 Starting interactive conversation mode")
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Type 'history' to see conversation history")
    print("Type 'summary' to see session summary")
    print("Type 'reset' to reset the conversation")
    print("-" * 60)
    
    session_id = None
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for using AI Sales Agent.")
                break
            
            if not user_input:
                continue
            
            if user_input.lower() == 'history':
                if session_id:
                    history_result = agent.get_conversation_history(session_id)
                    if history_result.get('success'):
                        print(f"\n📚 Conversation History (Session: {session_id[:8]}...):")
                        for msg in history_result['history']:
                            role_icon = "👤" if msg['role'] == 'user' else "🤖"
                            print(f"{role_icon} {msg['role'].title()}: {msg['content'][:100]}...")
                    else:
                        print(f"❌ Failed to get history: {history_result.get('error')}")
                else:
                    print("No active conversation session")
                continue
            
            if user_input.lower() == 'summary':
                if session_id:
                    summary_result = agent.get_session_summary(session_id)
                    if summary_result.get('success'):
                        print(f"\n📊 Session Summary:")
                        print(json.dumps(summary_result, indent=2, default=str))
                    else:
                        print(f"❌ Failed to get summary: {summary_result.get('error')}")
                else:
                    print("No active conversation session")
                continue
            
            if user_input.lower() == 'reset':
                if session_id:
                    reset_result = agent.reset_conversation(session_id)
                    if reset_result.get('success'):
                        print("✅ Conversation reset successfully")
                    else:
                        print(f"❌ Failed to reset: {reset_result.get('error')}")
                else:
                    print("No active conversation session")
                continue
            
            # Process message
            if not session_id:
                # Start new conversation
                response = agent.start_conversation(user_input)
                session_id = response.get('session_id')
                print(f"\n🆕 Started new conversation (ID: {session_id[:8]}...)")
            else:
                # Process message in existing conversation
                response = agent.process_message(session_id, user_input)
            
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using AI Sales Agent.")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def single_message_mode(agent, message):
    """Process a single message and exit"""
    print(f"\n🔄 Processing message: '{message}'")
    
    try:
        response = agent.start_conversation(message)
        print_response(response)
        
        # Show session summary
        session_id = response.get('session_id')
        if session_id:
            summary_result = agent.get_session_summary(session_id)
            if summary_result.get('success'):
                print(f"\n📋 Session ID: {session_id}")
                client_info = summary_result.get('client_info', {})
                if any(client_info.values()):
                    print(f"👤 Extracted Info: {json.dumps(client_info, indent=2, default=str)}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def run_health_check(agent):
    """Run system health check"""
    print("\n🏥 Running system health check...")
    
    try:
        health = agent.health_check()
        
        print(f"\n📊 System Status: {health.get('system', 'unknown').upper()}")
        
        if health.get('success'):
            print("\n✅ Services Status:")
            services = health.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status == "operational" else "❌"
                print(f"   {status_icon} {service.title()}: {status}")
            
            agent_info = health.get('agents', {})
            print(f"\n🤖 Agents: {agent_info.get('total', 0)} active")
            for agent_name in agent_info.get('available', []):
                print(f"   • {agent_name}")
            
            print(f"\n💾 Database: {health.get('database', 'unknown')}")
        else:
            print(f"\n❌ Error: {health.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")

def show_packages(agent):
    """Show available service packages"""
    print("\n📦 Available Service Packages:")
    
    try:
        packages_result = agent.get_service_packages()
        
        if packages_result.get('success'):
            packages = packages_result.get('packages', [])
            print(f"\nFound {len(packages)} service packages:\n")
            
            for i, pkg in enumerate(packages, 1):
                print(f"{i}. {pkg['name']}")
                print(f"   📝 {pkg['description']}")
                print(f"   💰 Price: {pkg['price_range']}")
                print(f"   ⏱️  Timeline: {pkg['typical_timeline']}")
                print(f"   🎯 Success Rate: {pkg.get('success_rate', 'N/A')}")
                print(f"   🏭 Industries: {', '.join(pkg['target_industries'][:3])}")
                print()
        else:
            print(f"❌ Failed to get packages: {packages_result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_analytics(agent, days=7):
    """Show analytics"""
    print(f"\n📈 Analytics (Last {days} days):")
    
    try:
        analytics_result = agent.get_analytics(days=days)
        
        if analytics_result.get('success'):
            analytics = analytics_result['analytics']
            
            print(f"   📊 Total Sessions: {analytics.get('total_sessions', 0)}")
            
            event_counts = analytics.get('event_counts', {})
            if event_counts:
                print("   🎯 Events:")
                for event, count in event_counts.items():
                    print(f"      • {event.replace('_', ' ').title()}: {count}")
            
            agent_status = analytics.get('agent_status', {})
            if agent_status:
                print("   🤖 Agents:")
                for name, info in agent_status.items():
                    status = "✅" if info.get('active') else "❌"
                    print(f"      • {name}: {status}")
        else:
            print(f"❌ Failed to get analytics: {analytics_result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main CLI application"""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="AI Sales Agent - Recruiting Agency Assistant")
    parser.add_argument('--message', '-m', type=str, help='Send a single message and exit')
    parser.add_argument('--health', action='store_true', help='Run health check and exit')
    parser.add_argument('--packages', action='store_true', help='Show service packages and exit')
    parser.add_argument('--analytics', action='store_true', help='Show analytics and exit')
    parser.add_argument('--days', type=int, default=7, help='Days for analytics (default: 7)')
    parser.add_argument('--db-path', type=str, default='sales_agent.db', help='Database path (default: sales_agent.db)')
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        # Initialize agent
        print("🚀 Initializing AI Sales Agent...")
        agent = EnhancedAISalesAgent(db_path=args.db_path)
        print("✅ AI Sales Agent initialized successfully!")
        
        # Handle different modes
        if args.health:
            run_health_check(agent)
        elif args.packages:
            show_packages(agent)
        elif args.analytics:
            show_analytics(agent, args.days)
        elif args.message:
            single_message_mode(agent, args.message)
        else:
            interactive_mode(agent)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Failed to start AI Sales Agent: {str(e)}")
        print("💡 Tip: The system can run with free providers (Groq / local) even without OpenAI.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
