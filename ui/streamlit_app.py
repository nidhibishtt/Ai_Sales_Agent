"""
Enhanced AI Sales Agent - Modern Web UI
Beautiful, professional interface for recruiting conversations
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
import re
import asyncio

# Configure page
st.set_page_config(
    page_title="AI Sales Agent - Recruiting Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
def inject_css(dark: bool = False):
    """Inject theme-aware CSS with modern chat aesthetics."""
    if dark:
        vars = {
            'bg_body': '#0f1115', 'bg_panel': '#171a21', 'bg_accent': '#20242c', 'border': '#2d3748',
            'text': '#e6edf3', 'text_muted': '#9ba3af', 'primary': '#5b8aff', 'primary_grad': 'linear-gradient(135deg,#4062bb,#5b8aff)',
            'user_bubble': 'linear-gradient(135deg,#4062bb,#7f53ac)', 'assistant_bubble': '#1f2329', 'code_bg': '#13161b',
            'assistant_text': '#e6edf3'
        }
    else:
        vars = {
            'bg_body': '#f5f7fb', 'bg_panel': '#ffffff', 'bg_accent': '#f0f3f9', 'border': '#e2e8f0',
            'text': '#1f2937', 'text_muted': '#4b5563', 'primary': '#6366f1', 'primary_grad': 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            'user_bubble': 'linear-gradient(135deg,#6366f1,#8b5cf6)', 'assistant_bubble': '#ffffff', 'code_bg': '#f0f3f9',
            'assistant_text': '#1f2937'
        }
    st.markdown(f"""
    <style>
        html, body .block-container {{padding-top: 1.2rem;}}
        body {{background:{vars['bg_body']}; color:{vars['text']};}}
        .main-header {{background:{vars['primary_grad']}; padding:1.4rem 2rem; border-radius:18px; box-shadow:0 4px 12px rgba(0,0,0,.15);}}
        .main-header h1 {{margin:0;font-size:1.9rem;font-weight:600;color:#fff;}}
        .main-header h3 {{margin:.25rem 0 0;color:#eef2ff;font-weight:500;}}
        .chat-wrapper {{max-width:900px;margin:0 auto;}}
        .chat-scroll {{max-height:70vh; overflow-y:auto; padding:0 .25rem 1rem 0; scrollbar-width:thin;}}
        .chat-scroll::-webkit-scrollbar {{width:8px;}}
        .chat-scroll::-webkit-scrollbar-track {{background:transparent;}}
        .chat-scroll::-webkit-scrollbar-thumb {{background:{vars['bg_accent']}; border-radius:4px;}}
        .msg {{display:flex; gap:.75rem; margin: .9rem 0; line-height:1.45; animation: fadeInUp .3s ease;}}
        .msg .avatar {{flex:0 0 38px; height:38px; width:38px; border-radius:50%; background:{vars['primary_grad']}; display:flex; align-items:center; justify-content:center; font-weight:600; color:#fff; font-size:.9rem; box-shadow:0 2px 6px rgba(0,0,0,.3);}}
        .msg.assistant .avatar {{background:#0ea5e9;}}
        .bubble {{background:{vars['assistant_bubble']}; padding:.9rem 1.05rem; border-radius:14px; position:relative; flex:1; border:1px solid {vars['border']}; box-shadow:0 1px 3px rgba(0,0,0,.08); color:{vars['assistant_text']};}}
        .msg.user .bubble {{background:{vars['user_bubble']}; color:#fff; border:1px solid {vars['primary']}55;}}
        .bubble pre, .bubble code {{background:{vars['code_bg']}; color:{vars['assistant_text']}; padding:.6rem .8rem; border-radius:8px; font-size:.8rem; overflow-x:auto; border:1px solid {vars['border']};}}
        .bubble blockquote {{border-left:3px solid {vars['primary']}; padding-left:.8rem; margin:.5rem 0; opacity:.9; color:{vars['assistant_text']};}}
        .bubble h1,h2,h3,h4 {{margin:.8rem 0 .4rem; color:{vars['assistant_text']};}}
        .bubble ul,ol {{margin:.5rem 0; padding-left:1.2rem; color:{vars['assistant_text']};}}
        .bubble p {{color:{vars['assistant_text']}; margin:.3rem 0;}}
        .bubble strong, .bubble em {{color:{vars['assistant_text']};}}
        .bubble a {{color:{vars['primary']};}}
        .meta {{font-size:.65rem; opacity:.65; margin-top:.35rem; text-transform:uppercase; letter-spacing:.05em;}}
        .typing-indicator {{display:flex; align-items:center; gap:.4rem; opacity:.7; font-style:italic;}}
        .typing-dots {{display:inline-block;}} .typing-dots::after {{content:'...'; animation: ellipsis 1.5s infinite;}}
        @keyframes ellipsis {{0%, 50% {{opacity: 1;}} 100% {{opacity: .3;}}}}
        @keyframes fadeInUp {{from {{opacity:0; transform:translateY(10px);}} to {{opacity:1; transform:translateY(0);}}}}
        .toolbar-chips {{margin:.8rem 0; display:flex; flex-wrap:wrap; gap:.4rem;}}
        .toolbar-chips span {{display:inline-block; background:{vars['bg_accent']}; padding:.45rem .75rem; border-radius:20px; font-size:.72rem; cursor:pointer; border:1px solid {vars['border']}; transition:all .2s;}}
        .toolbar-chips span:hover {{background:{vars['primary']}22; border-color:{vars['primary']}55; transform:translateY(-1px);}}
        .input-bar {{position:sticky; bottom:0; padding:1rem .25rem .5rem; background:linear-gradient(180deg,transparent 0%, {vars['bg_body']} 40%);}}
        .input-box textarea {{border-radius:14px !important; border:1px solid {vars['border']} !important; font-size:.9rem !important;}}
        .sidebar-conv {{background:{vars['bg_panel']}; border:1px solid {vars['border']}; border-radius:8px; padding:.6rem .8rem; margin:.3rem 0; cursor:pointer; transition:all .2s; font-size:.8rem;}}
        .sidebar-conv:hover {{background:{vars['bg_accent']}; border-color:{vars['primary']}44;}}
        .sidebar-conv.active {{background:{vars['primary']}15; border-color:{vars['primary']};}}
        .model-control {{background:{vars['bg_panel']}; border:1px solid {vars['border']}; border-radius:8px; padding:.5rem; margin:.3rem 0;}}
        .status-card {{background:{vars['bg_panel']}; color:{vars['text']};}}
        .extraction-card {{background:{vars['bg_panel']};}}
        .chip {{background:{vars['bg_accent']};}}
        .chip-missing {{background:#fee2e2;}}
        .chip-ok {{background:#dcfce7;}}
        .stButton > button {{background:{vars['primary_grad']}; border:none;}}
        .conv-badge {{padding:.35rem .6rem; background:{vars['bg_accent']}; border:1px solid {vars['border']}; border-radius:8px; font-size:.65rem; margin:.2rem 0; cursor:pointer;}}
        .conv-badge.active {{background:{vars['primary']}22; border-color:{vars['primary']};}}
        .summary-box {{background:{vars['bg_panel']}; border:1px solid {vars['border']}; padding:.9rem 1rem; border-radius:12px;}}
        .streaming-text {{animation: fadeInChar .05s ease forwards;}}
        @keyframes fadeInChar {{from {{opacity:0;}} to {{opacity:1;}}}}
    </style>
    """, unsafe_allow_html=True)


# Theme state & CSS injection
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
inject_css(st.session_state.dark_mode)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "extraction_results" not in st.session_state:
    st.session_state.extraction_results = []
if "system_metrics" not in st.session_state:
    st.session_state.system_metrics = {}
if "uploaded_job_spec" not in st.session_state:
    st.session_state.uploaded_job_spec = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "last_gap_prompt" not in st.session_state:
    st.session_state.last_gap_prompt = None
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = None
if "quick_prompts" not in st.session_state:
    st.session_state.quick_prompts = [
        "We need 3 senior backend engineers (Python, Django) in Bangalore",
        "Hiring a product manager for fintech app in Mumbai, urgent",
        "Looking for remote data scientist with NLP experience"
    ]
if "model_settings" not in st.session_state:
    st.session_state.model_settings = {
        "temperature": 0.2,
        "max_tokens": 500,
        "streaming": True,
        "show_typing": True
    }
if "conversation_titles" not in st.session_state:
    st.session_state.conversation_titles = {}
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

REQUIRED_FIELDS = [
    "roles", "location", "industry", "experience_level", "skills",
    "headcount", "urgency", "budget", "timeline", "remote"
]

def render_markdown(text: str) -> str:
    """Basic markdown to HTML conversion for chat messages."""
    # Code blocks
    text = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # Paragraphs (wrap text in p tags for better styling)
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<'):
            processed_lines.append(f'<p>{line}</p>')
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)

def generate_conversation_title(messages: List[Dict[str, str]]) -> str:
    """Generate a title for the conversation based on first few messages."""
    if not messages:
        return "New Conversation"
    first_user_msg = next((m['content'] for m in messages if m['role'] == 'user'), "")
    if len(first_user_msg) > 50:
        return first_user_msg[:47] + "..."
    return first_user_msg or "New Conversation"

def stream_text_effect(text: str, container, delay: float = 0.03):
    """Simulate streaming text effect."""
    if not st.session_state.model_settings.get("streaming", True):
        container.markdown(render_markdown(text), unsafe_allow_html=True)
        return
    
    placeholder = container.empty()
    displayed_text = ""
    
    for char in text:
        displayed_text += char
        placeholder.markdown(render_markdown(displayed_text), unsafe_allow_html=True)
        if delay > 0:
            time.sleep(delay)

def display_conversation_sidebar():
    """Display conversation history in sidebar."""
    st.sidebar.markdown("### 💬 Conversations")
    
    # Current conversation
    current_title = generate_conversation_title(st.session_state.messages)
    if st.session_state.active_conversation:
        st.session_state.conversation_titles[st.session_state.active_conversation] = current_title
    
    # List conversations
    conversations = list(st.session_state.conversation_titles.items())
    for conv_id, title in conversations[-5:]:  # Show last 5
        is_active = conv_id == st.session_state.active_conversation
        class_name = "sidebar-conv active" if is_active else "sidebar-conv"
        
        if st.sidebar.button(title, key=f"conv_{conv_id}", help=f"Switch to: {title}"):
            if conv_id != st.session_state.active_conversation:
                # Save current conversation
                if st.session_state.active_conversation:
                    st.session_state.conversations[st.session_state.active_conversation] = st.session_state.messages.copy()
                
                # Load selected conversation
                st.session_state.active_conversation = conv_id
                st.session_state.messages = st.session_state.conversations.get(conv_id, [])
                st.rerun()

def display_model_controls():
    """Display model settings in sidebar."""
    st.sidebar.markdown("### ⚙️ Model Settings")
    
    # Temperature
    temp = st.sidebar.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state.model_settings["temperature"],
        step=0.1,
        help="Higher = more creative, Lower = more focused"
    )
    st.session_state.model_settings["temperature"] = temp
    
    # Max tokens
    max_tokens = st.sidebar.slider(
        "Max Response Length", 
        min_value=100, 
        max_value=1000, 
        value=st.session_state.model_settings["max_tokens"],
        step=50
    )
    st.session_state.model_settings["max_tokens"] = max_tokens
    
    # Streaming
    streaming = st.sidebar.checkbox(
        "Streaming Response", 
        value=st.session_state.model_settings["streaming"],
        help="Show text as it's generated"
    )
    st.session_state.model_settings["streaming"] = streaming
    
    # Show typing indicator
    show_typing = st.sidebar.checkbox(
        "Typing Indicator", 
        value=st.session_state.model_settings["show_typing"]
    )
    st.session_state.model_settings["show_typing"] = show_typing

def compute_info_gaps(latest_entities: Dict[str, Any]) -> Dict[str, List[str]]:
    """Identify which required fields are missing or incomplete."""
    missing = []
    present = []
    for field in REQUIRED_FIELDS:
        value = latest_entities.get(field)
        if value in (None, "", [], {}):
            missing.append(field)
        else:
            present.append(field)
    return {"missing": missing, "present": present}

def build_gap_followup(field: str) -> str:
    mapping = {
        "roles": "Could you clarify the specific role titles and seniority levels you need?",
        "location": "What's the primary work location or are you open to remote/hybrid?",
        "industry": "Which industry/sector is your company operating in?",
        "experience_level": "What experience level are you targeting (e.g., junior, mid, senior)?",
        "skills": "Any must-have technical or domain skills?",
        "headcount": "How many hires are you planning for this role?",
        "urgency": "What is your target start date / urgency level?",
        "budget": "Do you have a compensation range or budget guideline?",
        "timeline": "What is your ideal hiring timeline?",
        "remote": "Is the role remote, onsite, or hybrid?"
    }
    return mapping.get(field, f"Can you provide more details about {field}?")

def display_info_gaps(latest_entities: Dict[str, Any]):
    gaps = compute_info_gaps(latest_entities)
    st.markdown("#### Coverage")
    gap_html = "".join([f"<span class='chip chip-ok'>{f}</span>" for f in gaps['present']])
    if gaps['missing']:
        gap_html += "".join([f"<span class='chip chip-missing'>{f}</span>" for f in gaps['missing']])
    st.markdown(gap_html, unsafe_allow_html=True)
    if gaps['missing']:
        st.markdown("#### Ask for Missing Details")
        cols = st.columns(2)
        for i, field in enumerate(gaps['missing']):
            with cols[i % 2]:
                if st.button(field.title(), key=f"gap_btn_{field}"):
                    prompt = build_gap_followup(field)
                    st.session_state.last_gap_prompt = prompt
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.spinner("Gathering details..."):
                        resp = process_user_message(st.session_state.agent, prompt)
                    st.session_state.messages.append({"role": "assistant", "content": resp})
                    st.rerun()

def generate_conversation_summary(messages: List[Dict[str, str]]) -> Optional[str]:
    if not messages:
        return None
    try:
        from services.llm_service import LLMService
        llm = LLMService()
        convo_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-12:]])
        prompt = (
            "Summarize the recruiting conversation below into: 1) Roles 2) Key requirements 3) Open questions. "
            "Keep it under 120 words.\n\nConversation:\n" + convo_text
        )
        result = llm.generate(prompt)
        return result
    except Exception as e:
        return f"Summary error: {e}";

def export_conversation(format_: str) -> bytes:
    data = {
        "messages": st.session_state.messages,
        "extractions": st.session_state.extraction_results,
        "generated": datetime.utcnow().isoformat() + "Z"
    }
    if format_ == "json":
        return json.dumps(data, default=str, indent=2).encode()
    # CSV simple flatten
    rows = []
    for m in st.session_state.messages:
        rows.append({"role": m.get("role"), "content": m.get("content")})
    import csv
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["role", "content"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()

def initialize_agent():
    """Initialize the AI Sales Agent"""
    try:
        import sys
        import os
        
        # Add project root to path
        if '/Users/vidhusinha/Desktop/Project' not in sys.path:
            sys.path.append('/Users/vidhusinha/Desktop/Project')
        
        from main import EnhancedAISalesAgent
        from services.llm_service import LLMService
        
        # Initialize agent
        agent = EnhancedAISalesAgent()
        llm_service = LLMService()
        
        # Get system status
        status = agent.get_system_status()
        
        return agent, llm_service, status
    except Exception as e:
        st.error(f"Failed to initialize AI Sales Agent: {str(e)}")
        return None, None, None

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Sales Agent</h1>
        <h3>Intelligent Recruiting Assistant</h3>
        <p>Powered by Groq LLM • 100% Extraction Accuracy • Lightning Fast</p>
    </div>
    """, unsafe_allow_html=True)

def display_system_status(status):
    """Display system status metrics"""
    if not status:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="status-card">
            <h4>🤖 LLM Provider</h4>
            <p class="success-metric">{}</p>
        </div>
        """.format(status.get('llm', {}).get('provider', 'Unknown').title()), unsafe_allow_html=True)
    
    with col2:
        agents_count = status.get('agents', {}).get('total', 0)
        st.markdown("""
        <div class="status-card">
            <h4>👥 Agents</h4>
            <p class="success-metric">{} Active</p>
        </div>
        """.format(agents_count), unsafe_allow_html=True)
    
    with col3:
        system_status = status.get('system', 'unknown')
        status_color = 'success-metric' if system_status == 'operational' else 'warning-metric'
        st.markdown("""
        <div class="status-card">
            <h4>⚡ System</h4>
            <p class="{}">{}</p>
        </div>
        """.format(status_color, system_status.title()), unsafe_allow_html=True)
    
    with col4:
        version = status.get('version', '2.0.0')
        st.markdown("""
        <div class="status-card">
            <h4>📊 Version</h4>
            <p class="success-metric">{}</p>
        </div>
        """.format(version), unsafe_allow_html=True)

def display_extraction_results(results):
    """Display entity extraction results"""
    if not results:
        return
    
    st.markdown("### 🔍 Latest Extraction Results")
    
    latest = results[-1] if results else {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="extraction-card">
            <h4>📋 Extracted Entities</h4>
        """, unsafe_allow_html=True)
        
        entities = latest.get('entities', {})
        for key, value in entities.items():
            if value:
                st.write(f"**{key.title()}:** {value}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="extraction-card">
            <h4>📊 Extraction Metrics</h4>
        """, unsafe_allow_html=True)
        method = latest.get('method', 'Unknown')
        confidence = latest.get('confidence', 0)
        st.write(f"**Method:** {method}")
        st.write(f"**Confidence:** {confidence:.1%}")

        # Simple accuracy visualization
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': "#f8d7da"},
                    {'range': [50, 80], 'color': "#fff3cd"},
                    {'range': [80, 100], 'color': "#d4edda"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

def display_performance_charts():
    """Display performance analytics"""
    st.markdown("### 📈 Performance Analytics")
    
    # Sample performance data (in real app, this would come from the agent)
    performance_data = pd.DataFrame({
        'Date': pd.date_range('2025-08-01', periods=10, freq='D'),
        'Conversations': [5, 8, 12, 15, 18, 22, 25, 28, 30, 35],
        'Extraction_Accuracy': [85, 87, 90, 92, 95, 97, 98, 99, 100, 100],
        'Response_Quality': [75, 78, 82, 85, 88, 90, 92, 94, 96, 98]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(performance_data, x='Date', y='Conversations', 
                      title='Daily Conversations',
                      color_discrete_sequence=['#667eea'])
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.line(performance_data, x='Date', y=['Extraction_Accuracy', 'Response_Quality'], 
                      title='Quality Metrics Over Time',
                      color_discrete_sequence=['#667eea', '#764ba2'])
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig2, use_container_width=True)

def process_user_message(agent, message):
    """Process user message and get AI response"""
    try:
        if not st.session_state.session_id:
            # Start new conversation
            result = agent.start_conversation(message)
            st.session_state.session_id = result.get('session_id')
            response = result.get('response', 'Hello! How can I help you with your hiring needs?')
        else:
            # Continue conversation
            result = agent.process_message(st.session_state.session_id, message)
            response = result.get('response', 'I understand. Could you tell me more?')
        
        # Extract entities for display
        try:
            from services.advanced_ner import create_advanced_ner_service
            from services.llm_service import LLMService
            
            llm_service = LLMService()
            ner_service = create_advanced_ner_service(llm_service)
            extraction_result = ner_service.extract_entities(message)
            
            # Calculate confidence
            if extraction_result.confidence_scores:
                avg_confidence = sum(extraction_result.confidence_scores.values()) / len(extraction_result.confidence_scores)
            else:
                avg_confidence = 0.8  # Default
            
            extraction_data = {
                'entities': extraction_result.entities,
                'method': extraction_result.extraction_method,
                'confidence': avg_confidence,
                'timestamp': datetime.now()
            }
            
            st.session_state.extraction_results.append(extraction_data)
            
        except Exception as e:
            st.sidebar.error(f"Extraction error: {str(e)}")
        
        return response
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Could you please try again?"

def main():
    """Main application"""
    display_header()
    
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("🚀 Initializing AI Sales Agent..."):
            agent, llm_service, status = initialize_agent()
            if agent:
                st.session_state.agent = agent
                st.session_state.system_metrics = status
                st.success("✅ AI Sales Agent initialized successfully!")
            else:
                st.error("❌ Failed to initialize agent")
                return
    
    # Sidebar with system info & controls
    with st.sidebar:
        # Theme toggle
        st.toggle("🌙 Dark Mode", key="dark_mode", on_change=lambda: inject_css(st.session_state.dark_mode))
        
        # Conversation history
        display_conversation_sidebar()
        st.markdown("---")
        
        # Model controls
        display_model_controls()
        st.markdown("---")
        
        st.markdown("## 🔧 System Status")
        display_system_status(st.session_state.system_metrics)
        st.markdown("## 📊 Quick Stats")
        c1, c2 = st.columns(2)
        c1.metric("Msgs", len(st.session_state.messages))
        c2.metric("Extracts", len(st.session_state.extraction_results))
        if st.session_state.extraction_results:
            latest_confidence = st.session_state.extraction_results[-1].get('confidence', 0)
            st.metric("Latest Accuracy", f"{latest_confidence:.1%}")
        st.markdown("---")
        
        # Upload job spec
        st.markdown("### 📄 Job Spec")
        uploaded = st.file_uploader("Upload .txt / .md spec", type=["txt", "md"], help="Use a short job description to auto-extract entities.")
        if uploaded:
            content = uploaded.read().decode("utf-8", errors="ignore")
            st.session_state.uploaded_job_spec = content
            if st.button("Extract From Spec"):
                st.session_state.messages.append({"role": "user", "content": content[:1500]})
                with st.spinner("Analyzing spec..."):
                    resp = process_user_message(st.session_state.agent, content[:1500])
                st.session_state.messages.append({"role": "assistant", "content": resp})
                st.rerun()
        st.markdown("---")
        
        if st.button("🧹 New Conversation"):
            # Save current conversation
            if st.session_state.messages:
                conv_id = str(uuid.uuid4())[:8]
                st.session_state.conversations[conv_id] = st.session_state.messages.copy()
                st.session_state.conversation_titles[conv_id] = generate_conversation_title(st.session_state.messages)
            
            # Reset state
            st.session_state.messages = []
            st.session_state.session_id = None
            st.session_state.extraction_results = []
            st.session_state.summary = None
            st.session_state.active_conversation = str(uuid.uuid4())[:8]
            st.rerun()
            
        st.markdown("## 🧪 Test Scenarios")
        test_scenarios = [
            "We are a fintech startup in Mumbai hiring 2 backend engineers and a UI/UX designer urgently.",
            "Need 5 senior React developers for our healthcare SaaS company in Bangalore ASAP",
            "Looking for a data scientist with ML experience for our AI startup, remote work ok"
        ]
        for i, scenario in enumerate(test_scenarios, 1):
            if st.button(f"Scenario {i}", key=f"test_{i}"):
                st.session_state.messages.append({"role": "user", "content": scenario})
                with st.spinner("Processing scenario..."):
                    response = process_user_message(st.session_state.agent, scenario)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        st.markdown("---")
        
        # Export
        st.markdown("### 📤 Export")
        if st.session_state.messages:
            colx, coly = st.columns(2)
            with colx:
                st.download_button("JSON", data=export_conversation("json"), file_name="conversation.json", mime="application/json")
            with coly:
                st.download_button("CSV", data=export_conversation("csv"), file_name="conversation.csv", mime="text/csv")

    # Tabs structure
    tabs = st.tabs(["💬 Chat", "🧠 Entities", "📈 Analytics"])

    with tabs[0]:
        # Conversation management row
        top_cols = st.columns([6,2,2])
        with top_cols[0]:
            st.markdown("#### Conversation")
        with top_cols[1]:
            if st.button("📝 Summarize", use_container_width=True):
                with st.spinner("Summarizing..."):
                    st.session_state.summary = generate_conversation_summary(st.session_state.messages)
        with top_cols[2]:
            if st.button("➕ New Chat", use_container_width=True):
                # Save current conversation
                if st.session_state.messages:
                    conv_id = str(uuid.uuid4())[:8]
                    st.session_state.conversations[conv_id] = st.session_state.messages.copy()
                    st.session_state.conversation_titles[conv_id] = generate_conversation_title(st.session_state.messages)
                
                # Reset
                st.session_state.messages = []
                st.session_state.session_id = None
                st.session_state.active_conversation = str(uuid.uuid4())[:8]
                st.session_state.conversations[st.session_state.active_conversation] = []
                st.rerun()

        # Quick prompts chips
        st.markdown("<div class='toolbar-chips'>", unsafe_allow_html=True)
        chip_cols = st.columns(3)
        for i, prompt in enumerate(st.session_state.quick_prompts):
            with chip_cols[i % 3]:
                if st.button(f"💡 {prompt[:25]}...", key=f"quick_{i}", help=prompt, use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": prompt, "ts": datetime.utcnow().strftime("%H:%M")})
                    with st.spinner("🤖 Generating response..."):
                        response = process_user_message(st.session_state.agent, prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response, "ts": datetime.utcnow().strftime("%H:%M")})
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Chat area
        st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)
        chat_scroll = st.container()
        
        with chat_scroll:
            st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)
            
            # Display messages
            for idx, message in enumerate(st.session_state.messages):
                role = message.get("role")
                content = message.get("content")
                avatar = "You" if role == "user" else "AI"
                role_class = "user" if role == "user" else "assistant"
                timestamp = message.get("ts") or datetime.utcnow().strftime("%H:%M")
                
                # Enhanced message rendering with markdown
                rendered_content = render_markdown(content)
                
                html = f"""
                <div class='msg {role_class}'>
                    <div class='avatar'>{avatar[0]}</div>
                    <div class='bubble'>
                        {rendered_content}
                        <div class='meta'>{avatar} • {timestamp}</div>
                    </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
            
            # Typing indicator
            if st.session_state.is_typing and st.session_state.model_settings.get("show_typing", True):
                st.markdown("""
                <div class='msg assistant'>
                    <div class='avatar'>AI</div>
                    <div class='bubble'>
                        <div class='typing-indicator'>
                            <span class='typing-dots'>AI is thinking</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Input bar
        st.markdown("<div class='input-bar'>", unsafe_allow_html=True)
        
        # Input with enhanced placeholder
        placeholder_text = "Message the recruiting assistant… (supports markdown)"
        user_input = st.chat_input(placeholder_text)
        
        if user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input, 
                "ts": datetime.utcnow().strftime("%H:%M")
            })
            
            # Show typing indicator
            if st.session_state.model_settings.get("show_typing", True):
                st.session_state.is_typing = True
                st.rerun()
            
            # Get AI response with streaming effect
            with st.spinner("🤖 Generating response..."):
                response = process_user_message(st.session_state.agent, user_input)
            
            # Hide typing indicator
            st.session_state.is_typing = False
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "ts": datetime.utcnow().strftime("%H:%M")
            })
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Summary box
        if st.session_state.summary:
            st.markdown("<div class='summary-box'><strong>💡 Summary:</strong><br>" + render_markdown(st.session_state.summary) + "</div>", unsafe_allow_html=True)

    # Entities tab
    with tabs[1]:
        st.markdown("### Extracted Entities & Coverage")
        if st.session_state.extraction_results:
            display_extraction_results(st.session_state.extraction_results)
            latest_entities = st.session_state.extraction_results[-1].get('entities', {})
            display_info_gaps(latest_entities)
        else:
            st.caption("No entities extracted yet. Start chatting or upload a job spec.")

    # Analytics tab
    with tabs[2]:
        st.markdown("### Performance & Metrics")
        if st.session_state.messages:
            display_performance_charts()
        else:
            st.caption("No analytics yet. Interact with the assistant to generate data.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 Enhanced AI Sales Agent • Powered by Groq LLM • Built with Streamlit</p>
        <p>© 2025 • Intelligent Recruiting Solutions</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
