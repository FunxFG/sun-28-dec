#!/usr/bin/env python3
"""
Generate Visual TGS with Sign Overlays on Satellite Imagery
"""

import requests
import json
import base64
from pathlib import Path

BASE_URL = "https://traffix-manager-1.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

def generate_visual_tgs():
    print("=" * 80)
    print("GENERATING VISUAL TGS WITH SATELLITE IMAGERY")
    print("=" * 80)
    print()
    
    # King William Street Road Closure devices
    devices = [
        {
            "device_code": "T1-1",
            "device_name": "Road Work Ahead",
            "position_lat": -34.9272,
            "position_lng": 138.6002,
            "distance_from_start": 150,
            "side": "Left"
        },
        {
            "device_code": "T1-1",
            "device_name": "Road Work Ahead",
            "position_lat": -34.9272,
            "position_lng": 138.6012,
            "distance_from_start": 150,
            "side": "Right"
        },
        {
            "device_code": "T1-7",
            "device_name": "Road Closed Ahead",
            "position_lat": -34.9278,
            "position_lng": 138.6002,
            "distance_from_start": 100,
            "side": "Left"
        },
        {
            "device_code": "T1-7",
            "device_name": "Road Closed Ahead",
            "position_lat": -34.9278,
            "position_lng": 138.6012,
            "distance_from_start": 100,
            "side": "Right"
        },
        {
            "device_code": "G9-4",
            "device_name": "Detour Left",
            "position_lat": -34.9282,
            "position_lng": 138.6002,
            "distance_from_start": 50,
            "side": "Left"
        },
        {
            "device_code": "G9-4",
            "device_name": "Detour Right",
            "position_lat": -34.9282,
            "position_lng": 138.6012,
            "distance_from_start": 50,
            "side": "Right"
        },
        {
            "device_code": "BARRIER",
            "device_name": "Road Closed",
            "position_lat": -34.9285,
            "position_lng": 138.6007,
            "distance_from_start": 0,
            "side": "Center"
        }
    ]
    
    print(f"📍 Generating TGS for: King William Street, Adelaide SA")
    print(f"   Center: -34.9285, 138.6007")
    print(f"   Devices: {len(devices)}")
    print()
    
    # Generate visual TGS
    print("Step 1: Calling Visual TGS API...")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{API_URL}/tgs/generate-visual",
            json={
                "center_lat": -34.9285,
                "center_lng": 138.6007,
                "placed_devices": devices,
                "include_streetview": False,  # Skip streetview for faster generation
                "plan_name": "King_William_Street_Road_Closure_Visual_TGS"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Visual TGS generated successfully!")
            print()
            
            # Show saved files
            if result.get('saved_files'):
                print(f"📁 Files Generated: {len(result['saved_files'])}")
                print()
                for file in result['saved_files']:
                    print(f"   📄 {file['filename']}")
                    print(f"      Type: {file['type']}")
                    print(f"      Size: {file.get('size', 0) / 1024:.1f} KB")
                    print(f"      Download: {BASE_URL}/api/downloads/file/{file['filename']}")
                    print()
            
            # Show metadata
            if result.get('metadata'):
                metadata = result['metadata']
                print(f"📊 Generation Details:")
                print(f"   Total signs: {metadata.get('total_signs', 0)}")
                print(f"   Files saved: {metadata.get('files_saved', 0)}")
                print(f"   Output directory: {metadata.get('output_directory', 'N/A')}")
                print()
            
            return result
            
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = generate_visual_tgs()
    
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print()
    
    if result:
        print("✅ Your TGS drawing is ready!")
        print()
        print("📥 DOWNLOAD YOUR VISUAL TGS:")
        print()
        print("   PNG (Satellite Image):")
        print("   https://traffix-manager-1.preview.emergentagent.com/api/downloads/file/King_William_Street_Road_Closure_Visual_TGS_XXXXXX_TGS_Drawing.png")
        print()
        print("   PDF (Professional Format):")
        print("   https://traffix-manager-1.preview.emergentagent.com/api/downloads/file/King_William_Street_Road_Closure_Visual_TGS_XXXXXX_TGS_Drawing.pdf")
        print()
        print("   (Replace XXXXXX with actual timestamp from filenames above)")
        print()
        print("🗺️ The TGS shows:")
        print("   - Satellite imagery of King William Street")
        print("   - Sign positions overlaid with markers")
        print("   - Device codes and names")
        print("   - Bilateral signage pairs")
        print("   - Road closure barricades")
        print()
    else:
        print("❌ Visual TGS generation failed")
        print("   Check error messages above")

