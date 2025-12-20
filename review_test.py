#!/usr/bin/env python3
"""
Traffic Management Plan Backend Review Test
Testing core existing functionality after server.py restore
"""

import requests
import sys
import json
from datetime import datetime, timezone

class TMPBackendReviewTester:
    def __init__(self, base_url="https://tmp-generator-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_plan_id = None
        self.failed_tests = []

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== 1. AUTHENTICATION TESTS ===")
        
        # Test registration
        test_email = f"review_test_{datetime.now().strftime('%H%M%S')}@example.com"
        register_data = {
            "email": test_email,
            "password": "ReviewTest123!",
            "company_name": "Review Test Company"
        }
        
        success, response = self.run_test(
            "POST /auth/register",
            "POST",
            "auth/register",
            200,
            data=register_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   ✅ User registered: {test_email}")
        else:
            print("   ❌ Registration failed")
            return False
        
        # Test login with same credentials
        login_data = {
            "email": test_email,
            "password": "ReviewTest123!"
        }
        
        success, response = self.run_test(
            "POST /auth/login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            print(f"   ✅ Login successful")
            return True
        else:
            print("   ❌ Login failed")
            return False

    def test_plans_crud(self):
        """Test Plans CRUD operations"""
        print("\n=== 2. PLANS CRUD TESTS ===")
        
        # Create plan
        plan_data = {
            "plan_name": "Review Test Plan",
            "work_details": {
                "work_type": "construction",
                "work_style": "static",
                "description": "Review test construction work",
                "start_date": "2025-02-01",
                "end_date": "2025-02-05",
                "start_address": "Brisbane CBD, QLD",
                "end_address": "South Brisbane, QLD"
            }
        }
        
        success, response = self.run_test(
            "POST /plans",
            "POST",
            "plans",
            200,
            data=plan_data
        )
        
        if success and 'id' in response:
            self.created_plan_id = response['id']
            print(f"   ✅ Plan created with ID: {self.created_plan_id}")
        else:
            print("   ❌ Plan creation failed")
            return False
        
        # Get plans list
        success, response = self.run_test(
            "GET /plans",
            "GET",
            "plans",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✅ Retrieved {len(response)} plans")
        else:
            print("   ❌ Get plans failed")
            return False
        
        # Get single plan
        success, response = self.run_test(
            f"GET /plans/{self.created_plan_id}",
            "GET",
            f"plans/{self.created_plan_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"   ✅ Retrieved plan: {response.get('plan_name', 'Unknown')}")
        else:
            print("   ❌ Get single plan failed")
            return False
        
        # Update plan
        update_data = {
            "plan_name": "Updated Review Test Plan",
            "work_details": {
                "work_type": "maintenance",
                "work_style": "mobile",
                "description": "Updated review test work",
                "start_date": "2025-03-01",
                "end_date": "2025-03-10",
                "start_address": "Brisbane CBD, QLD",
                "end_address": "South Brisbane, QLD"
            }
        }
        
        success, response = self.run_test(
            f"PUT /plans/{self.created_plan_id}",
            "PUT",
            f"plans/{self.created_plan_id}",
            200,
            data=update_data
        )
        
        if success and response.get('plan_name') == 'Updated Review Test Plan':
            print(f"   ✅ Plan updated successfully")
        else:
            print("   ❌ Plan update failed")
            return False
        
        # Delete plan
        success, response = self.run_test(
            f"DELETE /plans/{self.created_plan_id}",
            "DELETE",
            f"plans/{self.created_plan_id}",
            200
        )
        
        if success:
            print(f"   ✅ Plan deleted successfully")
            self.created_plan_id = None
            return True
        else:
            print("   ❌ Plan deletion failed")
            return False

    def test_core_analysis_endpoints(self):
        """Test core analysis endpoints"""
        print("\n=== 3. CORE ANALYSIS ENDPOINTS ===")
        
        # Test geocoding
        success, response = self.run_test(
            "GET /geocode",
            "GET",
            "geocode",
            200,
            data={"address": "Brisbane CBD, QLD"}
        )
        
        if success and 'lat' in response and 'lng' in response:
            print(f"   ✅ Geocoding: {response['lat']}, {response['lng']}")
            brisbane_coords = {"lat": response['lat'], "lng": response['lng']}
        else:
            print("   ❌ Geocoding failed")
            return False
        
        # Test road-data
        success, response = self.run_test(
            "GET /road-data",
            "GET",
            "road-data",
            200,
            data={
                "start_address": "Queen St, Brisbane QLD",
                "end_address": "George St, Brisbane QLD"
            }
        )
        
        if success and 'workzone_size' in response:
            print(f"   ✅ Road data: {response['workzone_size']}m workzone")
        else:
            print("   ❌ Road data failed")
            return False
        
        # Test traffic-assessment
        success, response = self.run_test(
            "GET /traffic-assessment",
            "GET",
            "traffic-assessment",
            200,
            data={
                "lat": brisbane_coords["lat"],
                "lng": brisbane_coords["lng"],
                "address": "Queen Street, Brisbane QLD"
            }
        )
        
        if success and 'aadt' in response:
            print(f"   ✅ Traffic assessment: AADT {response['aadt']}")
        else:
            print("   ❌ Traffic assessment failed")
            return False
        
        # Test site-assessment
        success, response = self.run_test(
            "GET /site-assessment",
            "GET",
            "site-assessment",
            200,
            data={
                "lat": brisbane_coords["lat"],
                "lng": brisbane_coords["lng"],
                "address": "Queen Street, Brisbane QLD"
            }
        )
        
        if success and 'road_geometry' in response:
            print(f"   ✅ Site assessment: {response['road_geometry']}")
            return True
        else:
            print("   ❌ Site assessment failed")
            return False

    def test_comprehensive_auto_populate(self):
        """Test comprehensive auto-populate endpoint"""
        print("\n=== 4. COMPREHENSIVE AUTO-POPULATE ===")
        
        success, response = self.run_test(
            "GET /comprehensive-auto-populate",
            "GET",
            "comprehensive-auto-populate",
            200,
            data={
                "lat": -27.4698,
                "lng": 153.0251,
                "start_address": "Queen Street, Brisbane QLD",
                "end_address": "George Street, Brisbane QLD",
                "work_type": "construction"
            }
        )
        
        if success:
            # Count data categories
            data_categories = len([k for k in response.keys() if k not in ['status', 'message']])
            print(f"   ✅ Comprehensive auto-populate: {data_categories} data categories")
            
            # Check for key fields
            key_fields = ['road_data', 'traffic_assessment', 'site_assessment']
            present_fields = [field for field in key_fields if field in response]
            print(f"   ✅ Key fields present: {present_fields}")
            
            return len(present_fields) >= 2
        else:
            print("   ❌ Comprehensive auto-populate failed")
            return False

    def test_pdf_generation(self):
        """Test PDF generation"""
        print("\n=== 5. PDF GENERATION ===")
        
        # First create a plan for PDF generation
        plan_data = {
            "plan_name": "PDF Test Plan",
            "work_details": {
                "work_type": "construction",
                "work_style": "static",
                "description": "PDF test construction work",
                "start_date": "2025-02-01",
                "end_date": "2025-02-05",
                "start_address": "Brisbane CBD, QLD",
                "end_address": "South Brisbane, QLD"
            }
        }
        
        success, response = self.run_test(
            "Create Plan for PDF Test",
            "POST",
            "plans",
            200,
            data=plan_data
        )
        
        if success and 'id' in response:
            plan_id = response['id']
            print(f"   ✅ Created plan for PDF test: {plan_id}")
        else:
            print("   ❌ Failed to create plan for PDF test")
            return False
        
        # Test PDF generation
        success, response = self.run_test(
            f"GET /plans/{plan_id}/pdf",
            "GET",
            f"plans/{plan_id}/pdf",
            200
        )
        
        # Clean up
        self.run_test(
            "Delete PDF Test Plan",
            "DELETE",
            f"plans/{plan_id}",
            200
        )
        
        if success:
            print(f"   ✅ PDF generation successful")
            return True
        else:
            print("   ❌ PDF generation failed")
            return False

    def run_review_tests(self):
        """Run all review tests"""
        print("🔍 TRAFFIC MANAGEMENT PLAN BACKEND REVIEW")
        print("=" * 60)
        print("Testing core existing functionality after server.py restore")
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        
        test_results = []
        
        # Run all test categories
        test_results.append(("Authentication", self.test_authentication()))
        test_results.append(("Plans CRUD", self.test_plans_crud()))
        test_results.append(("Core Analysis", self.test_core_analysis_endpoints()))
        test_results.append(("Auto-Populate", self.test_comprehensive_auto_populate()))
        test_results.append(("PDF Generation", self.test_pdf_generation()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REVIEW TEST SUMMARY")
        print("=" * 60)
        
        passed_categories = 0
        for category, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{category:20} {status}")
            if result:
                passed_categories += 1
        
        print(f"\nOverall Results:")
        print(f"  Categories: {passed_categories}/{len(test_results)} passed")
        print(f"  Individual Tests: {self.tests_passed}/{self.tests_run} passed")
        print(f"  Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for failed_test in self.failed_tests:
                print(f"  - {failed_test}")
        
        if passed_categories == len(test_results):
            print("\n🎉 ALL REVIEW TESTS PASSED!")
            print("✅ Core backend functionality is intact after server.py restore")
            return 0
        else:
            print(f"\n⚠️  {len(test_results) - passed_categories} test categories failed")
            print("❌ Backend issues detected - see failed tests above")
            return 1

if __name__ == "__main__":
    tester = TMPBackendReviewTester()
    exit_code = tester.run_review_tests()
    sys.exit(exit_code)