"""
Tests for the database models
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import uuid

from travel_orm.models import (
    TravelAdvisor, Itinerary, Day, ItineraryItem, 
    DataSource, InformationDocument, Model
)


class TestModels(unittest.TestCase):
    """Test cases for model classes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.advisor_id = uuid.uuid4()
        self.itinerary_id = uuid.uuid4()
        self.day_id = uuid.uuid4()
        self.item_id = uuid.uuid4()
        self.data_source_id = uuid.uuid4()
        self.doc_id = uuid.uuid4()
        
        # Create model instances for testing
        self.advisor = TravelAdvisor(
            id=self.advisor_id,
            name="Test Advisor",
            phone_number="555-123-4567",
            company_name="Test Company"
        )
        
        self.itinerary = Itinerary(
            id=self.itinerary_id,
            travel_advisor_id=self.advisor_id,
            start_date=date(2025, 7, 1),
            duration=7,
            destination="Test Destination"
        )
        
        self.day = Day(
            id=self.day_id,
            itinerary_id=self.itinerary_id,
            index=1,
            title="Day 1"
        )
        
        self.item = ItineraryItem(
            id=self.item_id,
            day_id=self.day_id,
            index=1,
            title="Test Item",
            type="hotel"
        )
        
        self.data_source = DataSource(
            id=self.data_source_id,
            type="email",
            url="s3://bucket/key"
        )
        
        self.doc = InformationDocument(
            id=self.doc_id,
            itinerary_id=self.itinerary_id,
            index=1,
            title="Test Document"
        )
    
    @patch('travel_orm.models.DatabaseConnection.session_scope')
    def test_create(self, mock_session_scope):
        """Test creating a model instance"""
        # Setup mock
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Test creating a travel advisor
        TravelAdvisor.create(
            name="New Advisor",
            phone_number="555-987-6543",
            company_name="New Company"
        )
        
        # Verify
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @patch('travel_orm.models.DatabaseConnection.session_scope')
    def test_get_by_id(self, mock_session_scope):
        """Test getting a model by ID"""
        # Setup mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Test getting a travel advisor by ID
        TravelAdvisor.get_by_id(self.advisor_id)
        
        # Verify
        mock_session.query.assert_called_once_with(TravelAdvisor)
        mock_query.get.assert_called_once_with(self.advisor_id)
    
    @patch('travel_orm.models.DatabaseConnection.session_scope')
    def test_list_all(self, mock_session_scope):
        """Test listing all model instances"""
        # Setup mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Test listing all travel advisors
        TravelAdvisor.list_all()
        
        # Verify
        mock_session.query.assert_called_once_with(TravelAdvisor)
        mock_query.all.assert_called_once()
        
        # Test with limit
        mock_session.reset_mock()
        mock_query.reset_mock()
        TravelAdvisor.list_all(limit=10)
        
        # Verify
        mock_session.query.assert_called_once_with(TravelAdvisor)
        mock_query.limit.assert_called_once_with(10)
        mock_query.limit.return_value.all.assert_called_once()
    
    @patch('travel_orm.models.DatabaseConnection.session_scope')
    def test_update(self, mock_session_scope):
        """Test updating a model instance"""
        # Setup mock
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Test updating a travel advisor
        self.advisor.update(
            name="Updated Name",
            phone_number="555-111-2222"
        )
        
        # Verify
        self.assertEqual(self.advisor.name, "Updated Name")
        self.assertEqual(self.advisor.phone_number, "555-111-2222")
        mock_session.add.assert_called_once_with(self.advisor)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @patch('travel_orm.models.DatabaseConnection.session_scope')
    def test_delete(self, mock_session_scope):
        """Test deleting a model instance"""
        # Setup mock
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Test deleting a travel advisor
        result = self.advisor.delete()
        
        # Verify
        self.assertTrue(result)
        mock_session.delete.assert_called_once_with(self.advisor)
    
    @patch('travel_orm.models.DatabaseConnection.session_scope')
    def test_execute_query(self, mock_session_scope):
        """Test executing a custom query"""
        # Setup mock
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_session_scope.return_value = mock_context
        
        # Define a query function
        def query_func(session):
            return session.query(TravelAdvisor).filter_by(name="Test").all()
        
        # Test executing the query
        TravelAdvisor.execute_query(query_func)
        
        # Verify
        mock_session.query.assert_called_once_with(TravelAdvisor)
        mock_session.query.return_value.filter_by.assert_called_once_with(name="Test")
        mock_session.query.return_value.filter_by.return_value.all.assert_called_once()
    
    def test_to_dict(self):
        """Test converting models to dictionaries"""
        # Test TravelAdvisor to_dict
        advisor_dict = self.advisor.to_dict()
        self.assertEqual(advisor_dict['id'], str(self.advisor_id))
        self.assertEqual(advisor_dict['name'], "Test Advisor")
        self.assertEqual(advisor_dict['phone_number'], "555-123-4567")
        self.assertEqual(advisor_dict['company_name'], "Test Company")
        
        # Test Itinerary to_dict
        itinerary_dict = self.itinerary.to_dict()
        self.assertEqual(itinerary_dict['id'], str(self.itinerary_id))
        self.assertEqual(itinerary_dict['travel_advisor_id'], str(self.advisor_id))
        self.assertEqual(itinerary_dict['start_date'], "2025-07-01")
        self.assertEqual(itinerary_dict['duration'], 7)
        self.assertEqual(itinerary_dict['destination'], "Test Destination")
        
        # Test Day to_dict
        day_dict = self.day.to_dict()
        self.assertEqual(day_dict['id'], str(self.day_id))
        self.assertEqual(day_dict['itinerary_id'], str(self.itinerary_id))
        self.assertEqual(day_dict['index'], 1)
        self.assertEqual(day_dict['title'], "Day 1")
        
        # Test ItineraryItem to_dict
        item_dict = self.item.to_dict()
        self.assertEqual(item_dict['id'], str(self.item_id))
        self.assertEqual(item_dict['day_id'], str(self.day_id))
        self.assertEqual(item_dict['index'], 1)
        self.assertEqual(item_dict['title'], "Test Item")
        self.assertEqual(item_dict['type'], "hotel")


if __name__ == '__main__':
    unittest.main()
