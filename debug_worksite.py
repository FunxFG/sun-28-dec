#!/usr/bin/env python3
"""
Debug script to check worksite TMP response structure
"""

import requests
import json

def test_worksite_response():
    # Register a user first
    register_data = {
        "email": "debug_test@example.com",
        "password": "DebugTest123!",
        "company_name": "Debug Test Company"
    }
    
    register_response = requests.post(
        "https://tmp-generator.preview.emergentagent.com/api/auth/register",
        json=register_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if register_response.status_code != 200:
        print(f"Registration failed: {register_response.status_code}")
        return
    
    token = register_response.json()['token']
    
    # Test worksite TMP
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
    
    response = requests.post(
        "https://tmp-generator.preview.emergentagent.com/api/tmp/worksite",
        json=test_data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        plan = data.get('plan', {})
        
        print("Plan sections:")
        for key in plan.keys():
            print(f"  - {key}")
        
        # Check if worksite_signage is in sign_spacing_and_tapers
        sign_spacing = plan.get('sign_spacing_and_tapers', {})
        print(f"\nSign spacing sections:")
        for key in sign_spacing.keys():
            print(f"  - {key}")
        
        # Check worksite_signage specifically
        worksite_signage = sign_spacing.get('worksite_signage', {})
        if worksite_signage:
            print(f"\nWorksite signage found in sign_spacing_and_tapers:")
            for key in worksite_signage.keys():
                print(f"  - {key}")
        else:
            print(f"\nNo worksite_signage found in sign_spacing_and_tapers")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_worksite_response()