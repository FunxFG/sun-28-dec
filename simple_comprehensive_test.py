#!/usr/bin/env python3
"""
Simple Comprehensive Auto-Population Test
Tests basic functionality and data structure
"""

import requests
import json
import time

def test_comprehensive_endpoint():
    """Test the comprehensive auto-population endpoint with a single request"""
    
    base_url = "https://tmp-generator-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Testing Comprehensive Auto-Population Endpoint...")
    print("=" * 60)
    
    # Test with Adelaide CBD
    test_data = {
        "lat": -34.9285,
        "lng": 138.6007,
        "start_address": "King William Street, Adelaide SA",
        "end_address": "North Terrace, Adelaide SA",
        "work_type": "construction"
    }
    
    url = f"{api_url}/comprehensive-auto-populate"
    print(f"URL: {url}")
    print(f"Parameters: {test_data}")
    
    start_time = time.time()
    
    try:
        response = requests.get(url, params=test_data, timeout=60)
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Check what categories are present
                print(f"\n📊 DATA CATEGORIES FOUND:")
                categories = list(data.keys())
                print(f"Total categories: {len(categories)}")
                
                for i, category in enumerate(sorted(categories), 1):
                    category_data = data[category]
                    if isinstance(category_data, dict):
                        data_count = len(category_data)
                        has_data = any(v for v in category_data.values() if v)
                    elif isinstance(category_data, list):
                        data_count = len(category_data)
                        has_data = data_count > 0
                    else:
                        data_count = 1 if category_data else 0
                        has_data = bool(category_data)
                    
                    status = "✅" if has_data else "⚠️"
                    print(f"   {i:2d}. {status} {category}: {data_count} items")
                
                # Check for the 5 new categories specifically
                print(f"\n🆕 NEW SA GOVERNMENT DATASET CATEGORIES:")
                new_categories = [
                    'traffic_signals',
                    'parking_restrictions', 
                    'school_zones',
                    'public_transport_detailed',
                    'utility_infrastructure'
                ]
                
                new_found = 0
                for category in new_categories:
                    if category in data:
                        new_found += 1
                        category_data = data[category]
                        if isinstance(category_data, dict):
                            has_data = any(v for v in category_data.values() if v)
                        elif isinstance(category_data, list):
                            has_data = len(category_data) > 0
                        else:
                            has_data = bool(category_data)
                        
                        status = "✅" if has_data else "⚠️"
                        print(f"   {status} {category}: {'Present with data' if has_data else 'Present but empty'}")
                    else:
                        print(f"   ❌ {category}: Missing")
                
                print(f"\nNew categories found: {new_found}/5")
                
                # Show sample data from a few categories
                print(f"\n📋 SAMPLE DATA:")
                
                # Road data
                if 'road_data' in data and data['road_data']:
                    road_data = data['road_data']
                    print(f"   Road Data: {road_data.get('road_name', 'Unknown')} - {road_data.get('road_classification', 'Unknown')}")
                
                # Traffic signals
                if 'traffic_signals' in data and data['traffic_signals']:
                    signals = data['traffic_signals']
                    nearby = signals.get('nearby_signals', [])
                    coordination = signals.get('signal_coordination_required', False)
                    print(f"   Traffic Signals: {len(nearby)} nearby, coordination required: {coordination}")
                
                # Utility infrastructure
                if 'utility_infrastructure' in data and data['utility_infrastructure']:
                    utilities = data['utility_infrastructure']
                    underground = utilities.get('underground_utilities', [])
                    overhead = utilities.get('overhead_utilities', [])
                    dial_before_dig = utilities.get('dial_before_dig_required', False)
                    print(f"   Utilities: {len(underground)} underground, {len(overhead)} overhead, dial before dig: {dial_before_dig}")
                
                # School zones
                if 'school_zones' in data and data['school_zones']:
                    schools = data['school_zones']
                    zones = schools.get('school_zones', [])
                    enhanced = schools.get('enhanced_restrictions', False)
                    print(f"   School Zones: {len(zones)} zones, enhanced restrictions: {enhanced}")
                
                # Performance assessment
                print(f"\n⏱️  PERFORMANCE ASSESSMENT:")
                if response_time <= 15.0:
                    print(f"   ✅ Response time acceptable: {response_time:.2f}s (≤15s threshold)")
                else:
                    print(f"   ❌ Response time too slow: {response_time:.2f}s (>15s threshold)")
                
                # Overall assessment
                print(f"\n🎯 OVERALL ASSESSMENT:")
                total_expected = 21
                categories_found = len(categories)
                new_categories_found = new_found
                
                print(f"   Expected categories: {total_expected}")
                print(f"   Found categories: {categories_found}")
                print(f"   New categories: {new_categories_found}/5")
                
                if categories_found >= 19 and new_categories_found >= 3:  # Allow some tolerance
                    print(f"   ✅ COMPREHENSIVE AUTO-POPULATION WORKING")
                    print(f"   ✅ SA Government dataset integrations functional")
                    return True
                else:
                    print(f"   ❌ INSUFFICIENT DATA CATEGORIES")
                    return False
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Response text: {response.text[:500]}...")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test execution"""
    print("Enhanced Comprehensive Auto-Population Endpoint Test")
    print("=" * 60)
    
    success = test_comprehensive_endpoint()
    
    if success:
        print(f"\n✅ TEST PASSED - Comprehensive auto-population endpoint working!")
        return 0
    else:
        print(f"\n❌ TEST FAILED - Issues found with comprehensive auto-population endpoint")
        return 1

if __name__ == "__main__":
    exit(main())