"""
Unit tests for the AI Sales Agent
"""
import unittest
import tempfile
import os
from unittest.mock import Mock, patch
import sqlite3

# Test the memory service without external dependencies first
from services.memory_service import MemoryService
from models.schemas import ClientInquiry, ConversationState, UrgencyLevel
from utils.helpers import generate_session_id


class TestMemoryService(unittest.TestCase):
    """Test the memory service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Use in-memory database for tests
        self.temp_db = ":memory:"
        self.memory_service = MemoryService(self.temp_db)
    
    def test_create_session(self):
        """Test session creation"""
        session_id = self.memory_service.create_session("Hello")
        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)
        
        # Test that session exists
        conversation_state = self.memory_service.get_conversation_state(session_id)
        self.assertIsNotNone(conversation_state)
        self.assertEqual(conversation_state.session_id, session_id)
    
    def test_conversation_state_persistence(self):
        """Test saving and retrieving conversation state"""
        session_id = self.memory_service.create_session()
        
        # Create a client inquiry
        client_inquiry = ClientInquiry(
            company_name="Test Corp",
            industry="technology",
            location="San Francisco",
            roles=["software engineer", "data scientist"],
            urgency=UrgencyLevel.HIGH
        )
        
        # Update the conversation state
        self.memory_service.update_client_inquiry(session_id, client_inquiry)
        
        # Retrieve and verify
        conversation_state = self.memory_service.get_conversation_state(session_id)
        self.assertEqual(conversation_state.client_inquiry.company_name, "Test Corp")
        self.assertEqual(conversation_state.client_inquiry.industry, "technology")
        self.assertEqual(len(conversation_state.client_inquiry.roles), 2)
    
    def test_message_history(self):
        """Test message history functionality"""
        session_id = self.memory_service.create_session()
        
        # Add messages
        self.memory_service.add_message(session_id, "user", "Hello, I need to hire developers")
        self.memory_service.add_message(session_id, "assistant", "Great! I can help with that.")
        
        # Get history
        history = self.memory_service.get_conversation_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')
    
    def test_analytics_tracking(self):
        """Test analytics event tracking"""
        session_id = self.memory_service.create_session()
        
        # Track some events
        self.memory_service.track_event(session_id, "test_event", {"test": "data"})
        self.memory_service.track_event(session_id, "another_event")
        
        # Get analytics
        analytics = self.memory_service.get_analytics_summary(session_id=session_id)
        event_counts = analytics.get('event_counts', {})
        
        # Should have session_created, test_event, and another_event
        self.assertGreaterEqual(len(event_counts), 2)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_generate_session_id(self):
        """Test session ID generation"""
        session_id = generate_session_id()
        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)
        
        # Test uniqueness
        session_id2 = generate_session_id()
        self.assertNotEqual(session_id, session_id2)
    
    def test_normalize_text(self):
        """Test text normalization"""
        from utils.helpers import normalize_text
        
        test_cases = [
            ("  Hello   World  ", "hello world"),
            ("UPPERCASE", "uppercase"),
            ("Mixed Case", "mixed case"),
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = normalize_text(input_text)
                self.assertEqual(result, expected)
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        from utils.helpers import extract_contact_info
        
        test_text = "Please reach me at john@example.com or call 555-123-4567"
        contact_info = extract_contact_info(test_text)
        
        self.assertIn('email', contact_info)
        self.assertIn('phone', contact_info)
        self.assertEqual(contact_info['email'], 'john@example.com')
        self.assertEqual(contact_info['phone'], '555-123-4567')
    
    def test_validate_email(self):
        """Test email validation"""
        from utils.helpers import validate_email
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "test@",
            ""
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(validate_email(email))
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(validate_email(email))


class TestServiceRecommendationEngine(unittest.TestCase):
    """Test the service recommendation engine"""
    
    def setUp(self):
        """Set up test environment"""
        from services.recommendation_engine import ServiceRecommendationEngine
        self.engine = ServiceRecommendationEngine()
    
    def test_get_all_packages(self):
        """Test getting all packages"""
        packages = self.engine.get_all_packages()
        self.assertIsInstance(packages, list)
        self.assertGreater(len(packages), 0)
    
    def test_get_package_by_id(self):
        """Test getting package by ID"""
        package = self.engine.get_package_by_id("tech_startup_pack")
        self.assertIsNotNone(package)
        self.assertEqual(package.package_id, "tech_startup_pack")
        
        # Test non-existent package
        package = self.engine.get_package_by_id("non_existent")
        self.assertIsNone(package)
    
    def test_recommend_packages(self):
        """Test package recommendation"""
        client_inquiry = ClientInquiry(
            industry="technology",
            roles=["software engineer", "ui/ux designer"],
            urgency=UrgencyLevel.HIGH,
            location="San Francisco"
        )
        
        recommendations = self.engine.recommend_packages(client_inquiry, max_recommendations=2)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 2)
        
        # Should recommend tech startup pack for technology industry
        if recommendations:
            package_ids = [pkg.package_id for pkg in recommendations]
            self.assertIn("tech_startup_pack", package_ids)


class TestClientInquiryModel(unittest.TestCase):
    """Test the ClientInquiry model"""
    
    def test_create_empty_inquiry(self):
        """Test creating an empty inquiry"""
        inquiry = ClientInquiry()
        self.assertIsNone(inquiry.company_name)
        self.assertEqual(inquiry.roles, [])
        self.assertEqual(inquiry.role_counts, {})
    
    def test_create_full_inquiry(self):
        """Test creating a full inquiry"""
        inquiry = ClientInquiry(
            company_name="Tech Corp",
            industry="technology",
            location="New York",
            roles=["software engineer", "product manager"],
            role_counts={"software engineer": 3, "product manager": 1},
            urgency=UrgencyLevel.HIGH,
            budget_range="$80k-120k",
            additional_requirements="Must have React experience"
        )
        
        self.assertEqual(inquiry.company_name, "Tech Corp")
        self.assertEqual(inquiry.industry, "technology")
        self.assertEqual(len(inquiry.roles), 2)
        self.assertEqual(inquiry.role_counts["software engineer"], 3)
        self.assertEqual(inquiry.urgency, UrgencyLevel.HIGH)
    
    def test_urgency_enum(self):
        """Test urgency level enum"""
        inquiry = ClientInquiry(urgency=UrgencyLevel.URGENT)
        self.assertEqual(inquiry.urgency.value, "urgent")
        
        # Test all urgency levels
        for level in UrgencyLevel:
            inquiry.urgency = level
            self.assertIsInstance(inquiry.urgency.value, str)


class TestMockAIServices(unittest.TestCase):
    """Test AI services with mocked external dependencies"""
    
    @patch('services.llm_service.get_llm_service')
    def test_ner_service_initialization(self, mock_get_llm_service):
        """Test NER service initialization"""
        from services.ner_service import NERExtractionService
        
        # Mock the LLM service
        mock_llm_service = Mock()
        mock_get_llm_service.return_value = mock_llm_service
        
        ner_service = NERExtractionService(mock_llm_service)
        self.assertIsNotNone(ner_service)
        self.assertEqual(ner_service.llm_service, mock_llm_service)
    
    @patch('services.llm_service.get_llm_service')
    def test_proposal_generator_initialization(self, mock_get_llm_service):
        """Test proposal generator initialization"""
        from services.proposal_generator import ProposalGeneratorService
        
        # Mock the LLM service
        mock_llm_service = Mock()
        mock_get_llm_service.return_value = mock_llm_service
        
        proposal_service = ProposalGeneratorService(mock_llm_service)
        self.assertIsNotNone(proposal_service)
        self.assertEqual(proposal_service.llm_service, mock_llm_service)


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.memory_service = MemoryService(":memory:")
        from services.recommendation_engine import ServiceRecommendationEngine
        self.recommendation_engine = ServiceRecommendationEngine()
    
    def test_complete_conversation_flow(self):
        """Test a complete conversation flow without LLM"""
        # 1. Start session
        session_id = self.memory_service.create_session("Hi, I need to hire developers")
        self.assertIsNotNone(session_id)
        
        # 2. Update client inquiry (simulating extraction)
        client_inquiry = ClientInquiry(
            company_name="StartupXYZ",
            industry="technology",
            location="Austin",
            roles=["backend engineer", "frontend engineer"],
            role_counts={"backend engineer": 2, "frontend engineer": 1},
            urgency=UrgencyLevel.HIGH
        )
        self.memory_service.update_client_inquiry(session_id, client_inquiry)
        
        # 3. Get recommendations
        recommendations = self.recommendation_engine.recommend_packages(client_inquiry)
        self.assertGreater(len(recommendations), 0)
        
        # 4. Update conversation with recommendations
        self.memory_service.set_recommended_packages(session_id, recommendations)
        
        # 5. Verify final state
        conversation_state = self.memory_service.get_conversation_state(session_id)
        self.assertIsNotNone(conversation_state)
        self.assertEqual(len(conversation_state.recommended_packages), len(recommendations))
        self.assertEqual(conversation_state.client_inquiry.company_name, "StartupXYZ")
    
    def test_conversation_stage_progression(self):
        """Test conversation stage progression"""
        session_id = self.memory_service.create_session()
        
        # Test stage updates
        stages = ["greeting", "inquiry", "recommendation", "proposal", "follow_up"]
        for stage in stages:
            self.memory_service.update_stage(session_id, stage)
            conversation_state = self.memory_service.get_conversation_state(session_id)
            self.assertEqual(conversation_state.current_stage, stage)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
