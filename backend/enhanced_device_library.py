"""
Enhanced AS 1742.3 Compliant Traffic Control Device Library
Integrated with SA Government Sign Index (1203 official signs)
"""
import json
import os
from pathlib import Path

# Load SA Sign Library
SA_SIGN_LIBRARY_PATH = Path(__file__).parent / 'sa_sign_library.json'

def load_sa_sign_library():
    """Load the official SA Government sign library"""
    try:
        with open(SA_SIGN_LIBRARY_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load SA sign library: {e}")
        return []

# Load SA signs
SA_SIGNS = load_sa_sign_library()

# Device categories based on AS 1742.3 structure + SA specific
DEVICE_CATEGORIES = {
    "warning": "Warning Signs",
    "regulatory": "Regulatory Signs",
    "guidance": "Guidance Signs (Guide Signs)",
    "delineation": "Delineation Devices",
    "barriers": "Barriers & Protection",
    "signals": "Traffic Signals & Boards",
    "vehicles": "Vehicles & Equipment",
    "roadwork": "Roadwork Signs",
    "parking": "Parking Signs",
    "railway_tram": "Railway & Tram Signs"
}

# Core AS 1742.3 Devices (Essential for TMP)
CORE_DEVICE_LIBRARY = {
    # ============================================
    # WARNING SIGNS (AS 1742.3 Part 1)
    # ============================================
    "warning": {
        "T1-1": {
            "code": "T1-1",
            "name": "Road Work Ahead",
            "description": "General warning of road works ahead",
            "size": "600mm or 900mm",
            "dimensions": {"width_mm": 600, "height_mm": 600},
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "🚧",
            "image_url": "https://www.dit.sa.gov.au/signs/T1-1.svg",
            "typical_use": "Primary advance warning for all road works",
            "as_1742_3_reference": "Part 1, Section 2.3"
        },
        "T1-2": {
            "code": "T1-2",
            "name": "Road Closed Ahead",
            "description": "Warning of complete road closure ahead",
            "size": "600mm or 900mm",
            "dimensions": {"width_mm": 600, "height_mm": 600},
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "🚫",
            "image_url": "https://www.dit.sa.gov.au/signs/T1-2.svg",
            "typical_use": "When road completely closed, requires detour",
            "as_1742_3_reference": "Part 1, Section 2.3"
        },
        "T1-3": {
            "code": "T1-3",
            "name": "One Lane Closed Ahead",
            "description": "Warning of lane closure requiring merge",
            "size": "600mm or 900mm",
            "dimensions": {"width_mm": 600, "height_mm": 600},
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "↗",
            "image_url": "https://www.dit.sa.gov.au/signs/T1-3.svg",
            "typical_use": "Lane closures on multi-lane roads",
            "as_1742_3_reference": "Part 1, Section 2.4"
        },
        "T1-7": {
            "code": "T1-7",
            "name": "Roadwork 400m",
            "description": "Distance to roadwork location",
            "size": "600mm x 300mm or 900mm x 450mm",
            "dimensions": {"width_mm": 600, "height_mm": 300},
            "color": "Yellow background, black text",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "400m",
            "image_url": "https://www.dit.sa.gov.au/signs/T1-7.svg",
            "typical_use": "Distance supplementary plate",
            "as_1742_3_reference": "Part 1, Section 2.3"
        }
    },
    
    # ============================================
    # REGULATORY SIGNS
    # ============================================
    "regulatory": {
        "R1-1": {
            "code": "R1-1",
            "name": "Stop",
            "description": "Mandatory stop at line or sign",
            "size": "750mm or 900mm",
            "dimensions": {"width_mm": 750, "height_mm": 750},
            "color": "Red octagon, white letters",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "⏹",
            "image_url": "https://www.dit.sa.gov.au/signs/R1-1.svg",
            "typical_use": "Temporary intersections, traffic control",
            "as_1742_3_reference": "Part 2, Section 3.2"
        },
        "R2-1": {
            "code": "R2-1",
            "name": "Give Way",
            "description": "Yield to oncoming traffic",
            "size": "750mm or 900mm",
            "dimensions": {"width_mm": 750, "height_mm": 650},
            "color": "Red border, white triangle",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "▽",
            "image_url": "https://www.dit.sa.gov.au/signs/R2-1.svg",
            "typical_use": "Temporary intersections, alternating traffic",
            "as_1742_3_reference": "Part 2, Section 3.3"
        },
        "R4-1": {
            "code": "R4-1",
            "name": "Speed Limit 40",
            "description": "Temporary speed limit 40 km/h",
            "size": "600mm or 750mm",
            "dimensions": {"width_mm": 600, "height_mm": 600},
            "color": "White circle, red border, black 40",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": False,
            "symbol": "40",
            "image_url": "https://www.dit.sa.gov.au/signs/R4-1.svg",
            "typical_use": "Reduced speed through work zones",
            "as_1742_3_reference": "Part 2, Section 4.2"
        },
        "R5-1": {
            "code": "R5-1",
            "name": "No Entry",
            "description": "Prohibition of entry to road",
            "size": "600mm or 750mm",
            "dimensions": {"width_mm": 600, "height_mm": 600},
            "color": "White circle, red border and bar",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "⊘",
            "image_url": "https://www.dit.sa.gov.au/signs/R5-1.svg",
            "typical_use": "Road closures, one-way temporary routes",
            "as_1742_3_reference": "Part 2, Section 5.2"
        }
    },
    
    # ============================================
    # GUIDANCE SIGNS
    # ============================================
    "guidance": {
        "G1-1": {
            "code": "G1-1",
            "name": "Detour Arrow Left",
            "description": "Direction guidance for detour route",
            "size": "900mm x 600mm",
            "dimensions": {"width_mm": 900, "height_mm": 600},
            "color": "Yellow background, black arrow",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "←",
            "image_url": "https://www.dit.sa.gov.au/signs/G1-1.svg",
            "typical_use": "Guide traffic around closures",
            "as_1742_3_reference": "Part 6, Section 2.1"
        },
        "G1-2": {
            "code": "G1-2",
            "name": "Detour Arrow Right",
            "description": "Direction guidance for detour route",
            "size": "900mm x 600mm",
            "dimensions": {"width_mm": 900, "height_mm": 600},
            "color": "Yellow background, black arrow",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "→",
            "image_url": "https://www.dit.sa.gov.au/signs/G1-2.svg",
            "typical_use": "Guide traffic around closures",
            "as_1742_3_reference": "Part 6, Section 2.1"
        }
    },
    
    # ============================================
    # DELINEATION DEVICES
    # ============================================
    "delineation": {
        "D1-1": {
            "code": "D1-1",
            "name": "Traffic Cones",
            "description": "750mm traffic cones for delineation",
            "size": "750mm height",
            "dimensions": {"width_mm": 300, "height_mm": 750},
            "color": "Orange with reflective bands",
            "mounting_height": 0.75,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🚧",
            "image_url": "https://www.dit.sa.gov.au/signs/cone.svg",
            "typical_use": "Lane closures, edge delineation",
            "as_1742_3_reference": "Part 3, Section 4.2"
        },
        "D1-2": {
            "code": "D1-2",
            "name": "Delineator Post",
            "description": "Flexible delineator posts",
            "size": "1200mm height",
            "dimensions": {"width_mm": 100, "height_mm": 1200},
            "color": "Orange with reflective tape",
            "mounting_height": 1.2,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "|",
            "image_url": "https://www.dit.sa.gov.au/signs/post.svg",
            "typical_use": "Long-term delineation",
            "as_1742_3_reference": "Part 3, Section 4.3"
        }
    },
    
    # ============================================
    # BARRIERS & PROTECTION
    # ============================================
    "barriers": {
        "B1-1": {
            "code": "B1-1",
            "name": "Water-Filled Barrier",
            "description": "1000mm water-filled safety barrier",
            "size": "1000mm height x 2000mm length",
            "dimensions": {"width_mm": 2000, "height_mm": 1000},
            "color": "White/Orange",
            "mounting_height": 1.0,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "▬",
            "image_url": "https://www.dit.sa.gov.au/signs/barrier.svg",
            "typical_use": "Positive separation, pedestrian protection",
            "as_1742_3_reference": "Part 3, Section 5.2"
        },
        "B1-2": {
            "code": "B1-2",
            "name": "Fencing (Chain Mesh)",
            "description": "Temporary chain mesh fencing 1.8m",
            "size": "1800mm height",
            "dimensions": {"width_mm": 3000, "height_mm": 1800},
            "color": "Galvanized metal",
            "mounting_height": 1.8,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "#",
            "image_url": "https://www.dit.sa.gov.au/signs/fence.svg",
            "typical_use": "Site security, pedestrian exclusion",
            "as_1742_3_reference": "Part 3, Section 5.3"
        }
    }
}


def get_device_library():
    """Get the complete device library"""
    return CORE_DEVICE_LIBRARY


def get_sa_sign_by_code(code):
    """Get a specific SA sign by code"""
    for sign in SA_SIGNS:
        if sign['code'] == code:
            return sign
    return None


def search_sa_signs(query, category=None, limit=20):
    """Search SA signs by description or code"""
    results = []
    query_lower = query.lower()
    
    for sign in SA_SIGNS:
        # Filter by category if specified
        if category and sign['category'].lower() != category.lower():
            continue
        
        # Search in code and description
        if (query_lower in sign['code'].lower() or 
            query_lower in sign['description'].lower()):
            results.append(sign)
            
        if len(results) >= limit:
            break
    
    return results


def get_sa_signs_by_category(category):
    """Get all SA signs in a category"""
    return [sign for sign in SA_SIGNS if sign['category'] == category]


def get_recommended_signs_for_tmp(work_type, road_classification):
    """Get recommended signs for a specific TMP scenario"""
    recommended = []
    
    # Always include core warning signs
    recommended.extend([
        CORE_DEVICE_LIBRARY['warning']['T1-1'],  # Road Work Ahead
        CORE_DEVICE_LIBRARY['delineation']['D1-1']  # Traffic Cones
    ])
    
    # Work type specific
    if 'closure' in work_type.lower():
        recommended.append(CORE_DEVICE_LIBRARY['warning']['T1-2'])  # Road Closed Ahead
        recommended.append(CORE_DEVICE_LIBRARY['regulatory']['R5-1'])  # No Entry
        recommended.extend([
            CORE_DEVICE_LIBRARY['guidance']['G1-1'],  # Detour Left
            CORE_DEVICE_LIBRARY['guidance']['G1-2']  # Detour Right
        ])
    
    if 'lane' in work_type.lower():
        recommended.append(CORE_DEVICE_LIBRARY['warning']['T1-3'])  # One Lane Closed
    
    # Road classification specific
    if 'highway' in road_classification.lower() or 'arterial' in road_classification.lower():
        recommended.append(CORE_DEVICE_LIBRARY['regulatory']['R4-1'])  # Speed Limit
        recommended.append(CORE_DEVICE_LIBRARY['barriers']['B1-1'])  # Water Barriers
    
    return recommended


def get_device_statistics():
    """Get statistics about the device library"""
    return {
        'total_core_devices': sum(len(devices) for devices in CORE_DEVICE_LIBRARY.values()),
        'total_sa_signs': len(SA_SIGNS),
        'categories': len(DEVICE_CATEGORIES),
        'sa_categories': len(set(sign['category'] for sign in SA_SIGNS))
    }
