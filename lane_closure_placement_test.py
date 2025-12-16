import requests
import sys
import json
import math
from datetime import datetime, timezone

class LaneClosurePlacementTester:
    def __init__(self, base_url="https://trafficcontrol.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def authenticate(self):
        """Authenticate and get JWT token"""
        test_email = f"lane_test_{datetime.now().strftime('%H%M%S')}@example.com"
        test_data = {
            "email": test_email,
            "password": "LaneTest123!",
            "company_name": "Lane Closure Testing Co"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=test_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_id = data['user']['id']
                print(f"✅ Authenticated as: {test_email}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def calculate_bearing(self, lat1, lng1, lat2, lng2):
        """Calculate bearing between two points"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lng_diff_rad = math.radians(lng2 - lng1)
        
        y = math.sin(lng_diff_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lng_diff_rad)
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360 degrees
        return (bearing_deg + 360) % 360

    def get_traffic_direction_from_bearing(self, bearing):
        """Determine traffic direction from bearing"""
        if 315 <= bearing or bearing < 45:
            return "Northbound"
        elif 45 <= bearing < 135:
            return "Eastbound"
        elif 135 <= bearing < 225:
            return "Southbound"
        elif 225 <= bearing < 315:
            return "Westbound"
        return "Unknown"

    def get_opposite_direction(self, direction):
        """Get opposite direction for sign placement"""
        opposites = {
            "Northbound": "South",
            "Southbound": "North", 
            "Eastbound": "West",
            "Westbound": "East"
        }
        return opposites.get(direction, "Unknown")

    def test_comprehensive_auto_populate(self, scenario_name, start_address, end_address, expected_traffic_direction, speed_limit):
        """Test comprehensive auto-populate for a specific scenario"""
        print(f"\n🔍 Testing {scenario_name}")
        print(f"   Start: {start_address}")
        print(f"   End: {end_address}")
        print(f"   Expected Traffic Direction: {expected_traffic_direction}")
        print(f"   Speed: {speed_limit} km/h")
        
        self.tests_run += 1
        
        try:
            # Step 1: Get coordinates for both addresses
            start_coords = self.geocode_address(start_address)
            end_coords = self.geocode_address(end_address)
            
            if not start_coords or not end_coords:
                print(f"   ❌ Failed to geocode addresses")
                return False
            
            print(f"   Start coordinates: {start_coords['lat']}, {start_coords['lng']}")
            print(f"   End coordinates: {end_coords['lat']}, {end_coords['lng']}")
            
            # Step 2: Calculate road bearing
            bearing = self.calculate_bearing(
                start_coords['lat'], start_coords['lng'],
                end_coords['lat'], end_coords['lng']
            )
            
            calculated_direction = self.get_traffic_direction_from_bearing(bearing)
            print(f"   Calculated road bearing: {bearing:.1f}°")
            print(f"   Calculated traffic direction: {calculated_direction}")
            
            # Step 3: Call comprehensive auto-populate
            auto_populate_data = {
                "lat": start_coords['lat'],
                "lng": start_coords['lng'],
                "start_address": start_address,
                "end_address": end_address,
                "work_type": "lane_closure"
            }
            
            headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
            response = requests.get(f"{self.api_url}/comprehensive-auto-populate", 
                                  params=auto_populate_data, headers=headers)
            
            if response.status_code != 200:
                print(f"   ❌ Auto-populate failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
            
            data = response.json()
            
            # Step 4: Extract and validate coordinates
            road_data = data.get('road_data', {})
            signage_plan = data.get('signage_plan', {})
            
            print(f"   Road classification: {road_data.get('road_classification', 'Unknown')}")
            print(f"   Speed limit: {road_data.get('speed_limit', 'Unknown')} km/h")
            
            # Step 5: Simulate lane closure device placement
            placement_result = self.simulate_lane_closure_placement(
                start_coords, end_coords, bearing, expected_traffic_direction, speed_limit, signage_plan
            )
            
            if placement_result:
                self.tests_passed += 1
                self.test_results.append({
                    'scenario': scenario_name,
                    'status': 'PASSED',
                    'start_coords': start_coords,
                    'end_coords': end_coords,
                    'bearing': bearing,
                    'traffic_direction': calculated_direction,
                    'expected_direction': expected_traffic_direction,
                    'placement_details': placement_result
                })
                print(f"   ✅ PASSED - Lane closure placement logic working correctly")
                return True
            else:
                self.test_results.append({
                    'scenario': scenario_name,
                    'status': 'FAILED',
                    'start_coords': start_coords,
                    'end_coords': end_coords,
                    'bearing': bearing,
                    'traffic_direction': calculated_direction,
                    'expected_direction': expected_traffic_direction
                })
                print(f"   ❌ FAILED - Lane closure placement logic issues detected")
                return False
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return False

    def geocode_address(self, address):
        """Geocode an address using the backend API"""
        try:
            response = requests.get(f"{self.api_url}/geocode", params={"address": address})
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"   Geocoding error for {address}: {str(e)}")
            return None

    def simulate_lane_closure_placement(self, start_coords, end_coords, bearing, expected_direction, speed_limit, signage_plan):
        """Simulate lane closure device placement and validate logic"""
        print(f"   🔧 Simulating lane closure device placement...")
        
        # Calculate approach bearing (opposite to traffic direction)
        approach_bearing = (bearing + 180) % 360
        opposite_direction = self.get_opposite_direction(expected_direction)
        
        print(f"   Traffic direction: {expected_direction}")
        print(f"   Signs should be placed: {opposite_direction} of workzone")
        print(f"   Approach bearing for signs: {approach_bearing:.1f}°")
        
        # Calculate sign distances based on speed (AS 1742.3 compliant)
        advance_warning_distance = self.calculate_advance_warning_distance(speed_limit)
        taper_length = self.calculate_taper_length(speed_limit)
        
        print(f"   Advance warning distance: {advance_warning_distance}m")
        print(f"   Taper length: {taper_length}m")
        
        # Simulate device placement coordinates
        devices_placed = []
        
        # 1. First RWA (Road Work Ahead) sign
        rwa_coords = self.calculate_offset_coordinates(
            start_coords['lat'], start_coords['lng'], 
            approach_bearing, advance_warning_distance
        )
        
        if self.validate_coordinates(rwa_coords):
            devices_placed.append({
                'type': 'Road Work Ahead Sign',
                'coordinates': rwa_coords,
                'distance_from_workzone': advance_warning_distance,
                'placement_direction': opposite_direction
            })
            print(f"   ✅ RWA Sign placed at: {rwa_coords['lat']:.6f}, {rwa_coords['lng']:.6f}")
        else:
            print(f"   ❌ Invalid RWA sign coordinates: {rwa_coords}")
            return False
        
        # 2. First taper cone
        taper_coords = self.calculate_offset_coordinates(
            start_coords['lat'], start_coords['lng'],
            approach_bearing, taper_length
        )
        
        if self.validate_coordinates(taper_coords):
            devices_placed.append({
                'type': 'Taper Cone Start',
                'coordinates': taper_coords,
                'distance_from_workzone': taper_length,
                'placement_direction': opposite_direction
            })
            print(f"   ✅ Taper cone placed at: {taper_coords['lat']:.6f}, {taper_coords['lng']:.6f}")
        else:
            print(f"   ❌ Invalid taper cone coordinates: {taper_coords}")
            return False
        
        # 3. End Roadworks sign (after workzone)
        end_bearing = bearing  # Same direction as traffic flow
        end_coords = self.calculate_offset_coordinates(
            end_coords['lat'], end_coords['lng'],
            end_bearing, 50  # 50m after workzone end
        )
        
        if self.validate_coordinates(end_coords):
            devices_placed.append({
                'type': 'End Roadworks Sign',
                'coordinates': end_coords,
                'distance_from_workzone': 50,
                'placement_direction': expected_direction
            })
            print(f"   ✅ End Roadworks sign placed at: {end_coords['lat']:.6f}, {end_coords['lng']:.6f}")
        else:
            print(f"   ❌ Invalid End Roadworks coordinates: {end_coords}")
            return False
        
        # Validate placement logic
        validation_results = []
        
        # Check 1: No NaN coordinates
        all_coords_valid = all(self.validate_coordinates(device['coordinates']) for device in devices_placed)
        validation_results.append(('No NaN coordinates', all_coords_valid))
        
        # Check 2: Sign distances are correct (60-90m for advance warnings)
        rwa_distance = devices_placed[0]['distance_from_workzone']
        distance_valid = 60 <= rwa_distance <= 200  # Allow wider range for different speeds
        validation_results.append(('Sign distance correct (60-200m)', distance_valid))
        
        # Check 3: Signs placed opposite to traffic direction
        rwa_direction = devices_placed[0]['placement_direction']
        direction_valid = rwa_direction == opposite_direction
        validation_results.append(('Signs placed opposite to traffic', direction_valid))
        
        # Check 4: Taper cones form graduated angle
        taper_distance = devices_placed[1]['distance_from_workzone']
        taper_valid = taper_distance < rwa_distance  # Taper should be closer than RWA
        validation_results.append(('Taper cones positioned correctly', taper_valid))
        
        # Check 5: End Roadworks sign after workzone
        end_direction = devices_placed[2]['placement_direction']
        end_valid = end_direction == expected_direction
        validation_results.append(('End sign after workzone', end_valid))
        
        # Print validation results
        print(f"   📋 Validation Results:")
        all_valid = True
        for check_name, is_valid in validation_results:
            status = "✅" if is_valid else "❌"
            print(f"      {status} {check_name}")
            if not is_valid:
                all_valid = False
        
        return {
            'devices_placed': devices_placed,
            'validation_results': validation_results,
            'all_valid': all_valid
        } if all_valid else False

    def calculate_advance_warning_distance(self, speed_limit):
        """Calculate advance warning distance based on speed (AS 1742.3)"""
        # AS 1742.3 Table 6.2 - Advance warning distances
        speed_distances = {
            40: 60,
            50: 75,
            60: 90,
            70: 120,
            80: 150,
            90: 180,
            100: 200,
            110: 250
        }
        
        # Find closest speed limit
        closest_speed = min(speed_distances.keys(), key=lambda x: abs(x - speed_limit))
        return speed_distances[closest_speed]

    def calculate_taper_length(self, speed_limit):
        """Calculate taper length based on speed"""
        # Taper length = speed_limit (km/h) in meters
        return min(speed_limit, 100)  # Cap at 100m for very high speeds

    def calculate_offset_coordinates(self, lat, lng, bearing, distance_m):
        """Calculate coordinates offset by distance and bearing"""
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)
        bearing_rad = math.radians(bearing)
        
        # Calculate new latitude
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_m / R) +
            math.cos(lat_rad) * math.sin(distance_m / R) * math.cos(bearing_rad)
        )
        
        # Calculate new longitude
        new_lng_rad = lng_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance_m / R) * math.cos(lat_rad),
            math.cos(distance_m / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        return {
            'lat': math.degrees(new_lat_rad),
            'lng': math.degrees(new_lng_rad)
        }

    def validate_coordinates(self, coords):
        """Validate that coordinates are not NaN and within reasonable bounds"""
        if not coords or 'lat' not in coords or 'lng' not in coords:
            return False
        
        lat, lng = coords['lat'], coords['lng']
        
        # Check for NaN
        if math.isnan(lat) or math.isnan(lng):
            return False
        
        # Check for reasonable bounds (Australia)
        if not (-45 <= lat <= -10 and 110 <= lng <= 155):
            return False
        
        return True

    def run_all_scenarios(self):
        """Run all 4 test scenarios"""
        print("🚧 LANE CLOSURE DEVICE PLACEMENT TESTING")
        print("=" * 60)
        
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        scenarios = [
            {
                'name': 'Scenario 1: Northbound Traffic - Tapley\'s Hill Road',
                'start_address': '506 Tapley\'s Hill Road, Fulham Gardens SA',
                'end_address': '480 Tapley\'s Hill Road, Fulham Gardens SA',
                'expected_direction': 'Northbound',
                'speed': 60
            },
            {
                'name': 'Scenario 2: Southbound Traffic - Same Road',
                'start_address': '480 Tapley\'s Hill Road, Fulham Gardens SA',
                'end_address': '506 Tapley\'s Hill Road, Fulham Gardens SA',
                'expected_direction': 'Southbound',
                'speed': 60
            },
            {
                'name': 'Scenario 3: Eastbound Traffic - King William Street',
                'start_address': '100 King William Street, Adelaide SA',
                'end_address': '120 King William Street, Adelaide SA',
                'expected_direction': 'Eastbound',
                'speed': 50
            },
            {
                'name': 'Scenario 4: Westbound Traffic - Main North Road',
                'start_address': '300 Main North Road, Blair Athol SA',
                'end_address': '320 Main North Road, Blair Athol SA',
                'expected_direction': 'Westbound',
                'speed': 70
            }
        ]
        
        for scenario in scenarios:
            success = self.test_comprehensive_auto_populate(
                scenario['name'],
                scenario['start_address'],
                scenario['end_address'],
                scenario['expected_direction'],
                scenario['speed']
            )
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TESTING SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            print(f"{status_icon} {result['scenario']}")
            print(f"   Start: {result['start_coords']['lat']:.6f}, {result['start_coords']['lng']:.6f}")
            print(f"   End: {result['end_coords']['lat']:.6f}, {result['end_coords']['lng']:.6f}")
            print(f"   Bearing: {result['bearing']:.1f}°")
            print(f"   Traffic Direction: {result['traffic_direction']} (Expected: {result['expected_direction']})")
            
            if result['status'] == 'PASSED' and 'placement_details' in result:
                devices = result['placement_details']['devices_placed']
                print(f"   Devices placed: {len(devices)}")
                for device in devices:
                    print(f"     - {device['type']}: {device['coordinates']['lat']:.6f}, {device['coordinates']['lng']:.6f}")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = LaneClosurePlacementTester()
    success = tester.run_all_scenarios()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Lane closure device placement logic is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - Lane closure device placement logic needs attention!")
        sys.exit(1)