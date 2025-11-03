#!/usr/bin/env python3
"""
Test different search terms to find one that works
"""
import requests

def test_search_terms():
    base_url = "https://trafficplan-ai.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    search_terms = ["stop", "speed", "parking", "railway", "TES", "W5"]
    
    for term in search_terms:
        print(f"\n🔍 Testing search term: '{term}'")
        try:
            response = requests.get(f"{api_url}/sa-signs/search", params={"q": term, "limit": 3})
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"   ✅ Success - Found {len(results)} results")
                for result in results[:2]:  # Show first 2 results
                    print(f"     - {result.get('code')}: {result.get('description', 'No description')[:50]}...")
                if len(results) > 0:
                    return term  # Return the first working term
            else:
                print(f"   ❌ Failed - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return None

if __name__ == "__main__":
    working_term = test_search_terms()
    if working_term:
        print(f"\n✅ Found working search term: '{working_term}'")
    else:
        print(f"\n❌ No working search terms found")