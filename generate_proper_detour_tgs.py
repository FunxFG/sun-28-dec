#!/usr/bin/env python3
"""
Generate proper TGS for King William Street with visible detour routing
"""

import requests
import json

# Accurate King William Street, Adelaide coordinates
# King William Street runs north-south through Adelaide CBD
# We'll close it between Currie Street and North Terrace

# Work zone: King William St between Currie St and North Terrace
work_zone_start_lat = -34.9255  # Near Currie Street
work_zone_start_lng = 138.6007
work_zone_end_lat = -34.9215    # Near North Terrace
work_zone_end_lng = 138.6007

center_lat = (work_zone_start_lat + work_zone_end_lat) / 2
center_lng = (work_zone_start_lng + work_zone_end_lng) / 2

print("=" * 80)
print("GENERATING KING WILLIAM STREET TGS WITH DETOUR")
print("=" * 80)
print(f"Location: King William Street, Adelaide CBD")
print(f"Between: Currie Street and North Terrace")
print(f"Center: {center_lat}, {center_lng}")
print()

# Create devices with proper detour routing
devices = []

# Advance warning signs - 150m south of closure
devices.extend([
    {
        "device_code": "T1-1",
        "device_name": "Road Work Ahead",
        "position_lat": work_zone_start_lat + 0.0015,  # ~150m south
        "position_lng": work_zone_start_lng - 0.0003,
        "distance_from_start": 150,
        "side": "Left"
    },
    {
        "device_code": "T1-1",
        "device_name": "Road Work Ahead",
        "position_lat": work_zone_start_lat + 0.0015,
        "position_lng": work_zone_start_lng + 0.0003,
        "distance_from_start": 150,
        "side": "Right"
    }
])

# Road closed ahead - 100m before closure
devices.extend([
    {
        "device_code": "T1-7",
        "device_name": "Road Closed Ahead",
        "position_lat": work_zone_start_lat + 0.001,
        "position_lng": work_zone_start_lng - 0.0003,
        "distance_from_start": 100,
        "side": "Left"
    },
    {
        "device_code": "T1-7",
        "device_name": "Road Closed Ahead",
        "position_lat": work_zone_start_lat + 0.001,
        "position_lng": work_zone_start_lng + 0.0003,
        "distance_from_start": 100,
        "side": "Right"
    }
])

# Detour signs pointing to Morphett Street (west) and King William Road (east)
# Left detour to Morphett Street
devices.extend([
    {
        "device_code": "G9-4",
        "device_name": "Detour Left to Morphett St",
        "position_lat": work_zone_start_lat + 0.0005,
        "position_lng": work_zone_start_lng - 0.0003,
        "distance_from_start": 50,
        "side": "Left"
    },
    # Right detour to Pulteney Street
    {
        "device_code": "G9-4",
        "device_name": "Detour Right to Pulteney St",
        "position_lat": work_zone_start_lat + 0.0005,
        "position_lng": work_zone_start_lng + 0.0003,
        "distance_from_start": 50,
        "side": "Right"
    }
])

# Physical barriers at closure point (south end)
devices.extend([
    {
        "device_code": "BARRIER",
        "device_name": "Road Closed - South Barrier",
        "position_lat": work_zone_start_lat,
        "position_lng": work_zone_start_lng - 0.0002,
        "distance_from_start": 0,
        "side": "Left"
    },
    {
        "device_code": "BARRIER",
        "device_name": "Road Closed - South Barrier",
        "position_lat": work_zone_start_lat,
        "position_lng": work_zone_start_lng + 0.0002,
        "distance_from_start": 0,
        "side": "Right"
    }
])

# Barriers at north end (near North Terrace)
devices.extend([
    {
        "device_code": "BARRIER",
        "device_name": "Road Closed - North Barrier",
        "position_lat": work_zone_end_lat,
        "position_lng": work_zone_end_lng - 0.0002,
        "distance_from_start": 400,
        "side": "Left"
    },
    {
        "device_code": "BARRIER",
        "device_name": "Road Closed - North Barrier",
        "position_lat": work_zone_end_lat,
        "position_lng": work_zone_end_lng + 0.0002,
        "distance_from_start": 400,
        "side": "Right"
    }
])

# Detour route markers (on parallel streets)
# Morphett Street (west parallel)
devices.extend([
    {
        "device_code": "G9-4",
        "device_name": "Detour Route",
        "position_lat": center_lat,
        "position_lng": center_lng - 0.0015,  # Morphett St
        "distance_from_start": 200,
        "side": "Detour"
    }
])

# Pulteney Street (east parallel)
devices.extend([
    {
        "device_code": "G9-4",
        "device_name": "Detour Route",
        "position_lat": center_lat,
        "position_lng": center_lng + 0.0015,  # Pulteney St
        "distance_from_start": 200,
        "side": "Detour"
    }
])

print(f"Total devices: {len(devices)}")
print()

# Generate TGS with detour
print("Generating Visual TGS with detour routes...")
print("-" * 80)

response = requests.post(
    "https://roadworksai.preview.emergentagent.com/api/tgs/generate-improved",
    json={
        "center_lat": center_lat,
        "center_lng": center_lng,
        "placed_devices": devices,
        "plan_name": "King_William_Street_Adelaide_Road_Closure_with_Detour"
    },
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print("✅ TGS Generated Successfully!")
    print()
    print("📥 Download Links:")
    print()
    print("PNG:")
    print(f"https://roadworksai.preview.emergentagent.com/api/downloads/file/{result['png_filename']}")
    print()
    print("PDF:")
    print(f"https://roadworksai.preview.emergentagent.com/api/downloads/file/{result['pdf_filename']}")
    print()
    print("🗺️ This TGS shows:")
    print("  - Actual King William Street satellite imagery")
    print("  - Road closure between Currie St and North Terrace")
    print("  - Detour routes via Morphett St (west) and Pulteney St (east)")
    print("  - 12 traffic control devices with actual sign images")
    print("  - Bilateral warning and closure signs")
    print("  - Physical barriers at both ends")
    print()
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

