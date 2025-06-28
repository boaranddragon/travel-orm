#!/usr/bin/env python3
"""
Test script to verify existing TravelORM models still work correctly
"""

import sys
import os
from datetime import datetime, date

# Add the TravelORM to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from travel_orm.models import (
        TravelAdvisor, Itinerary, DataSource, InformationDocument, 
        Day, ItineraryItem
    )
    print("✅ Successfully imported existing TravelORM models")
except ImportError as e:
    print(f"❌ Failed to import TravelORM models: {e}")
    sys.exit(1)

def test_existing_travel_advisor():
    """Test that existing TravelAdvisor functionality still works"""
    print("\n🔍 Testing existing TravelAdvisor functionality...")
    
    # Test creation without email (backward compatibility)
    advisor = TravelAdvisor(
        name="Test Advisor",
        company_name="Test Company",
        phone_number="123-456-7890"
    )
    assert advisor.name == "Test Advisor"
    assert advisor.company_name == "Test Company"
    print("✅ TravelAdvisor creation without email works (backward compatibility)")
    
    # Test existing relationships
    assert hasattr(advisor, 'itineraries'), "TravelAdvisor missing itineraries relationship"
    print("✅ TravelAdvisor existing relationships preserved")
    
    # Test to_dict method
    advisor_dict = advisor.to_dict()
    expected_fields = ['id', 'name', 'email', 'phone_number', 'website', 'profile_image', 
                      'company_name', 'company_logo', 'created_at', 'updated_at']
    for field in expected_fields:
        assert field in advisor_dict, f"Missing field {field} in to_dict()"
    print("✅ TravelAdvisor.to_dict() includes all expected fields")
    
    return True

def test_existing_itinerary_item():
    """Test that existing ItineraryItem functionality still works"""
    print("\n🔍 Testing existing ItineraryItem functionality...")
    
    # Test creation with day_id (existing functionality)
    item = ItineraryItem(
        day_id="550e8400-e29b-41d4-a716-446655440000",
        data_source_id="550e8400-e29b-41d4-a716-446655440001",
        index=1,
        title="Test Hotel",
        type="hotel",
        detail_text="A nice hotel"
    )
    assert item.title == "Test Hotel"
    assert item.type == "hotel"
    assert item.day_id is not None
    print("✅ ItineraryItem creation with day_id works (existing functionality)")
    
    # Test existing relationships
    assert hasattr(item, 'day'), "ItineraryItem missing day relationship"
    assert hasattr(item, 'data_source'), "ItineraryItem missing data_source relationship"
    print("✅ ItineraryItem existing relationships preserved")
    
    # Test to_dict method
    item_dict = item.to_dict()
    expected_fields = ['id', 'day_id', 'data_source_id', 'index', 'title', 'type', 
                      'detail_text', 'photos', 'created_at', 'updated_at']
    for field in expected_fields:
        assert field in item_dict, f"Missing field {field} in to_dict()"
    print("✅ ItineraryItem.to_dict() includes all expected fields")
    
    return True

def test_existing_day_model():
    """Test that Day model works correctly (including the fix)"""
    print("\n🔍 Testing Day model...")
    
    # Test creation
    day = Day(
        itinerary_id="550e8400-e29b-41d4-a716-446655440000",
        indices=[1, 2, 3],
        title="Day 1-3: Tokyo"
    )
    assert day.indices == [1, 2, 3]
    assert day.title == "Day 1-3: Tokyo"
    print("✅ Day model creation works correctly")
    
    # Test __repr__ method (this was fixed)
    repr_str = repr(day)
    assert "Day(" in repr_str
    assert "indices=[1, 2, 3]" in repr_str
    print("✅ Day.__repr__() works correctly with indices")
    
    # Test to_dict method
    day_dict = day.to_dict()
    assert 'indices' in day_dict
    assert day_dict['indices'] == [1, 2, 3]
    print("✅ Day.to_dict() includes indices correctly")
    
    return True

def test_existing_data_source():
    """Test that DataSource model still works"""
    print("\n🔍 Testing DataSource model...")
    
    # Test creation
    data_source = DataSource(
        type="email",
        url="test@example.com"
    )
    assert data_source.type == "email"
    assert data_source.url == "test@example.com"
    print("✅ DataSource model creation works")
    
    # Test relationships
    assert hasattr(data_source, 'information_documents'), "DataSource missing information_documents relationship"
    assert hasattr(data_source, 'itinerary_items'), "DataSource missing itinerary_items relationship"
    print("✅ DataSource relationships preserved")
    
    return True

def test_existing_itinerary():
    """Test that Itinerary model still works"""
    print("\n🔍 Testing Itinerary model...")
    
    # Test creation
    itinerary = Itinerary(
        travel_advisor_id="550e8400-e29b-41d4-a716-446655440000",
        start_date=date(2025, 7, 1),
        duration=7,
        destination="Tokyo, Japan"
    )
    assert itinerary.destination == "Tokyo, Japan"
    assert itinerary.duration == 7
    print("✅ Itinerary model creation works")
    
    # Test relationships
    assert hasattr(itinerary, 'travel_advisor'), "Itinerary missing travel_advisor relationship"
    assert hasattr(itinerary, 'days'), "Itinerary missing days relationship"
    assert hasattr(itinerary, 'information_documents'), "Itinerary missing information_documents relationship"
    print("✅ Itinerary relationships preserved")
    
    return True

def test_existing_information_document():
    """Test that InformationDocument model still works"""
    print("\n🔍 Testing InformationDocument model...")
    
    # Test creation
    info_doc = InformationDocument(
        itinerary_id="550e8400-e29b-41d4-a716-446655440000",
        data_source_id="550e8400-e29b-41d4-a716-446655440001",
        index=1,
        title="Travel Confirmation",
        text="Your travel is confirmed"
    )
    assert info_doc.title == "Travel Confirmation"
    assert info_doc.index == 1
    print("✅ InformationDocument model creation works")
    
    # Test relationships
    assert hasattr(info_doc, 'itinerary'), "InformationDocument missing itinerary relationship"
    assert hasattr(info_doc, 'data_source'), "InformationDocument missing data_source relationship"
    print("✅ InformationDocument relationships preserved")
    
    return True

def main():
    """Run all existing model tests"""
    print("🚀 Starting Existing TravelORM Model Tests")
    print("=" * 60)
    
    tests = [
        test_existing_travel_advisor,
        test_existing_itinerary_item,
        test_existing_day_model,
        test_existing_data_source,
        test_existing_itinerary,
        test_existing_information_document
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
        print("🎉 All existing model tests passed!")
        print("📋 Backward compatibility maintained")
        return 0
    else:
        print("⚠️  Some existing model tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
