"""
Complete AS 1742.3 Compliant Traffic Control Device Library
Includes all warning, regulatory, guidance signs and traffic control devices
"""

# Device categories based on AS 1742.3 structure
DEVICE_CATEGORIES = {
    "warning": "Warning Signs",
    "regulatory": "Regulatory Signs",
    "guidance": "Guidance Signs",
    "delineation": "Delineation Devices",
    "barriers": "Barriers & Protection",
    "signals": "Traffic Signals & Boards",
    "vehicles": "Vehicles & Equipment"
}

# Complete device library with AS 1742.3 codes
DEVICE_LIBRARY = {
    # ============================================
    # WARNING SIGNS (AS 1742.3 Part 1)
    # ============================================
    "warning": {
        "T1-1": {
            "code": "T1-1",
            "name": "Road Work Ahead",
            "description": "General warning of road works ahead",
            "size": "600mm or 900mm",
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "🚧",
            "image_path": "/assets/signs/T1-1.svg",
            "typical_use": "Primary advance warning for all road works"
        },
        "T1-2": {
            "code": "T1-2",
            "name": "Road Closed Ahead",
            "description": "Warning of complete road closure ahead",
            "size": "600mm or 900mm",
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "🚫",
            "image_path": "/assets/signs/T1-2.svg",
            "typical_use": "When road completely closed, requires detour"
        },
        "T1-3": {
            "code": "T1-3",
            "name": "Lane Closure Ahead",
            "description": "Warning of lane closure ahead",
            "size": "600mm or 900mm",
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "⚠️",
            "image_path": "/assets/signs/T1-3.svg",
            "typical_use": "Multi-lane roads with lane closure"
        },
        "T1-4": {
            "code": "T1-4",
            "name": "Detour Ahead",
            "description": "Advance warning of detour",
            "size": "600mm or 900mm",
            "color": "Yellow background, black symbols",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "↪️",
            "image_path": "/assets/signs/T1-4.svg",
            "typical_use": "Before detour diversion point"
        },
        "T1-5": {
            "code": "T1-5",
            "name": "Distance to Work (e.g., 500m)",
            "description": "Distance indicator to work area",
            "size": "600mm",
            "color": "Yellow background, black text",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "📏",
            "image_path": "/assets/signs/T1-5.svg",
            "typical_use": "Supplement to Road Work Ahead sign"
        },
        "T1-6": {
            "code": "T1-6",
            "name": "Symbolic Worker Sign",
            "description": "Worker symbol with shovel",
            "size": "600mm or 900mm",
            "color": "Yellow background, black symbol",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": False,
            "symbol": "👷",
            "image_path": "/assets/signs/T1-6.svg",
            "typical_use": "At work site boundary, workers present"
        },
        "T1-7": {
            "code": "T1-7",
            "name": "Loose Stones",
            "description": "Warning of loose surface material",
            "size": "600mm",
            "color": "Yellow background, black symbol",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "⚠️",
            "image_path": "/assets/signs/T1-7.svg",
            "typical_use": "Unsealed or re-sealed road surface"
        },
        "T1-8": {
            "code": "T1-8",
            "name": "Uneven Surface",
            "description": "Warning of rough or uneven road",
            "size": "600mm",
            "color": "Yellow background, black symbol",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": True,
            "symbol": "〰️",
            "image_path": "/assets/signs/T1-8.svg",
            "typical_use": "Milled surface, potholes, repairs"
        }
    },

    # ============================================
    # REGULATORY SIGNS (AS 1742.3 Part 4)
    # ============================================
    "regulatory": {
        "R4-1": {
            "code": "R4-1",
            "name": "Temporary Speed Limit 40",
            "description": "40 km/h speed limit in work zone",
            "size": "600mm",
            "color": "White background, red circle, black numerals",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": False,
            "symbol": "4️⃣0️⃣",
            "image_path": "/assets/signs/R4-1-40.svg",
            "typical_use": "Speed reduction at work site"
        },
        "R4-1-60": {
            "code": "R4-1",
            "name": "Temporary Speed Limit 60",
            "description": "60 km/h speed limit",
            "size": "600mm",
            "color": "White background, red circle, black numerals",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": False,
            "symbol": "6️⃣0️⃣",
            "image_path": "/assets/signs/R4-1-60.svg",
            "typical_use": "Progressive speed reduction"
        },
        "R4-1-80": {
            "code": "R4-1",
            "name": "Temporary Speed Limit 80",
            "description": "80 km/h speed limit",
            "size": "600mm",
            "color": "White background, red circle, black numerals",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": False,
            "symbol": "8️⃣0️⃣",
            "image_path": "/assets/signs/R4-1-80.svg",
            "typical_use": "Progressive speed increase on exit"
        },
        "R1-1": {
            "code": "R1-1",
            "name": "Stop Sign",
            "description": "Temporary stop control",
            "size": "600mm or 900mm",
            "color": "Red octagon, white letters",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": True,
            "symbol": "🛑",
            "image_path": "/assets/signs/R1-1.svg",
            "typical_use": "Temporary intersection control"
        },
        "R1-2": {
            "code": "R1-2",
            "name": "Give Way Sign",
            "description": "Temporary give way control",
            "size": "600mm or 900mm",
            "color": "Red triangle inverted, white background",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": True,
            "symbol": "▽",
            "image_path": "/assets/signs/R1-2.svg",
            "typical_use": "Temporary intersection control"
        },
        "R2-1": {
            "code": "R2-1",
            "name": "No Entry",
            "description": "Road closed - no entry",
            "size": "600mm",
            "color": "White bar on red circle",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "⛔",
            "image_path": "/assets/signs/R2-1.svg",
            "typical_use": "Complete road closure point"
        },
        "R2-10": {
            "code": "R2-10",
            "name": "STOP/SLOW Bat",
            "description": "Manual traffic control paddle",
            "size": "450mm diameter",
            "color": "Red STOP / Yellow SLOW",
            "mounting_height": "Hand-held",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🚦",
            "image_path": "/assets/signs/R2-10.svg",
            "typical_use": "Manual traffic controller"
        }
    },

    # ============================================
    # GUIDANCE SIGNS (AS 1742.3 Part 5)
    # ============================================
    "guidance": {
        "G2-1": {
            "code": "G2-1",
            "name": "Detour (with arrow)",
            "description": "Directional detour sign",
            "size": "900mm x 450mm",
            "color": "Yellow background, black text/arrow",
            "mounting_height": 2.3,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "↗️",
            "image_path": "/assets/signs/G2-1.svg",
            "typical_use": "At detour turn points"
        },
        "G2-2": {
            "code": "G2-2",
            "name": "End Detour",
            "description": "Return to normal route",
            "size": "900mm x 450mm",
            "color": "Yellow background, black text",
            "mounting_height": 2.3,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "✓",
            "image_path": "/assets/signs/G2-2.svg",
            "typical_use": "Where detour rejoins normal route"
        },
        "G2-4": {
            "code": "G2-4",
            "name": "End Road Work",
            "description": "End of work zone",
            "size": "600mm",
            "color": "White background, black text",
            "mounting_height": 2.1,
            "bilateral_required": True,
            "advance_distance_required": False,
            "symbol": "✅",
            "image_path": "/assets/signs/G2-4.svg",
            "typical_use": "Termination of work zone"
        },
        "G9-1": {
            "code": "G9-1",
            "name": "Lane Merge Arrow",
            "description": "Indicates lane merge direction",
            "size": "1200mm x 600mm",
            "color": "Yellow background, black arrow",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "↖️",
            "image_path": "/assets/signs/G9-1.svg",
            "typical_use": "At taper start point"
        },
        "G9-9": {
            "code": "G9-9",
            "name": "Keep Left/Right",
            "description": "Direction around obstruction",
            "size": "600mm x 900mm",
            "color": "White background, black arrow",
            "mounting_height": 2.1,
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "⬅️",
            "image_path": "/assets/signs/G9-9.svg",
            "typical_use": "At work zone or barrier"
        }
    },

    # ============================================
    # DELINEATION DEVICES
    # ============================================
    "delineation": {
        "D5-1": {
            "code": "D5-1",
            "name": "Traffic Cone 700mm",
            "description": "Standard traffic cone",
            "size": "700mm height",
            "color": "Orange with reflective sleeves",
            "mounting_height": "Ground level",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🔶",
            "image_path": "/assets/devices/cone-700.svg",
            "typical_use": "Lane delineation, taper, buffer",
            "spacing_rules": "Speed-dependent (10-30m)"
        },
        "D5-2": {
            "code": "D5-2",
            "name": "Traffic Cone 900mm",
            "description": "Large traffic cone",
            "size": "900mm height",
            "color": "Orange with reflective sleeves",
            "mounting_height": "Ground level",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🔶",
            "image_path": "/assets/devices/cone-900.svg",
            "typical_use": "High-speed roads, night works",
            "spacing_rules": "Speed-dependent (10-30m)"
        },
        "D6-1": {
            "code": "D6-1",
            "name": "Delineator Post",
            "description": "Flexible guide post",
            "size": "1100mm height",
            "color": "White or orange with reflectors",
            "mounting_height": "Ground level",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "│",
            "image_path": "/assets/devices/delineator.svg",
            "typical_use": "Edge delineation, long-term works",
            "spacing_rules": "5-10m spacing"
        },
        "D7-1": {
            "code": "D7-1",
            "name": "Channelizing Device",
            "description": "Reflective panel on stand",
            "size": "1400mm x 200mm",
            "color": "Orange/white chevrons",
            "mounting_height": "1200mm to 1400mm",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "⚡",
            "image_path": "/assets/devices/channelizer.svg",
            "typical_use": "Lane shifts, merge tapers",
            "spacing_rules": "As per taper calculation"
        }
    },

    # ============================================
    # BARRIERS & PROTECTION
    # ============================================
    "barriers": {
        "B1-1": {
            "code": "B1-1",
            "name": "Water-Filled Barrier",
            "description": "Temporary concrete/plastic barrier",
            "size": "1000mm height x 2000mm length",
            "color": "White or orange, reflective",
            "mounting_height": "Ground level",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🛡️",
            "image_path": "/assets/devices/water-barrier.svg",
            "typical_use": "Positive protection, work zone separation",
            "spacing_rules": "Continuous or 50m intervals"
        },
        "B1-2": {
            "code": "B1-2",
            "name": "Concrete Barrier",
            "description": "Permanent-type safety barrier",
            "size": "810mm height",
            "color": "Concrete grey, reflective markings",
            "mounting_height": "Ground level",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🛡️",
            "image_path": "/assets/devices/concrete-barrier.svg",
            "typical_use": "High-speed protection, long-term",
            "spacing_rules": "Continuous"
        },
        "B2-1": {
            "code": "B2-1",
            "name": "Mesh Fence/Hoarding",
            "description": "Temporary fencing",
            "size": "1800mm height",
            "color": "Orange or green",
            "mounting_height": "Ground level",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "⬜",
            "image_path": "/assets/devices/fence.svg",
            "typical_use": "Site boundary, pedestrian exclusion",
            "spacing_rules": "Continuous"
        }
    },

    # ============================================
    # TRAFFIC SIGNALS & BOARDS
    # ============================================
    "signals": {
        "S1-1": {
            "code": "S1-1",
            "name": "Portable Traffic Signals",
            "description": "Temporary traffic lights",
            "size": "300mm lens diameter",
            "color": "Red/Yellow/Green",
            "mounting_height": "2400mm to lens center",
            "bilateral_required": False,
            "advance_distance_required": True,
            "symbol": "🚥",
            "image_path": "/assets/devices/temp-signals.svg",
            "typical_use": "Alternating traffic control",
            "spacing_rules": "Advance warning required"
        },
        "S2-1": {
            "code": "S2-1",
            "name": "Arrow Board Type A",
            "description": "Flashing arrow for lane closure",
            "size": "1500mm x 750mm",
            "color": "Yellow LED arrows",
            "mounting_height": "1500mm",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "➡️",
            "image_path": "/assets/devices/arrow-board-a.svg",
            "typical_use": "Lane merge direction",
            "spacing_rules": "At taper start"
        },
        "S2-2": {
            "code": "S2-2",
            "name": "Arrow Board Type B",
            "description": "Large flashing arrow board",
            "size": "2400mm x 1200mm",
            "color": "Yellow LED arrows",
            "mounting_height": "1500mm",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "➡️",
            "image_path": "/assets/devices/arrow-board-b.svg",
            "typical_use": "High-speed roads, night works",
            "spacing_rules": "At taper start"
        },
        "S3-1": {
            "code": "S3-1",
            "name": "Variable Message Sign (VMS)",
            "description": "Electronic message display",
            "size": "Various (typically 5m x 3m)",
            "color": "LED matrix - amber/white",
            "mounting_height": "Trailer-mounted",
            "bilateral_required": False,
            "advance_distance_required": True,
            "symbol": "📟",
            "image_path": "/assets/devices/vms.svg",
            "typical_use": "Advance warnings, queue alerts",
            "spacing_rules": "500m+ advance"
        }
    },

    # ============================================
    # VEHICLES & EQUIPMENT
    # ============================================
    "vehicles": {
        "V1-1": {
            "code": "V1-1",
            "name": "Truck-Mounted Attenuator (TMA)",
            "description": "Impact protection vehicle",
            "size": "Truck with crash cushion",
            "color": "High-vis, chevron markings",
            "mounting_height": "N/A",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🚛",
            "image_path": "/assets/vehicles/tma.svg",
            "typical_use": "Mobile works, buffer protection",
            "spacing_rules": "40-60m before work"
        },
        "V2-1": {
            "code": "V2-1",
            "name": "Shadow Vehicle",
            "description": "Protection vehicle with signage",
            "size": "Utility or truck",
            "color": "High-vis, flashing beacons",
            "mounting_height": "N/A",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🚗",
            "image_path": "/assets/vehicles/shadow.svg",
            "typical_use": "Mobile works convoy",
            "spacing_rules": "Maintains buffer distance"
        },
        "V3-1": {
            "code": "V3-1",
            "name": "Traffic Control Vehicle",
            "description": "Vehicle with mounted signs/lights",
            "size": "Various",
            "color": "High-vis, chevrons, beacons",
            "mounting_height": "N/A",
            "bilateral_required": False,
            "advance_distance_required": False,
            "symbol": "🚙",
            "image_path": "/assets/vehicles/control.svg",
            "typical_use": "Mobile/short-term works",
            "spacing_rules": "Per mobile TGS"
        }
    }
}

