#!/usr/bin/env python3
"""
Test script to verify TravelORM model consistency with the database
"""

import sys
import os
from datetime import datetime, date

# Add the TravelORM to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from travel_orm.models import (
        TravelAdvisor, Itinerary, DataSource, InformationDocument, 
        Day, ItineraryItem, ProcessingEmail, StrandedItineraryItem
    )
    from travel_orm.connection import DatabaseConnection
    from sqlalchemy import text  # Import text for raw SQL queries
    print("✅ Successfully imported all TravelORM models")
except ImportError as e:
    print(f"❌ Failed to import TravelORM models: {e}")
    sys.exit(1)

def test_database_connection():
    """Test basic database connectivity"""
    print("\n🔍 Testing database connection...")
    try:
        with DatabaseConnection.session_scope() as session:
            result = session.execute(text("SELECT 1 as test")).fetchone()
            if result and result[0] == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection failed - unexpected result")
                return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_existence():
    """Test that all expected tables exist in the database"""
    print("\n🔍 Testing table existence...")
    
    expected_tables = [
        'travel_advisors', 'itineraries', 'data_sources', 
        'information_documents', 'days', 'itinerary_items',
        'processing_emails', 'stranded_itinerary_items'
    ]
    
    try:
        with DatabaseConnection.session_scope() as session:
            for table in expected_tables:
                result = session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """)).fetchone()
                
                if result and result[0]:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' does not exist")
                    return False
            
            print("✅ All expected tables exist")
            return True
            
    except Exception as e:
        print(f"❌ Error checking table existence: {e}")
        return False

def test_travel_advisor_email_field():
    """Test that travel_advisors table has the email field"""
    print("\n🔍 Testing travel_advisors email field...")
    
    try:
        with DatabaseConnection.session_scope() as session:
            result = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'travel_advisors' AND column_name = 'email'
                )
            """)).fetchone()
            
            if result and result[0]:
                print("✅ travel_advisors.email column exists")
                return True
            else:
                print("❌ travel_advisors.email column does not exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking email field: {e}")
        return False

def test_model_creation():
    """Test creating instances of each model"""
    print("\n🔍 Testing model creation...")
    
    try:
        # Test TravelAdvisor with email field
        advisor = TravelAdvisor(
            name="Test Advisor",
            email="test@example.com",
            company_name="Test Company"
        )
        print("✅ TravelAdvisor model creation successful")
        
        # Test ProcessingEmail
        processing_email = ProcessingEmail(
            email="process@example.com",
            travel_advisor_id="550e8400-e29b-41d4-a716-446655440000"  # dummy UUID
        )
        print("✅ ProcessingEmail model creation successful")
        
        # Test StrandedItineraryItem
        stranded_item = StrandedItineraryItem(
            travel_advisor_id=None,  # Test NULL allowed
            itinerary_item_id="550e8400-e29b-41d4-a716-446655440001"  # dummy UUID
        )
        print("✅ StrandedItineraryItem model creation successful")
        
        # Test ItineraryItem with NULL day_id
        itinerary_item = ItineraryItem(
            day_id=None,  # Test NULL allowed
            data_source_id="550e8400-e29b-41d4-a716-446655440002",  # dummy UUID
            index=1,
            title="Test Item",
            type="hotel"
        )
        print("✅ ItineraryItem model creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating model instances: {e}")
        return False

def test_model_relationships():
    """Test that model relationships are properly defined"""
    print("\n🔍 Testing model relationships...")
    
    try:
        # Check TravelAdvisor relationships
        advisor = TravelAdvisor()
        assert hasattr(advisor, 'processing_emails'), "TravelAdvisor missing processing_emails relationship"
        assert hasattr(advisor, 'stranded_items'), "TravelAdvisor missing stranded_items relationship"
        print("✅ TravelAdvisor relationships defined")
        
        # Check ItineraryItem relationships
        item = ItineraryItem()
        assert hasattr(item, 'stranded_record'), "ItineraryItem missing stranded_record relationship"
        print("✅ ItineraryItem relationships defined")
        
        # Check ProcessingEmail relationships
        proc_email = ProcessingEmail()
        assert hasattr(proc_email, 'travel_advisor'), "ProcessingEmail missing travel_advisor relationship"
        print("✅ ProcessingEmail relationships defined")
        
        # Check StrandedItineraryItem relationships
        stranded = StrandedItineraryItem()
        assert hasattr(stranded, 'travel_advisor'), "StrandedItineraryItem missing travel_advisor relationship"
        assert hasattr(stranded, 'itinerary_item'), "StrandedItineraryItem missing itinerary_item relationship"
        print("✅ StrandedItineraryItem relationships defined")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking relationships: {e}")
        return False

