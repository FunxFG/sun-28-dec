#!/usr/bin/env python3
"""
Comprehensive 6-Scenario TMP Testing - Road Closures + Pedestrian Controls
Testing the comprehensive auto-populate endpoint with 6 specific scenarios as requested.
"""

import requests
import sys
import json
import time
from datetime import datetime

class Comprehensive6ScenarioTester:
    def __init__(self, base_url="https://roadworksai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.scenario_results = {}

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
                print(f"   Response: {response.text[:500]}...")
                self.failed_tests.append(name)
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(name)
            return False, {}

    def validate_comprehensive_response_structure(self, response, scenario_name):
        """Validate that response contains all 26 expected datasets"""
        print(f"\n📋 Validating {scenario_name} Response Structure...")
        
        # Expected 26 datasets from comprehensive auto-populate
        expected_fields = [
            'road_data', 'traffic_assessment', 'site_assessment', 'side_streets',
            'intersections', 'control_measures', 'pedestrian_control_measures',
            'recommended_devices', 'signage_plan', 'suggested_risks',
            'governing_body_details', 'notification_requirements',
            'environmental_constraints', 'staging_recommendations',
            'detour_routes', 'public_facilities', 'traffic_signals',
            'parking_restrictions', 'school_zones', 'public_transport_detailed',
            'utility_infrastructure', 'location_metadata_system',
            'dit_infrastructure_assets', 'sa_traffic_intelligence',
            'crash_statistics', 'weather_conditions'
        ]
        
        present_fields = []
        missing_fields = []
        
        for field in expected_fields:
            if field in response:
                present_fields.append(field)
            else:
                missing_fields.append(field)
        
        print(f"   Present fields: {len(present_fields)}/{len(expected_fields)}")
        print(f"   Present: {present_fields}")
        
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
            return False
        else:
            print(f"   ✅ All 26 datasets present")
            return True

    def test_scenario_1_urban_cbd_road_closure(self):
        """
        SCENARIO 1: Urban CBD Road Closure - King William Street
        Expected: Top 40 Road detection, heavy pedestrian controls, DDA compliance
        """
        print(f"\n{'='*80}")
        print(f"🏙️  SCENARIO 1: Urban CBD Road Closure - King William Street")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        success, response = self.run_test(
            "Scenario 1 - Urban CBD Road Closure",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9285,
                "lng": 138.6007,
                "start_address": "King William Street, Adelaide SA",
                "end_address": "North Terrace, Adelaide SA",
                "work_type": "Road Closure"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not success:
            self.scenario_results['scenario_1'] = {'status': 'FAILED', 'reason': 'API call failed'}
            return False
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        # Validate response structure
        if not self.validate_comprehensive_response_structure(response, "Scenario 1"):
            self.scenario_results['scenario_1'] = {'status': 'FAILED', 'reason': 'Missing required fields'}
            return False
        
        # Scenario-specific validations
        validation_results = []
        
        # 1. Top 40 Road detection
        sa_traffic = response.get('sa_traffic_intelligence', {})
        top_40_road = sa_traffic.get('top_40_road_analysis', {})
        is_top_40_road = top_40_road.get('is_top_40_road', False)
        
        if is_top_40_road:
            validation_results.append("✅ Top 40 Road detection: King William St detected")
        else:
            validation_results.append("⚠️ Top 40 Road detection: Not detected as Top 40")
        
        # 2. Top 40 Intersection detection
        top_40_intersection = sa_traffic.get('top_40_intersection_analysis', {})
        is_top_40_intersection = top_40_intersection.get('is_top_40_intersection', False)
        intersection_rank = top_40_intersection.get('rank')
        vehicle_exposure = top_40_intersection.get('vehicle_exposure')
        
        if is_top_40_intersection and intersection_rank == 1 and vehicle_exposure == 95400:
            validation_results.append("✅ Top 40 Intersection: King William/North Terrace detected as #1 (95,400 exposure)")
        elif is_top_40_intersection:
            validation_results.append(f"⚠️ Top 40 Intersection detected but rank/exposure differs: #{intersection_rank}, {vehicle_exposure}")
        else:
            validation_results.append("❌ Top 40 Intersection: Not detected")
        
        # 3. Heavy pedestrian control measures
        pedestrian_controls = response.get('pedestrian_control_measures', {})
        barriers_required = pedestrian_controls.get('barriers_required', {})
        dda_compliance = pedestrian_controls.get('dda_compliance', {})
        
        if barriers_required and len(str(barriers_required).get('length', '')) > 0:
            validation_results.append("✅ Heavy pedestrian control measures detected")
        else:
            validation_results.append("❌ Heavy pedestrian control measures not detected")
        
        # 4. DDA compliance requirements
        if dda_compliance:
            width_req = dda_compliance.get('width_requirements')
            grade_req = dda_compliance.get('grade_requirements')
            if '1.0m' in str(width_req) and '1:14' in str(grade_req):
                validation_results.append("✅ DDA compliance: 1.0m width, 1:14 grade requirements")
            else:
                validation_results.append(f"⚠️ DDA compliance present but requirements differ: {width_req}, {grade_req}")
        else:
            validation_results.append("❌ DDA compliance requirements not found")
        
        # 5. Detour routes for road closure
        detour_routes = response.get('detour_routes', {})
        if detour_routes and 'routes' in detour_routes:
            validation_results.append("✅ Detour routes calculated for road closure")
        else:
            validation_results.append("❌ Detour routes not calculated")
        
        # 6. Bilateral signage requirements
        signage_plan = response.get('signage_plan', {})
        bilateral_req = signage_plan.get('bilateral_requirements')
        side_street_signs = signage_plan.get('side_street_signs', {})
        
        if bilateral_req:
            validation_results.append("✅ Bilateral signage requirements documented")
        else:
            validation_results.append("❌ Bilateral signage requirements not found")
        
        # 7. Side street double gating
        if 'double gating' in str(side_street_signs).lower():
            validation_results.append("✅ Side street double gating documented")
        else:
            validation_results.append("❌ Side street double gating not documented")
        
        # 8. School zones detection
        school_zones = response.get('school_zones', {})
        nearby_schools = school_zones.get('nearby_schools', [])
        if nearby_schools and len(nearby_schools) > 0:
            validation_results.append("✅ School zones detected")
        else:
            validation_results.append("⚠️ School zones not detected (may be expected for CBD)")
        
        # 9. Public transport impact
        public_transport = response.get('public_transport_detailed', {})
        if public_transport and len(str(public_transport)) > 50:
            validation_results.append("✅ Public transport impact assessed")
        else:
            validation_results.append("❌ Public transport impact not assessed")
        
        # 10. Traffic signals coordination
        traffic_signals = response.get('traffic_signals', {})
        coordination_required = traffic_signals.get('coordination_required', False)
        if coordination_required:
            validation_results.append("✅ Traffic signals coordination required")
        else:
            validation_results.append("⚠️ Traffic signals coordination not flagged")
        
        # Print all validation results
        print(f"\n📊 Scenario 1 Validation Results:")
        for result in validation_results:
            print(f"   {result}")
        
        # Determine overall success
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        if len(failed_validations) <= 2:  # Allow up to 2 failures
            self.scenario_results['scenario_1'] = {'status': 'PASSED', 'validations': validation_results}
            print(f"\n✅ SCENARIO 1 PASSED ({len(failed_validations)} minor issues)")
            return True
        else:
            self.scenario_results['scenario_1'] = {'status': 'FAILED', 'validations': validation_results}
            print(f"\n❌ SCENARIO 1 FAILED ({len(failed_validations)} critical issues)")
            return False

    def test_scenario_2_highway_road_closure(self):
        """
        SCENARIO 2: Highway Road Closure - Port Wakefield Road
        Expected: High-speed classification, longer warning distances, heavy vehicle considerations
        """
        print(f"\n{'='*80}")
        print(f"🛣️  SCENARIO 2: Highway Road Closure - Port Wakefield Road")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        success, response = self.run_test(
            "Scenario 2 - Highway Road Closure",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.8500,
                "lng": 138.5900,
                "start_address": "Port Wakefield Road, Adelaide SA",
                "end_address": "Grand Junction Road, Adelaide SA",
                "work_type": "Road Closure"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not success:
            self.scenario_results['scenario_2'] = {'status': 'FAILED', 'reason': 'API call failed'}
            return False
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        # Validate response structure
        if not self.validate_comprehensive_response_structure(response, "Scenario 2"):
            self.scenario_results['scenario_2'] = {'status': 'FAILED', 'reason': 'Missing required fields'}
            return False
        
        # Scenario-specific validations
        validation_results = []
        
        # 1. High-speed road classification
        road_data = response.get('road_data', {})
        speed_limit = road_data.get('speed_limit', 0)
        road_classification = road_data.get('road_classification', '')
        
        if speed_limit >= 80:
            validation_results.append(f"✅ High-speed road: {speed_limit} km/h")
        else:
            validation_results.append(f"❌ Expected ≥80 km/h, got {speed_limit} km/h")
        
        # 2. Longer advance warning distances
        signage_plan = response.get('signage_plan', {})
        distances = signage_plan.get('distances_documented', {})
        advance_warning_distance = distances.get('advance_warning_distance')
        
        if advance_warning_distance:
            # Extract numeric value
            import re
            distance_match = re.search(r'(\d+)', str(advance_warning_distance))
            if distance_match:
                distance_value = int(distance_match.group(1))
                if distance_value >= 150:
                    validation_results.append(f"✅ Advance warning distance: {distance_value}m (≥150m)")
                else:
                    validation_results.append(f"❌ Advance warning distance: {distance_value}m (<150m)")
            else:
                validation_results.append(f"⚠️ Advance warning distance format unclear: {advance_warning_distance}")
        else:
            validation_results.append("❌ Advance warning distance not documented")
        
        # 3. Heavy vehicle considerations
        traffic_assessment = response.get('traffic_assessment', {})
        heavy_vehicle_pct = traffic_assessment.get('heavy_vehicle_percentage', '0%')
        
        # Extract percentage
        import re
        pct_match = re.search(r'(\d+)', str(heavy_vehicle_pct))
        if pct_match:
            pct_value = int(pct_match.group(1))
            if pct_value >= 15:
                validation_results.append(f"✅ Heavy vehicle percentage: {pct_value}% (≥15%)")
            else:
                validation_results.append(f"⚠️ Heavy vehicle percentage: {pct_value}% (<15%)")
        else:
            validation_results.append(f"❌ Heavy vehicle percentage not found: {heavy_vehicle_pct}")
        
        # 4. Reduced pedestrian controls (highway environment)
        pedestrian_controls = response.get('pedestrian_control_measures', {})
        barriers_required = pedestrian_controls.get('barriers_required', {})
        
        # Highway should have minimal pedestrian controls
        if not barriers_required or len(str(barriers_required)) < 50:
            validation_results.append("✅ Reduced pedestrian controls (highway environment)")
        else:
            validation_results.append("⚠️ Heavy pedestrian controls on highway (may be inappropriate)")
        
        # 5. Major detour routing
        detour_routes = response.get('detour_routes', {})
        if detour_routes and 'routes' in detour_routes:
            validation_results.append("✅ Major detour routing calculated")
        else:
            validation_results.append("❌ Detour routing not calculated")
        
        # 6. LMS official road classification
        location_metadata = response.get('location_metadata_system', {})
        road_classification_official = location_metadata.get('road_classification_official', '')
        
        if 'State Arterial' in road_classification_official or 'Arterial' in road_classification_official:
            validation_results.append(f"✅ LMS road classification: {road_classification_official}")
        else:
            validation_results.append(f"⚠️ LMS road classification: {road_classification_official}")
        
        # 7. DIT infrastructure assets
        dit_assets = response.get('dit_infrastructure_assets', {})
        maintenance_authority = location_metadata.get('maintenance_authority', '')
        
        if 'DIT SA' in maintenance_authority or 'DIT' in maintenance_authority:
            validation_results.append(f"✅ DIT SA maintenance authority: {maintenance_authority}")
        else:
            validation_results.append(f"⚠️ Maintenance authority: {maintenance_authority}")
        
        # Print all validation results
        print(f"\n📊 Scenario 2 Validation Results:")
        for result in validation_results:
            print(f"   {result}")
        
        # Determine overall success
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        if len(failed_validations) <= 2:
            self.scenario_results['scenario_2'] = {'status': 'PASSED', 'validations': validation_results}
            print(f"\n✅ SCENARIO 2 PASSED ({len(failed_validations)} minor issues)")
            return True
        else:
            self.scenario_results['scenario_2'] = {'status': 'FAILED', 'validations': validation_results}
            print(f"\n❌ SCENARIO 2 FAILED ({len(failed_validations)} critical issues)")
            return False

    def test_scenario_3_pedestrian_priority_zone(self):
        """
        SCENARIO 3: Pedestrian Priority Zone - Rundle Mall Road Closure
        Expected: Maximum pedestrian controls, tactile indicators, lighting requirements
        """
        print(f"\n{'='*80}")
        print(f"🚶 SCENARIO 3: Pedestrian Priority Zone - Rundle Mall Road Closure")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        success, response = self.run_test(
            "Scenario 3 - Pedestrian Priority Zone",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9230,
                "lng": 138.6010,
                "start_address": "Rundle Mall, Adelaide SA",
                "end_address": "Pulteney Street, Adelaide SA",
                "work_type": "Road Closure"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not success:
            self.scenario_results['scenario_3'] = {'status': 'FAILED', 'reason': 'API call failed'}
            return False
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        # Validate response structure
        if not self.validate_comprehensive_response_structure(response, "Scenario 3"):
            self.scenario_results['scenario_3'] = {'status': 'FAILED', 'reason': 'Missing required fields'}
            return False
        
        # Scenario-specific validations
        validation_results = []
        
        # 1. Maximum pedestrian control measures
        pedestrian_controls = response.get('pedestrian_control_measures', {})
        barriers_required = pedestrian_controls.get('barriers_required', {})
        
        if barriers_required and len(str(barriers_required)) > 100:
            validation_results.append("✅ Maximum pedestrian control measures (mall environment)")
        else:
            validation_results.append("❌ Insufficient pedestrian control measures for mall")
        
        # 2. DDA compliance with tactile indicators
        dda_compliance = pedestrian_controls.get('dda_compliance', {})
        tactile_indicators = dda_compliance.get('tactile_indicators', False)
        
        if tactile_indicators:
            validation_results.append("✅ DDA compliance: Tactile indicators required")
        else:
            validation_results.append("❌ DDA compliance: Tactile indicators not specified")
        
        # 3. Lighting requirements
        safety_measures = pedestrian_controls.get('safety_measures', {})
        lighting_req = safety_measures.get('lighting') or safety_measures.get('lighting_requirements')
        
        if lighting_req and ('20 lux' in str(lighting_req) or 'lighting' in str(lighting_req).lower()):
            validation_results.append("✅ Lighting requirements specified")
        else:
            validation_results.append("❌ Lighting requirements not specified")
        
        # 4. School/hospital access considerations
        public_facilities = response.get('public_facilities', {})
        schools = public_facilities.get('schools', [])
        hospitals = public_facilities.get('hospitals', [])
        
        if (schools and len(schools) > 0) or (hospitals and len(hospitals) > 0):
            validation_results.append("✅ School/hospital access considerations")
        else:
            validation_results.append("⚠️ No schools/hospitals detected nearby")
        
        # 5. Public transport heavily affected
        public_transport = response.get('public_transport_detailed', {})
        if public_transport and len(str(public_transport)) > 100:
            validation_results.append("✅ Public transport impact assessed")
        else:
            validation_results.append("❌ Public transport impact not adequately assessed")
        
        # 6. Extensive parking restrictions
        parking_restrictions = response.get('parking_restrictions', {})
        restrictions = parking_restrictions.get('restrictions', [])
        
        if restrictions and len(restrictions) > 0:
            validation_results.append("✅ Parking restrictions documented")
        else:
            validation_results.append("⚠️ Parking restrictions not documented")
        
        # 7. High crash statistics
        crash_statistics = response.get('crash_statistics', {})
        total_crashes = crash_statistics.get('total_crashes', 0)
        
        if total_crashes and total_crashes > 0:
            validation_results.append(f"✅ Crash statistics: {total_crashes} crashes")
        else:
            validation_results.append("⚠️ Crash statistics not available")
        
        # Print all validation results
        print(f"\n📊 Scenario 3 Validation Results:")
        for result in validation_results:
            print(f"   {result}")
        
        # Determine overall success
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        if len(failed_validations) <= 3:  # Allow up to 3 failures for this complex scenario
            self.scenario_results['scenario_3'] = {'status': 'PASSED', 'validations': validation_results}
            print(f"\n✅ SCENARIO 3 PASSED ({len(failed_validations)} minor issues)")
            return True
        else:
            self.scenario_results['scenario_3'] = {'status': 'FAILED', 'validations': validation_results}
            print(f"\n❌ SCENARIO 3 FAILED ({len(failed_validations)} critical issues)")
            return False

    def test_scenario_4_school_zone_single_lane(self):
        """
        SCENARIO 4: Single Lane Closure with School Zone - Unley Road
        Expected: School zone detection, 40 km/h restrictions, timing restrictions
        """
        print(f"\n{'='*80}")
        print(f"🏫 SCENARIO 4: Single Lane Closure with School Zone - Unley Road")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        success, response = self.run_test(
            "Scenario 4 - School Zone Single Lane Closure",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9500,
                "lng": 138.6100,
                "start_address": "Unley Road, Unley SA",
                "end_address": "Cross Road, Unley SA",
                "work_type": "Construction"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not success:
            self.scenario_results['scenario_4'] = {'status': 'FAILED', 'reason': 'API call failed'}
            return False
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        # Validate response structure
        if not self.validate_comprehensive_response_structure(response, "Scenario 4"):
            self.scenario_results['scenario_4'] = {'status': 'FAILED', 'reason': 'Missing required fields'}
            return False
        
        # Scenario-specific validations
        validation_results = []
        
        # 1. School zone detection
        school_zones = response.get('school_zones', {})
        nearby_schools = school_zones.get('nearby_schools', [])
        
        if nearby_schools and len(nearby_schools) > 0:
            validation_results.append(f"✅ School zone detection: {len(nearby_schools)} schools found")
        else:
            validation_results.append("❌ School zone not detected")
        
        # 2. Enhanced 40 km/h restrictions
        enhanced_restrictions = school_zones.get('enhanced_restrictions', False)
        speed_limit_school = school_zones.get('speed_limit_school_zone', '')
        
        if enhanced_restrictions:
            validation_results.append("✅ Enhanced school zone restrictions enabled")
        else:
            validation_results.append("❌ Enhanced school zone restrictions not enabled")
        
        if '40 km/h' in speed_limit_school or '40km/h' in speed_limit_school:
            validation_results.append("✅ School zone speed limit: 40 km/h")
        else:
            validation_results.append(f"❌ School zone speed limit not 40 km/h: {speed_limit_school}")
        
        # 3. School hours specified
        school_hours = school_zones.get('school_hours', '')
        if school_hours and len(school_hours) > 0:
            validation_results.append(f"✅ School hours specified: {school_hours}")
        else:
            validation_results.append("❌ School hours not specified")
        
        # 4. Pedestrian control measures for school children
        pedestrian_controls = response.get('pedestrian_control_measures', {})
        school_specific = pedestrian_controls.get('school_specific_measures') or pedestrian_controls.get('safety_measures')
        
        if school_specific and 'school' in str(school_specific).lower():
            validation_results.append("✅ School-specific pedestrian measures")
        else:
            validation_results.append("⚠️ School-specific pedestrian measures not clearly specified")
        
        # 5. Timing restrictions (work outside school hours)
        staging_recommendations = response.get('staging_recommendations', {})
        timing_restrictions = staging_recommendations.get('timing_restrictions') or staging_recommendations.get('recommended_timing')
        
        if timing_restrictions and 'school' in str(timing_restrictions).lower():
            validation_results.append("✅ School hour timing restrictions recommended")
        else:
            validation_results.append("⚠️ School hour timing restrictions not specified")
        
        # 6. Single lane closure signage
        signage_plan = response.get('signage_plan', {})
        lane_closure_signs = signage_plan.get('lane_closure_signs') or signage_plan.get('workzone_signs')
        
        if lane_closure_signs:
            validation_results.append("✅ Single lane closure signage planned")
        else:
            validation_results.append("❌ Single lane closure signage not planned")
        
        # 7. Local traffic volume data
        traffic_assessment = response.get('traffic_assessment', {})
        aadt = traffic_assessment.get('aadt', 0)
        
        if aadt and aadt > 0:
            validation_results.append(f"✅ Local traffic volume data: {aadt:,} AADT")
        else:
            validation_results.append("❌ Local traffic volume data not available")
        
        # Print all validation results
        print(f"\n📊 Scenario 4 Validation Results:")
        for result in validation_results:
            print(f"   {result}")
        
        # Determine overall success
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        if len(failed_validations) <= 2:
            self.scenario_results['scenario_4'] = {'status': 'PASSED', 'validations': validation_results}
            print(f"\n✅ SCENARIO 4 PASSED ({len(failed_validations)} minor issues)")
            return True
        else:
            self.scenario_results['scenario_4'] = {'status': 'FAILED', 'validations': validation_results}
            print(f"\n❌ SCENARIO 4 FAILED ({len(failed_validations)} critical issues)")
            return False

    def test_scenario_5_top_40_intersection(self):
        """
        SCENARIO 5: Top 40 Intersection Works - Anzac Highway / Sir Donald Bradman Drive
        Expected: Top 40 intersection detection (Rank #4, 81,100 exposure), complex staging
        """
        print(f"\n{'='*80}")
        print(f"🚦 SCENARIO 5: Top 40 Intersection Works - Anzac Hwy / Sir Donald Bradman Dr")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        success, response = self.run_test(
            "Scenario 5 - Top 40 Intersection Works",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9450,
                "lng": 138.5700,
                "start_address": "Anzac Highway, Adelaide SA",
                "end_address": "Sir Donald Bradman Drive, Adelaide SA",
                "work_type": "Construction"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not success:
            self.scenario_results['scenario_5'] = {'status': 'FAILED', 'reason': 'API call failed'}
            return False
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        # Validate response structure
        if not self.validate_comprehensive_response_structure(response, "Scenario 5"):
            self.scenario_results['scenario_5'] = {'status': 'FAILED', 'reason': 'Missing required fields'}
            return False
        
        # Scenario-specific validations
        validation_results = []
        
        # 1. Top 40 Intersection detection
        sa_traffic = response.get('sa_traffic_intelligence', {})
        top_40_intersection = sa_traffic.get('top_40_intersection_analysis', {})
        is_top_40_intersection = top_40_intersection.get('is_top_40_intersection', False)
        rank = top_40_intersection.get('rank')
        vehicle_exposure = top_40_intersection.get('vehicle_exposure')
        
        if is_top_40_intersection:
            validation_results.append("✅ Top 40 Intersection detected")
            
            if rank == 4:
                validation_results.append("✅ Correct rank: #4")
            else:
                validation_results.append(f"⚠️ Expected rank #4, got #{rank}")
            
            if vehicle_exposure == 81100:
                validation_results.append("✅ Correct vehicle exposure: 81,100")
            else:
                validation_results.append(f"⚠️ Expected 81,100 exposure, got {vehicle_exposure}")
        else:
            validation_results.append("❌ Top 40 Intersection not detected")
        
        # 2. Very high traffic level assessment
        overall_traffic_level = sa_traffic.get('overall_traffic_level', '')
        if overall_traffic_level in ['VERY HIGH', 'HIGH']:
            validation_results.append(f"✅ Traffic level assessment: {overall_traffic_level}")
        else:
            validation_results.append(f"⚠️ Expected VERY HIGH/HIGH traffic, got {overall_traffic_level}")
        
        # 3. Traffic signal coordination requirements
        traffic_signals = response.get('traffic_signals', {})
        coordination_required = traffic_signals.get('coordination_required', False)
        
        if coordination_required:
            validation_results.append("✅ Traffic signal coordination required")
        else:
            validation_results.append("❌ Traffic signal coordination not flagged")
        
        # 4. Multiple advance warnings
        signage_plan = response.get('signage_plan', {})
        advance_warning_signs = signage_plan.get('advance_warning_signs', [])
        
        if advance_warning_signs and len(advance_warning_signs) >= 2:
            validation_results.append(f"✅ Multiple advance warnings: {len(advance_warning_signs)} signs")
        else:
            validation_results.append("❌ Insufficient advance warning signs")
        
        # 5. Night/weekend work recommendations
        recommendations = sa_traffic.get('recommendations', [])
        night_weekend_rec = any('night' in str(rec).lower() or 'weekend' in str(rec).lower() for rec in recommendations)
        
        if night_weekend_rec:
            validation_results.append("✅ Night/weekend work recommendations")
        else:
            validation_results.append("⚠️ Night/weekend work not specifically recommended")
        
        # 6. Complex staging requirements
        staging_recommendations = response.get('staging_recommendations', {})
        recommended_stages = staging_recommendations.get('recommended_stages', [])
        
        if recommended_stages and len(recommended_stages) >= 3:
            validation_results.append(f"✅ Complex staging: {len(recommended_stages)} stages")
        else:
            validation_results.append(f"⚠️ Expected ≥3 stages, got {len(recommended_stages) if recommended_stages else 0}")
        
        # 7. Emergency access maintenance
        emergency_access = staging_recommendations.get('emergency_access') or staging_recommendations.get('safety_considerations')
        
        if emergency_access and 'emergency' in str(emergency_access).lower():
            validation_results.append("✅ Emergency access maintenance considered")
        else:
            validation_results.append("⚠️ Emergency access maintenance not explicitly mentioned")
        
        # Print all validation results
        print(f"\n📊 Scenario 5 Validation Results:")
        for result in validation_results:
            print(f"   {result}")
        
        # Determine overall success
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        if len(failed_validations) <= 2:
            self.scenario_results['scenario_5'] = {'status': 'PASSED', 'validations': validation_results}
            print(f"\n✅ SCENARIO 5 PASSED ({len(failed_validations)} minor issues)")
            return True
        else:
            self.scenario_results['scenario_5'] = {'status': 'FAILED', 'validations': validation_results}
            print(f"\n❌ SCENARIO 5 FAILED ({len(failed_validations)} critical issues)")
            return False

    def test_scenario_6_multi_lane_arterial(self):
        """
        SCENARIO 6: Multi-Lane Arterial - South Eastern Freeway
        Expected: National Highway classification, 100+ km/h, maximum warning distances
        """
        print(f"\n{'='*80}")
        print(f"🛤️  SCENARIO 6: Multi-Lane Arterial - South Eastern Freeway")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        success, response = self.run_test(
            "Scenario 6 - Multi-Lane Arterial",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9800,
                "lng": 138.6500,
                "start_address": "South Eastern Freeway, Adelaide SA",
                "end_address": "Glen Osmond Road, Adelaide SA",
                "work_type": "Maintenance"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not success:
            self.scenario_results['scenario_6'] = {'status': 'FAILED', 'reason': 'API call failed'}
            return False
        
        print(f"   Response time: {response_time:.2f} seconds")
        
        # Validate response structure
        if not self.validate_comprehensive_response_structure(response, "Scenario 6"):
            self.scenario_results['scenario_6'] = {'status': 'FAILED', 'reason': 'Missing required fields'}
            return False
        
        # Scenario-specific validations
        validation_results = []
        
        # 1. National Highway classification
        road_data = response.get('road_data', {})
        road_classification = road_data.get('road_classification', '')
        
        if 'National Highway' in road_classification or 'Freeway' in road_classification:
            validation_results.append(f"✅ Highway classification: {road_classification}")
        else:
            validation_results.append(f"⚠️ Expected National Highway/Freeway, got {road_classification}")
        
        # 2. Very high speed (100+ km/h)
        speed_limit = road_data.get('speed_limit', 0)
        if speed_limit >= 100:
            validation_results.append(f"✅ High speed limit: {speed_limit} km/h")
        else:
            validation_results.append(f"❌ Expected ≥100 km/h, got {speed_limit} km/h")
        
        # 3. Maximum advance warning distances (250m+)
        signage_plan = response.get('signage_plan', {})
        distances = signage_plan.get('distances_documented', {})
        advance_warning_distance = distances.get('advance_warning_distance', '')
        
        if advance_warning_distance:
            import re
            distance_match = re.search(r'(\d+)', str(advance_warning_distance))
            if distance_match:
                distance_value = int(distance_match.group(1))
                if distance_value >= 250:
                    validation_results.append(f"✅ Maximum advance warning: {distance_value}m (≥250m)")
                else:
                    validation_results.append(f"❌ Advance warning: {distance_value}m (<250m)")
            else:
                validation_results.append(f"⚠️ Advance warning distance unclear: {advance_warning_distance}")
        else:
            validation_results.append("❌ Advance warning distance not documented")
        
        # 4. Multiple lanes (4+)
        lanes = road_data.get('lanes', 0)
        if lanes >= 4:
            validation_results.append(f"✅ Multiple lanes: {lanes} lanes")
        else:
            validation_results.append(f"⚠️ Expected ≥4 lanes, got {lanes}")
        
        # 5. DIT SA maintenance authority
        location_metadata = response.get('location_metadata_system', {})
        maintenance_authority = location_metadata.get('maintenance_authority', '')
        
        if 'DIT SA' in maintenance_authority:
            validation_results.append(f"✅ DIT SA maintenance authority: {maintenance_authority}")
        else:
            validation_results.append(f"⚠️ Maintenance authority: {maintenance_authority}")
        
        # 6. High AADT (>30,000)
        traffic_assessment = response.get('traffic_assessment', {})
        aadt = traffic_assessment.get('aadt', 0)
        
        if aadt > 30000:
            validation_results.append(f"✅ High AADT: {aadt:,} (>30,000)")
        else:
            validation_results.append(f"⚠️ Expected AADT >30,000, got {aadt:,}")
        
        # 7. Heavy vehicle traffic (>20%)
        heavy_vehicle_pct = traffic_assessment.get('heavy_vehicle_percentage', '0%')
        import re
        pct_match = re.search(r'(\d+)', str(heavy_vehicle_pct))
        if pct_match:
            pct_value = int(pct_match.group(1))
            if pct_value >= 20:
                validation_results.append(f"✅ Heavy vehicle traffic: {pct_value}% (≥20%)")
            else:
                validation_results.append(f"⚠️ Heavy vehicle traffic: {pct_value}% (<20%)")
        else:
            validation_results.append(f"❌ Heavy vehicle percentage not found: {heavy_vehicle_pct}")
        
        # Print all validation results
        print(f"\n📊 Scenario 6 Validation Results:")
        for result in validation_results:
            print(f"   {result}")
        
        # Determine overall success
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        if len(failed_validations) <= 2:
            self.scenario_results['scenario_6'] = {'status': 'PASSED', 'validations': validation_results}
            print(f"\n✅ SCENARIO 6 PASSED ({len(failed_validations)} minor issues)")
            return True
        else:
            self.scenario_results['scenario_6'] = {'status': 'FAILED', 'validations': validation_results}
            print(f"\n❌ SCENARIO 6 FAILED ({len(failed_validations)} critical issues)")
            return False

    def run_all_scenarios(self):
        """Run all 6 comprehensive scenarios"""
        print(f"\n{'='*100}")
        print(f"🚀 COMPREHENSIVE 6-SCENARIO TMP TESTING - ROAD CLOSURES + PEDESTRIAN CONTROLS")
        print(f"{'='*100}")
        print(f"Testing comprehensive auto-populate endpoint with 6 specific scenarios")
        print(f"Base URL: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all scenarios
        scenario_functions = [
            self.test_scenario_1_urban_cbd_road_closure,
            self.test_scenario_2_highway_road_closure,
            self.test_scenario_3_pedestrian_priority_zone,
            self.test_scenario_4_school_zone_single_lane,
            self.test_scenario_5_top_40_intersection,
            self.test_scenario_6_multi_lane_arterial
        ]
        
        passed_scenarios = 0
        
        for scenario_func in scenario_functions:
            try:
                if scenario_func():
                    passed_scenarios += 1
            except Exception as e:
                print(f"❌ Scenario failed with exception: {str(e)}")
        
        # Print final summary
        print(f"\n{'='*100}")
        print(f"📊 COMPREHENSIVE 6-SCENARIO TESTING SUMMARY")
        print(f"{'='*100}")
        
        for scenario_name, result in self.scenario_results.items():
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"{status_icon} {scenario_name.upper()}: {result['status']}")
            if result['status'] == 'FAILED' and 'reason' in result:
                print(f"   Reason: {result['reason']}")
        
        print(f"\n📈 Overall Results:")
        print(f"   Scenarios Passed: {passed_scenarios}/6")
        print(f"   Success Rate: {(passed_scenarios/6)*100:.1f}%")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        
        if passed_scenarios >= 4:  # 4/6 scenarios must pass
            print(f"\n🎉 COMPREHENSIVE TESTING PASSED - {passed_scenarios}/6 scenarios successful")
            return True
        else:
            print(f"\n❌ COMPREHENSIVE TESTING FAILED - Only {passed_scenarios}/6 scenarios successful")
            return False

def main():
    """Main function to run comprehensive 6-scenario testing"""
    tester = Comprehensive6ScenarioTester()
    
    try:
        success = tester.run_all_scenarios()
        
        if success:
            print(f"\n✅ All comprehensive scenario testing completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Comprehensive scenario testing failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()