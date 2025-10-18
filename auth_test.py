#!/usr/bin/env python3
"""
Authentication Endpoints Testing
Test authentication endpoints to verify they return correct data format.
"""

import requests
import json
import jwt
from datetime import datetime

class AuthenticationTester:
    def __init__(self, base_url="https://traffic-plan-genius.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
        
        if details:
            print(f"   {details}")
        print()

    def validate_jwt_token(self, token):
        """Validate JWT token format without verification"""
        try:
            # Decode without verification to check structure
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Check required fields
            required_fields = ['user_id', 'email', 'exp']
            missing_fields = [field for field in required_fields if field not in decoded]
            
            if missing_fields:
                return False, f"Missing JWT fields: {missing_fields}"
            
            return True, f"Valid JWT with fields: {list(decoded.keys())}"
        except Exception as e:
            return False, f"Invalid JWT format: {str(e)}"

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("🔍 Testing User Registration Endpoint")
        
        # Generate unique email for this test
        timestamp = datetime.now().strftime('%H%M%S%f')
        test_email = f"test_{timestamp}@example.com"
        
        # Test data as specified in review request
        test_data = {
            "email": test_email,
            "password": "test123",
            "company_name": "Test Co"
        }
        
        try:
            url = f"{self.api_url}/auth/register"
            headers = {'Content-Type': 'application/json'}
            
            print(f"   POST {url}")
            print(f"   Body: {json.dumps(test_data, indent=2)}")
            
            response = requests.post(url, json=test_data, headers=headers)
            
            print(f"   Status Code: {response.status_code}")
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Registration Status Code", False, f"Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            # Parse response
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                self.log_test("Registration Response Format", False, "Response is not valid JSON")
                return False
            
            # Validate response structure
            success = True
            details = []
            
            # Check for "token" field
            if "token" not in response_data:
                success = False
                details.append("Missing 'token' field")
            else:
                # Validate JWT token format
                token_valid, token_msg = self.validate_jwt_token(response_data["token"])
                if token_valid:
                    details.append(f"✅ Token: {token_msg}")
                else:
                    success = False
                    details.append(f"❌ Token: {token_msg}")
            
            # Check for "user" object
            if "user" not in response_data:
                success = False
                details.append("Missing 'user' object")
            else:
                user_obj = response_data["user"]
                
                # Check user object fields
                required_user_fields = ["id", "email", "company_name"]
                missing_user_fields = [field for field in required_user_fields if field not in user_obj]
                
                if missing_user_fields:
                    success = False
                    details.append(f"Missing user fields: {missing_user_fields}")
                else:
                    details.append(f"✅ User object has all required fields: {required_user_fields}")
                    
                    # Validate field values
                    if user_obj.get("email") == test_email:
                        details.append(f"✅ Email matches: {test_email}")
                    else:
                        success = False
                        details.append(f"❌ Email mismatch: expected {test_email}, got {user_obj.get('email')}")
                    
                    if user_obj.get("company_name") == "Test Co":
                        details.append(f"✅ Company name matches: Test Co")
                    else:
                        success = False
                        details.append(f"❌ Company name mismatch: expected 'Test Co', got {user_obj.get('company_name')}")
                    
                    if user_obj.get("id"):
                        details.append(f"✅ User ID present: {user_obj.get('id')}")
                    else:
                        success = False
                        details.append("❌ User ID missing or empty")
            
            self.log_test("User Registration", success, "; ".join(details))
            
            # Store credentials for login test
            if success:
                self.test_email = test_email
                self.test_password = "test123"
                self.registered_token = response_data.get("token")
                return True
            
            return False
            
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False

    def test_user_login(self):
        """Test user login endpoint"""
        print("🔍 Testing User Login Endpoint")
        
        # Use credentials from registration test
        if not hasattr(self, 'test_email'):
            self.log_test("User Login", False, "No registered user available for login test")
            return False
        
        # Test data as specified in review request
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            url = f"{self.api_url}/auth/login"
            headers = {'Content-Type': 'application/json'}
            
            print(f"   POST {url}")
            print(f"   Body: {json.dumps(login_data, indent=2)}")
            
            response = requests.post(url, json=login_data, headers=headers)
            
            print(f"   Status Code: {response.status_code}")
            
            # Check status code
            if response.status_code != 200:
                self.log_test("Login Status Code", False, f"Expected 200, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            # Parse response
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                self.log_test("Login Response Format", False, "Response is not valid JSON")
                return False
            
            # Validate response structure (same as registration)
            success = True
            details = []
            
            # Check for "token" field
            if "token" not in response_data:
                success = False
                details.append("Missing 'token' field")
            else:
                # Validate JWT token format
                token_valid, token_msg = self.validate_jwt_token(response_data["token"])
                if token_valid:
                    details.append(f"✅ Token: {token_msg}")
                else:
                    success = False
                    details.append(f"❌ Token: {token_msg}")
            
            # Check for "user" object
            if "user" not in response_data:
                success = False
                details.append("Missing 'user' object")
            else:
                user_obj = response_data["user"]
                
                # Check user object fields
                required_user_fields = ["id", "email", "company_name"]
                missing_user_fields = [field for field in required_user_fields if field not in user_obj]
                
                if missing_user_fields:
                    success = False
                    details.append(f"Missing user fields: {missing_user_fields}")
                else:
                    details.append(f"✅ User object has all required fields: {required_user_fields}")
                    
                    # Validate field values
                    if user_obj.get("email") == self.test_email:
                        details.append(f"✅ Email matches: {self.test_email}")
                    else:
                        success = False
                        details.append(f"❌ Email mismatch: expected {self.test_email}, got {user_obj.get('email')}")
                    
                    if user_obj.get("company_name") == "Test Co":
                        details.append(f"✅ Company name matches: Test Co")
                    else:
                        success = False
                        details.append(f"❌ Company name mismatch: expected 'Test Co', got {user_obj.get('company_name')}")
                    
                    if user_obj.get("id"):
                        details.append(f"✅ User ID present: {user_obj.get('id')}")
                    else:
                        success = False
                        details.append("❌ User ID missing or empty")
            
            self.log_test("User Login", success, "; ".join(details))
            return success
            
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        print("🔍 Testing Invalid Login (should return 401)")
        
        # Test data with invalid credentials
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        try:
            url = f"{self.api_url}/auth/login"
            headers = {'Content-Type': 'application/json'}
            
            print(f"   POST {url}")
            print(f"   Body: {json.dumps(login_data, indent=2)}")
            
            response = requests.post(url, json=login_data, headers=headers)
            
            print(f"   Status Code: {response.status_code}")
            
            # Should return 401 for invalid credentials
            if response.status_code == 401:
                self.log_test("Invalid Login Returns 401", True, "Correctly returned 401 for invalid credentials")
                return True
            else:
                self.log_test("Invalid Login Returns 401", False, f"Expected 401, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Invalid Login Returns 401", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚦 Authentication Endpoints Testing Suite")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print()
        
        # Run tests in sequence
        tests = [
            self.test_user_registration,
            self.test_user_login,
            self.test_invalid_login
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                print()
        
        # Print final results
        print("=" * 60)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All authentication tests passed!")
            print()
            print("✅ Success Criteria Met:")
            print("   ✅ Both endpoints return 200 OK")
            print("   ✅ Response has 'token' field")
            print("   ✅ Response has 'user' object with id, email, company_name")
            print("   ✅ Token is valid JWT format")
            return True
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())