def get_device_by_code(code: str):
    """Get device specification by AS 1742.3 code"""
    for category, devices in DEVICE_LIBRARY.items():
        if code in devices:
            return devices[code]
    return None

def get_devices_by_category(category: str):
    """Get all devices in a category"""
    return DEVICE_LIBRARY.get(category, {})

def search_devices(search_term: str):
    """Search devices by name or description"""
    results = []
    search_lower = search_term.lower()
    
    for category, devices in DEVICE_LIBRARY.items():
        for code, device in devices.items():
            if (search_lower in device['name'].lower() or 
                search_lower in device['description'].lower() or
                search_lower in code.lower()):
                results.append({**device, 'category': category})
    
    return results

def get_required_devices_for_scenario(scenario: dict):
    """
    Get recommended devices based on work scenario
    scenario = {
        'work_type': 'static' | 'mobile' | 'intersection',
        'speed_limit': int,
        'lanes': int,
        'duration': 'short' | 'medium' | 'long',
        'time_of_day': 'day' | 'night'
    }
    """
    required = []
    
    # Always need warning signs
    required.append('T1-1')  # Road Work Ahead
    
    if scenario.get('work_type') == 'static':
        if scenario.get('lanes', 1) > 1:
            required.append('T1-3')  # Lane Closure Ahead
        required.append('T1-6')  # Symbolic Worker
        required.append('R4-1')  # Speed Limit
        required.append('G2-4')  # End Road Work
        
        # High speed needs more protection
        if scenario.get('speed_limit', 50) >= 70:
            required.append('V1-1')  # TMA
            required.append('S2-2')  # Large Arrow Board
        
    elif scenario.get('work_type') == 'mobile':
        required.append('V1-1')  # TMA
        required.append('V2-1')  # Shadow Vehicle
        
    # Night works need enhanced devices
    if scenario.get('time_of_day') == 'night':
        required.append('D5-2')  # Large cones
        required.append('S2-2')  # Large arrow board
    
    return required
