import requests
import sys
import json
from datetime import datetime, timezone

class SafeRoadWorksAPITester:
    def __init__(self, base_url="https://austromap.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_plan_id = None

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
                response = requests.get(url, headers=test_headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

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

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        test_data = {
            "email": test_email,
            "password": "TestPass123!",
            "company_name": "Test Traffic Company"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {test_email}")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        test_email = f"login_test_{datetime.now().strftime('%H%M%S')}@example.com"
        register_data = {
            "email": test_email,
            "password": "LoginTest123!",
            "company_name": "Login Test Company"
        }
        
        # Register user
        success, _ = self.run_test(
            "User Registration for Login Test",
            "POST",
            "auth/register",
            200,
            data=register_data
        )
        
        if not success:
            return False
        
        # Now test login
        login_data = {
            "email": test_email,
            "password": "LoginTest123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            print(f"   Login successful for: {test_email}")
            return True
        return False

    def test_geocoding(self):
        """Test geocoding endpoint"""
        success, response = self.run_test(
            "Geocoding API",
            "GET",
            "geocode",
            200,
            data={"address": "Brisbane, QLD, Australia"}
        )
        
        if success and 'lat' in response and 'lng' in response:
            print(f"   Geocoded coordinates: {response['lat']}, {response['lng']}")
            return True
        return False

    def test_road_data(self):
        """Test road data endpoint"""
        success, response = self.run_test(
            "Road Data API",
            "GET",
            "road-data",
            200,
            data={
                "start_address": "Brisbane CBD, QLD, Australia",
                "end_address": "South Brisbane, QLD, Australia"
            }
        )
        
        if success and 'workzone_size' in response:
            print(f"   Workzone size: {response['workzone_size']} meters")
            return True
        return False

    def test_create_plan(self):
        """Test creating a traffic management plan"""
        plan_data = {
            "plan_name": "Test Traffic Plan",
            "company_details": {
                "name": "Test Company",
                "address": "123 Test Street, Brisbane, QLD",
                "abn": "12345678901",
                "phone": "07 1234 5678",
                "liaison_name": "John Doe",
                "liaison_phone": "0412 345 678",
                "liaison_email": "john@testcompany.com"
            },
            "traffic_company": {
                "name": "Traffic Management Co",
                "address": "456 Traffic Ave, Brisbane, QLD",
                "phone": "07 8765 4321",
                "liaison_name": "Jane Smith",
                "liaison_phone": "0498 765 432",
                "liaison_email": "jane@trafficco.com"
            },
            "work_details": {
                "work_type": "maintenance",
                "work_style": "static",
                "description": "Road maintenance work",
                "start_date": "2025-02-01",
                "end_date": "2025-02-05",
                "start_address": "Brisbane CBD, QLD",
                "end_address": "South Brisbane, QLD"
            },
            "road_occupancy": {
                "footpath": True,
                "left_shoulder": False,
                "left_lane": True,
                "center_lane": False,
                "right_lane": False,
                "right_shoulder": False,
                "median_strip": False,
                "complete_road_closure": False
            },
            "control_measures": {
                "twenty_min_rule": True,
                "signage": True,
                "speed_reduction": True,
                "detour": False
            },
            "road_data": {
                "traffic_volume": 15000,
                "road_classification": "Major Urban Road",
                "road_type": "Arterial",
                "governing_body": "Local Council",
                "workzone_size": 500.0
            },
            "devices": [
                {
                    "device_type": "sign",
                    "device_name": "Road Work Ahead",
                    "position_lat": -27.4698,
                    "position_lng": 153.0251,
                    "properties": {}
                }
            ],
            "map_center_lat": -27.4698,
            "map_center_lng": 153.0251,
            "map_zoom": 15
        }
        
        success, response = self.run_test(
            "Create Traffic Plan",
            "POST",
            "plans",
            200,
            data=plan_data
        )
        
        if success and 'id' in response:
            self.created_plan_id = response['id']
            print(f"   Created plan ID: {self.created_plan_id}")
            return True
        return False

    def test_get_plans(self):
        """Test getting user's plans"""
        success, response = self.run_test(
            "Get User Plans",
            "GET",
            "plans",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} plans")
            return True
        return False

    def test_get_single_plan(self):
        """Test getting a single plan"""
        if not self.created_plan_id:
            print("❌ No plan ID available for single plan test")
            return False
            
        success, response = self.run_test(
            "Get Single Plan",
            "GET",
            f"plans/{self.created_plan_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"   Retrieved plan: {response['plan_name']}")
            return True
        return False

    def test_update_plan(self):
        """Test updating a plan"""
        if not self.created_plan_id:
            print("❌ No plan ID available for update test")
            return False
            
        update_data = {
            "plan_name": "Updated Test Traffic Plan",
            "company_details": {
                "name": "Updated Test Company",
                "address": "123 Test Street, Brisbane, QLD",
                "abn": "12345678901",
                "phone": "07 1234 5678",
                "liaison_name": "John Doe",
                "liaison_phone": "0412 345 678",
                "liaison_email": "john@testcompany.com"
            },
            "traffic_company": {
                "name": "Traffic Management Co",
                "address": "456 Traffic Ave, Brisbane, QLD",
                "phone": "07 8765 4321",
                "liaison_name": "Jane Smith",
                "liaison_phone": "0498 765 432",
                "liaison_email": "jane@trafficco.com"
            },
            "work_details": {
                "work_type": "construction",
                "work_style": "mobile",
                "description": "Updated road construction work",
                "start_date": "2025-03-01",
                "end_date": "2025-03-10",
                "start_address": "Brisbane CBD, QLD",
                "end_address": "South Brisbane, QLD"
            },
            "road_occupancy": {
                "footpath": True,
                "left_shoulder": True,
                "left_lane": True,
                "center_lane": False,
                "right_lane": False,
                "right_shoulder": False,
                "median_strip": False,
                "complete_road_closure": False
            },
            "control_measures": {
                "twenty_min_rule": True,
                "signage": True,
                "speed_reduction": True,
                "detour": True
            },
            "road_data": {
                "traffic_volume": 20000,
                "road_classification": "Major Urban Road",
                "road_type": "Arterial",
                "governing_body": "Local Council",
                "workzone_size": 750.0
            },
            "devices": [],
            "map_center_lat": -27.4698,
            "map_center_lng": 153.0251,
            "map_zoom": 15
        }
        
        success, response = self.run_test(
            "Update Plan",
            "PUT",
            f"plans/{self.created_plan_id}",
            200,
            data=update_data
        )
        
        if success and response.get('plan_name') == 'Updated Test Traffic Plan':
            print(f"   Plan updated successfully")
            return True
        return False

    def test_pdf_generation(self):
        """Test PDF generation"""
        if not self.created_plan_id:
            print("❌ No plan ID available for PDF test")
            return False
            
        success, response = self.run_test(
            "Generate PDF",
            "GET",
            f"plans/{self.created_plan_id}/pdf",
            200
        )
        
        if success:
            print(f"   PDF generated successfully")
            return True
        return False

    def test_delete_plan(self):
        """Test deleting a plan"""
        if not self.created_plan_id:
            print("❌ No plan ID available for delete test")
            return False
            
        success, response = self.run_test(
            "Delete Plan",
            "DELETE",
            f"plans/{self.created_plan_id}",
            200
        )
        
        if success:
            print(f"   Plan deleted successfully")
            return True
        return False

    def test_get_all_risks(self):
        """Test getting all risks from risk registry"""
        success, response = self.run_test(
            "Get All Risks",
            "GET",
            "risks",
            200
        )
        
        if success and 'risks' in response and 'total_risks' in response:
            risks_count = len(response['risks'])
            total_count = response['total_risks']
            print(f"   Retrieved {risks_count} risks, total: {total_count}")
            
            # Verify expected structure
            if risks_count > 0:
                first_risk = response['risks'][0]
                required_fields = ['id', 'category', 'title', 'description', 'default_likelihood', 'default_consequence']
                missing_fields = [field for field in required_fields if field not in first_risk]
                if missing_fields:
                    print(f"   ⚠️ Missing fields in risk data: {missing_fields}")
                    return False
                
            # Check if we have the expected 25 risks
            if total_count == 25:
                print(f"   ✅ Correct number of risks (25) returned")
            else:
                print(f"   ⚠️ Expected 25 risks, got {total_count}")
                
            return True
        return False

    def test_get_risks_by_category(self):
        """Test getting risks filtered by category"""
        success, response = self.run_test(
            "Get Risks by Category (people)",
            "GET",
            "risks",
            200,
            data={"category": "people"}
        )
        
        if success and 'risks' in response:
            risks_count = len(response['risks'])
            print(f"   Retrieved {risks_count} risks in 'people' category")
            
            # Verify all returned risks are in the people category
            if risks_count > 0:
                people_risks = [r for r in response['risks'] if r.get('category') == 'people']
                if len(people_risks) == risks_count:
                    print(f"   ✅ All risks correctly filtered to 'people' category")
                    return True
                else:
                    print(f"   ❌ Category filtering failed - found mixed categories")
                    return False
            return True
        return False

    def test_get_risk_by_id(self):
        """Test getting a specific risk by ID"""
        success, response = self.run_test(
            "Get Risk by ID (risk_001)",
            "GET",
            "risks/risk_001",
            200
        )
        
        if success and 'id' in response:
            risk_id = response['id']
            risk_title = response.get('title', 'Unknown')
            print(f"   Retrieved risk: {risk_id} - {risk_title}")
            
            # Verify required fields
            required_fields = ['id', 'category', 'title', 'description', 'controls', 'references']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
                
            print(f"   ✅ Risk details complete with all required fields")
            return True
        return False

    def test_get_nonexistent_risk(self):
        """Test getting a non-existent risk (should return 404)"""
        success, response = self.run_test(
            "Get Non-existent Risk (should return 404)",
            "GET",
            "risks/risk_999",
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for non-existent risk")
            return True
        return False

    def test_calculate_risk_score(self):
        """Test risk score calculation endpoint"""
        test_data = {
            "likelihood": "possible",
            "consequence": "significant"
        }
        
        success, response = self.run_test(
            "Calculate Risk Score",
            "POST",
            "risks/calculate",
            200,
            data=test_data
        )
        
        if success and 'risk_score' in response:
            risk_score = response['risk_score']
            print(f"   Calculated risk score: {risk_score}")
            
            # Verify response structure
            expected_fields = ['score', 'rating', 'color', 'action']
            missing_fields = [field for field in expected_fields if field not in risk_score]
            if missing_fields:
                print(f"   ❌ Missing fields in risk score: {missing_fields}")
                return False
                
            print(f"   ✅ Risk calculation: {risk_score['rating']} (Score: {risk_score['score']})")
            return True
        return False

    def test_calculate_risk_invalid_data(self):
        """Test risk calculation with invalid data (should return 400)"""
        test_data = {
            "likelihood": "invalid_level",
            "consequence": "also_invalid"
        }
        
        success, response = self.run_test(
            "Calculate Risk with Invalid Data (should return 400)",
            "POST",
            "risks/calculate",
            400,
            data=test_data
        )
        
        if success:
            print(f"   ✅ Correctly returned 400 for invalid risk data")
            return True
        return False

def main():
    print("🚦 SafeRoadWorks API Testing Suite")
    print("=" * 50)
    
    tester = SafeRoadWorksAPITester()
    
    # Test sequence
    tests = [
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Geocoding API", tester.test_geocoding),
        ("Road Data API", tester.test_road_data),
        ("Create Traffic Plan", tester.test_create_plan),
        ("Get User Plans", tester.test_get_plans),
        ("Get Single Plan", tester.test_get_single_plan),
        ("Update Plan", tester.test_update_plan),
        ("PDF Generation", tester.test_pdf_generation),
        ("Delete Plan", tester.test_delete_plan)
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())