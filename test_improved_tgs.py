#!/usr/bin/env python3
import requests
import json

# Test the improved TGS generator
devices = [
    {"device_code": "T1-1", "device_name": "Road Work Ahead", "position_lat": -34.9272, "position_lng": 138.6002},
    {"device_code": "T1-1", "device_name": "Road Work Ahead", "position_lat": -34.9272, "position_lng": 138.6012},
    {"device_code": "T1-7", "device_name": "Road Closed Ahead", "position_lat": -34.9278, "position_lng": 138.6002},
    {"device_code": "T1-7", "device_name": "Road Closed Ahead", "position_lat": -34.9278, "position_lng": 138.6012},
    {"device_code": "G9-4", "device_name": "Detour Left", "position_lat": -34.9282, "position_lng": 138.6002},
    {"device_code": "G9-4", "device_name": "Detour Right", "position_lat": -34.9282, "position_lng": 138.6012},
    {"device_code": "BARRIER", "device_name": "Road Closed", "position_lat": -34.9285, "position_lng": 138.6007}
]

response = requests.post(
    "https://traffic-plan-mapper.preview.emergentagent.com/api/tgs/generate-improved",
    json={
        "center_lat": -34.9285,
        "center_lng": 138.6007,
        "placed_devices": devices,
        "plan_name": "King_William_Street_Improved_TGS"
    },
    timeout=60
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ Success!")
    print(f"PNG: {result.get('png_filename')}")
    print(f"PDF: {result.get('pdf_filename')}")
else:
    print(f"❌ Error: {response.text}")

