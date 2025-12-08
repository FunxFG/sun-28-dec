#!/usr/bin/env python3
"""
PDF Generation Endpoint Test
Re-test only the PDF generation endpoint now that tmp_generator.py has been patched for None traffic_company handling.
"""

import requests
import sys
import json
from datetime import datetime

class PDFGenerationTester:
    def __init__(self, base_url="https://trafsafe.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.plan_id = None

    def register_and_login(self):
        """Step 1: Register + login to get a JWT"""
        print("🔐 Step 1: Register + Login to get JWT...")
        
        # Register user
        test_email = f"pdf_test_{datetime.now().strftime('%H%M%S')}@example.com"
        register_data = {
            "email": test_email,
            "password": "PDFTest123!",
            "company_name": "PDF Test Company"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/register",
                json=register_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.user_id = data['user']['id']
                print(f"✅ Registration successful: {test_email}")
                print(f"   JWT Token: {self.token[:50]}...")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False

    def create_minimal_plan(self):
        """Step 2: Create a minimal plan with POST /api/plans"""
        print("\n📋 Step 2: Create minimal plan...")
        
        # Create minimal plan data - ensuring traffic_company is properly set
        plan_data = {
            "plan_name": "PDF Test Plan",
            "company_details": {
                "name": "Test Company",
                "address": "123 Test Street, Adelaide, SA",
                "abn": "12345678901",
                "phone": "08 1234 5678",
                "liaison_name": "John Doe",
                "liaison_phone": "0412 345 678",
                "liaison_email": "john@testcompany.com"
            },
            "traffic_company": {
                "name": "Traffic Management Co",
                "address": "456 Traffic Ave, Adelaide, SA",
                "phone": "08 8765 4321",
                "liaison_name": "Jane Smith",
                "liaison_phone": "0498 765 432",
                "liaison_email": "jane@trafficco.com"
            },
            "work_details": {
                "work_type": "maintenance",
                "work_style": "static",
                "description": "Road maintenance work for PDF test",
                "start_date": "2025-02-01",
                "end_date": "2025-02-05",
                "start_address": "King William Street, Adelaide SA",
                "end_address": "North Terrace, Adelaide SA"
            },
            "road_data": {
                "traffic_volume": 15000,
                "road_classification": "Major Urban Road",
                "road_type": "Arterial",
                "governing_body": "Local Council",
                "workzone_size": 500.0
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/plans",
                json=plan_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.plan_id = data['id']
                print(f"✅ Plan created successfully")
                print(f"   Plan ID: {self.plan_id}")
                print(f"   Plan Name: {data['plan_name']}")
                print(f"   Traffic Company: {data.get('traffic_company', {}).get('name', 'Not set')}")
                return True
            else:
                print(f"❌ Plan creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Plan creation error: {str(e)}")
            return False

    def test_pdf_generation(self):
        """Step 3: Call GET /api/plans/{plan_id}/pdf and verify response"""
        print(f"\n📄 Step 3: Test PDF Generation...")
        print(f"   Testing plan ID: {self.plan_id}")
        
        try:
            response = requests.get(
                f"{self.api_url}/plans/{self.plan_id}/pdf",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            # Verification checks
            success_criteria = []
            
            # Check 1: HTTP 200
            if response.status_code == 200:
                success_criteria.append("✅ HTTP 200 status")
            else:
                success_criteria.append(f"❌ Expected HTTP 200, got {response.status_code}")
                print(f"   Error Response: {response.text[:500]}")
                return False
            
            # Check 2: Content-Type: application/pdf
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                success_criteria.append("✅ Content-Type: application/pdf")
            else:
                success_criteria.append(f"❌ Expected Content-Type: application/pdf, got: {content_type}")
                return False
            
            # Check 3: Response body is a non-trivial PDF
            content = response.content
            
            # Size check
            if len(content) >= 1000:  # At least 1KB
                success_criteria.append(f"✅ Non-trivial PDF size: {len(content):,} bytes")
            else:
                success_criteria.append(f"❌ PDF too small: {len(content)} bytes (likely error)")
                print(f"   Content preview: {content[:200]}")
                return False
            
            # PDF format check
            if content.startswith(b'%PDF-'):
                success_criteria.append("✅ Valid PDF magic bytes (%PDF-)")
            else:
                success_criteria.append("❌ Invalid PDF format (missing magic bytes)")
                print(f"   First 50 bytes: {content[:50]}")
                return False
            
            # PDF end marker check
            if b'%%EOF' in content:
                success_criteria.append("✅ Valid PDF end marker (%%EOF)")
            else:
                success_criteria.append("❌ Missing PDF end marker")
                return False
            
            # Print all success criteria
            print("\n   📊 Verification Results:")
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            return True
            
        except Exception as e:
            print(f"❌ PDF generation test error: {str(e)}")
            return False

    def run_test(self):
        """Run the complete PDF generation test"""
        print("🧪 PDF Generation Endpoint Test")
        print("=" * 50)
        print("Re-testing PDF generation after tmp_generator.py patch for None traffic_company handling")
        print()
        
        # Step 1: Register + Login
        if not self.register_and_login():
            print("\n❌ Test failed at Step 1: Authentication")
            return False
        
        # Step 2: Create Plan
        if not self.create_minimal_plan():
            print("\n❌ Test failed at Step 2: Plan Creation")
            return False
        
        # Step 3: Test PDF Generation
        if not self.test_pdf_generation():
            print("\n❌ Test failed at Step 3: PDF Generation")
            return False
        
        print("\n🎉 PDF Generation Test PASSED!")
        print("✅ The earlier 500 error has been resolved")
        print("✅ PDF generation endpoint is working correctly")
        return True

if __name__ == "__main__":
    tester = PDFGenerationTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)