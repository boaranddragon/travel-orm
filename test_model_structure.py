#!/usr/bin/env python3
"""
Test script to verify TravelORM model structure without database connectivity
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
    print("✅ Successfully imported all TravelORM models")
except ImportError as e:
    print(f"❌ Failed to import TravelORM models: {e}")
    sys.exit(1)

def test_travel_advisor_model():
    """Test TravelAdvisor model structure"""
    print("\n🔍 Testing TravelAdvisor model...")
    
    # Test that email field exists
    advisor = TravelAdvisor()
    assert hasattr(advisor, 'email'), "TravelAdvisor missing email field"
    print("✅ TravelAdvisor has email field")
    
    # Test relationships
    assert hasattr(advisor, 'processing_emails'), "TravelAdvisor missing processing_emails relationship"
    assert hasattr(advisor, 'stranded_items'), "TravelAdvisor missing stranded_items relationship"
    print("✅ TravelAdvisor has new IG Mode relationships")
    
    # Test model creation with email
    advisor = TravelAdvisor(
        name="Test Advisor",
        email="test@example.com",
        company_name="Test Company"
    )
    assert advisor.name == "Test Advisor"
    assert advisor.email == "test@example.com"
    print("✅ TravelAdvisor model creation with email successful")
    
    return True

def test_processing_email_model():
    """Test ProcessingEmail model structure"""
    print("\n🔍 Testing ProcessingEmail model...")
    
    # Test model creation
    proc_email = ProcessingEmail(
        email="process@example.com",
        travel_advisor_id="550e8400-e29b-41d4-a716-446655440000"
    )
    assert proc_email.email == "process@example.com"
    print("✅ ProcessingEmail model creation successful")
    
    # Test relationships
    assert hasattr(proc_email, 'travel_advisor'), "ProcessingEmail missing travel_advisor relationship"
    print("✅ ProcessingEmail has travel_advisor relationship")
    
    # Test table name
    assert ProcessingEmail.__tablename__ == 'processing_emails'
    print("✅ ProcessingEmail has correct table name")
    
    return True

def test_stranded_itinerary_item_model():
    """Test StrandedItineraryItem model structure"""
    print("\n🔍 Testing StrandedItineraryItem model...")
    
    # Test model creation with NULL travel_advisor_id
    stranded = StrandedItineraryItem(
        travel_advisor_id=None,  # Test NULL allowed
        itinerary_item_id="550e8400-e29b-41d4-a716-446655440001"
    )
    assert stranded.travel_advisor_id is None
    print("✅ StrandedItineraryItem allows NULL travel_advisor_id")
    
    # Test model creation with travel_advisor_id
    stranded_with_advisor = StrandedItineraryItem(
        travel_advisor_id="550e8400-e29b-41d4-a716-446655440000",
        itinerary_item_id="550e8400-e29b-41d4-a716-446655440001"
    )
    assert stranded_with_advisor.travel_advisor_id is not None
    print("✅ StrandedItineraryItem accepts travel_advisor_id")
    
    # Test relationships
    assert hasattr(stranded, 'travel_advisor'), "StrandedItineraryItem missing travel_advisor relationship"
    assert hasattr(stranded, 'itinerary_item'), "StrandedItineraryItem missing itinerary_item relationship"
    print("✅ StrandedItineraryItem has proper relationships")
    
    # Test table name
    assert StrandedItineraryItem.__tablename__ == 'stranded_itinerary_items'
    print("✅ StrandedItineraryItem has correct table name")
    
    return True

def test_itinerary_item_model():
    """Test ItineraryItem model updates"""
    print("\n🔍 Testing ItineraryItem model...")
    
    # Test model creation with NULL day_id
    item = ItineraryItem(
        day_id=None,  # Test NULL allowed
        data_source_id="550e8400-e29b-41d4-a716-446655440002",
        index=1,
        title="Test Item",
        type="hotel"
    )
    assert item.day_id is None
    print("✅ ItineraryItem allows NULL day_id")
    
    # Test new relationship
    assert hasattr(item, 'stranded_record'), "ItineraryItem missing stranded_record relationship"
    print("✅ ItineraryItem has stranded_record relationship")
    
    return True

def test_model_to_dict_methods():
    """Test that to_dict methods work with new fields"""
    print("\n🔍 Testing to_dict methods...")
    
    # Test TravelAdvisor to_dict with email
    advisor = TravelAdvisor(name="Test", email="test@example.com")
    advisor_dict = advisor.to_dict()
    assert 'email' in advisor_dict
    assert advisor_dict['email'] == "test@example.com"
    print("✅ TravelAdvisor.to_dict() includes email field")
    
    # Test ProcessingEmail to_dict
    proc_email = ProcessingEmail(
        email="test@example.com",
        travel_advisor_id="550e8400-e29b-41d4-a716-446655440000"
    )
    proc_dict = proc_email.to_dict()
    assert 'email' in proc_dict
    assert 'travel_advisor_id' in proc_dict
    print("✅ ProcessingEmail.to_dict() works correctly")
    
    # Test StrandedItineraryItem to_dict
    stranded = StrandedItineraryItem(
        travel_advisor_id=None,
        itinerary_item_id="550e8400-e29b-41d4-a716-446655440001"
    )
    stranded_dict = stranded.to_dict()
    assert 'travel_advisor_id' in stranded_dict
    assert 'itinerary_item_id' in stranded_dict
    assert stranded_dict['travel_advisor_id'] is None
    print("✅ StrandedItineraryItem.to_dict() works correctly")
    
    return True

def test_model_repr_methods():
    """Test that __repr__ methods work correctly"""
    print("\n🔍 Testing __repr__ methods...")
    
    # Test ProcessingEmail repr
    proc_email = ProcessingEmail(
        email="test@example.com",
        travel_advisor_id="550e8400-e29b-41d4-a716-446655440000"
    )
    repr_str = repr(proc_email)
    assert "ProcessingEmail" in repr_str
    assert "test@example.com" in repr_str
    print("✅ ProcessingEmail.__repr__() works correctly")
    
    # Test StrandedItineraryItem repr
    stranded = StrandedItineraryItem(
        travel_advisor_id=None,
        itinerary_item_id="550e8400-e29b-41d4-a716-446655440001"
    )
    repr_str = repr(stranded)
    assert "StrandedItineraryItem" in repr_str
    print("✅ StrandedItineraryItem.__repr__() works correctly")
    
    return True

def main():
    """Run all model structure tests"""
    print("🚀 Starting TravelORM Model Structure Tests")
    print("=" * 60)
    
    tests = [
        test_travel_advisor_model,
        test_processing_email_model,
        test_stranded_itinerary_item_model,
        test_itinerary_item_model,
        test_model_to_dict_methods,
        test_model_repr_methods
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
        print("🎉 All model structure tests passed!")
        print("📋 TravelORM models are properly structured for IG Mode")
        return 0
    else:
        print("⚠️  Some model structure tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
