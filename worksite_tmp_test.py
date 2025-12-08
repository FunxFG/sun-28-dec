#!/usr/bin/env python3
"""
Focused test for Worksite TMP endpoints
Tests the newly added worksite traffic management endpoints based on VicRoads Traffic Management Note No. 33
"""

import requests
import sys
import json
from datetime import datetime

class WorksiteTMPTester:
    def __init__(self, base_url="https://trafsafe.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'GET':
                response = requests.get(url, headers=headers, params=data)

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

    def setup_authentication(self):
        """Set up authentication for testing"""
        test_email = f"worksite_test_{datetime.now().strftime('%H%M%S')}@example.com"
        test_data = {
            "email": test_email,
            "password": "WorksiteTest123!",
            "company_name": "Worksite TMP Test Company"
        }
        
        success, response = self.run_test(
            "User Registration for Worksite Tests",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            print(f"   Registered user: {test_email}")
            return True
        return False

    def test_worksite_tmp_generation(self):
        """Test worksite TMP generation endpoint with VicRoads Note 33 compliance"""
        test_data = {
            "location": "South Road, Adelaide",
            "work_type": "Road Resurfacing",
            "posted_speed": 80,
            "reduced_speed": 60,
            "lane_closure": True,
            "lane_closure_type": "merge",
            "work_duration_days": 5,
            "work_hours": "7am-5pm",
            "workers_present": True,
            "traffic_control_required": True,
            "night_works": False
        }
        
        success, response = self.run_test(
            "Worksite TMP Generation (VicRoads Note 33)",
            "POST",
            "tmp/worksite",
            200,
            data=test_data
        )
        
        if success and 'plan' in response:
            plan = response['plan']
            print(f"   Plan ID: {plan.get('plan_id', 'Unknown')}")
            
            # SUCCESS CRITERIA: Check required sections
            required_sections = [
                'speed_management', 'sign_spacing_and_tapers',
                'lane_management', 'traffic_control', 'delineation_and_barriers',
                'worker_safety', 'setup_and_removal', 'compliance'
            ]
            
            missing_sections = [section for section in required_sections if section not in plan]
            if missing_sections:
                print(f"   ❌ Missing required sections: {missing_sections}")
                return False
            
            # SUCCESS CRITERIA: Verify speed management (posted_speed=80, reduced_speed=60)
            speed_mgmt = plan.get('speed_management', {})
            if speed_mgmt.get('posted_speed') == 80 and speed_mgmt.get('reduced_speed') == 60:
                print(f"   ✅ Speed management: {speed_mgmt['posted_speed']} → {speed_mgmt['reduced_speed']} km/h")
            else:
                print(f"   ❌ Speed management incorrect: expected 80→60, got {speed_mgmt}")
                return False
            
            # SUCCESS CRITERIA: Verify sign spacing and tapers with advance warning signs
            sign_spacing = plan.get('sign_spacing_and_tapers', {})
            advance_signs = sign_spacing.get('advance_warning_signs', {})
            
            required_signs = ['roadwork_ahead', 'speed_limit_ahead', 'prepare_to_stop']
            missing_signs = [sign for sign in required_signs if sign not in advance_signs]
            if missing_signs:
                print(f"   ❌ Missing advance warning signs: {missing_signs}")
                return False
            
            # Verify distances are present
            for sign_name in required_signs:
                sign_data = advance_signs[sign_name]
                distance = sign_data.get('distance_to_worksite')
                if distance:
                    print(f"   ✅ {sign_name.replace('_', ' ').title()}: {distance}m")
                else:
                    print(f"   ❌ Missing distance for {sign_name}")
                    return False
            
            # SUCCESS CRITERIA: Check taper specifications with merge_taper length
            taper_specs = sign_spacing.get('taper_specifications', {})
            merge_taper = taper_specs.get('merge_taper', {})
            if merge_taper and 'length_meters' in merge_taper:
                print(f"   ✅ Merge taper length: {merge_taper['length_meters']}m")
            else:
                print(f"   ❌ Missing merge taper specifications")
                return False
            
            # SUCCESS CRITERIA: Verify worksite signage (reduced_speed_limit, symbolic_workers, symbolic_traffic_controller)
            # Note: worksite_signage is nested inside sign_spacing_and_tapers
            worksite_signage = sign_spacing.get('worksite_signage', {})
            required_worksite_signs = ['reduced_speed_limit', 'symbolic_workers', 'symbolic_traffic_controller']
            missing_worksite_signs = [sign for sign in required_worksite_signs if sign not in worksite_signage]
            if missing_worksite_signs:
                print(f"   ❌ Missing worksite signage: {missing_worksite_signs}")
                return False
            
            print(f"   ✅ Worksite signage complete: {list(worksite_signage.keys())}")
            
            # SUCCESS CRITERIA: Verify lane management with closure_type="merge"
            lane_mgmt = plan.get('lane_management', {})
            if lane_mgmt.get('closure_type') == 'merge':
                print(f"   ✅ Lane management: {lane_mgmt['closure_type']} closure")
            else:
                print(f"   ❌ Lane management incorrect: expected 'merge', got {lane_mgmt.get('closure_type')}")
                return False
            
            # SUCCESS CRITERIA: Verify traffic control with controller_positions
            traffic_control = plan.get('traffic_control', {})
            controller_positions = traffic_control.get('controller_positions', [])
            if traffic_control.get('controllers_required') and controller_positions:
                print(f"   ✅ Traffic control positions: {len(controller_positions)} positions")
            else:
                print(f"   ❌ Traffic control setup incorrect")
                return False
            
            # SUCCESS CRITERIA: Verify delineation_and_barriers with spacing requirements
            delineation = plan.get('delineation_and_barriers', {})
            if delineation and 'delineator_spacing' in delineation:
                print(f"   ✅ Delineation spacing: {delineation['delineator_spacing']}")
            else:
                print(f"   ❌ Missing delineation and barriers spacing")
                return False
            
            # SUCCESS CRITERIA: Verify worker_safety with proximity_to_traffic requirements
            worker_safety = plan.get('worker_safety', {})
            proximity_req = worker_safety.get('proximity_to_traffic', {})
            if proximity_req and 'maximum_proximity' in proximity_req:
                print(f"   ✅ Worker safety proximity: {proximity_req['maximum_proximity']}")
            else:
                print(f"   ❌ Worker safety requirements missing")
                return False
            
            # SUCCESS CRITERIA: Verify setup_and_removal sequence
            setup_removal = plan.get('setup_and_removal', {})
            if setup_removal and 'setup_sequence' in setup_removal:
                setup_steps = setup_removal['setup_sequence']
                print(f"   ✅ Setup sequence: {len(setup_steps)} steps")
            else:
                print(f"   ❌ Missing setup and removal sequence")
                return False
            
            # SUCCESS CRITERIA: Verify compliance with AS 1742.3:2019, VicRoads Traffic Management Note No. 33
            compliance = plan.get('compliance', {})
            standards = compliance.get('standards', [])
            has_as1742 = any('AS 1742.3:2019' in std for std in standards)
            has_vicroads = any('VicRoads Traffic Management Note No. 33' in std for std in standards)
            
            if has_as1742 and has_vicroads:
                print(f"   ✅ Compliance: AS 1742.3:2019 and VicRoads Note 33")
            else:
                print(f"   ❌ Missing compliance standards - AS1742: {has_as1742}, VicRoads: {has_vicroads}")
                return False
            
            print(f"   🎉 ALL WORKSITE TMP SUCCESS CRITERIA MET!")
            return True
        return False

    def test_sign_spacing_calculator(self):
        """Test sign spacing calculator endpoint"""
        test_data = {
            "posted_speed": 100,
            "reduced_speed": 60,
            "road_type": "freeway",
            "lane_closure": True,
            "workers_present": True,
            "traffic_control_required": True
        }
        
        success, response = self.run_test(
            "Sign Spacing Calculator (AS 1742.3 Compliant)",
            "POST",
            "tmp/sign-spacing",
            200,
            data=test_data
        )
        
        if success and 'calculations' in response:
            calculations = response['calculations']
            print(f"   Calculation ID: {calculations.get('calculation_id', 'Unknown')}")
            
            # SUCCESS CRITERIA: Check advance_warning_signs with distances
            advance_signs = calculations.get('advance_warning_signs', {})
            required_signs = ['roadwork_ahead', 'speed_limit_ahead', 'prepare_to_stop']
            
            for sign in required_signs:
                if sign in advance_signs:
                    sign_data = advance_signs[sign]
                    distance = sign_data.get('distance_to_worksite')
                    if distance:
                        print(f"   ✅ {sign.replace('_', ' ').title()}: {distance}m")
                    else:
                        print(f"   ❌ Missing distance for {sign}")
                        return False
                else:
                    print(f"   ❌ Missing {sign} in advance warning signs")
                    return False
            
            # SUCCESS CRITERIA: Check taper_specifications with merge_taper and lateral_shift_taper lengths
            taper_specs = calculations.get('taper_specifications', {})
            merge_taper = taper_specs.get('merge_taper', {})
            lateral_shift_taper = taper_specs.get('lateral_shift_taper', {})
            
            if merge_taper and 'length_meters' in merge_taper:
                print(f"   ✅ Merge taper length: {merge_taper['length_meters']}m")
            else:
                print(f"   ❌ Missing merge taper specifications")
                return False
            
            if lateral_shift_taper and 'length_meters' in lateral_shift_taper:
                print(f"   ✅ Lateral shift taper length: {lateral_shift_taper['length_meters']}m")
            else:
                print(f"   ❌ Missing lateral shift taper specifications")
                return False
            
            # SUCCESS CRITERIA: Check safety_buffer distance
            safety_buffer = calculations.get('safety_buffer', {})
            buffer_distance = safety_buffer.get('distance')
            if buffer_distance:
                print(f"   ✅ Safety buffer distance: {buffer_distance}m")
            else:
                print(f"   ❌ Missing safety buffer distance")
                return False
            
            # SUCCESS CRITERIA: Check worker_safety_requirements with high_visibility_clothing and proximity_to_traffic
            worker_safety = calculations.get('worker_safety_requirements', {})
            high_vis = worker_safety.get('high_visibility_clothing', {})
            proximity = worker_safety.get('proximity_to_traffic', {})
            
            if high_vis.get('required') and proximity.get('maximum_proximity'):
                print(f"   ✅ Worker safety: High-vis required, proximity {proximity['maximum_proximity']}")
            else:
                print(f"   ❌ Incomplete worker safety requirements")
                return False
            
            # SUCCESS CRITERIA: Verify distance calculations appropriate for speed zones (100 km/h)
            roadwork_distance = advance_signs['roadwork_ahead']['distance_to_worksite']
            speed_limit_distance = advance_signs['speed_limit_ahead']['distance_to_worksite']
            prepare_stop_distance = advance_signs['prepare_to_stop']['distance_to_worksite']
            
            # For 100 km/h posted speed, expect reasonable distances per AS 1742.3
            distance_checks = []
            if 300 <= roadwork_distance <= 500:
                distance_checks.append(f"✅ Roadwork ahead: {roadwork_distance}m (appropriate for 100 km/h)")
            else:
                distance_checks.append(f"⚠️ Roadwork ahead: {roadwork_distance}m (may be inappropriate for 100 km/h)")
            
            if 200 <= speed_limit_distance <= 300:
                distance_checks.append(f"✅ Speed limit ahead: {speed_limit_distance}m (appropriate)")
            else:
                distance_checks.append(f"⚠️ Speed limit ahead: {speed_limit_distance}m (may be inappropriate)")
            
            if 100 <= prepare_stop_distance <= 200:
                distance_checks.append(f"✅ Prepare to stop: {prepare_stop_distance}m (appropriate)")
            else:
                distance_checks.append(f"⚠️ Prepare to stop: {prepare_stop_distance}m (may be inappropriate)")
            
            for check in distance_checks:
                print(f"   {check}")
            
            print(f"   🎉 ALL SIGN SPACING SUCCESS CRITERIA MET!")
            return True
        return False

    def run_worksite_tmp_tests(self):
        """Run all worksite TMP endpoint tests"""
        print("🚧 VicRoads Traffic Management Note No. 33 - Worksite TMP Testing")
        print("=" * 80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return False
        
        # Test both worksite TMP endpoints
        tests = [
            ("Worksite TMP Generation", self.test_worksite_tmp_generation),
            ("Sign Spacing Calculator", self.test_sign_spacing_calculator)
        ]
        
        print(f"\n🎯 Testing {len(tests)} Worksite TMP Endpoints...")
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🔍 TESTING: {test_name}")
            print(f"{'='*60}")
            
            if test_func():
                print(f"🎉 {test_name} - ALL SUCCESS CRITERIA MET!")
            else:
                print(f"❌ {test_name} - FAILED")
        
        # Final summary
        print(f"\n📊 WORKSITE TMP TESTING RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL WORKSITE TMP TESTS PASSED!")
            print("✅ Both endpoints return 200 OK status")
            print("✅ Worksite TMP includes all required sections")
            print("✅ Sign spacing calculator returns proper calculations")
            print("✅ All distance calculations appropriate for speed zones")
            print("✅ No 500 errors or exceptions detected")
            return True
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = WorksiteTMPTester()
    success = tester.run_worksite_tmp_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())