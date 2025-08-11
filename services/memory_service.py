
"""
Enhanced Memory Service for AI Sales Agent
Provides conversation state management and context handling with LangChain integration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sqlite3
from pathlib import Path

# LangChain imports (now available)
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferWindowMemory
from langchain.schema import BaseMemory
from langchain.llms.base import LLM

from models.schemas import ClientInquiry, UrgencyLevel


class ConversationState:
    """Represents the current state of a conversation"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client_inquiry: Optional[ClientInquiry] = None
        self.current_stage: str = "greeting"  # greeting, extraction, recommendation, proposal, followup
        self.context: Dict[str, Any] = {}
        self.messages: List[Dict[str, str]] = []
        self.extracted_entities: Dict[str, Any] = {}
        self.recommendations: List[Dict[str, Any]] = []
        self.last_updated: datetime = datetime.now()


class LLMWrapper(LLM):
    """Wrapper to make our LLM service compatible with LangChain"""
    
    def __init__(self, llm_service):
        super().__init__()
        object.__setattr__(self, '_llm_service', llm_service)
    
    def _call(self, prompt: str, stop=None) -> str:
        return self._llm_service.generate(prompt)
    
    @property
    def _llm_type(self) -> str:
        return "custom_wrapper"


class EnhancedMemoryService:
    """Enhanced conversation memory with LangChain integration and persistence"""
    
    def __init__(self, llm_service, db_path: str = "conversation_memory.db"):
        self.llm_service = llm_service
        self.db_path = Path(db_path)
        self.memories: Dict[str, BaseMemory] = {}
        self.conversation_states: Dict[str, ConversationState] = {}
        self.langchain_llm = LLMWrapper(llm_service)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    state_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message_type TEXT,
                    content TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES conversations (session_id)
                )
            """)
    
    def get_or_create_memory(self, session_id: str, memory_type: str = "summary") -> BaseMemory:
        """Get or create memory for a session with LangChain integration"""
        if session_id not in self.memories:
            try:
                if memory_type == "summary":
                    self.memories[session_id] = ConversationSummaryBufferMemory(
                        llm=self.langchain_llm,
                        max_token_limit=1000,
                        return_messages=True
                    )
                else:
                    self.memories[session_id] = ConversationBufferWindowMemory(
                        k=10,
                        return_messages=True
                    )
            except Exception as e:
                print(f"Error creating memory: {e}")
                # Fallback to simple buffer memory
                self.memories[session_id] = ConversationBufferWindowMemory(
                    k=10,
                    return_messages=True
                )
        
        return self.memories[session_id]
    
    def get_conversation_state(self, session_id: str) -> ConversationState:
        """Get conversation state for a session"""
        if session_id not in self.conversation_states:
            # Try to load from database
            state = self._load_state_from_db(session_id)
            if state:
                self.conversation_states[session_id] = state
            else:
                # Create new state
                self.conversation_states[session_id] = ConversationState(session_id=session_id)
        
        return self.conversation_states[session_id]
    
    def update_conversation_state(self, session_id: str, **updates) -> ConversationState:
        """Update conversation state with new information"""
        state = self.get_conversation_state(session_id)
        
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
            else:
                state.context[key] = value
        
        state.last_updated = datetime.now()
        
        # Persist to database
        self._save_state_to_db(state)
        
        return state
    
    def add_message(self, session_id: str, message_type: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation history and memory"""
        state = self.get_conversation_state(session_id)
        memory = self.get_or_create_memory(session_id)
        
        # Add to state
        message_entry = {
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        state.messages.append(message_entry)
        
        # Add to LangChain memory
        try:
            if message_type == "human":
                memory.chat_memory.add_user_message(content)
            elif message_type == "ai":
                memory.chat_memory.add_ai_message(content)
        except Exception as e:
            print(f"Error adding to memory: {e}")
        
        # Persist to database
        self._save_message_to_db(session_id, message_type, content, metadata)
        self.update_conversation_state(session_id, messages=state.messages)
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Get intelligent summary of conversation using LangChain"""
        memory = self.get_or_create_memory(session_id, "summary")
        
        try:
            if hasattr(memory, 'predict_new_summary'):
                return memory.predict_new_summary([], "")
            else:
                # Generate summary using our LLM
                state = self.get_conversation_state(session_id)
                recent_messages = state.messages[-5:]  # Last 5 messages
                
                if not recent_messages:
                    return "New conversation"
                
                summary_prompt = "Summarize this conversation in 2-3 sentences, focusing on the client's hiring needs:\n"
                for msg in recent_messages:
                    summary_prompt += f"{msg['type']}: {msg['content']}\n"
                
                return self.llm_service.generate(summary_prompt)
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Conversation in progress"
    
    def get_context_for_agent(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive context for agent decision making"""
        state = self.get_conversation_state(session_id)
        
        context = {
            "session_id": session_id,
            "current_stage": state.current_stage,
            "client_inquiry": state.client_inquiry.dict() if state.client_inquiry else None,
            "extracted_entities": state.extracted_entities,
            "recommendations": state.recommendations,
            "conversation_summary": self.get_conversation_summary(session_id),
            "message_count": len(state.messages),
            "last_updated": state.last_updated.isoformat(),
            "context": state.context
        }
        
        # Add recent messages for immediate context
        if state.messages:
            context["recent_messages"] = state.messages[-3:]
        
        return context
    
    def determine_next_action(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Intelligent next action determination with context awareness"""
        context = self.get_context_for_agent(session_id)
        state = self.get_conversation_state(session_id)
        
        # Enhanced rule-based logic for stage transitions
        current_stage = state.current_stage
        next_stage = current_stage
        action = "continue"
        confidence = 0.5
        
        user_lower = user_input.lower()
        
        # Stage progression logic with confidence scoring
        if current_stage == "greeting":
            hiring_keywords = ["hire", "need", "looking", "recruit", "position", "candidate", "developer", "engineer"]
            if any(keyword in user_lower for keyword in hiring_keywords):
                next_stage = "extraction"
                action = "extract_requirements"
                confidence = 0.8
        
        elif current_stage == "extraction":
            if state.client_inquiry and len(state.client_inquiry.roles) > 0:
                next_stage = "recommendation"
                action = "recommend_services"
                confidence = 0.9
            elif any(word in user_lower for word in ["tell me", "more", "details"]):
                action = "ask_clarification"
                confidence = 0.7
        
        elif current_stage == "recommendation":
            positive_words = ["yes", "interested", "sounds good", "proceed", "that works", "perfect"]
            if any(word in user_lower for word in positive_words):
                next_stage = "proposal"
                action = "generate_proposal"
                confidence = 0.9
            elif any(word in user_lower for word in ["no", "different", "other options"]):
                action = "provide_alternatives"
                confidence = 0.8
        
        elif current_stage == "proposal":
            accept_words = ["accept", "agree", "move forward", "yes", "proceed", "sounds good"]
            if any(word in user_lower for word in accept_words):
                next_stage = "followup"
                action = "schedule_followup"
                confidence = 0.95
            elif any(word in user_lower for word in ["modify", "change", "adjust"]):
                action = "modify_proposal"
                confidence = 0.8
        
        # Update stage if it changed
        if next_stage != current_stage:
            self.update_conversation_state(session_id, current_stage=next_stage)
        
        return {
            "current_stage": current_stage,
            "next_stage": next_stage,
            "recommended_action": action,
            "confidence": confidence,
            "context": context
        }
    
    def clear_session(self, session_id: str):
        """Clear all session data"""
        if session_id in self.memories:
            del self.memories[session_id]
        if session_id in self.conversation_states:
            del self.conversation_states[session_id]
        
        # Clear from database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
    
    def get_conversation_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get conversation quality and progress metrics"""
        state = self.get_conversation_state(session_id)
        
        # Calculate metrics
        total_messages = len(state.messages)
        user_messages = len([m for m in state.messages if m['type'] == 'human'])
        ai_messages = len([m for m in state.messages if m['type'] == 'ai'])
        
        # Engagement score based on message exchange
        engagement = min(user_messages / max(ai_messages, 1), 2.0) / 2.0
        
        # Progress score based on stage
        stage_progress = {
            "greeting": 0.2,
            "extraction": 0.4,
            "recommendation": 0.6,
            "proposal": 0.8,
            "followup": 1.0
        }
        
        progress = stage_progress.get(state.current_stage, 0.0)
        
        # Information completeness
        inquiry = state.client_inquiry
        completeness = 0.0
        if inquiry:
            fields = [inquiry.company_name, inquiry.location, inquiry.roles, inquiry.urgency]
            completeness = sum(1 for field in fields if field) / len(fields)
        
        return {
            "session_id": session_id,
            "total_messages": total_messages,
            "user_messages": user_messages, 
            "ai_messages": ai_messages,
            "engagement_score": engagement,
            "progress_score": progress,
            "information_completeness": completeness,
            "current_stage": state.current_stage,
            "last_updated": state.last_updated.isoformat()
        }
    
    def _save_state_to_db(self, state: ConversationState):
        """Save conversation state to database"""
        state_data = {
            "session_id": state.session_id,
            "client_inquiry": state.client_inquiry.dict() if state.client_inquiry else None,
            "current_stage": state.current_stage,
            "context": state.context,
            "extracted_entities": state.extracted_entities,
            "recommendations": state.recommendations,
            "last_updated": state.last_updated.isoformat()
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversations (session_id, state_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (state.session_id, json.dumps(state_data)))
    
    def _load_state_from_db(self, session_id: str) -> Optional[ConversationState]:
        """Load conversation state from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT state_data FROM conversations WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if row:
                try:
                    data = json.loads(row[0])
                    state = ConversationState(session_id=session_id)
                    
                    # Restore client inquiry
                    if data.get("client_inquiry"):
                        state.client_inquiry = ClientInquiry(**data["client_inquiry"])
                    
                    state.current_stage = data.get("current_stage", "greeting")
                    state.context = data.get("context", {})
                    state.extracted_entities = data.get("extracted_entities", {})
                    state.recommendations = data.get("recommendations", [])
                    
                    if data.get("last_updated"):
                        state.last_updated = datetime.fromisoformat(data["last_updated"])
                    
                    return state
                except Exception as e:
                    print(f"Error loading state: {e}")
                    return None
        
        return None
    
    def _save_message_to_db(self, session_id: str, message_type: str, content: str, metadata: Dict[str, Any] = None):
        """Save message to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO messages (session_id, message_type, content, metadata)
                VALUES (?, ?, ?, ?)
            """, (session_id, message_type, content, json.dumps(metadata or {})))


# Factory functions
def create_enhanced_memory_service(llm_service) -> EnhancedMemoryService:
    """Create enhanced memory service with LangChain integration"""
    return EnhancedMemoryService(llm_service)

def create_memory_service(llm_service) -> EnhancedMemoryService:
    """Alias for backward compatibility"""
    return EnhancedMemoryService(llm_service)
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from models.schemas import ConversationState, ClientInquiry, ServicePackage
from utils.helpers import generate_session_id, get_timestamp


class MemoryService:
    """Service for managing conversation memory and session state"""
    
    def __init__(self, db_path: str = "sales_agent.db"):
        self.db_path = db_path
        self._conn = None
        # For in-memory databases, keep a persistent connection
        if db_path == ":memory:":
            self._conn = sqlite3.connect(db_path)
            self._conn.row_factory = sqlite3.Row
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    client_inquiry TEXT,
                    recommended_packages TEXT,
                    conversation_history TEXT,
                    current_stage TEXT,
                    next_actions TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Messages table for detailed conversation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES conversations (session_id)
                )
            """)
            
            # Analytics table for tracking interaction patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES conversations (session_id)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper cleanup"""
        if self._conn:
            # Use persistent connection for in-memory databases
            yield self._conn
        else:
            # Create new connection for file databases
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def create_session(self, initial_message: str = None) -> str:
        """Create a new conversation session"""
        session_id = generate_session_id()
        
        # Create initial conversation state
        conversation_state = ConversationState(
            session_id=session_id,
            client_inquiry=ClientInquiry(),
            current_stage="greeting"
        )
        
        # Add initial message if provided
        if initial_message:
            conversation_state.conversation_history.append({
                "role": "user",
                "content": initial_message,
                "timestamp": get_timestamp()
            })
        
        # Save to database
        self.save_conversation_state(conversation_state)
        
        # Add initial message to messages table
        if initial_message:
            self.add_message(session_id, "user", initial_message)
        
        # Track session creation
        self.track_event(session_id, "session_created", {"initial_message": bool(initial_message)})
        
        return session_id
    
    def get_conversation_state(self, session_id: str) -> Optional[ConversationState]:
        """Retrieve conversation state by session ID"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Parse JSON fields
            client_inquiry_data = json.loads(row['client_inquiry']) if row['client_inquiry'] else {}
            recommended_packages_data = json.loads(row['recommended_packages']) if row['recommended_packages'] else []
            conversation_history_data = json.loads(row['conversation_history']) if row['conversation_history'] else []
            next_actions_data = json.loads(row['next_actions']) if row['next_actions'] else []
            
            # Create objects
            client_inquiry = ClientInquiry(**client_inquiry_data) if client_inquiry_data else ClientInquiry()
            recommended_packages = [ServicePackage(**pkg) for pkg in recommended_packages_data]
            
            return ConversationState(
                session_id=row['session_id'],
                client_inquiry=client_inquiry,
                recommended_packages=recommended_packages,
                conversation_history=conversation_history_data,
                current_stage=row['current_stage'],
                next_actions=next_actions_data,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
    
    def save_conversation_state(self, conversation_state: ConversationState):
        """Save conversation state to database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Update timestamp
            conversation_state.updated_at = datetime.now()
            
            # Serialize complex objects
            client_inquiry_json = conversation_state.client_inquiry.model_dump_json()
            recommended_packages_json = json.dumps([pkg.model_dump() for pkg in conversation_state.recommended_packages])
            conversation_history_json = json.dumps(conversation_state.conversation_history)
            next_actions_json = json.dumps(conversation_state.next_actions)
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations 
                (session_id, client_inquiry, recommended_packages, conversation_history, 
                 current_stage, next_actions, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_state.session_id,
                client_inquiry_json,
                recommended_packages_json,
                conversation_history_json,
                conversation_state.current_stage,
                next_actions_json,
                conversation_state.created_at.isoformat(),
                conversation_state.updated_at.isoformat()
            ))
            
            conn.commit()
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation history"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                role,
                content,
                get_timestamp(),
                metadata_json
            ))
            
            conn.commit()
        
        # Also update conversation state
        conversation_state = self.get_conversation_state(session_id)
        if conversation_state:
            conversation_state.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": get_timestamp(),
                "metadata": metadata or {}
            })
            self.save_conversation_state(conversation_state)
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT role, content, timestamp, metadata 
                FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (session_id,))
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                messages.append({
                    "role": row['role'],
                    "content": row['content'],
                    "timestamp": row['timestamp'],
                    "metadata": metadata
                })
            
            return list(reversed(messages))  # Return in chronological order
    
    def track_event(self, session_id: str, event_type: str, event_data: Dict[str, Any] = None):
        """Track an analytics event"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analytics (session_id, event_type, event_data, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                session_id,
                event_type,
                json.dumps(event_data) if event_data else None,
                get_timestamp()
            ))
            
            conn.commit()
    
    def update_client_inquiry(self, session_id: str, client_inquiry: ClientInquiry):
        """Update client inquiry for a session"""
        conversation_state = self.get_conversation_state(session_id)
        if conversation_state:
            conversation_state.client_inquiry = client_inquiry
            self.save_conversation_state(conversation_state)
            
            # Track the update
            self.track_event(session_id, "client_inquiry_updated", {
                "roles_count": len(client_inquiry.roles),
                "has_location": bool(client_inquiry.location),
                "has_industry": bool(client_inquiry.industry),
                "urgency": client_inquiry.urgency.value if client_inquiry.urgency else None
            })
    
    def update_stage(self, session_id: str, new_stage: str):
        """Update conversation stage"""
        conversation_state = self.get_conversation_state(session_id)
        if conversation_state:
            old_stage = conversation_state.current_stage
            conversation_state.current_stage = new_stage
            self.save_conversation_state(conversation_state)
            
            # Track stage change
            self.track_event(session_id, "stage_changed", {
                "from": old_stage,
                "to": new_stage
            })
    
    def set_recommended_packages(self, session_id: str, packages: List[ServicePackage]):
        """Set recommended packages for a session"""
        conversation_state = self.get_conversation_state(session_id)
        if conversation_state:
            conversation_state.recommended_packages = packages
            self.save_conversation_state(conversation_state)
            
            # Track recommendations
            self.track_event(session_id, "packages_recommended", {
                "package_count": len(packages),
                "package_ids": [pkg.package_id for pkg in packages]
            })
    
    def get_recent_sessions(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent conversation sessions"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, current_stage, created_at, updated_at
                FROM conversations 
                WHERE created_at > ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (cutoff_date, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_analytics_summary(self, session_id: str = None, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            base_query = "SELECT event_type, COUNT(*) as count FROM analytics WHERE timestamp > ?"
            params = [cutoff_date]
            
            if session_id:
                base_query += " AND session_id = ?"
                params.append(session_id)
            
            base_query += " GROUP BY event_type"
            
            cursor.execute(base_query, params)
            event_counts = dict(cursor.fetchall())
            
            # Get total sessions
            session_query = "SELECT COUNT(DISTINCT session_id) as total FROM conversations WHERE created_at > ?"
            cursor.execute(session_query, [cutoff_date])
            total_sessions = cursor.fetchone()['total']
            
            return {
                "event_counts": event_counts,
                "total_sessions": total_sessions,
                "time_period_days": days
            }
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old session data"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Delete old analytics
            cursor.execute("DELETE FROM analytics WHERE timestamp < ?", (cutoff_date,))
            
            # Delete old messages
            cursor.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff_date,))
            
            # Delete old conversations
            cursor.execute("DELETE FROM conversations WHERE created_at < ?", (cutoff_date,))
            
            conn.commit()
            
            return cursor.rowcount
