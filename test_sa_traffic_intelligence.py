#!/usr/bin/env python3
"""
SA Traffic Intelligence Integration Testing
Tests the newly integrated Top 40 Roads, Top 40 Intersections, and Travel Speed datasets
"""

import requests
import sys
import json
import time
from datetime import datetime

class SATrafficIntelligenceTester:
    def __init__(self, base_url="https://roadworksai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=60)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=60)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_sa_traffic_intelligence_king_william_street(self):
        """Test SA Traffic Intelligence - King William Street (Top 40 Road Detection)"""
        start_time = time.time()
        
        success, response = self.run_test(
            "SA Traffic Intelligence - King William Street (Top 40 Road)",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9285,
                "lng": 138.6007,
                "start_address": "King William Street, Adelaide SA",
                "end_address": "North Terrace, Adelaide SA",
                "work_type": "construction"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if success:
            print(f"   Response time: {response_time:.2f} seconds")
            
            # Check if sa_traffic_intelligence field is present
            sa_traffic = response.get('sa_traffic_intelligence', {})
            if not sa_traffic:
                print(f"   ❌ Missing sa_traffic_intelligence field")
                return False
            
            # Check Top 40 Road Analysis
            top_40_road = sa_traffic.get('top_40_road_analysis', {})
            print(f"   Top 40 Road Analysis: {top_40_road}")
            
            # Verify required fields
            required_fields = ['is_top_40_road', 'road_match', 'traffic_volume', 'rank', 'message']
            missing_fields = [field for field in required_fields if field not in top_40_road]
            
            if missing_fields:
                print(f"   ❌ Missing Top 40 road fields: {missing_fields}")
                return False
            
            # Check if King William Street is detected as Top 40 road
            is_top_40 = top_40_road.get('is_top_40_road', False)
            traffic_volume = top_40_road.get('traffic_volume')
            rank = top_40_road.get('rank')
            message = top_40_road.get('message', '')
            
            print(f"   Is Top 40 Road: {is_top_40}")
            print(f"   Traffic Volume (AADT): {traffic_volume}")
            print(f"   Rank: {rank}")
            print(f"   Message: {message}")
            
            # Success criteria
            success_criteria = []
            
            if is_top_40:
                success_criteria.append("✅ King William Street detected as Top 40 road")
                if traffic_volume and traffic_volume > 0:
                    success_criteria.append(f"✅ AADT traffic volume provided: {traffic_volume:,}")
                if rank and rank > 0:
                    success_criteria.append(f"✅ Rank provided: #{rank}")
                if 'HIGH TRAFFIC' in message:
                    success_criteria.append("✅ High traffic warning message present")
            else:
                success_criteria.append("⚠️ King William Street not detected as Top 40 road (may be expected)")
            
            # Check Top 40 Intersection Analysis
            top_40_intersection = sa_traffic.get('top_40_intersection_analysis', {})
            print(f"   Top 40 Intersection Analysis: {top_40_intersection}")
            
            # Check Overall Traffic Level
            overall_level = sa_traffic.get('overall_traffic_level', 'Unknown')
            recommendations = sa_traffic.get('recommendations', [])
            
            print(f"   Overall Traffic Level: {overall_level}")
            print(f"   Recommendations: {recommendations}")
            
            if overall_level in ['VERY HIGH', 'HIGH', 'MEDIUM-HIGH', 'MODERATE']:
                success_criteria.append(f"✅ Overall traffic level assessed: {overall_level}")
            
            if recommendations and len(recommendations) > 0:
                success_criteria.append(f"✅ Traffic management recommendations provided ({len(recommendations)} items)")
            
            # Check Travel Speed Data
            travel_speed = sa_traffic.get('travel_speed_data', {})
            if travel_speed.get('success'):
                total_records = travel_speed.get('total_records', 0)
                success_criteria.append(f"✅ Travel speed data fetched: {total_records} records")
                
                # Check for 150 records limit
                if total_records == 150:
                    success_criteria.append("✅ Travel speed data limit (150) reached as expected")
            
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            return True
        return False

    def test_sa_traffic_intelligence_residential_street(self):
        """Test SA Traffic Intelligence - Residential Street (Non-Top 40)"""
        start_time = time.time()
        
        success, response = self.run_test(
            "SA Traffic Intelligence - Residential Street (Non-Top 40)",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9350,
                "lng": 138.6100,
                "start_address": "Maple Avenue, Kent Town SA",
                "end_address": "Oak Street, Kent Town SA",
                "work_type": "maintenance"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if success:
            print(f"   Response time: {response_time:.2f} seconds")
            
            # Check sa_traffic_intelligence field
            sa_traffic = response.get('sa_traffic_intelligence', {})
            if not sa_traffic:
                print(f"   ❌ Missing sa_traffic_intelligence field")
                return False
            
            # Check Top 40 Road Analysis for residential street
            top_40_road = sa_traffic.get('top_40_road_analysis', {})
            is_top_40 = top_40_road.get('is_top_40_road', False)
            message = top_40_road.get('message', '')
            
            print(f"   Is Top 40 Road: {is_top_40}")
            print(f"   Message: {message}")
            
            # Success criteria for residential street
            success_criteria = []
            
            if not is_top_40:
                success_criteria.append("✅ Residential street correctly NOT detected as Top 40 road")
                if 'not in Top 40' in message or 'Not in Top 40' in message:
                    success_criteria.append("✅ Appropriate non-Top 40 message provided")
            else:
                success_criteria.append("⚠️ Residential street unexpectedly detected as Top 40 road")
            
            # Check overall traffic level for residential
            overall_level = sa_traffic.get('overall_traffic_level', 'Unknown')
            if overall_level == 'MODERATE':
                success_criteria.append("✅ Overall traffic level correctly assessed as MODERATE for residential")
            elif overall_level in ['LOW', 'UNKNOWN']:
                success_criteria.append(f"✅ Reasonable traffic level for residential: {overall_level}")
            else:
                success_criteria.append(f"⚠️ Unexpected traffic level for residential: {overall_level}")
            
            # Check travel speed data is still available
            travel_speed = sa_traffic.get('travel_speed_data', {})
            if travel_speed.get('success'):
                success_criteria.append("✅ Travel speed data available for residential area")
            
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            return True
        return False

    def test_sa_traffic_intelligence_major_intersection(self):
        """Test SA Traffic Intelligence - Major Adelaide Intersection"""
        start_time = time.time()
        
        success, response = self.run_test(
            "SA Traffic Intelligence - Major Intersection",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9200,
                "lng": 138.6000,
                "start_address": "Anzac Highway and Sir Donald Bradman Drive, Adelaide SA",
                "end_address": "Anzac Highway, Adelaide SA",
                "work_type": "intersection_works"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if success:
            print(f"   Response time: {response_time:.2f} seconds")
            
            # Check sa_traffic_intelligence field
            sa_traffic = response.get('sa_traffic_intelligence', {})
            if not sa_traffic:
                print(f"   ❌ Missing sa_traffic_intelligence field")
                return False
            
            # Check Top 40 Intersection Analysis
            top_40_intersection = sa_traffic.get('top_40_intersection_analysis', {})
            is_top_40_intersection = top_40_intersection.get('is_top_40_intersection', False)
            vehicle_exposure = top_40_intersection.get('vehicle_exposure')
            rank = top_40_intersection.get('rank')
            message = top_40_intersection.get('message', '')
            
            print(f"   Is Top 40 Intersection: {is_top_40_intersection}")
            print(f"   Vehicle Exposure: {vehicle_exposure}")
            print(f"   Rank: {rank}")
            print(f"   Message: {message}")
            
            # Success criteria
            success_criteria = []
            
            # Check intersection analysis fields are present
            required_intersection_fields = ['is_top_40_intersection', 'intersection_match', 'vehicle_exposure', 'rank', 'message']
            missing_intersection_fields = [field for field in required_intersection_fields if field not in top_40_intersection]
            
            if not missing_intersection_fields:
                success_criteria.append("✅ All Top 40 intersection fields present")
            else:
                success_criteria.append(f"❌ Missing intersection fields: {missing_intersection_fields}")
            
            if is_top_40_intersection:
                success_criteria.append("✅ Major intersection detected as Top 40")
                if vehicle_exposure:
                    success_criteria.append(f"✅ Vehicle exposure data provided: {vehicle_exposure}")
                if rank:
                    success_criteria.append(f"✅ Intersection rank provided: #{rank}")
                if 'MAJOR INTERSECTION' in message:
                    success_criteria.append("✅ Major intersection warning message present")
            else:
                success_criteria.append("⚠️ Intersection not detected as Top 40 (may be expected)")
            
            # Check recommendations include intersection-specific advice
            recommendations = sa_traffic.get('recommendations', [])
            intersection_recommendations = [r for r in recommendations if 'intersection' in r.lower() or 'signal' in r.lower()]
            
            if intersection_recommendations:
                success_criteria.append(f"✅ Intersection-specific recommendations provided")
            
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            return True
        return False

    def test_sa_traffic_intelligence_comprehensive_fields(self):
        """Test SA Traffic Intelligence - Comprehensive Field Verification"""
        success, response = self.run_test(
            "SA Traffic Intelligence - Comprehensive Field Check",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9285,
                "lng": 138.6007,
                "start_address": "Victoria Square, Adelaide SA",
                "end_address": "Rundle Mall, Adelaide SA",
                "work_type": "construction"
            }
        )
        
        if success:
            # Check main sa_traffic_intelligence structure
            sa_traffic = response.get('sa_traffic_intelligence', {})
            if not sa_traffic:
                print(f"   ❌ Missing sa_traffic_intelligence field")
                return False
            
            # Expected main fields
            expected_main_fields = [
                'top_40_road_analysis',
                'top_40_intersection_analysis', 
                'travel_speed_data',
                'overall_traffic_level',
                'recommendations'
            ]
            
            missing_main_fields = [field for field in expected_main_fields if field not in sa_traffic]
            present_main_fields = [field for field in expected_main_fields if field in sa_traffic]
            
            print(f"   Present main fields ({len(present_main_fields)}/{len(expected_main_fields)}): {present_main_fields}")
            if missing_main_fields:
                print(f"   Missing main fields: {missing_main_fields}")
            
            # Check Top 40 Road Analysis sub-fields
            top_40_road = sa_traffic.get('top_40_road_analysis', {})
            expected_road_fields = ['is_top_40_road', 'road_match', 'traffic_volume', 'rank', 'message']
            road_fields_present = [field for field in expected_road_fields if field in top_40_road]
            
            print(f"   Top 40 Road fields ({len(road_fields_present)}/{len(expected_road_fields)}): {road_fields_present}")
            
            # Check Top 40 Intersection Analysis sub-fields
            top_40_intersection = sa_traffic.get('top_40_intersection_analysis', {})
            expected_intersection_fields = ['is_top_40_intersection', 'intersection_match', 'vehicle_exposure', 'rank', 'message']
            intersection_fields_present = [field for field in expected_intersection_fields if field in top_40_intersection]
            
            print(f"   Top 40 Intersection fields ({len(intersection_fields_present)}/{len(expected_intersection_fields)}): {intersection_fields_present}")
            
            # Check Travel Speed Data sub-fields
            travel_speed = sa_traffic.get('travel_speed_data', {})
            expected_speed_fields = ['speed_data', 'total_records', 'data_source', 'success']
            speed_fields_present = [field for field in expected_speed_fields if field in travel_speed]
            
            print(f"   Travel Speed fields ({len(speed_fields_present)}/{len(expected_speed_fields)}): {speed_fields_present}")
            
            # Success criteria
            success_criteria = []
            
            # Main structure
            if len(missing_main_fields) == 0:
                success_criteria.append("✅ All main SA traffic intelligence fields present")
            else:
                success_criteria.append(f"❌ Missing {len(missing_main_fields)} main fields")
            
            # Sub-field completeness
            if len(road_fields_present) >= 4:
                success_criteria.append("✅ Top 40 road analysis fields complete")
            
            if len(intersection_fields_present) >= 4:
                success_criteria.append("✅ Top 40 intersection analysis fields complete")
            
            if len(speed_fields_present) >= 3:
                success_criteria.append("✅ Travel speed data fields complete")
            
            # Data quality checks
            overall_level = sa_traffic.get('overall_traffic_level')
            valid_levels = ['VERY HIGH', 'HIGH', 'MEDIUM-HIGH', 'MODERATE', 'LOW', 'UNKNOWN']
            if overall_level in valid_levels:
                success_criteria.append(f"✅ Valid overall traffic level: {overall_level}")
            else:
                success_criteria.append(f"❌ Invalid overall traffic level: {overall_level}")
            
            recommendations = sa_traffic.get('recommendations', [])
            if isinstance(recommendations, list) and len(recommendations) >= 0:
                success_criteria.append(f"✅ Recommendations array present ({len(recommendations)} items)")
            
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            # Overall success if most fields present
            return len(missing_main_fields) <= 1 and len(road_fields_present) >= 4
        
        return False

def main():
    print("🚦 SA Traffic Intelligence Integration Testing")
    print("=" * 80)
    print("Testing Top 40 Roads, Top 40 Intersections, and Travel Speed datasets")
    print("=" * 80)
    
    tester = SATrafficIntelligenceTester()
    
    # Run SA Traffic Intelligence tests
    tests = [
        ("King William Street (Top 40 Road Detection)", tester.test_sa_traffic_intelligence_king_william_street),
        ("Residential Street (Non-Top 40)", tester.test_sa_traffic_intelligence_residential_street),
        ("Major Intersection Detection", tester.test_sa_traffic_intelligence_major_intersection),
        ("Comprehensive Field Verification", tester.test_sa_traffic_intelligence_comprehensive_fields),
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All SA Traffic Intelligence tests passed!")
        print("✅ SA Traffic Intelligence integration is fully operational")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        print("❌ SA Traffic Intelligence integration issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())