#!/usr/bin/env python3
"""
Test script for Location Metadata System integration
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append('/app/backend')

from comprehensive_auto_population import (
    fetch_location_metadata_system_data,
    fetch_dit_infrastructure_assets,
    get_comprehensive_auto_population
)

async def test_lms_integration():
    """Test the new LMS integration functions"""
    
    # Test coordinates (Adelaide CBD area)
    lat = -34.9285
    lng = 138.6007
    road_name = "King William Street"
    address = "King William Street, Adelaide SA"
    
    print("Testing Location Metadata System integration...")
    print("=" * 50)
    
    try:
        # Test LMS data fetch
        print("1. Testing fetch_location_metadata_system_data...")
        lms_data = await fetch_location_metadata_system_data(lat, lng, road_name)
        print(f"   Road Name: {lms_data.get('road_name')}")
        print(f"   Classification: {lms_data.get('road_classification_official')}")
        print(f"   Maintenance Authority: {lms_data.get('maintenance_authority')}")
        print(f"   CRRS Code: {lms_data.get('crrs_code')}")
        print(f"   Data Source: {lms_data.get('data_source')}")
        print()
        
        # Test DIT infrastructure assets
        print("2. Testing fetch_dit_infrastructure_assets...")
        dit_data = await fetch_dit_infrastructure_assets(lat, lng, address)
        print(f"   Road Condition: {dit_data.get('road_condition')}")
        print(f"   Pavement Type: {dit_data.get('pavement_type')}")
        print(f"   Asset Inventory: {len(dit_data.get('asset_inventory', []))} items")
        print(f"   Data Source: {dit_data.get('data_source')}")
        print()
        
        # Test comprehensive integration
        print("3. Testing comprehensive auto-population with LMS integration...")
        result = await get_comprehensive_auto_population(lat, lng, address, address, "road_maintenance")
        
        print(f"   Road Data Available: {'road_data' in result}")
        print(f"   LMS Data Available: {'location_metadata_system' in result}")
        print(f"   DIT Assets Available: {'dit_infrastructure_assets' in result}")
        
        if 'location_metadata_system' in result:
            lms_result = result['location_metadata_system']
            print(f"   LMS Road Classification: {lms_result.get('road_classification_official')}")
            print(f"   LMS Functional Hierarchy: {lms_result.get('functional_hierarchy')}")
        
        if 'dit_infrastructure_assets' in result:
            dit_result = result['dit_infrastructure_assets']
            print(f"   DIT Road Condition: {dit_result.get('road_condition')}")
            maintenance_schedule = dit_result.get('maintenance_schedule') or {}
            print(f"   DIT Maintenance Contact: {maintenance_schedule.get('contact', 'N/A')}")
        
        print()
        print("✅ Location Metadata System integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lms_integration())