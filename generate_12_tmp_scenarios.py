"""
Comprehensive TMP with TGS Generator - 12 Scenarios
Generates complete Traffic Management Plans with visual TGS including sign overlays
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys
sys.path.append('/app/backend')

from visual_tgs_with_signs import generate_complete_visual_tgs
from enhanced_device_library import get_recommended_signs_for_tmp
from comprehensive_auto_population import get_comprehensive_auto_population

# 12 Test Scenarios covering various work types and locations
SCENARIOS = [
    {
        "id": 1,
        "name": "CBD Lane Closure - King William Street",
        "location": "King William Street, Adelaide SA",
        "center_lat": -34.9285,
        "center_lng": 138.6007,
        "work_type": "lane closure",
        "road_classification": "State Arterial Road",
        "duration": "3 days",
        "speed_limit": 50
    },
    {
        "id": 2,
        "name": "Highway Maintenance - Port Wakefield Road",
        "location": "Port Wakefield Road, Adelaide SA",
        "center_lat": -34.8,
        "center_lng": 138.5,
        "work_type": "maintenance",
        "road_classification": "National Highway",
        "duration": "1 week",
        "speed_limit": 100
    },
    {
        "id": 3,
        "name": "School Zone Roadwork - Unley",
        "location": "Unley Road, Unley SA",
        "center_lat": -34.95,
        "center_lng": 138.62,
        "work_type": "roadwork",
        "road_classification": "Urban Collector",
        "duration": "2 days",
        "speed_limit": 60
    },
    {
        "id": 4,
        "name": "Complete Road Closure - North Terrace",
        "location": "North Terrace, Adelaide SA",
        "center_lat": -34.9205,
        "center_lng": 138.6010,
        "work_type": "road closure",
        "road_classification": "State Arterial Road",
        "duration": "1 day",
        "speed_limit": 50
    },
    {
        "id": 5,
        "name": "Utility Installation - Residential Street",
        "location": "Residential Avenue, Norwood SA",
        "center_lat": -34.92,
        "center_lng": 138.64,
        "work_type": "utility installation",
        "road_classification": "Local Road",
        "duration": "5 days",
        "speed_limit": 50
    },
    {
        "id": 6,
        "name": "Bridge Work - Torrens River Crossing",
        "location": "Adelaide Bridge, Adelaide SA",
        "center_lat": -34.915,
        "center_lng": 138.595,
        "work_type": "bridge maintenance",
        "road_classification": "Regional Road",
        "duration": "2 weeks",
        "speed_limit": 60
    },
    {
        "id": 7,
        "name": "Emergency Repair - Arterial Road",
        "location": "Anzac Highway, Adelaide SA",
        "center_lat": -34.938,
        "center_lng": 138.585,
        "work_type": "emergency repair",
        "road_classification": "State Arterial Road",
        "duration": "12 hours",
        "speed_limit": 70
    },
    {
        "id": 8,
        "name": "Intersection Upgrade - Marion Road",
        "location": "Marion Road & Sturt Road, Marion SA",
        "center_lat": -35.01,
        "center_lng": 138.55,
        "work_type": "intersection upgrade",
        "road_classification": "Regional Road",
        "duration": "4 weeks",
        "speed_limit": 80
    },
    {
        "id": 9,
        "name": "Pedestrian Crossing Installation",
        "location": "Rundle Mall, Adelaide SA",
        "center_lat": -34.924,
        "center_lng": 138.599,
        "work_type": "pedestrian infrastructure",
        "road_classification": "Urban Collector",
        "duration": "3 days",
        "speed_limit": 40
    },
    {
        "id": 10,
        "name": "Roundabout Construction",
        "location": "Prospect Road, Prospect SA",
        "center_lat": -34.885,
        "center_lng": 138.595,
        "work_type": "roundabout construction",
        "road_classification": "Regional Road",
        "duration": "8 weeks",
        "speed_limit": 60
    },
    {
        "id": 11,
        "name": "Tram Line Maintenance",
        "location": "Jetty Road, Glenelg SA",
        "center_lat": -34.98,
        "center_lng": 138.515,
        "work_type": "tram infrastructure",
        "road_classification": "Urban Collector",
        "duration": "1 week",
        "speed_limit": 50
    },
    {
        "id": 12,
        "name": "Highway Resurfacing - Southern Expressway",
        "location": "Southern Expressway, Adelaide SA",
        "center_lat": -35.05,
        "center_lng": 138.55,
        "work_type": "resurfacing",
        "road_classification": "National Highway",
        "duration": "2 months",
        "speed_limit": 110
    }
]


async def generate_devices_for_scenario(scenario):
    """Generate device placements for a scenario"""
    devices = []
    
    # Get recommended signs from our library
    recommended = get_recommended_signs_for_tmp(
        scenario['work_type'],
        scenario['road_classification']
    )
    
    # Create device positions based on recommendations
    base_lat = scenario['center_lat']
    base_lng = scenario['center_lng']
    
    # Position devices at varying distances
    distances = [50, 100, 200, 300, 500]  # meters
    offset = 0.0001  # approximate meters in degrees
    
    for i, device in enumerate(recommended[:5]):  # Limit to 5 devices per scenario
        if i < len(distances):
            # Alternate left and right sides
            side_multiplier = 1 if i % 2 == 0 else -1
            
            devices.append({
                'code': device.get('code', f'SIGN-{i+1}'),
                'name': device.get('name', 'Traffic Sign'),
                'latitude': base_lat + (distances[i] * offset),
                'longitude': base_lng + (side_multiplier * distances[i] * offset * 0.5),
                'distance': distances[i],
                'side': 'left' if side_multiplier == 1 else 'right',
                'dimensions': device.get('dimensions', {'width_mm': 600, 'height_mm': 600}),
                'description': device.get('description', 'Traffic control device')
            })
    
    return devices


async def generate_scenario_tmp(scenario):
    """Generate complete TMP for a scenario"""
    print(f"\n{'='*80}")
    print(f"🚧 Generating TMP #{scenario['id']}: {scenario['name']}")
    print(f"📍 Location: {scenario['location']}")
    print(f"🔧 Work Type: {scenario['work_type']}")
    print(f"🛣️ Classification: {scenario['road_classification']}")
    print(f"⏱️ Duration: {scenario['duration']}")
    print(f"{'='*80}\n")
    
    result = {
        'scenario': scenario,
        'tmp_data': {},
        'visual_tgs': {},
        'devices': [],
        'auto_population': {},
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Step 1: Get comprehensive auto-population data
        print("📊 Fetching comprehensive auto-population data...")
        auto_pop_data = await get_comprehensive_auto_population(
            lat=scenario['center_lat'],
            lng=scenario['center_lng'],
            start_address=scenario['location'],
            end_address=scenario['location'],
            work_type=scenario['work_type']
        )
        result['auto_population'] = auto_pop_data
        print(f"✅ Auto-population complete: {len(auto_pop_data)} data categories")
        
        # Step 2: Generate device placements
        print("🚦 Generating device placements...")
        devices = await generate_devices_for_scenario(scenario)
        result['devices'] = devices
        print(f"✅ Placed {len(devices)} traffic control devices")
        
        # Step 3: Generate visual TGS with sign overlays
        print("🗺️ Generating visual TGS with sign overlays...")
        visual_result = await generate_complete_visual_tgs(
            center_lat=scenario['center_lat'],
            center_lng=scenario['center_lng'],
            placed_devices=devices,
            include_streetview=True
        )
        result['visual_tgs'] = visual_result
        
        if visual_result.get('satellite_tgs', {}).get('success'):
            print(f"✅ Satellite TGS generated successfully")
            print(f"   Dimensions: {visual_result['satellite_tgs']['dimensions']}")
            print(f"   Total signs: {visual_result['satellite_tgs']['total_signs']}")
        
        if visual_result.get('streetview_images'):
            print(f"✅ Street View images: {len(visual_result['streetview_images'])} perspectives")
        
        # Step 4: Generate TMP document data
        print("📄 Compiling TMP document...")
        result['tmp_data'] = {
            'project_name': scenario['name'],
            'location': scenario['location'],
            'work_type': scenario['work_type'],
            'duration': scenario['duration'],
            'speed_limit': scenario['speed_limit'],
            'road_classification': scenario['road_classification'],
            'devices_count': len(devices),
            'data_categories': len(auto_pop_data),
            'has_visual_tgs': visual_result.get('satellite_tgs', {}).get('success', False),
            'has_streetview': len(visual_result.get('streetview_images', [])) > 0
        }
        
        print(f"\n✅ TMP #{scenario['id']} COMPLETE!")
        print(f"   📊 Data categories: {result['tmp_data']['data_categories']}")
        print(f"   🚦 Devices placed: {result['tmp_data']['devices_count']}")
        print(f"   🗺️ Visual TGS: {'Yes' if result['tmp_data']['has_visual_tgs'] else 'No'}")
        print(f"   📷 Street View: {'Yes' if result['tmp_data']['has_streetview'] else 'No'}")
        
    except Exception as e:
        print(f"❌ Error generating TMP #{scenario['id']}: {str(e)}")
        result['error'] = str(e)
    
    return result


async def generate_all_scenarios():
    """Generate all 12 TMP scenarios"""
    print("\n" + "="*80)
    print("🚀 GENERATING 12 COMPREHENSIVE TMP SCENARIOS WITH VISUAL TGS")
    print("="*80)
    
    all_results = []
    
    for scenario in SCENARIOS:
        result = await generate_scenario_tmp(scenario)
        all_results.append(result)
        
        # Save individual scenario
        output_file = f"/app/tmp_scenario_{scenario['id']:02d}.json"
        with open(output_file, 'w') as f:
            # Remove base64 images to reduce file size for JSON
            result_copy = result.copy()
            if 'visual_tgs' in result_copy:
                if 'satellite_tgs' in result_copy['visual_tgs']:
                    if 'image_base64' in result_copy['visual_tgs']['satellite_tgs']:
                        result_copy['visual_tgs']['satellite_tgs']['image_base64'] = '[BASE64_DATA_REMOVED]'
                
                if 'streetview_images' in result_copy['visual_tgs']:
                    for img in result_copy['visual_tgs']['streetview_images']:
                        if 'image_base64' in img:
                            img['image_base64'] = '[BASE64_DATA_REMOVED]'
            
            json.dump(result_copy, f, indent=2)
        print(f"💾 Saved to: {output_file}")
    
    # Generate summary
    print("\n" + "="*80)
    print("📊 GENERATION SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in all_results if 'error' not in r)
    failed = len(all_results) - successful
    
    print(f"\n✅ Successfully generated: {successful}/12 scenarios")
    print(f"❌ Failed: {failed}/12 scenarios")
    
    print("\n📋 Scenario Details:")
    print("-" * 80)
    
    for i, result in enumerate(all_results, 1):
        scenario = result['scenario']
        status = "✅" if 'error' not in result else "❌"
        devices = result['tmp_data'].get('devices_count', 0) if 'tmp_data' in result else 0
        visual_tgs = "Yes" if result.get('tmp_data', {}).get('has_visual_tgs') else "No"
        
        print(f"{status} #{i:2d}. {scenario['name'][:50]:<50} | Devices: {devices} | TGS: {visual_tgs}")
    
    # Save master summary
    summary_file = "/app/tmp_all_scenarios_summary.json"
    with open(summary_file, 'w') as f:
        summary = {
            'total_scenarios': len(SCENARIOS),
            'successful': successful,
            'failed': failed,
            'generation_time': datetime.now().isoformat(),
            'scenarios': [
                {
                    'id': r['scenario']['id'],
                    'name': r['scenario']['name'],
                    'status': 'success' if 'error' not in r else 'failed',
                    'devices': r['tmp_data'].get('devices_count', 0) if 'tmp_data' in r else 0,
                    'has_visual_tgs': r.get('tmp_data', {}).get('has_visual_tgs', False),
                    'has_streetview': r.get('tmp_data', {}).get('has_streetview', False),
                    'data_file': f"tmp_scenario_{r['scenario']['id']:02d}.json"
                }
                for r in all_results
            ]
        }
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Master summary saved to: {summary_file}")
    print("\n" + "="*80)
    print("🎉 ALL SCENARIOS GENERATED!")
    print("="*80)
    
    return all_results


if __name__ == "__main__":
    print("Starting comprehensive TMP generation...")
    results = asyncio.run(generate_all_scenarios())
    print(f"\n✅ Complete! Generated {len(results)} TMP scenarios with visual TGS")
