#!/usr/bin/env python3
"""
Focused test for SA Government Datasets Integration
Tests Location Metadata System and DIT Infrastructure Assets
"""
import requests
import sys
import json
from datetime import datetime

class SADatasetsAPITester:
    def __init__(self, base_url="https://tmp-generator.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

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

    def authenticate(self):
        """Quick authentication for testing"""
        test_email = f"sa_test_{datetime.now().strftime('%H%M%S')}@example.com"
        test_data = {
            "email": test_email,
            "password": "TestPass123!",
            "company_name": "SA Datasets Test Company"
        }
        
        success, response = self.run_test(
            "User Registration for SA Datasets Testing",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            print(f"   Authenticated as: {test_email}")
            return True
        return False

    def test_location_metadata_system_adelaide_cbd(self):
        """Test Location Metadata System (LMS) - Adelaide CBD (King William Street)"""
        print("\n" + "="*80)
        print("🏛️ TESTING LOCATION METADATA SYSTEM (LMS) INTEGRATION")
        print("="*80)
        
        import time
        start_time = time.time()
        
        success, response = self.run_test(
            "Location Metadata System - Adelaide CBD (King William Street)",
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
            
            # Check for Location Metadata System data
            lms_data = response.get('location_metadata_system', {})
            if not lms_data:
                print(f"   ❌ Location Metadata System data missing")
                return False
            
            print(f"   ✅ Location Metadata System data present")
            
            # Verify required LMS fields
            required_lms_fields = [
                'road_classification_official', 'maintenance_authority', 'crrs_code',
                'austroads_class_code', 'functional_hierarchy', 'speed_limit_official',
                'sealed_status', 'road_category_code', 'dataset_references'
            ]
            
            missing_lms_fields = [field for field in required_lms_fields if field not in lms_data]
            if missing_lms_fields:
                print(f"   ❌ Missing LMS fields: {missing_lms_fields}")
                return False
            
            # Display LMS field values
            road_classification = lms_data.get('road_classification_official')
            maintenance_authority = lms_data.get('maintenance_authority')
            crrs_code = lms_data.get('crrs_code')
            austroads_class = lms_data.get('austroads_class_code')
            functional_hierarchy = lms_data.get('functional_hierarchy')
            speed_limit = lms_data.get('speed_limit_official')
            sealed_status = lms_data.get('sealed_status')
            dataset_refs = lms_data.get('dataset_references', [])
            
            print(f"\n   📋 LOCATION METADATA SYSTEM RESULTS:")
            print(f"   Road classification (official): {road_classification}")
            print(f"   Maintenance authority: {maintenance_authority}")
            print(f"   CRRS code: {crrs_code}")
            print(f"   Austroads class code: {austroads_class}")
            print(f"   Functional hierarchy: {functional_hierarchy}")
            print(f"   Speed limit (official): {speed_limit}")
            print(f"   Sealed status: {sealed_status}")
            print(f"   Dataset references: {dataset_refs}")
            
            # Validation checks
            success_criteria = []
            
            # King William Street should be State Arterial or higher
            if road_classification in ['State Arterial Road', 'National Highway', 'Regional Road']:
                success_criteria.append(f"✅ Appropriate road classification: {road_classification}")
            else:
                success_criteria.append(f"⚠️ Expected State Arterial+, got: {road_classification}")
            
            # Maintenance authority validation
            if 'Department for Infrastructure and Transport SA' in maintenance_authority:
                success_criteria.append(f"✅ Correct maintenance authority: DIT SA")
            elif 'Local Council' in maintenance_authority and road_classification == 'Local Road':
                success_criteria.append(f"✅ Correct maintenance authority for local road")
            else:
                success_criteria.append(f"⚠️ Maintenance authority: {maintenance_authority}")
            
            # CRRS code validation
            if crrs_code and crrs_code.startswith('SA-'):
                success_criteria.append(f"✅ CRRS code generated: {crrs_code}")
            else:
                success_criteria.append(f"❌ Invalid CRRS code: {crrs_code}")
            
            # Austroads class validation
            valid_austroads_classes = ['Arterial - Principal', 'Arterial - Major', 'Arterial - Minor', 'Collector', 'Local Access']
            if austroads_class in valid_austroads_classes:
                success_criteria.append(f"✅ Valid Austroads class: {austroads_class}")
            else:
                success_criteria.append(f"❌ Invalid Austroads class: {austroads_class}")
            
            # Dataset references validation
            if len(dataset_refs) >= 2 and any('558' in ref for ref in dataset_refs) and any('1639' in ref for ref in dataset_refs):
                success_criteria.append(f"✅ LMS dataset references present (558 & 1639)")
            else:
                success_criteria.append(f"❌ Missing LMS dataset references")
            
            print(f"\n   📊 VALIDATION RESULTS:")
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            return len([c for c in success_criteria if c.startswith('✅')]) >= 4
        return False

    def test_dit_infrastructure_assets_adelaide_cbd(self):
        """Test DIT Infrastructure Assets - Adelaide CBD"""
        print("\n" + "="*80)
        print("🏗️ TESTING DIT INFRASTRUCTURE ASSETS INTEGRATION")
        print("="*80)
        
        import time
        start_time = time.time()
        
        success, response = self.run_test(
            "DIT Infrastructure Assets - Adelaide CBD",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.9285,
                "lng": 138.6007,
                "start_address": "King William Street, Adelaide SA",
                "end_address": "North Terrace, Adelaide SA",
                "work_type": "maintenance"
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if success:
            print(f"   Response time: {response_time:.2f} seconds")
            
            # Check for DIT Infrastructure Assets data
            dit_assets = response.get('dit_infrastructure_assets', {})
            if not dit_assets:
                print(f"   ❌ DIT Infrastructure Assets data missing")
                return False
            
            print(f"   ✅ DIT Infrastructure Assets data present")
            
            # Verify required DIT fields
            required_dit_fields = [
                'road_condition', 'pavement_type', 'asset_inventory', 'maintenance_schedule'
            ]
            
            missing_dit_fields = [field for field in required_dit_fields if field not in dit_assets]
            if missing_dit_fields:
                print(f"   ❌ Missing DIT fields: {missing_dit_fields}")
                return False
            
            # Display DIT field values
            road_condition = dit_assets.get('road_condition')
            pavement_type = dit_assets.get('pavement_type')
            asset_inventory = dit_assets.get('asset_inventory', [])
            maintenance_schedule = dit_assets.get('maintenance_schedule', {})
            
            print(f"\n   📋 DIT INFRASTRUCTURE ASSETS RESULTS:")
            print(f"   Road condition: {road_condition}")
            print(f"   Pavement type: {pavement_type}")
            print(f"   Asset inventory count: {len(asset_inventory)}")
            if asset_inventory:
                print(f"   Asset inventory items:")
                for i, asset in enumerate(asset_inventory[:3]):  # Show first 3
                    print(f"     {i+1}. {asset.get('asset_type', 'Unknown')}: {asset.get('details', 'No details')}")
            print(f"   Maintenance schedule: {maintenance_schedule}")
            
            # Validation checks
            success_criteria = []
            
            # Road condition validation
            valid_conditions = ['Good', 'Fair', 'Poor', 'Requires Assessment']
            if road_condition in valid_conditions:
                success_criteria.append(f"✅ Valid road condition: {road_condition}")
            else:
                success_criteria.append(f"❌ Invalid road condition: {road_condition}")
            
            # Pavement type validation
            if pavement_type and pavement_type != 'None':
                success_criteria.append(f"✅ Pavement type specified: {pavement_type}")
            else:
                success_criteria.append(f"❌ Pavement type not specified")
            
            # Asset inventory validation
            if len(asset_inventory) > 0:
                success_criteria.append(f"✅ Asset inventory populated ({len(asset_inventory)} items)")
                # Check first asset structure
                if asset_inventory[0].get('asset_type') and asset_inventory[0].get('details'):
                    success_criteria.append(f"✅ Asset inventory structure valid")
                else:
                    success_criteria.append(f"❌ Asset inventory structure invalid")
            else:
                success_criteria.append(f"❌ Asset inventory empty")
            
            # Maintenance schedule validation
            required_schedule_fields = ['inspection_frequency', 'contact', 'phone']
            schedule_fields_present = [field for field in required_schedule_fields if field in maintenance_schedule]
            if len(schedule_fields_present) >= 2:
                success_criteria.append(f"✅ Maintenance schedule complete")
                
                # Check for DIT contact info
                contact = maintenance_schedule.get('contact', '')
                if 'Department for Infrastructure and Transport SA' in contact:
                    success_criteria.append(f"✅ DIT contact information present")
                else:
                    success_criteria.append(f"⚠️ Non-DIT contact: {contact}")
            else:
                success_criteria.append(f"❌ Maintenance schedule incomplete")
            
            print(f"\n   📊 VALIDATION RESULTS:")
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            return len([c for c in success_criteria if c.startswith('✅')]) >= 4
        return False

    def test_highway_scenario(self):
        """Test Highway scenario - Port Wakefield Road"""
        print("\n" + "="*80)
        print("🛣️ TESTING HIGHWAY SCENARIO (Port Wakefield Road)")
        print("="*80)
        
        success, response = self.run_test(
            "Highway Test - Port Wakefield Road",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.8,
                "lng": 138.5,
                "start_address": "Port Wakefield Road, Adelaide SA",
                "end_address": "Northern Expressway, Adelaide SA",
                "work_type": "maintenance"
            }
        )
        
        if success:
            # Check LMS data for highway classification
            lms_data = response.get('location_metadata_system', {})
            dit_assets = response.get('dit_infrastructure_assets', {})
            
            print(f"\n   📋 HIGHWAY SCENARIO RESULTS:")
            if lms_data:
                road_classification = lms_data.get('road_classification_official')
                maintenance_authority = lms_data.get('maintenance_authority')
                
                print(f"   LMS Road classification: {road_classification}")
                print(f"   LMS Maintenance authority: {maintenance_authority}")
                
                # Highway should be National Highway or State Arterial
                if road_classification in ['National Highway', 'State Arterial Road']:
                    print(f"   ✅ Highway correctly classified as: {road_classification}")
                else:
                    print(f"   ⚠️ Expected National Highway/State Arterial, got: {road_classification}")
            
            if dit_assets:
                road_condition = dit_assets.get('road_condition')
                pavement_type = dit_assets.get('pavement_type')
                print(f"   DIT Road condition: {road_condition}")
                print(f"   DIT Pavement type: {pavement_type}")
            
            return True
        return False

    def test_residential_scenario(self):
        """Test Residential scenario"""
        print("\n" + "="*80)
        print("🏘️ TESTING RESIDENTIAL SCENARIO")
        print("="*80)
        
        success, response = self.run_test(
            "Residential Test - Local Street",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -34.95,
                "lng": 138.62,
                "start_address": "Residential Street, Unley SA",
                "end_address": "Local Avenue, Unley SA",
                "work_type": "maintenance"
            }
        )
        
        if success:
            # Check LMS data for local road classification
            lms_data = response.get('location_metadata_system', {})
            dit_assets = response.get('dit_infrastructure_assets', {})
            
            print(f"\n   📋 RESIDENTIAL SCENARIO RESULTS:")
            if lms_data:
                road_classification = lms_data.get('road_classification_official')
                maintenance_authority = lms_data.get('maintenance_authority')
                
                print(f"   LMS Road classification: {road_classification}")
                print(f"   LMS Maintenance authority: {maintenance_authority}")
                
                # Residential should be Local Road with Council maintenance
                if road_classification == 'Local Road':
                    print(f"   ✅ Residential correctly classified as Local Road")
                else:
                    print(f"   ⚠️ Expected Local Road, got: {road_classification}")
                
                if 'Local Council' in maintenance_authority:
                    print(f"   ✅ Local Council maintenance authority correct")
                else:
                    print(f"   ⚠️ Expected Local Council, got: {maintenance_authority}")
            
            if dit_assets:
                road_condition = dit_assets.get('road_condition')
                pavement_type = dit_assets.get('pavement_type')
                print(f"   DIT Road condition: {road_condition}")
                print(f"   DIT Pavement type: {pavement_type}")
            
            return True
        return False

def main():
    print("🏛️ SA GOVERNMENT DATASETS INTEGRATION TESTING")
    print("Testing Location Metadata System (LMS) and DIT Infrastructure Assets")
    print("=" * 80)
    
    tester = SADatasetsAPITester()
    
    # Authenticate first
    if not tester.authenticate():
        print("❌ Authentication failed - cannot proceed with tests")
        return 1
    
    # Run SA Government dataset tests
    tests = [
        ("Location Metadata System - Adelaide CBD", tester.test_location_metadata_system_adelaide_cbd),
        ("DIT Infrastructure Assets - Adelaide CBD", tester.test_dit_infrastructure_assets_adelaide_cbd),
        ("Highway Scenario Test", tester.test_highway_scenario),
        ("Residential Scenario Test", tester.test_residential_scenario),
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
        print("🎉 All SA Government dataset integration tests passed!")
        print("✅ Location Metadata System and DIT Infrastructure Assets working correctly")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        print("❌ SA Government dataset integration issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())