def test_database_schema_consistency():
    """Test that the database schema matches our models"""
    print("\n🔍 Testing database schema consistency...")
    
    try:
        with DatabaseConnection.session_scope() as session:
            # Test processing_emails table structure
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'processing_emails'
                ORDER BY ordinal_position
            """)).fetchall()
            
            expected_columns = ['id', 'email', 'travel_advisor_id', 'created_at', 'updated_at']
            actual_columns = [row[0] for row in result]
            
            for col in expected_columns:
                if col in actual_columns:
                    print(f"✅ processing_emails.{col} column exists")
                else:
                    print(f"❌ processing_emails.{col} column missing")
                    return False
            
            # Test stranded_itinerary_items table structure
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'stranded_itinerary_items'
                ORDER BY ordinal_position
            """)).fetchall()
            
            expected_columns = ['id', 'travel_advisor_id', 'itinerary_item_id', 'created_at', 'updated_at']
            actual_columns = [row[0] for row in result]
            
            for col in expected_columns:
                if col in actual_columns:
                    print(f"✅ stranded_itinerary_items.{col} column exists")
                else:
                    print(f"❌ stranded_itinerary_items.{col} column missing")
                    return False
            
            print("✅ Database schema consistency verified")
            return True
            
    except Exception as e:
        print(f"❌ Error checking schema consistency: {e}")
        return False

def test_database_crud_operations():
    """Test basic CRUD operations with new models"""
    print("\n🔍 Testing database CRUD operations...")
    
    try:
        with DatabaseConnection.session_scope() as session:
            # Test creating a TravelAdvisor with email
            advisor = TravelAdvisor(
                name="Test CRUD Advisor",
                email="crud@example.com",
                company_name="CRUD Test Company"
            )
            session.add(advisor)
            session.flush()  # Get the ID
            advisor_id = advisor.id
            print("✅ TravelAdvisor with email created successfully")
            
            # Test creating a ProcessingEmail
            proc_email = ProcessingEmail(
                email="crud-processing@example.com",
                travel_advisor_id=advisor_id
            )
            session.add(proc_email)
            session.flush()
            print("✅ ProcessingEmail created successfully")
            
            # Test creating an ItineraryItem with NULL day_id
            data_source = DataSource(
                type="email",
                url="crud-test@example.com"
            )
            session.add(data_source)
            session.flush()
            
            item = ItineraryItem(
                day_id=None,  # Test NULL
                data_source_id=data_source.id,
                index=1,
                title="CRUD Test Item",
                type="hotel"
            )
            session.add(item)
            session.flush()
            item_id = item.id
            print("✅ ItineraryItem with NULL day_id created successfully")
            
            # Test creating a StrandedItineraryItem
            stranded = StrandedItineraryItem(
                travel_advisor_id=advisor_id,
                itinerary_item_id=item_id
            )
            session.add(stranded)
            session.flush()
            print("✅ StrandedItineraryItem created successfully")
            
            # Clean up test data
            session.delete(stranded)
            session.delete(item)
            session.delete(data_source)
            session.delete(proc_email)
            session.delete(advisor)
            print("✅ Test data cleaned up successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Error in CRUD operations: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting TravelORM Database Consistency Tests")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_table_existence,
        test_travel_advisor_email_field,
        test_model_creation,
        test_model_relationships,
        test_database_schema_consistency,
        test_database_crud_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! TravelORM models are consistent with database.")
        return 0
    else:
        print("⚠️  Some tests failed. Database schema may need updates.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
