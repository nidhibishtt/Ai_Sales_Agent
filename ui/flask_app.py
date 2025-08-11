"""
Flask-based AI Sales Agent UI
Modern chat interface with real-time features
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import json
import uuid
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append('/Users/vidhusinha/Desktop/Project')

from main import EnhancedAISalesAgent
from services.llm_service import LLMService
from services.advanced_ner import create_advanced_ner_service

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
agent = None
llm_service = None
ner_service = None

def initialize_agent():
    """Initialize the AI Sales Agent"""
    global agent, llm_service, ner_service
    try:
        agent = EnhancedAISalesAgent()
        llm_service = LLMService()
        ner_service = create_advanced_ner_service(llm_service)
        return True
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return False

# Initialize on startup
initialize_agent()

@app.route('/')
def index():
    """Legacy chat interface (kept for backward compatibility)"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@app.route('/new')
def new_ui():
    """Scratch-built new UI interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('new_chat.html')

@app.route('/api/system-status')
def system_status():
    """Get system status"""
    if agent:
        status = agent.get_system_status()
        return jsonify(status)
    return jsonify({'error': 'Agent not initialized'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():  # supports new UI conversation_id while keeping legacy behavior
    try:
        data = request.json or {}
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        if not agent:
            return jsonify({'error': 'Agent not initialized'}), 500

        # Check if user wants to end conversation
        end_keywords = ['goodbye', 'bye', 'thanks', 'thank you', 'that\'s all', 'end chat', 'finish', 'done', 'complete']
        if any(keyword in message.lower() for keyword in end_keywords):
            # Auto-summarize before ending
            try:
                if 'agent_session_id' in session:
                    # Get conversation history for summary
                    from services.memory_service import MemoryService
                    memory = MemoryService()
                    history = memory.get_conversation_history(session['agent_session_id'])
                    
                    if len(history) > 2:  # Only summarize if there's substantial conversation
                        messages = [{'role': msg['role'], 'content': msg['content']} for msg in history]
                        transcript = '\n'.join([f"{m['role'].upper()}: {m['content']}" for m in messages[-20:]])
                        
                        summary_prompt = (
                            "Provide a final summary of this recruiting conversation. Include: "
                            "1) Client's hiring needs 2) Positions requested 3) Timeline 4) Next steps discussed. "
                            "Keep it professional and concise.\n\nConversation:\n" + transcript
                        )
                        summary = llm_service.generate(summary_prompt)
                        
                        return jsonify({
                            'response': f"Thank you for your time! Here's a summary of our discussion:\n\n{summary}\n\nFeel free to reach out anytime for your hiring needs.",
                            'extraction': None,
                            'timestamp': datetime.utcnow().isoformat(),
                            'conversation_ended': True
                        })
            except Exception as e:
                print(f"Auto-summary error: {e}")

        # Legacy single-session flow (no conversation_id supplied)
        if not conversation_id:
            if 'conversation_started' not in session:
                result = agent.start_conversation(message)
                print(f"DEBUG: start_conversation result: {result}")
                session['conversation_started'] = True
                session['agent_session_id'] = result.get('session_id')
                response_text = result.get('response', 'Hello! How can I help with your hiring needs?')
            else:
                result = agent.process_message(session['agent_session_id'], message)
                print(f"DEBUG: process_message result: {result}")
                print(f"DEBUG: session_id: {session.get('agent_session_id')}")
                response_text = result.get('response', 'I understand. Could you tell me more?')
                if not result.get('response'):
                    print(f"DEBUG: No response in result, full result: {result}")
        else:
            # For multi-conversation UI we currently map all to a single backend agent session
            if 'agent_session_id' not in session:
                init_result = agent.start_conversation(message)
                session['agent_session_id'] = init_result.get('session_id')
                response_text = init_result.get('response', 'Hello! How can I help with your hiring needs?')
            else:
                result = agent.process_message(session['agent_session_id'], message)
                response_text = result.get('response', 'I understand. Could you tell me more?')

        extraction_data = None
        try:
            if ner_service:
                extraction_result = ner_service.extract_entities(message)
                if extraction_result.confidence_scores:
                    avg_conf = sum(extraction_result.confidence_scores.values()) / len(extraction_result.confidence_scores)
                else:
                    avg_conf = 0.8
                extraction_data = {
                    'entities': extraction_result.entities,
                    'method': extraction_result.extraction_method,
                    'confidence': avg_conf,
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Extraction error: {e}")

        return jsonify({
            'response': response_text,
            'extraction': extraction_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """Summarize a conversation (client sends messages array)."""
    try:
        data = request.json or {}
        messages = data.get('messages', [])
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400
        # Filter out any system style messages if present
        user_visible = [m for m in messages if m.get('role') in ('user','assistant')]
        if len(user_visible) < 2:  # need at least one user + one assistant ideally
            return jsonify({'summary': 'Not enough conversation content to summarize yet.'})
        # Build compact transcript
        transcript = []
        for m in user_visible[-30:]:  # limit for token economy
            role = m.get('role')
            content = (m.get('content') or '').strip().replace('\n',' ')
            if content:
                transcript.append(f"{role.upper()}: {content}")
        joined = '\n'.join(transcript)
        prompt = (
            "You are an expert recruiting operations analyst. Summarize the following recruiting conversation. "
            "Provide structured bullet sections: 1) Hiring Requirements 2) Roles & Headcount 3) Key Skills/Tech 4) Timeline & Urgency 5) Budget or Constraints (if any) 6) Proposed Next Actions 7) Open Questions to Clarify 8) Extracted Entities (company, roles, location, industry). Be concise, no fluff.\n\nConversation Transcript:\n" + joined + "\n\nStructured Summary:" )
        if not llm_service:
            return jsonify({'summary': 'LLM service unavailable'}), 503
        summary_text = llm_service.generate(prompt)
        return jsonify({'summary': summary_text})
    except Exception as e:  # pragma: no cover
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations')
def get_conversations():
    """Get conversation history (placeholder)"""
    # In a real app, this would fetch from database
    return jsonify([])

@app.route('/api/export/<format>')
def export_conversation(format):
    """Export conversation"""
    # Placeholder for export functionality
    return jsonify({'message': f'Export as {format} not implemented yet'})

@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('status', {'message': 'Connected to AI Sales Agent'})

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('typing')
def on_typing(data):
    """Handle typing indicator"""
    emit('typing', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
