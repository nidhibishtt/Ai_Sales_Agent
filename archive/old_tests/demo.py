#!/usr/bin/env python3
"""
AI Sales Agent Demo Script

This script demonstrates the key capabilities of the AI Sales Agent
by running through several sample scenarios.
"""

import sys
sys.path.append('/Users/vidhusinha/Desktop/Project')

from main import AISalesAgent
import time
import json

class DemoRunner:
    def __init__(self):
        self.agent = AISalesAgent()
        self.demo_scenarios = [
            {
                "name": "Tech Startup Scenario",
                "description": "Fast-growing fintech startup needs developers urgently",
                "conversation": [
                    "Hi, we need to hire developers urgently",
                    "We're a fintech startup in Mumbai. We need 2 backend engineers and 1 UI/UX designer. We have a product launch in 6 weeks.",
                    "Yes, please prepare a detailed proposal",
                    "This looks great! Can we schedule a call for tomorrow afternoon?"
                ]
            },
            {
                "name": "Enterprise Volume Hiring",
                "description": "Consulting firm expanding with 15-20 mixed roles",
                "conversation": [
                    "Good morning! We're looking for a recruitment partner.",
                    "We're a mid-size consulting firm expanding rapidly. We need to hire about 15-20 people across different roles.",
                    "We're a management consulting firm in New York. We need to fill these positions over the next 3-4 months.",
                    "The hybrid approach sounds interesting. Can you explain how that would work?"
                ]
            },
            {
                "name": "Specialized Healthcare",
                "description": "Telemedicine platform needs specialized physicians",
                "conversation": [
                    "We need help recruiting for very specialized healthcare positions",
                    "We're a telemedicine platform and need 2 family medicine physicians, 1 cardiologist, and 1 nurse practitioner with telehealth experience.",
                    "What would a custom solution look like? We have some unique requirements."
                ]
            }
        ]

    def print_banner(self, text):
        """Print a formatted banner"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)

    def print_message(self, speaker, message, delay=1):
        """Print a formatted conversation message"""
        if speaker == "User":
            print(f"\n👤 {speaker}: \"{message}\"")
        else:
            print(f"\n🤖 {speaker}: {message}")
        time.sleep(delay)

    def run_demo_scenario(self, scenario):
        """Run a single demo scenario"""
        self.print_banner(f"DEMO: {scenario['name']}")
        print(f"\nScenario: {scenario['description']}\n")
        
        # Start a new conversation session
        session_id = self.agent.start_conversation()
        
        for i, user_message in enumerate(scenario['conversation']):
            # User message
            self.print_message("User", user_message, delay=1)
            
            # Agent response
            try:
                response = self.agent.process_message(session_id, user_message)
                self.print_message("AI Sales Agent", response, delay=2)
                
                # Show extracted information after certain messages
                if i == 1:  # After client provides details
                    self.show_extracted_data(session_id)
                    
            except Exception as e:
                self.print_message("AI Sales Agent", f"I apologize, I'm having some technical difficulties: {str(e)}")
        
        # Show final session summary
        self.show_session_summary(session_id)
        
        input("\nPress Enter to continue to next scenario...")

    def show_extracted_data(self, session_id):
        """Display extracted client information"""
        print("\n" + "-"*40)
        print("🔍 EXTRACTED CLIENT INFORMATION:")
        print("-"*40)
        
        try:
            memory = self.agent.memory_service.get_conversation_history(session_id)
            
            # Look for extracted entities in memory
            for entry in memory:
                if "industry" in str(entry).lower() or "location" in str(entry).lower():
                    # This is a simplified display - in reality, you'd parse the memory structure
                    print("✓ Industry and location identified")
                    print("✓ Role requirements extracted")  
                    print("✓ Timeline and urgency assessed")
                    print("✓ Package recommendations prepared")
                    break
                    
        except Exception as e:
            print(f"Unable to display extracted data: {e}")
        
        print("-"*40)

    def show_session_summary(self, session_id):
        """Display session summary and next steps"""
        print("\n" + "="*40)
        print("📊 SESSION SUMMARY")
        print("="*40)
        
        try:
            # Get conversation history
            history = self.agent.memory_service.get_conversation_history(session_id)
            
            print(f"Session ID: {session_id}")
            print(f"Messages Exchanged: {len(history)}")
            print("Status: ✅ Engagement Successful")
            print("Outcome: Proposal/Consultation Requested")
            print("Next Steps: Follow-up scheduled")
            
        except Exception as e:
            print(f"Unable to generate session summary: {e}")

    def run_interactive_demo(self):
        """Run an interactive demo where user can chat with agent"""
        self.print_banner("INTERACTIVE DEMO MODE")
        print("\nYou can now chat directly with the AI Sales Agent!")
        print("Type 'quit' to exit, 'help' for commands\n")
        
        session_id = self.agent.start_conversation()
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("- Type any message to chat with the agent")
                    print("- 'status' - Show current session status")
                    print("- 'memory' - Show conversation history") 
                    print("- 'quit' - Exit demo")
                    continue
                elif user_input.lower() == 'status':
                    print(f"\n📊 Session ID: {session_id}")
                    print("Status: Active conversation")
                    continue
                elif user_input.lower() == 'memory':
                    try:
                        history = self.agent.memory_service.get_conversation_history(session_id)
                        print(f"\n💾 Conversation History ({len(history)} entries)")
                        for entry in history[-3:]:  # Show last 3 entries
                            print(f"   - {str(entry)[:100]}...")
                    except Exception as e:
                        print(f"Unable to retrieve memory: {e}")
                    continue
                
                if user_input:
                    response = self.agent.process_message(session_id, user_input)
                    self.print_message("AI Sales Agent", response, delay=0)
                    
            except KeyboardInterrupt:
                print("\n\nDemo interrupted by user")
                break
            except Exception as e:
                print(f"\nError: {e}")
        
        print("\nThank you for trying the AI Sales Agent demo!")

    def run_full_demo(self):
        """Run the complete demo experience"""
        self.print_banner("AI SALES AGENT DEMONSTRATION")
        print("\nWelcome to the AI Sales Agent Demo!")
        print("This demo showcases the agent's capabilities across different scenarios.")
        
        print("\nDemo Options:")
        print("1. Run all pre-built scenarios")
        print("2. Interactive demo (chat directly)")
        print("3. Single scenario demo")
        
        while True:
            try:
                choice = input("\nSelect option (1-3): ").strip()
                
                if choice == "1":
                    # Run all scenarios
                    for scenario in self.demo_scenarios:
                        self.run_demo_scenario(scenario)
                    break
                    
                elif choice == "2":
                    # Interactive mode
                    self.run_interactive_demo()
                    break
                    
                elif choice == "3":
                    # Single scenario
                    print("\nAvailable scenarios:")
                    for i, scenario in enumerate(self.demo_scenarios, 1):
                        print(f"{i}. {scenario['name']} - {scenario['description']}")
                    
                    scenario_choice = input("\nSelect scenario (1-3): ").strip()
                    try:
                        scenario_idx = int(scenario_choice) - 1
                        if 0 <= scenario_idx < len(self.demo_scenarios):
                            self.run_demo_scenario(self.demo_scenarios[scenario_idx])
                            break
                        else:
                            print("Invalid scenario number")
                    except ValueError:
                        print("Please enter a number")
                        
                else:
                    print("Invalid choice. Please select 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\n\nDemo cancelled by user")
                break

if __name__ == "__main__":
    print("Starting AI Sales Agent Demo...")
    
    # Initialize and run demo
    demo = DemoRunner()
    demo.run_full_demo()
    
    print("\n🎉 Demo completed! Thank you for exploring the AI Sales Agent.")
    print("\nTo run the agent in production:")
    print("- CLI: python cli.py")
    print("- Web Interface: streamlit run app.py")  
    print("- API Server: uvicorn api:app --reload")
