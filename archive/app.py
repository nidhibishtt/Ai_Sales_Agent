"""
Streamlit interface for the AI Sales Agent
"""
import streamlit as st
import os
import json
from datetime import datetime
from main import EnhancedAISalesAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Sales Agent - Recruiting Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Fixed styling with proper colors
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 2px solid #f0f0f0;
        color: #333;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        color: #333 !important;
        border: 1px solid #e0e0e0;
    }
    .user-message {
        background-color: #e3f2fd !important;
        margin-left: 20%;
        color: #1565c0 !important;
    }
    .assistant-message {
        background-color: #f5f5f5 !important;
        margin-right: 20%;
        color: #333 !important;
    }
    .system-message {
        background-color: #fff3e0 !important;
        font-style: italic;
        text-align: center;
        color: #e65100 !important;
    }
    .metrics-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #333;
    }
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #28a745;
        color: white !important;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    /* Fix for main content area */
    .main .block-container {
        background-color: white !important;
        color: #333 !important;
    }
    /* Fix for text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ccc !important;
    }
    /* Fix for buttons */
    .stButton button {
        background-color: #1f77b4 !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_agent():
    """Initialize the AI Sales Agent (cached)"""
    try:
        return EnhancedAISalesAgent()
    except Exception as e:
        st.error(f"Failed to initialize AI Sales Agent: {str(e)}")
        st.info("The system will try different LLM providers (Groq, Hugging Face, Mock). Check your .env file for API keys.")
        return None

def format_message(message, role):
    """Format a chat message for display"""
    timestamp = message.get('timestamp', '')
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = timestamp
    else:
        time_str = datetime.now().strftime('%H:%M:%S')
    
    if role == 'user':
        css_class = "user-message"
        icon = "👤"
        role_name = "You"
    elif role == 'assistant':
        css_class = "assistant-message"
        icon = "🤖"
        role_name = "AI Sales Agent"
    else:
        css_class = "system-message"
        icon = "ℹ️"
        role_name = "System"
    
    content = message.get('content', '')
    
    return f"""
    <div class="chat-message {css_class}">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="margin-right: 0.5rem;">{icon}</span>
            <strong style="color: inherit;">{role_name}</strong>
            <span style="margin-left: auto; color: #666; font-size: 0.8rem;">{time_str}</span>
        </div>
        <div style="white-space: pre-wrap; color: inherit;">{content}</div>
    </div>
    """

def display_conversation_state(state):
    """Display current conversation state"""
    if not state or not state.get('success'):
        return
    
    client_info = state.get('client_info', {})
    
    st.markdown("### 📊 Conversation State")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stage = state.get('current_stage', 'unknown')
        st.markdown(f'<div class="stage-badge">{stage.upper()}</div>', unsafe_allow_html=True)
        st.metric("Current Stage", stage.replace('_', ' ').title())
    
    with col2:
        message_count = state.get('message_count', 0)
        st.metric("Messages", message_count)
    
    with col3:
        packages_count = state.get('recommended_packages', 0)
        st.metric("Recommended Packages", packages_count)
    
    if client_info:
        st.markdown("#### 👤 Client Information")
        
        info_cols = st.columns(4)
        with info_cols[0]:
            if client_info.get('company_name'):
                st.info(f"**Company:** {client_info['company_name']}")
        
        with info_cols[1]:
            if client_info.get('industry'):
                st.info(f"**Industry:** {client_info['industry']}")
        
        with info_cols[2]:
            if client_info.get('location'):
                st.info(f"**Location:** {client_info['location']}")
        
        with info_cols[3]:
            if client_info.get('urgency'):
                st.info(f"**Urgency:** {client_info['urgency']}")
        
        if client_info.get('roles'):
            st.markdown("**Roles Needed:**")
            for role in client_info['roles']:
                count = client_info.get('role_counts', {}).get(role, '')
                count_text = f" ({count})" if count else ""
                st.write(f"• {role}{count_text}")
    
    next_actions = state.get('next_actions', [])
    if next_actions:
        st.markdown("#### ⏭️ Next Actions")
        for action in next_actions:
            st.write(f"• {action}")

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header"><h1>🤖 AI Sales Agent</h1><p>Recruiting Agency Assistant</p></div>', unsafe_allow_html=True)
    
    # Initialize agent
    agent = initialize_agent()
    if not agent:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Controls")
        
        # Session management
        if st.button("🆕 New Conversation", type="primary", use_container_width=True):
            if 'current_session_id' in st.session_state:
                del st.session_state['current_session_id']
                del st.session_state['conversation_history']
            st.rerun()
        
        if st.button("🔄 Reset Current Conversation", use_container_width=True):
            if 'current_session_id' in st.session_state:
                result = agent.reset_conversation(st.session_state['current_session_id'])
                if result.get('success'):
                    st.success("Conversation reset!")
                    if 'conversation_history' in st.session_state:
                        del st.session_state['conversation_history']
                    st.rerun()
                else:
                    st.error(f"Reset failed: {result.get('error', 'Unknown error')}")
        
        st.divider()
        
        # System status
        st.header("📈 System Status")
        health = agent.health_check()
        
        if health.get('success'):
            st.success("✅ System Operational")
            
            # Services status
            services = health.get('services', {})
            for service, status in services.items():
                icon = "✅" if status == "operational" else "❌"
                st.write(f"{icon} {service.title()}")
            
            # Agent count
            agent_info = health.get('agents', {})
            st.metric("Active Agents", agent_info.get('total', 0))
            
        else:
            st.error("❌ System Error")
            st.write(health.get('error', 'Unknown error'))
        
        st.divider()
        
        # Sample inputs
        st.header("💡 Sample Inputs")
        sample_messages = [
            "Hi, we need to hire 2 backend engineers urgently",
            "We're a fintech startup in Mumbai looking for developers",
            "What are your pricing options?",
            "Can you schedule a call?",
            "Send me more information about your services"
        ]
        
        for msg in sample_messages:
            if st.button(f"📝 {msg[:30]}...", key=f"sample_{hash(msg)}", use_container_width=True):
                st.session_state['sample_input'] = msg
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Conversation")
        
        # Initialize session state
        if 'current_session_id' not in st.session_state:
            st.session_state['current_session_id'] = None
        if 'conversation_history' not in st.session_state:
            st.session_state['conversation_history'] = []
        
        # Chat container
        chat_container = st.container()
        
        # Display conversation history
        with chat_container:
            if st.session_state['conversation_history']:
                for message in st.session_state['conversation_history']:
                    role = message.get('role', 'unknown')
                    st.markdown(format_message(message, role), unsafe_allow_html=True)
            else:
                st.info("👋 Welcome! Start a conversation by sending a message below.")
        
        # Message input with Enter key support
        with st.form(key="message_form", clear_on_submit=True):
            user_input = st.text_area(
                "Your message:",
                value=st.session_state.get('sample_input', ''),
                height=100,
                placeholder="Tell me about your hiring needs... (Press Ctrl+Enter to send)",
                help="Press Ctrl+Enter or click Send button to send your message"
            )
            
            # Clear sample input after using it
            if 'sample_input' in st.session_state:
                del st.session_state['sample_input']
            
            send_message = st.form_submit_button("📤 Send Message", type="primary", use_container_width=True)
        
        # Process message
        if send_message and user_input.strip():
            with st.spinner("🤖 Processing your message..."):
                try:
                    # Start new conversation if needed
                    if not st.session_state['current_session_id']:
                        result = agent.start_conversation(user_input)
                        st.session_state['current_session_id'] = result.get('session_id')
                    else:
                        # Process message in existing conversation
                        result = agent.process_message(st.session_state['current_session_id'], user_input)
                    
                    if result.get('success'):
                        # Update conversation history
                        history_result = agent.get_conversation_history(st.session_state['current_session_id'])
                        if history_result.get('success'):
                            st.session_state['conversation_history'] = history_result['history']
                        
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
    
    with col2:
        st.header("📋 Session Info")
        
        if st.session_state['current_session_id']:
            # Get session summary
            summary = agent.get_session_summary(st.session_state['current_session_id'])
            display_conversation_state(summary)
            
            # Show session ID
            st.markdown(f"**Session ID:** `{st.session_state['current_session_id'][:8]}...`")
            
            # Service packages
            if st.button("📦 View Service Packages", use_container_width=True):
                packages_result = agent.get_service_packages()
                if packages_result.get('success'):
                    with st.expander("Available Service Packages", expanded=True):
                        for pkg in packages_result['packages']:
                            st.markdown(f"**{pkg['name']}**")
                            st.write(pkg['description'])
                            st.write(f"*Price: {pkg['price_range']}*")
                            st.write(f"*Timeline: {pkg['typical_timeline']}*")
                            st.divider()
        else:
            st.info("Start a conversation to see session details")
    
    # Analytics section (bottom of page)
    if st.checkbox("📊 Show Analytics"):
        st.header("📈 Analytics Dashboard")
        
        analytics_result = agent.get_analytics(days=7)
        if analytics_result.get('success'):
            analytics = analytics_result['analytics']
            
            # Metrics
            metrics_cols = st.columns(4)
            with metrics_cols[0]:
                st.metric("Total Sessions", analytics.get('total_sessions', 0))
            with metrics_cols[1]:
                event_counts = analytics.get('event_counts', {})
                total_events = sum(event_counts.values())
                st.metric("Total Events", total_events)
            with metrics_cols[2]:
                st.metric("Available Agents", len(analytics.get('available_agents', [])))
            with metrics_cols[3]:
                st.metric("Time Period", f"{analytics.get('time_period_days', 7)} days")
            
            # Event breakdown
            if event_counts:
                st.subheader("Event Breakdown")
                event_data = [{"Event": k.replace('_', ' ').title(), "Count": v} for k, v in event_counts.items()]
                st.dataframe(event_data, hide_index=True)
            
            # Agent status
            agent_status = analytics.get('agent_status', {})
            if agent_status:
                st.subheader("Agent Status")
                agent_data = []
                for name, info in agent_status.items():
                    agent_data.append({
                        "Agent": name.replace('_', ' ').title(),
                        "Class": info.get('class', 'Unknown'),
                        "Status": "✅ Active" if info.get('active') else "❌ Inactive"
                    })
                st.dataframe(agent_data, hide_index=True)

if __name__ == "__main__":
    main()
