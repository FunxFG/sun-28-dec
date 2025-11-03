#!/usr/bin/env python3
"""
Simple focused test for SA Government Datasets Integration
Tests Location Metadata System and DIT Infrastructure Assets with shorter timeout
"""
import requests
import sys
import json
from datetime import datetime

def test_sa_datasets_integration():
    """Test SA Government datasets integration with simple approach"""
    print("🏛️ SA GOVERNMENT DATASETS INTEGRATION TESTING")
    print("Testing Location Metadata System (LMS) and DIT Infrastructure Assets")
    print("=" * 80)
    
    base_url = "https://trafficplan-ai.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Quick authentication
    test_email = f"sa_test_{datetime.now().strftime('%H%M%S')}@example.com"
    auth_data = {
        "email": test_email,
        "password": "TestPass123!",
        "company_name": "SA Datasets Test Company"
    }
    
    print(f"\n🔐 Authenticating as: {test_email}")
    try:
        auth_response = requests.post(f"{api_url}/auth/register", json=auth_data, timeout=10)
        if auth_response.status_code == 200:
            token = auth_response.json()['token']
            print(f"✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False
    
    # Test comprehensive auto-populate endpoint with SA datasets
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    test_scenarios = [
        {
            "name": "Adelaide CBD (King William Street) - Should be State Arterial or higher",
            "params": {
                "lat": -34.9285,
                "lng": 138.6007,
                "start_address": "King William Street, Adelaide SA",
                "end_address": "North Terrace, Adelaide SA",
                "work_type": "construction"
            }
        },
        {
            "name": "Highway (Port Wakefield Road) - Should be National Highway",
            "params": {
                "lat": -34.8,
                "lng": 138.5,
                "start_address": "Port Wakefield Road, Adelaide SA",
                "end_address": "Northern Expressway, Adelaide SA",
                "work_type": "maintenance"
            }
        },
        {
            "name": "Residential Street - Should be Local Road with Council maintenance",
            "params": {
                "lat": -34.95,
                "lng": 138.62,
                "start_address": "Residential Street, Unley SA",
                "end_address": "Local Avenue, Unley SA",
                "work_type": "maintenance"
            }
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\n" + "="*80)
        print(f"🧪 TESTING: {scenario['name']}")
        print("="*80)
        
        try:
            print(f"📡 Making API call to comprehensive-auto-populate...")
            response = requests.get(
                f"{api_url}/comprehensive-auto-populate",
                params=scenario['params'],
                headers=headers,
                timeout=60  # Increased timeout
            )
            
            if response.status_code == 200:
                print(f"✅ API call successful (200 OK)")
                data = response.json()
                
                # Check for Location Metadata System data
                lms_data = data.get('location_metadata_system', {})
                dit_assets = data.get('dit_infrastructure_assets', {})
                
                print(f"\n📋 LOCATION METADATA SYSTEM RESULTS:")
                if lms_data:
                    print(f"   ✅ Location Metadata System data present")
                    
                    # Key LMS fields
                    road_classification = lms_data.get('road_classification_official', 'Not specified')
                    maintenance_authority = lms_data.get('maintenance_authority', 'Not specified')
                    crrs_code = lms_data.get('crrs_code', 'Not generated')
                    austroads_class = lms_data.get('austroads_class_code', 'Not specified')
                    functional_hierarchy = lms_data.get('functional_hierarchy', 'Not specified')
                    speed_limit = lms_data.get('speed_limit_official', 'Not specified')
                    sealed_status = lms_data.get('sealed_status', 'Not specified')
                    dataset_refs = lms_data.get('dataset_references', [])
                    
                    print(f"   • Road classification (official): {road_classification}")
                    print(f"   • Maintenance authority: {maintenance_authority}")
                    print(f"   • CRRS code: {crrs_code}")
                    print(f"   • Austroads class code: {austroads_class}")
                    print(f"   • Functional hierarchy: {functional_hierarchy}")
                    print(f"   • Speed limit (official): {speed_limit}")
                    print(f"   • Sealed status: {sealed_status}")
                    print(f"   • Dataset references: {len(dataset_refs)} references")
                    
                    # Validation
                    lms_valid = True
                    if not road_classification or road_classification == 'Not specified':
                        print(f"   ❌ Road classification not populated")
                        lms_valid = False
                    if not crrs_code or not crrs_code.startswith('SA-'):
                        print(f"   ❌ CRRS code not properly generated")
                        lms_valid = False
                    if len(dataset_refs) < 2:
                        print(f"   ❌ Dataset references incomplete")
                        lms_valid = False
                    
                    if lms_valid:
                        print(f"   ✅ Location Metadata System validation passed")
                else:
                    print(f"   ❌ Location Metadata System data missing")
                
                print(f"\n🏗️ DIT INFRASTRUCTURE ASSETS RESULTS:")
                if dit_assets:
                    print(f"   ✅ DIT Infrastructure Assets data present")
                    
                    # Key DIT fields
                    road_condition = dit_assets.get('road_condition', 'Not assessed')
                    pavement_type = dit_assets.get('pavement_type', 'Not specified')
                    asset_inventory = dit_assets.get('asset_inventory', [])
                    maintenance_schedule = dit_assets.get('maintenance_schedule', {})
                    
                    print(f"   • Road condition: {road_condition}")
                    print(f"   • Pavement type: {pavement_type}")
                    print(f"   • Asset inventory: {len(asset_inventory)} items")
                    print(f"   • Maintenance schedule: {'Present' if maintenance_schedule else 'Missing'}")
                    
                    # Show asset inventory details
                    if asset_inventory:
                        print(f"   • Asset inventory items:")
                        for i, asset in enumerate(asset_inventory[:3]):  # Show first 3
                            asset_type = asset.get('asset_type', 'Unknown')
                            details = asset.get('details', 'No details')
                            print(f"     {i+1}. {asset_type}: {details}")
                    
                    # Validation
                    dit_valid = True
                    if not road_condition or road_condition == 'Not assessed':
                        print(f"   ❌ Road condition not assessed")
                        dit_valid = False
                    if not pavement_type or pavement_type == 'Not specified':
                        print(f"   ❌ Pavement type not specified")
                        dit_valid = False
                    if len(asset_inventory) == 0:
                        print(f"   ❌ Asset inventory empty")
                        dit_valid = False
                    
                    if dit_valid:
                        print(f"   ✅ DIT Infrastructure Assets validation passed")
                else:
                    print(f"   ❌ DIT Infrastructure Assets data missing")
                
                # Overall scenario result
                scenario_success = bool(lms_data) and bool(dit_assets)
                results.append({
                    'scenario': scenario['name'],
                    'success': scenario_success,
                    'lms_present': bool(lms_data),
                    'dit_present': bool(dit_assets),
                    'road_classification': lms_data.get('road_classification_official', 'N/A') if lms_data else 'N/A',
                    'maintenance_authority': lms_data.get('maintenance_authority', 'N/A') if lms_data else 'N/A'
                })
                
                if scenario_success:
                    print(f"\n🎉 SCENARIO PASSED: Both LMS and DIT data successfully integrated")
                else:
                    print(f"\n⚠️ SCENARIO PARTIAL: Some data missing")
                    
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            print(f"❌ API call timed out (60 seconds)")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'error': 'Timeout'
            })
        except Exception as e:
            print(f"❌ API call error: {str(e)}")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'error': str(e)
            })
    
    # Final summary
    print(f"\n" + "="*80)
    print(f"📊 FINAL RESULTS SUMMARY")
    print("="*80)
    
    successful_scenarios = [r for r in results if r.get('success', False)]
    total_scenarios = len(results)
    
    print(f"✅ Successful scenarios: {len(successful_scenarios)}/{total_scenarios}")
    
    for result in results:
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        scenario_name = result['scenario']
        print(f"{status} - {scenario_name}")
        
        if result.get('success', False):
            road_class = result.get('road_classification', 'N/A')
            maintenance_auth = result.get('maintenance_authority', 'N/A')
            print(f"      Road Classification: {road_class}")
            print(f"      Maintenance Authority: {maintenance_auth}")
        elif result.get('error'):
            print(f"      Error: {result['error']}")
    
    # Success criteria
    if len(successful_scenarios) >= 2:  # At least 2 out of 3 scenarios should pass
        print(f"\n🎉 SA GOVERNMENT DATASETS INTEGRATION SUCCESSFUL!")
        print(f"✅ Location Metadata System and DIT Infrastructure Assets working correctly")
        return True
    else:
        print(f"\n⚠️ SA GOVERNMENT DATASETS INTEGRATION NEEDS ATTENTION")
        print(f"❌ Some scenarios failed - check API performance and data sources")
        return False

if __name__ == "__main__":
    success = test_sa_datasets_integration()
    sys.exit(0 if success else 1)