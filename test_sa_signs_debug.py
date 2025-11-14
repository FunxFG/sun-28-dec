#!/usr/bin/env python3
"""
Debug SA Sign Library to see what codes are available
"""
import requests
import json

def test_sa_signs_debug():
    base_url = "https://tmp-generator.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Get first few signs to see what codes are available
    print("🔍 Getting first 5 SA signs to see available codes...")
    
    try:
        response = requests.get(f"{api_url}/sa-signs", params={"limit": 5, "skip": 0})
        if response.status_code == 200:
            data = response.json()
            signs = data.get('signs', [])
            
            print(f"Found {len(signs)} signs:")
            for i, sign in enumerate(signs):
                code = sign.get('code', 'No code')
                description = sign.get('description', 'No description')
                category = sign.get('category', 'No category')
                print(f"  {i+1}. Code: {code}")
                print(f"     Description: {description[:80]}...")
                print(f"     Category: {category}")
                print()
            
            # Test with the first available code
            if signs:
                first_code = signs[0].get('code')
                print(f"🔍 Testing with first available code: {first_code}")
                
                response2 = requests.get(f"{api_url}/sa-signs/{first_code}")
                if response2.status_code == 200:
                    sign_data = response2.json()
                    print(f"✅ Successfully retrieved sign {first_code}")
                    print(f"   Description: {sign_data.get('description', 'No description')}")
                    print(f"   Category: {sign_data.get('category', 'No category')}")
                    if 'dimensions' in sign_data:
                        dims = sign_data['dimensions']
                        print(f"   Dimensions: {dims.get('width_mm', 'N/A')}mm x {dims.get('height_mm', 'N/A')}mm")
                else:
                    print(f"❌ Failed to retrieve sign {first_code}: {response2.status_code}")
                    print(f"   Response: {response2.text}")
        else:
            print(f"❌ Failed to get signs: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    # Test search for "road" to see if any results come up
    print("\n🔍 Testing search for 'road'...")
    try:
        response = requests.get(f"{api_url}/sa-signs/search", params={"q": "road", "limit": 5})
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Search for 'road' returned {len(results)} results")
            for result in results:
                print(f"  - {result.get('code')}: {result.get('description', 'No description')[:60]}...")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {str(e)}")

    # Test search for "warning" to see if any results come up
    print("\n🔍 Testing search for 'warning'...")
    try:
        response = requests.get(f"{api_url}/sa-signs/search", params={"q": "warning", "limit": 5})
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Search for 'warning' returned {len(results)} results")
            for result in results:
                print(f"  - {result.get('code')}: {result.get('description', 'No description')[:60]}...")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {str(e)}")

if __name__ == "__main__":
    test_sa_signs_debug()