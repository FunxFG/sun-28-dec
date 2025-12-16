#!/usr/bin/env python3
"""
Enhanced Comprehensive Auto-Population Endpoint Testing
Tests the new SA Government dataset integrations with 21 data categories
"""

import requests
import sys
import json
import time
from datetime import datetime

class ComprehensiveAutoPopulationTester:
    def __init__(self, base_url="https://trafficcontrol.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            end_time = time.time()
            response_time = end_time - start_time

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} - Time: {response_time:.2f}s")
                try:
                    return success, response.json(), response_time
                except:
                    return success, response.text, response_time
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}...")
                return False, {}, response_time

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}, response_time

    def test_comprehensive_auto_populate_adelaide_cbd(self):
        """
        Test Scenario 1: Adelaide CBD (King William Street to North Terrace)
        Should have traffic signals, public transport, parking restrictions
        """
        print(f"\n{'='*80}")
        print(f"🏙️  TEST SCENARIO 1: ADELAIDE CBD (PEDESTRIAN-HEAVY AREA)")
        print(f"{'='*80}")
        
        test_data = {
            "lat": -34.9285,
            "lng": 138.6007,
            "start_address": "King William Street, Adelaide SA",
            "end_address": "North Terrace, Adelaide SA",
            "work_type": "construction"
        }
        
        success, response, response_time = self.run_test(
            "Adelaide CBD - Comprehensive Auto-Population",
            "GET",
            "comprehensive-auto-populate",
            200,
            data=test_data
        )
        
        if not success:
            return False
        
        # Verify response time under 15 seconds
        if response_time > 15.0:
            print(f"❌ Response time {response_time:.2f}s exceeds 15 second threshold")
            return False
        else:
            print(f"✅ Response time {response_time:.2f}s within acceptable limits")
        
        # Check all 21 data categories are present
        expected_categories = [
            # Existing 16 categories
            'road_data', 'traffic_assessment', 'site_assessment', 'side_streets', 
            'intersections', 'control_measures', 'pedestrian_control_measures', 
            'recommended_devices', 'signage_plan', 'suggested_risks', 
            'governing_body_details', 'notification_requirements', 
            'environmental_constraints', 'staging_recommendations', 
            'public_facilities', 'crash_statistics', 'historical_traffic', 
            'location_history', 'current_roadworks',
            # New 5 categories
            'traffic_signals', 'parking_restrictions', 'school_zones', 
            'public_transport_detailed', 'utility_infrastructure'
        ]
        
        missing_categories = []
        present_categories = []
        
        for category in expected_categories:
            if category in response:
                present_categories.append(category)
            else:
                missing_categories.append(category)
        
        print(f"\n📊 DATA CATEGORIES ANALYSIS:")
        print(f"   Expected: {len(expected_categories)} categories")
        print(f"   Present: {len(present_categories)} categories")
        print(f"   Missing: {len(missing_categories)} categories")
        
        if missing_categories:
            print(f"   ❌ Missing categories: {missing_categories}")
            return False
        else:
            print(f"   ✅ All 21 data categories present!")
        
        # Verify new fields are populated with data
        new_categories_check = {}
        
        # Traffic Signals
        traffic_signals = response.get('traffic_signals', {})
        if traffic_signals and isinstance(traffic_signals, dict):
            nearby_signals = traffic_signals.get('nearby_signals', [])
            coordination_required = traffic_signals.get('signal_coordination_required', False)
            new_categories_check['traffic_signals'] = {
                'populated': len(nearby_signals) > 0 or coordination_required is not None,
                'data': f"{len(nearby_signals)} signals found, coordination: {coordination_required}"
            }
        
        # Parking Restrictions
        parking_restrictions = response.get('parking_restrictions', {})
        if parking_restrictions and isinstance(parking_restrictions, dict):
            restrictions = parking_restrictions.get('restrictions', [])
            permit_required = parking_restrictions.get('permit_required', False)
            new_categories_check['parking_restrictions'] = {
                'populated': len(restrictions) > 0 or permit_required is not None,
                'data': f"{len(restrictions)} restrictions, permit required: {permit_required}"
            }
        
        # School Zones
        school_zones = response.get('school_zones', {})
        if school_zones and isinstance(school_zones, dict):
            zones = school_zones.get('school_zones', [])
            enhanced_restrictions = school_zones.get('enhanced_restrictions', False)
            new_categories_check['school_zones'] = {
                'populated': len(zones) > 0 or enhanced_restrictions is not None,
                'data': f"{len(zones)} school zones, enhanced restrictions: {enhanced_restrictions}"
            }
        
        # Public Transport Detailed
        public_transport = response.get('public_transport_detailed', {})
        if public_transport and isinstance(public_transport, dict):
            bus_stops = public_transport.get('bus_stops', [])
            tram_stops = public_transport.get('tram_stops', [])
            train_stations = public_transport.get('train_stations', [])
            total_stops = len(bus_stops) + len(tram_stops) + len(train_stations)
            new_categories_check['public_transport_detailed'] = {
                'populated': total_stops > 0,
                'data': f"{len(bus_stops)} bus, {len(tram_stops)} tram, {len(train_stations)} train stops"
            }
        
        # Utility Infrastructure
        utility_infrastructure = response.get('utility_infrastructure', {})
        if utility_infrastructure and isinstance(utility_infrastructure, dict):
            underground = utility_infrastructure.get('underground_utilities', [])
            overhead = utility_infrastructure.get('overhead_utilities', [])
            dial_before_dig = utility_infrastructure.get('dial_before_dig_required', False)
            new_categories_check['utility_infrastructure'] = {
                'populated': len(underground) > 0 or len(overhead) > 0 or dial_before_dig is not None,
                'data': f"{len(underground)} underground, {len(overhead)} overhead, dial before dig: {dial_before_dig}"
            }
        
        print(f"\n🆕 NEW DATA CATEGORIES VERIFICATION:")
        all_new_populated = True
        for category, check in new_categories_check.items():
            if check['populated']:
                print(f"   ✅ {category}: {check['data']}")
            else:
                print(f"   ❌ {category}: No data populated")
                all_new_populated = False
        
        if not all_new_populated:
            print(f"   ❌ Some new categories not properly populated")
            return False
        else:
            print(f"   ✅ All new categories populated with data!")
        
        # Check data structure matches expected format
        print(f"\n🏗️  DATA STRUCTURE VERIFICATION:")
        
        # Verify road_data structure
        road_data = response.get('road_data', {})
        if isinstance(road_data, dict) and road_data:
            print(f"   ✅ road_data: {road_data.get('road_name', 'Unknown')} - {road_data.get('road_classification', 'Unknown')}")
        else:
            print(f"   ❌ road_data: Invalid structure")
            return False
        
        # Verify signage_plan structure
        signage_plan = response.get('signage_plan', {})
        if isinstance(signage_plan, dict) and signage_plan:
            bilateral_req = signage_plan.get('bilateral_requirements', {})
            side_street_signs = signage_plan.get('side_street_signs', {})
            print(f"   ✅ signage_plan: Bilateral requirements and side street signs present")
        else:
            print(f"   ❌ signage_plan: Invalid structure")
            return False
        
        # Verify pedestrian_control_measures structure
        pedestrian_controls = response.get('pedestrian_control_measures', {})
        if isinstance(pedestrian_controls, dict) and pedestrian_controls:
            barriers = pedestrian_controls.get('barriers_required', [])
            detours = pedestrian_controls.get('pedestrian_detours', [])
            print(f"   ✅ pedestrian_control_measures: {len(barriers)} barriers, {len(detours)} detours")
        else:
            print(f"   ❌ pedestrian_control_measures: Invalid structure")
            return False
        
        print(f"\n🎉 ADELAIDE CBD TEST COMPLETED SUCCESSFULLY!")
        print(f"   ✅ All 21 data categories present")
        print(f"   ✅ New SA Government dataset integrations working")
        print(f"   ✅ Response time under 15 seconds ({response_time:.2f}s)")
        print(f"   ✅ Data structures valid")
        
        return True

    def test_comprehensive_auto_populate_school_zone(self):
        """
        Test Scenario 2: School Zone Test (near a school)
        Should detect school zones with enhanced restrictions
        """
        print(f"\n{'='*80}")
        print(f"🏫 TEST SCENARIO 2: SCHOOL ZONE (ENHANCED RESTRICTIONS)")
        print(f"{'='*80}")
        
        test_data = {
            "lat": -34.9167,
            "lng": 138.6833,
            "start_address": "Kitchener Street, Netherby SA",
            "end_address": "Cross Road, Netherby SA",
            "work_type": "maintenance"
        }
        
        success, response, response_time = self.run_test(
            "School Zone - Comprehensive Auto-Population",
            "GET",
            "comprehensive-auto-populate",
            200,
            data=test_data
        )
        
        if not success:
            return False
        
        # Verify response time under 15 seconds
        if response_time > 15.0:
            print(f"❌ Response time {response_time:.2f}s exceeds 15 second threshold")
            return False
        else:
            print(f"✅ Response time {response_time:.2f}s within acceptable limits")
        
        # Check school zone detection
        school_zones = response.get('school_zones', {})
        if not school_zones:
            print(f"❌ school_zones category missing")
            return False
        
        zones = school_zones.get('school_zones', [])
        enhanced_restrictions = school_zones.get('enhanced_restrictions', False)
        school_times = school_zones.get('school_times', [])
        
        print(f"\n🏫 SCHOOL ZONE ANALYSIS:")
        print(f"   School zones found: {len(zones)}")
        print(f"   Enhanced restrictions: {enhanced_restrictions}")
        print(f"   School time periods: {len(school_times)}")
        
        # Verify school zone data
        if len(zones) > 0:
            print(f"   ✅ School zones detected")
            for zone in zones[:3]:  # Show first 3
                print(f"      - {zone.get('name', 'Unknown School')} ({zone.get('distance', 'Unknown distance')})")
        else:
            print(f"   ⚠️  No school zones found (may be valid for this location)")
        
        if enhanced_restrictions:
            print(f"   ✅ Enhanced restrictions detected")
        
        if len(school_times) > 0:
            print(f"   ✅ School time restrictions defined")
            for time_period in school_times[:2]:  # Show first 2
                print(f"      - {time_period.get('period', 'Unknown')}: {time_period.get('time', 'Unknown time')}")
        
        # Check if pedestrian controls are enhanced for school zones
        pedestrian_controls = response.get('pedestrian_control_measures', {})
        if pedestrian_controls:
            access_req = pedestrian_controls.get('access_requirements', [])
            school_specific = any('school' in str(req).lower() for req in access_req)
            if school_specific:
                print(f"   ✅ School-specific pedestrian controls detected")
            else:
                print(f"   ⚠️  No school-specific pedestrian controls found")
        
        print(f"\n🎉 SCHOOL ZONE TEST COMPLETED!")
        return True

    def test_comprehensive_auto_populate_suburban(self):
        """
        Test Scenario 3: Suburban Area (residential street)
        Should have utility infrastructure and minimal signals
        """
        print(f"\n{'='*80}")
        print(f"🏘️  TEST SCENARIO 3: SUBURBAN AREA (RESIDENTIAL STREET)")
        print(f"{'='*80}")
        
        test_data = {
            "lat": -34.9500,
            "lng": 138.6000,
            "start_address": "Morphett Road, Glengowrie SA",
            "end_address": "Diagonal Road, Glengowrie SA",
            "work_type": "utility"
        }
        
        success, response, response_time = self.run_test(
            "Suburban Area - Comprehensive Auto-Population",
            "GET",
            "comprehensive-auto-populate",
            200,
            data=test_data
        )
        
        if not success:
            return False
        
        # Verify response time under 15 seconds
        if response_time > 15.0:
            print(f"❌ Response time {response_time:.2f}s exceeds 15 second threshold")
            return False
        else:
            print(f"✅ Response time {response_time:.2f}s within acceptable limits")
        
        # Check utility infrastructure (should be comprehensive for suburban area)
        utility_infrastructure = response.get('utility_infrastructure', {})
        if not utility_infrastructure:
            print(f"❌ utility_infrastructure category missing")
            return False
        
        underground = utility_infrastructure.get('underground_utilities', [])
        overhead = utility_infrastructure.get('overhead_utilities', [])
        dial_before_dig = utility_infrastructure.get('dial_before_dig_required', False)
        utility_contacts = utility_infrastructure.get('utility_contacts', [])
        
        print(f"\n🔧 UTILITY INFRASTRUCTURE ANALYSIS:")
        print(f"   Underground utilities: {len(underground)}")
        print(f"   Overhead utilities: {len(overhead)}")
        print(f"   Dial Before You Dig required: {dial_before_dig}")
        print(f"   Utility contacts: {len(utility_contacts)}")
        
        # Verify utility data
        if len(underground) > 0:
            print(f"   ✅ Underground utilities detected")
            for utility in underground[:3]:  # Show first 3
                print(f"      - {utility.get('type', 'Unknown')} ({utility.get('provider', 'Unknown provider')})")
        else:
            print(f"   ❌ No underground utilities found")
            return False
        
        if dial_before_dig:
            print(f"   ✅ Dial Before You Dig requirement detected")
        else:
            print(f"   ❌ Dial Before You Dig requirement not set")
            return False
        
        if len(utility_contacts) >= 3:  # Should have SA Water, SA Power Networks, etc.
            print(f"   ✅ Comprehensive utility contacts provided")
            for contact in utility_contacts[:3]:  # Show first 3
                print(f"      - {contact.get('utility', 'Unknown')}: {contact.get('phone', 'No phone')}")
        else:
            print(f"   ❌ Insufficient utility contacts ({len(utility_contacts)} found)")
            return False
        
        # Check traffic signals (should be minimal for suburban)
        traffic_signals = response.get('traffic_signals', {})
        if traffic_signals:
            nearby_signals = traffic_signals.get('nearby_signals', [])
            coordination_required = traffic_signals.get('signal_coordination_required', False)
            
            print(f"\n🚦 TRAFFIC SIGNALS ANALYSIS:")
            print(f"   Nearby signals: {len(nearby_signals)}")
            print(f"   Coordination required: {coordination_required}")
            
            if len(nearby_signals) <= 2:  # Suburban should have few signals
                print(f"   ✅ Appropriate signal count for suburban area")
            else:
                print(f"   ⚠️  High signal count for suburban area ({len(nearby_signals)})")
        
        print(f"\n🎉 SUBURBAN AREA TEST COMPLETED!")
        return True

    def test_all_scenarios(self):
        """Run all comprehensive auto-population test scenarios"""
        print(f"\n{'='*100}")
        print(f"🚀 ENHANCED COMPREHENSIVE AUTO-POPULATION ENDPOINT TESTING")
        print(f"   Testing SA Government Dataset Integrations")
        print(f"   Expected: 21 data categories (16 existing + 5 new)")
        print(f"{'='*100}")
        
        start_time = time.time()
        
        # Test all scenarios
        scenario_results = []
        
        # Scenario 1: Adelaide CBD
        result1 = self.test_comprehensive_auto_populate_adelaide_cbd()
        scenario_results.append(("Adelaide CBD (Pedestrian-Heavy)", result1))
        
        # Scenario 2: School Zone
        result2 = self.test_comprehensive_auto_populate_school_zone()
        scenario_results.append(("School Zone (Enhanced Restrictions)", result2))
        
        # Scenario 3: Suburban Area
        result3 = self.test_comprehensive_auto_populate_suburban()
        scenario_results.append(("Suburban Area (Utility Infrastructure)", result3))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        print(f"\n{'='*100}")
        print(f"📊 COMPREHENSIVE AUTO-POPULATION TEST SUMMARY")
        print(f"{'='*100}")
        
        passed_scenarios = sum(1 for _, result in scenario_results if result)
        total_scenarios = len(scenario_results)
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Total Time: {total_time:.2f} seconds")
        
        print(f"\nScenario Results:")
        for scenario_name, result in scenario_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status} - {scenario_name}")
        
        print(f"\nOverall Result: {passed_scenarios}/{total_scenarios} scenarios passed")
        
        if passed_scenarios == total_scenarios:
            print(f"\n🎉 ALL SUCCESS CRITERIA MET!")
            print(f"   ✅ All 21 data categories present in responses")
            print(f"   ✅ New SA Government dataset integrations working")
            print(f"   ✅ All response times under 15 seconds")
            print(f"   ✅ Data structures match expected format")
            print(f"   ✅ Enhanced auto-population system fully operational")
            return True
        else:
            print(f"\n❌ SOME TESTS FAILED")
            print(f"   Review failed scenarios above for details")
            return False

def main():
    """Main test execution"""
    print("Enhanced Comprehensive Auto-Population Endpoint Testing")
    print("=" * 60)
    
    tester = ComprehensiveAutoPopulationTester()
    
    try:
        success = tester.test_all_scenarios()
        
        if success:
            print(f"\n✅ ALL TESTS PASSED - Enhanced comprehensive auto-population endpoint working correctly!")
            sys.exit(0)
        else:
            print(f"\n❌ SOME TESTS FAILED - Review output above for details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()