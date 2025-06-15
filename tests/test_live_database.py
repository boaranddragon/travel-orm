"""
Live database testing for TravelORM

This script tests the TravelORM library against the actual AWS RDS database.
It requires proper AWS credentials and environment variables to be set.

Environment variables:
- DB_SECRET_NAME: Name of the AWS Secrets Manager secret containing database credentials
  (default: 'travel-itinerary-db-credentials')
- AWS_REGION: AWS region where the secret is stored (default: 'us-west-1')

Usage:
    python test_live_database.py
"""

import os
import sys
import uuid
import logging
from datetime import date, datetime, timedelta

# Add the parent directory to the path so we can import the travel_orm package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from travel_orm.connection import test_connection, DatabaseConnection
from travel_orm.models import (
    TravelAdvisor, Itinerary, Day, ItineraryItem, 
    DataSource, InformationDocument
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set AWS region if not already set
if 'AWS_REGION' not in os.environ:
    os.environ['AWS_REGION'] = 'us-west-1'

# Set DB_SECRET_NAME if not already set
if 'DB_SECRET_NAME' not in os.environ:
    os.environ['DB_SECRET_NAME'] = 'travel-itinerary-db-credentials'


class LiveDatabaseTest:
    """Test class for running live database tests"""
    
    def __init__(self):
        """Initialize test class"""
        self.test_id = str(uuid.uuid4())[:8]  # Use a unique ID for this test run
        self.created_objects = {
            'advisor': None,
            'data_source': None,
            'itinerary': None,
            'days': [],
            'items': [],
            'documents': []
        }
        logger.info(f"Initialized test run with ID: {self.test_id}")
    
    def run_tests(self):
        """Run all tests"""
        try:
            self.test_connection()
            self.test_create_advisor()
            self.test_create_data_source()
            self.test_create_itinerary()
            self.test_create_days()
            self.test_create_items()
            self.test_create_document()
            self.test_query_operations()
            self.test_update_operations()
            logger.info("All tests completed successfully!")
            return True
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            return False
        finally:
            self.cleanup()
    
    def test_connection(self):
        """Test database connection"""
        logger.info("Testing database connection...")
        result = test_connection()
        logger.info(result)
        if "Successfully connected" not in result:
            raise Exception("Failed to connect to database")
    
    def test_create_advisor(self):
        """Test creating a travel advisor"""
        logger.info("Testing travel advisor creation...")
        advisor = TravelAdvisor.create(
            name=f"Test Advisor {self.test_id}",
            phone_number="555-123-4567",
            website="https://example.com",
            company_name=f"Test Company {self.test_id}"
        )
        logger.info(f"Created advisor: {advisor}")
        self.created_objects['advisor'] = advisor
        
        # Verify by retrieving
        retrieved = TravelAdvisor.get_by_id(advisor.id)
        if not retrieved or retrieved.name != advisor.name:
            raise Exception("Failed to retrieve created advisor")
        
        # Store the retrieved object for future use
        self.created_objects['advisor'] = retrieved
        logger.info("Travel advisor creation test passed")
    
    def test_create_data_source(self):
        """Test creating a data source"""
        logger.info("Testing data source creation...")
        data_source = DataSource.create(
            type="email",
            url=f"s3://test-bucket/test-{self.test_id}.eml"
        )
        logger.info(f"Created data source: {data_source}")
        self.created_objects['data_source'] = data_source
        
        # Verify by retrieving
        retrieved = DataSource.get_by_id(data_source.id)
        if not retrieved or retrieved.url != data_source.url:
            raise Exception("Failed to retrieve created data source")
            
        # Store the retrieved object for future use
        self.created_objects['data_source'] = retrieved
        logger.info("Data source creation test passed")
    
    def test_create_itinerary(self):
        """Test creating an itinerary"""
        logger.info("Testing itinerary creation...")
        start_date = date.today() + timedelta(days=30)  # 30 days from now
        itinerary = Itinerary.create(
            owner_id=self.created_objects['advisor'].id,
            start_date=start_date,
            duration=7,
            destination=f"Test Destination {self.test_id}"
        )
        logger.info(f"Created itinerary: {itinerary}")
        self.created_objects['itinerary'] = itinerary
        
        # Verify by retrieving
        retrieved = Itinerary.get_by_id(itinerary.id)
        if not retrieved or retrieved.destination != itinerary.destination:
            raise Exception("Failed to retrieve created itinerary")
            
        # Store the retrieved object for future use
        self.created_objects['itinerary'] = retrieved
        logger.info("Itinerary creation test passed")
    
    def test_create_days(self):
        """Test creating days for an itinerary"""
        logger.info("Testing day creation...")
        itinerary = self.created_objects['itinerary']
        
        for i in range(1, 4):  # Create 3 days
            day = Day.create(
                itinerary_id=itinerary.id,
                index=i,
                title=f"Day {i} - Test {self.test_id}"
            )
            logger.info(f"Created day: {day}")
            
            # Verify by retrieving and store the retrieved object
            retrieved = Day.get_by_id(day.id)
            if not retrieved:
                raise Exception(f"Failed to retrieve created day {i}")
            self.created_objects['days'].append(retrieved)
        
        # Verify all days were created
        def query_func(session):
            return session.query(Day).filter_by(itinerary_id=itinerary.id).order_by(Day.index).all()
        
        days = Day.execute_query(query_func)
        if len(days) != 3:
            raise Exception(f"Expected 3 days, got {len(days)}")
        logger.info("Day creation test passed")
    
    def test_create_items(self):
        """Test creating itinerary items"""
        logger.info("Testing itinerary item creation...")
        
        # Create items for each day
        for day in self.created_objects['days']:
            # Create a hotel item
            hotel = ItineraryItem.create(
                day_id=day.id,
                index=1,
                title=f"Hotel {day.index} - Test {self.test_id}",
                type="hotel",
                detail_text="Test hotel details",
                data_source_id=self.created_objects['data_source'].id
            )
            logger.info(f"Created hotel item: {hotel}")
            self.created_objects['items'].append(hotel)
            
            # Create an activity item
            activity = ItineraryItem.create(
                day_id=day.id,
                index=2,
                title=f"Activity {day.index} - Test {self.test_id}",
                type="activity",
                detail_text="Test activity details"
            )
            logger.info(f"Created activity item: {activity}")
            self.created_objects['items'].append(activity)
        
        # Verify by retrieving
        def query_func(session):
            return session.query(ItineraryItem).filter(
                ItineraryItem.day_id.in_([day.id for day in self.created_objects['days']])
            ).all()
        
        items = ItineraryItem.execute_query(query_func)
        if len(items) != 6:  # 2 items per day, 3 days
            raise Exception(f"Expected 6 items, got {len(items)}")
        logger.info("Itinerary item creation test passed")
    
    def test_create_document(self):
        """Test creating an information document"""
        logger.info("Testing information document creation...")
        document = InformationDocument.create(
            itinerary_id=self.created_objects['itinerary'].id,
            data_source_id=self.created_objects['data_source'].id,
            index=1,
            title=f"Test Document {self.test_id}",
            text="This is a test document.",
            formatted_text="<p>This is a test document.</p>"
        )
        logger.info(f"Created document: {document}")
        self.created_objects['documents'].append(document)
        
        # Verify by retrieving
        retrieved = InformationDocument.get_by_id(document.id)
        if not retrieved or retrieved.title != document.title:
            raise Exception("Failed to retrieve created document")
        logger.info("Information document creation test passed")
    
    def test_query_operations(self):
        """Test complex query operations"""
        logger.info("Testing complex query operations...")
        
        # Test querying itineraries by advisor
        def query_itineraries_by_advisor(session):
            return session.query(Itinerary).filter_by(
                travel_advisor_id=self.created_objects['advisor'].id
            ).all()
        
        itineraries = Itinerary.execute_query(query_itineraries_by_advisor)
        if len(itineraries) < 1:
            raise Exception("Failed to query itineraries by advisor")
        logger.info(f"Found {len(itineraries)} itineraries for advisor")
        
        # Test querying items by type
        def query_items_by_type(session):
            return session.query(ItineraryItem).filter_by(type="hotel").all()
        
        hotels = ItineraryItem.execute_query(query_items_by_type)
        if len(hotels) < 3:  # We created 3 hotels (1 per day)
            raise Exception("Failed to query items by type")
        logger.info(f"Found {len(hotels)} hotel items")
        
        # Test a more complex join query
        def query_items_with_day_and_itinerary(session):
            return session.query(ItineraryItem, Day, Itinerary).join(
                Day, ItineraryItem.day_id == Day.id
            ).join(
                Itinerary, Day.itinerary_id == Itinerary.id
            ).filter(
                Itinerary.id == self.created_objects['itinerary'].id
            ).all()
        
        results = ItineraryItem.execute_query(query_items_with_day_and_itinerary)
        if len(results) != 6:  # 2 items per day, 3 days
            raise Exception(f"Expected 6 results from join query, got {len(results)}")
        logger.info("Complex query operations test passed")
    
    def test_update_operations(self):
        """Test update operations"""
        logger.info("Testing update operations...")
        
        # Update itinerary
        itinerary = self.created_objects['itinerary']
        updated_itinerary = itinerary.update(
            destination=f"Updated Destination {self.test_id}",
            duration=10
        )
        
        # Verify update
        retrieved = Itinerary.get_by_id(itinerary.id)
        if retrieved.destination != f"Updated Destination {self.test_id}" or retrieved.duration != 10:
            raise Exception("Failed to update itinerary")
        logger.info("Itinerary update test passed")
        
        # Update an item
        item = self.created_objects['items'][0]
        updated_item = item.update(
            title=f"Updated Item {self.test_id}",
            detail_text="Updated details"
        )
        
        # Verify update
        retrieved = ItineraryItem.get_by_id(item.id)
        if retrieved.title != f"Updated Item {self.test_id}" or retrieved.detail_text != "Updated details":
            raise Exception("Failed to update item")
        logger.info("Item update test passed")
    
    def cleanup(self):
        """Clean up test data"""
        logger.info("Cleaning up test data...")
        
        try:
            # Delete in reverse order of creation to respect foreign key constraints
            for document in self.created_objects['documents']:
                if document and hasattr(document, 'id'):
                    document.delete()
            
            for item in self.created_objects['items']:
                if item and hasattr(item, 'id'):
                    item.delete()
            
            for day in self.created_objects['days']:
                if day and hasattr(day, 'id'):
                    day.delete()
            
            if self.created_objects['itinerary'] and hasattr(self.created_objects['itinerary'], 'id'):
                self.created_objects['itinerary'].delete()
            
            if self.created_objects['data_source'] and hasattr(self.created_objects['data_source'], 'id'):
                self.created_objects['data_source'].delete()
            
            if self.created_objects['advisor'] and hasattr(self.created_objects['advisor'], 'id'):
                self.created_objects['advisor'].delete()
            
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    test = LiveDatabaseTest()
    success = test.run_tests()
    sys.exit(0 if success else 1)
