#!/usr/bin/env python3
"""
Quick test script for SA Sign Library endpoints only
"""
import requests
import sys
import json
from datetime import datetime, timezone

class SASignsAPITester:
    def __init__(self, base_url="https://traffix-manager-1.preview.emergentagent.com"):
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
                response = requests.get(url, headers=test_headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)

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

    def test_sa_signs_stats(self):
        """Test SA Signs statistics endpoint"""
        success, response = self.run_test(
            "SA Signs Statistics",
            "GET",
            "sa-signs/stats",
            200
        )
        
        if success:
            # Check required fields
            required_fields = ['total_core_devices', 'total_sa_signs', 'categories']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            total_sa_signs = response.get('total_sa_signs', 0)
            total_core_devices = response.get('total_core_devices', 0)
            categories_count = response.get('categories', 0)
            
            print(f"   Total SA signs: {total_sa_signs}")
            print(f"   Total core devices: {total_core_devices}")
            print(f"   Categories count: {categories_count}")
            
            # Verify expected 1203 SA signs
            if total_sa_signs == 1203:
                print(f"   ✅ Correct number of SA signs (1203)")
            else:
                print(f"   ⚠️ Expected 1203 SA signs, got {total_sa_signs}")
            
            return True
        return False

    def test_sa_signs_get_all_paginated(self):
        """Test getting all SA signs with pagination"""
        success, response = self.run_test(
            "SA Signs - Get All (Paginated)",
            "GET",
            "sa-signs",
            200,
            data={"limit": 10, "skip": 0}
        )
        
        if success:
            # Check response structure
            required_fields = ['total', 'skip', 'limit', 'signs']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            total = response.get('total', 0)
            signs = response.get('signs', [])
            
            print(f"   Total signs: {total}")
            print(f"   Returned signs: {len(signs)}")
            
            # Check sign structure if signs exist
            if signs:
                first_sign = signs[0]
                print(f"   First sign: {first_sign.get('code')} - {first_sign.get('description', 'No description')[:50]}...")
            
            return True
        return False

    def test_sa_signs_search_functionality(self):
        """Test SA signs search functionality"""
        success, response = self.run_test(
            "SA Signs - Search (warning)",
            "GET",
            "sa-signs/search",
            200,
            data={"q": "warning", "limit": 20}
        )
        
        if success:
            results = response.get('results', [])
            count = response.get('count', 0)
            
            print(f"   Results found: {count}")
            
            if results:
                first_result = results[0]
                print(f"   First result: {first_result.get('code')} - {first_result.get('description', 'No description')[:50]}...")
            
            return True
        return False

    def test_sa_signs_get_by_code_as1742(self):
        """Test getting specific SA sign by available code"""
        success, response = self.run_test(
            "SA Signs - Get by Available Code (13699)",
            "GET",
            "sa-signs/13699",
            200
        )
        
        if success:
            code = response.get('code')
            description = response.get('description')
            category = response.get('category')
            dimensions = response.get('dimensions', {})
            
            print(f"   Sign code: {code}")
            print(f"   Description: {description}")
            print(f"   Category: {category}")
            
            # Check dimensions structure if present
            if dimensions and 'width_mm' in dimensions and 'height_mm' in dimensions:
                width = dimensions.get('width_mm')
                height = dimensions.get('height_mm')
                print(f"   Dimensions: {width}mm x {height}mm")
            else:
                print(f"   ⚠️ Dimensions not available")
            
            return True
        return False

    def test_sa_signs_recommend_for_tmp(self):
        """Test SA signs recommendation for TMP"""
        request_data = {
            "work_type": "lane closure",
            "road_classification": "State Arterial Road"
        }
        
        success, response = self.run_test(
            "SA Signs - Recommend for TMP",
            "POST",
            "sa-signs/recommend",
            200,
            data=request_data
        )
        
        if success:
            if 'recommended_signs' in response:
                recommended_signs = response.get('recommended_signs', [])
                print(f"   Recommended signs: {len(recommended_signs)}")
                
                if recommended_signs:
                    first_sign = recommended_signs[0]
                    print(f"   First recommendation: {first_sign.get('code')} - {first_sign.get('description', 'No description')[:50]}...")
                
                return True
            else:
                print(f"   ❌ Missing 'recommended_signs' in response")
                return False
        return False

def main():
    print("🚦 SA Sign Library API Testing")
    print("=" * 50)
    
    tester = SASignsAPITester()
    
    # SA Sign Library tests
    tests = [
        ("SA Signs Statistics", tester.test_sa_signs_stats),
        ("SA Signs Get All Paginated", tester.test_sa_signs_get_all_paginated),
        ("SA Signs Search Functionality", tester.test_sa_signs_search_functionality),
        ("SA Signs Get by Available Code", tester.test_sa_signs_get_by_code_as1742),
        ("SA Signs Recommend for TMP", tester.test_sa_signs_recommend_for_tmp),
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
        print("🎉 All SA Sign Library API tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())