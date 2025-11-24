import requests
import sys
import json

class QuickBackendVerification:
    def __init__(self, base_url="https://roadworksai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

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

    def test_risks_endpoint(self):
        """Test GET /api/risks - Verify still returns 50 risks"""
        success, response = self.run_test(
            "GET /api/risks (should return 50 risks)",
            "GET",
            "risks",
            200
        )
        
        if success and 'risks' in response:
            risks_count = len(response['risks'])
            total_count = response.get('total_count', risks_count)
            print(f"   Retrieved {risks_count} risks, total: {total_count}")
            
            if total_count == 50:
                print(f"   ✅ Correct - API returns 50 risks as expected")
                return True
            else:
                print(f"   ❌ Expected 50 risks, got {total_count}")
                return False
        return False

    def test_devices_endpoint(self):
        """Test GET /api/devices - Verify device library endpoint works"""
        success, response = self.run_test(
            "GET /api/devices (device library)",
            "GET",
            "devices",
            200
        )
        
        if success and 'library' in response and 'categories' in response:
            categories = response['categories']
            total_devices = response.get('total_devices', 0)
            print(f"   Device categories: {len(categories)}")
            print(f"   Total devices: {total_devices}")
            print(f"   Categories: {', '.join(categories)}")
            
            if total_devices > 0 and len(categories) > 0:
                print(f"   ✅ Device library endpoint working correctly")
                return True
            else:
                print(f"   ❌ Device library appears empty")
                return False
        return False

    def test_geocode_endpoint(self):
        """Test POST /api/geocode - Test geocoding for Brisbane CBD, QLD"""
        # Note: The API uses GET method with query params, not POST
        success, response = self.run_test(
            "GET /api/geocode (Brisbane CBD, QLD)",
            "GET",
            "geocode",
            200,
            params={"address": "Brisbane CBD, QLD"}
        )
        
        if success and 'lat' in response and 'lng' in response:
            lat = response['lat']
            lng = response['lng']
            formatted_address = response.get('formatted_address', 'N/A')
            print(f"   Coordinates: {lat}, {lng}")
            print(f"   Formatted address: {formatted_address}")
            
            # Brisbane CBD should be around -27.47, 153.02
            if -27.5 < lat < -27.4 and 153.0 < lng < 153.1:
                print(f"   ✅ Geocoding working - coordinates are in Brisbane area")
                return True
            else:
                print(f"   ❌ Coordinates don't match Brisbane CBD area")
                return False
        return False

    def test_road_data_endpoint(self):
        """Test GET /api/road-data - Test road data endpoint"""
        success, response = self.run_test(
            "GET /api/road-data (Brisbane CBD to South Brisbane)",
            "GET",
            "road-data",
            200,
            params={
                "start_address": "Brisbane CBD, QLD",
                "end_address": "South Brisbane, QLD"
            }
        )
        
        if success and 'workzone_size' in response:
            workzone_size = response['workzone_size']
            road_classification = response.get('road_classification', 'N/A')
            traffic_volume = response.get('traffic_volume', 'N/A')
            governing_body = response.get('governing_body', 'N/A')
            
            print(f"   Workzone size: {workzone_size} meters")
            print(f"   Road classification: {road_classification}")
            print(f"   Traffic volume: {traffic_volume}")
            print(f"   Governing body: {governing_body}")
            
            if workzone_size > 0:
                print(f"   ✅ Road data endpoint working correctly")
                return True
            else:
                print(f"   ❌ Invalid workzone size returned")
                return False
        return False

def main():
    print("🚦 Quick Backend Verification Test")
    print("Testing after auto-placement duplicate function fix")
    print("=" * 60)
    
    tester = QuickBackendVerification()
    
    # Test the specific endpoints requested
    tests = [
        ("GET /api/risks", tester.test_risks_endpoint),
        ("GET /api/devices", tester.test_devices_endpoint), 
        ("GET /api/geocode", tester.test_geocode_endpoint),
        ("GET /api/road-data", tester.test_road_data_endpoint)
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend endpoints operational!")
        print("✅ Backend is working correctly after duplicate function fix")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        print("❌ Backend issues detected - needs investigation")
        return 1

if __name__ == "__main__":
    sys.exit(main())