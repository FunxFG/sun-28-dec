#!/usr/bin/env python3
"""
Quick test of comprehensive auto-populate endpoint
"""

import requests
import json
import time

def test_comprehensive_endpoint():
    """Test the comprehensive auto-populate endpoint with one scenario"""
    
    base_url = "https://roadworksai.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Testing Comprehensive Auto-Populate Endpoint...")
    print(f"   Base URL: {base_url}")
    
    # Test Scenario 1: King William Street
    params = {
        "lat": -34.9285,
        "lng": 138.6007,
        "start_address": "King William Street, Adelaide SA",
        "end_address": "North Terrace, Adelaide SA",
        "work_type": "Road Closure"
    }
    
    url = f"{api_url}/comprehensive-auto-populate"
    
    try:
        print(f"\n📡 Making request to: {url}")
        print(f"   Parameters: {params}")
        
        start_time = time.time()
        response = requests.get(url, params=params, timeout=120)  # 2 minute timeout
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"   Response time: {response_time:.2f} seconds")
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Check basic structure
                print(f"\n📊 Response Analysis:")
                print(f"   Response type: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"   Top-level keys: {list(data.keys())}")
                    
                    # Check for key fields
                    key_fields = [
                        'road_data', 'traffic_assessment', 'site_assessment',
                        'pedestrian_control_measures', 'signage_plan', 'detour_routes',
                        'sa_traffic_intelligence'
                    ]
                    
                    present_fields = []
                    missing_fields = []
                    
                    for field in key_fields:
                        if field in data:
                            present_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    print(f"   Present key fields: {present_fields}")
                    if missing_fields:
                        print(f"   Missing key fields: {missing_fields}")
                    
                    # Check SA Traffic Intelligence
                    if 'sa_traffic_intelligence' in data:
                        sa_traffic = data['sa_traffic_intelligence']
                        print(f"\n🚦 SA Traffic Intelligence:")
                        print(f"   Type: {type(sa_traffic)}")
                        if isinstance(sa_traffic, dict):
                            print(f"   Keys: {list(sa_traffic.keys())}")
                            
                            # Check Top 40 Road Analysis
                            if 'top_40_road_analysis' in sa_traffic:
                                top_40_road = sa_traffic['top_40_road_analysis']
                                print(f"   Top 40 Road: {top_40_road}")
                            
                            # Check Top 40 Intersection Analysis
                            if 'top_40_intersection_analysis' in sa_traffic:
                                top_40_intersection = sa_traffic['top_40_intersection_analysis']
                                print(f"   Top 40 Intersection: {top_40_intersection}")
                    
                    # Check Pedestrian Controls
                    if 'pedestrian_control_measures' in data:
                        ped_controls = data['pedestrian_control_measures']
                        print(f"\n🚶 Pedestrian Control Measures:")
                        print(f"   Type: {type(ped_controls)}")
                        if isinstance(ped_controls, dict):
                            print(f"   Keys: {list(ped_controls.keys())}")
                    
                    # Check Detour Routes
                    if 'detour_routes' in data:
                        detours = data['detour_routes']
                        print(f"\n🛣️ Detour Routes:")
                        print(f"   Type: {type(detours)}")
                        if isinstance(detours, dict):
                            print(f"   Keys: {list(detours.keys())}")
                    
                    print(f"\n✅ SUCCESS: Comprehensive endpoint working!")
                    print(f"   Response time: {response_time:.2f}s")
                    print(f"   Fields present: {len(present_fields)}/{len(key_fields)}")
                    
                    return True
                else:
                    print(f"❌ FAILED: Response is not a dictionary")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ FAILED: Invalid JSON response: {str(e)}")
                print(f"   Response text (first 500 chars): {response.text[:500]}")
                return False
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ FAILED: Request timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Quick Comprehensive Auto-Populate Test")
    print("=" * 60)
    
    success = test_comprehensive_endpoint()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
    else:
        print(f"\n💥 Test failed!")
    
    return success

if __name__ == "__main__":
    main()