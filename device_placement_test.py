#!/usr/bin/env python3
"""
Device Placement Backend API Flow Testing
Tests the complete device placement backend API chain for SafeRoadWorks
"""

import requests
import sys
import json
from datetime import datetime

class DevicePlacementAPITester:
    def __init__(self, base_url="https://tmp-generator-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            else:
                response = requests.request(method, url, params=params, timeout=30)

            success = response.status_code == expected_status
            
            print(f"   Status: {response.status_code}")
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_geocode_torrens_road(self):
        """Test 1: Geocode Test - Verify address geocoding for 185 Torrens Road, Ridleyton SA"""
        success, response = self.run_test(
            "Geocode Test - 185 Torrens Road, Ridleyton SA",
            "GET",
            "geocode",
            200,
            params={"address": "185 Torrens Road, Ridleyton SA"}
        )
        
        if success:
            # Verify expected response structure
            if 'lat' in response and 'lng' in response:
                lat = response['lat']
                lng = response['lng']
                print(f"   ✅ Coordinates: lat={lat}, lng={lng}")
                
                # Verify coordinates are in Adelaide area (rough bounds)
                if -35.2 <= lat <= -34.7 and 138.4 <= lng <= 138.8:
                    print(f"   ✅ Coordinates are in Adelaide area")
                    self.test_results.append({
                        'test': 'Geocode Test',
                        'status': 'PASS',
                        'coordinates': {'lat': lat, 'lng': lng},
                        'details': f"Successfully geocoded to {lat}, {lng}"
                    })
                    return True, {'lat': lat, 'lng': lng}
                else:
                    print(f"   ❌ Coordinates outside Adelaide area")
                    self.test_results.append({
                        'test': 'Geocode Test',
                        'status': 'FAIL',
                        'details': f"Coordinates {lat}, {lng} outside Adelaide area"
                    })
            else:
                print(f"   ❌ Missing lat/lng in response")
                self.test_results.append({
                    'test': 'Geocode Test',
                    'status': 'FAIL',
                    'details': "Missing lat/lng fields in response"
                })
        else:
            self.test_results.append({
                'test': 'Geocode Test',
                'status': 'FAIL',
                'details': "API request failed"
            })
        
        return False, {}

    def test_road_data_torrens_road(self):
        """Test 2: Road Data Test - Verify road information for Torrens Road segment"""
        success, response = self.run_test(
            "Road Data Test - Torrens Road Segment",
            "GET",
            "road-data",
            200,
            params={
                "start_address": "185 Torrens Road, Ridleyton SA",
                "end_address": "200 Torrens Road, Ridleyton SA"
            }
        )
        
        if success:
            # Verify expected response structure
            required_fields = ['road_name', 'speed_limit', 'start_coords']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                road_name = response.get('road_name', 'Unknown')
                speed_limit = response.get('speed_limit', 0)
                start_coords = response.get('start_coords', {})
                
                print(f"   ✅ Road name: {road_name}")
                print(f"   ✅ Speed limit: {speed_limit} km/h")
                print(f"   ✅ Start coordinates: {start_coords}")
                
                # Additional fields to check
                additional_info = []
                if 'workzone_size' in response:
                    additional_info.append(f"Workzone size: {response['workzone_size']}m")
                if 'road_classification' in response:
                    additional_info.append(f"Classification: {response['road_classification']}")
                if 'data_source' in response:
                    additional_info.append(f"Data source: {response['data_source']}")
                
                if additional_info:
                    print(f"   ℹ️  Additional info: {'; '.join(additional_info)}")
                
                self.test_results.append({
                    'test': 'Road Data Test',
                    'status': 'PASS',
                    'road_name': road_name,
                    'speed_limit': speed_limit,
                    'start_coords': start_coords,
                    'details': f"Successfully retrieved road data for {road_name}"
                })
                return True, response
            else:
                print(f"   ❌ Missing required fields: {missing_fields}")
                self.test_results.append({
                    'test': 'Road Data Test',
                    'status': 'FAIL',
                    'details': f"Missing required fields: {missing_fields}"
                })
        else:
            self.test_results.append({
                'test': 'Road Data Test',
                'status': 'FAIL',
                'details': "API request failed"
            })
        
        return False, {}

    def test_comprehensive_auto_populate_torrens_road(self):
        """Test 3: Comprehensive Auto-populate Test - CRITICAL - Verify road edge geometry"""
        success, response = self.run_test(
            "Comprehensive Auto-populate Test - Road Edge Geometry",
            "GET",
            "comprehensive-auto-populate",
            200,
            params={
                "start_address": "185 Torrens Road, Ridleyton SA",
                "end_address": "200 Torrens Road, Ridleyton SA",
                "lat": -34.8899492,
                "lng": 138.5719451,
                "work_type": "construction"
            }
        )
        
        if success:
            print(f"   ✅ Comprehensive auto-populate endpoint responded successfully")
            
            # Check for road_edge_geometry field
            road_edge_geometry = response.get('road_edge_geometry')
            
            if road_edge_geometry:
                print(f"   ✅ road_edge_geometry field present")
                
                # Check for start geometry
                start_geometry = road_edge_geometry.get('start', {})
                
                if start_geometry:
                    print(f"   ✅ road_edge_geometry.start field present")
                    
                    # Check for left_edge with 2+ points
                    left_edge = start_geometry.get('left_edge', [])
                    right_edge = start_geometry.get('right_edge', [])
                    width = start_geometry.get('width')
                    bearing = start_geometry.get('bearing')
                    
                    success_criteria = []
                    
                    # Verify left_edge has 2+ points
                    if isinstance(left_edge, list) and len(left_edge) >= 2:
                        success_criteria.append(f"✅ left_edge has {len(left_edge)} points (≥2 required)")
                    else:
                        success_criteria.append(f"❌ left_edge has {len(left_edge) if isinstance(left_edge, list) else 0} points (<2)")
                    
                    # Verify right_edge has 2+ points
                    if isinstance(right_edge, list) and len(right_edge) >= 2:
                        success_criteria.append(f"✅ right_edge has {len(right_edge)} points (≥2 required)")
                    else:
                        success_criteria.append(f"❌ right_edge has {len(right_edge) if isinstance(right_edge, list) else 0} points (<2)")
                    
                    # Verify width is present
                    if width is not None:
                        success_criteria.append(f"✅ road width: {width} meters")
                    else:
                        success_criteria.append(f"❌ road width missing")
                    
                    # Verify bearing is present
                    if bearing is not None:
                        success_criteria.append(f"✅ road bearing: {bearing}°")
                    else:
                        success_criteria.append(f"❌ road bearing missing")
                    
                    # Print all criteria
                    for criterion in success_criteria:
                        print(f"   {criterion}")
                    
                    # Check if all critical criteria are met
                    critical_pass = (
                        isinstance(left_edge, list) and len(left_edge) >= 2 and
                        isinstance(right_edge, list) and len(right_edge) >= 2 and
                        width is not None and
                        bearing is not None
                    )
                    
                    if critical_pass:
                        self.test_results.append({
                            'test': 'Comprehensive Auto-populate Test',
                            'status': 'PASS',
                            'road_edge_geometry': {
                                'left_edge_points': len(left_edge),
                                'right_edge_points': len(right_edge),
                                'width': width,
                                'bearing': bearing
                            },
                            'details': "All road edge geometry requirements met"
                        })
                        return True, response
                    else:
                        self.test_results.append({
                            'test': 'Comprehensive Auto-populate Test',
                            'status': 'FAIL',
                            'details': "Road edge geometry requirements not fully met"
                        })
                else:
                    print(f"   ❌ road_edge_geometry.start field missing")
                    self.test_results.append({
                        'test': 'Comprehensive Auto-populate Test',
                        'status': 'FAIL',
                        'details': "road_edge_geometry.start field missing"
                    })
            else:
                print(f"   ❌ road_edge_geometry field missing from response")
                
                # Check what fields are actually present
                available_fields = list(response.keys()) if isinstance(response, dict) else []
                print(f"   ℹ️  Available fields: {available_fields[:10]}...")  # Show first 10 fields
                
                self.test_results.append({
                    'test': 'Comprehensive Auto-populate Test',
                    'status': 'FAIL',
                    'details': f"road_edge_geometry field missing. Available fields: {len(available_fields)} total"
                })
        else:
            self.test_results.append({
                'test': 'Comprehensive Auto-populate Test',
                'status': 'FAIL',
                'details': "API request failed"
            })
        
        return False, {}

    def run_all_tests(self):
        """Run all device placement API tests"""
        print("=" * 80)
        print("DEVICE PLACEMENT BACKEND API FLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Location: 185 Torrens Road, Ridleyton SA")
        print()
        
        # Test 1: Geocoding
        geocode_success, geocode_data = self.test_geocode_torrens_road()
        
        # Test 2: Road Data
        road_data_success, road_data = self.test_road_data_torrens_road()
        
        # Test 3: Comprehensive Auto-populate (CRITICAL)
        auto_populate_success, auto_populate_data = self.test_comprehensive_auto_populate_torrens_road()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            print(f"   {result['details']}")
            print()
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Critical assessment
        critical_tests = ['Geocode Test', 'Road Data Test', 'Comprehensive Auto-populate Test']
        critical_passed = sum(1 for result in self.test_results if result['test'] in critical_tests and result['status'] == 'PASS')
        
        print(f"\nCRITICAL TESTS: {critical_passed}/{len(critical_tests)} passed")
        
        if critical_passed == len(critical_tests):
            print("🎉 ALL CRITICAL TESTS PASSED - Device placement API flow is operational!")
            return True
        else:
            print("⚠️  CRITICAL TESTS FAILED - Device placement API flow has issues")
            return False

def main():
    """Main test execution"""
    tester = DevicePlacementAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()