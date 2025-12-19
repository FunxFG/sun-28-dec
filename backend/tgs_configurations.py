"""
TGS (Traffic Guidance Scheme) Configurations
Based on ADVANCED Traffic Management Generic TGS Package 2026
AS 1742.3:2019 Compliant

This module contains standard TGS configurations for various roadwork scenarios.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

# ==================== TGS TYPES ====================

TGS_TYPES = {
    "STOP_SLOW_LOW_SPEED": {
        "name": "Stop-Slow 40-50-60-70km",
        "description": "Work in traffic lane with traffic controllers",
        "speed_range": [40, 50, 60, 70],
        "requires_tc": True,
    },
    "STOP_SLOW_HIGH_SPEED": {
        "name": "Stop-Slow 80-90-100-110km",
        "description": "Work in traffic lane on high-speed roads",
        "speed_range": [80, 90, 100, 110],
        "requires_tc": True,
    },
    "LANE_CLOSURE_NO_MEDIAN": {
        "name": "Lane Closure - No Median",
        "description": "Single lane closure on undivided road",
        "requires_tc": False,  # Can use arrow boards
    },
    "LANE_CLOSURE_RAISED_MEDIAN": {
        "name": "Lane Closure - Raised Median",
        "description": "Single lane closure on divided road",
        "requires_tc": False,
    },
    "CONTRA_FLOW": {
        "name": "Contra Flow",
        "description": "Traffic diverted to opposing lane",
        "requires_tc": True,
    },
    "ROAD_CLOSURE": {
        "name": "Road Closure with Detour",
        "description": "Complete road closure with alternate route",
        "requires_tc": True,
    },
    "ROUNDABOUT_STOP_SLOW": {
        "name": "Roundabout Stop-Slow",
        "description": "Work near or within roundabout",
        "requires_tc": True,
    },
    "T_INTERSECTION": {
        "name": "T-Intersection Stop-Slow",
        "description": "Work at T-intersection",
        "requires_tc": True,
    },
    "FOOTPATH_CLOSURE": {
        "name": "Footpath Works - Pedestrian Management",
        "description": "Footpath closure with pedestrian detour",
        "requires_tc": False,
    },
}

# ==================== SIGN SEQUENCES ====================

# Standard sign sequence for Stop-Slow operations (40-70 km/h)
SIGN_SEQUENCE_STOP_SLOW_LOW = [
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 195, "side": "left"},
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 145, "side": "left"},
    {"sign": "T1-2", "name": "Prepare to Stop", "distance_from_workzone": 130, "side": "left"},
    {"sign": "T1-2", "name": "Prepare to Stop", "distance_from_workzone": 60, "side": "left"},
    {"sign": "R4-1", "name": "Speed Limit 40", "distance_from_workzone": 45, "side": "left"},
    {"sign": "TC", "name": "Stop Here When Directed", "distance_from_workzone": 0, "side": "left"},
]

# Standard sign sequence for Stop-Slow operations (80-110 km/h)
SIGN_SEQUENCE_STOP_SLOW_HIGH = [
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 400, "side": "left"},
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 320, "side": "left"},
    {"sign": "T1-2", "name": "Prepare to Stop", "distance_from_workzone": 240, "side": "left"},
    {"sign": "T1-2", "name": "Prepare to Stop", "distance_from_workzone": 80, "side": "left"},
    {"sign": "R4-1", "name": "Speed Limit 60", "distance_from_workzone": 0, "side": "left"},
    {"sign": "TC", "name": "Stop Here When Directed", "distance_from_workzone": -90, "side": "left"},
]

# Standard sign sequence for Lane Closure (40-70 km/h)
SIGN_SEQUENCE_LANE_CLOSURE_LOW = [
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 160, "side": "left"},
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 80, "side": "left"},
    {"sign": "T1-25", "name": "Lane Status / Merge", "distance_from_workzone": 60, "side": "left"},
    {"sign": "R4-1", "name": "Speed Limit 40", "distance_from_workzone": 45, "side": "left"},
    {"sign": "Arrow Board", "name": "Arrow Board", "distance_from_workzone": 30, "side": "left"},
    # Taper cones start here
]

# Standard sign sequence for Lane Closure (80-110 km/h)
SIGN_SEQUENCE_LANE_CLOSURE_HIGH = [
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 320, "side": "left"},
    {"sign": "T1-1", "name": "Road Work Ahead", "distance_from_workzone": 240, "side": "left"},
    {"sign": "T1-2", "name": "Prepare to Stop", "distance_from_workzone": 160, "side": "left"},
    {"sign": "T1-25", "name": "Lane Status / Merge", "distance_from_workzone": 80, "side": "left"},
    {"sign": "R4-1", "name": "Speed Limit 60", "distance_from_workzone": 60, "side": "left"},
    {"sign": "Arrow Board", "name": "Arrow Board", "distance_from_workzone": 45, "side": "left"},
    # Taper cones start here
]

# End of roadwork sign sequence
SIGN_SEQUENCE_END = [
    {"sign": "T1-11", "name": "End Road Work", "distance_from_workzone": -50, "side": "left"},
]

# ==================== TAPER CONFIGURATIONS ====================

TAPER_CONFIGS = {
    "low_speed": {  # 40-70 km/h
        "taper_length_m": 15,
        "cone_spacing_m": 3,
        "num_cones": 6,  # 15m / 3m spacing + 1
    },
    "medium_speed": {  # 60-80 km/h
        "taper_length_m": 30,
        "cone_spacing_m": 5,
        "num_cones": 7,
    },
    "high_speed": {  # 80-100 km/h
        "taper_length_m": 90,
        "cone_spacing_m": 10,
        "num_cones": 10,
    },
    "very_high_speed": {  # 100-110 km/h
        "taper_length_m": 145,
        "cone_spacing_m": 15,
        "num_cones": 10,
    },
}

# Taper length formula: L = W × S² / 155 (where W=lane width, S=speed limit)
def calculate_taper_length(lane_width_m: float, speed_limit_kmh: int) -> float:
    """Calculate taper length per AS 1742.3 formula"""
    return (lane_width_m * (speed_limit_kmh ** 2)) / 155

# ==================== BUFFER ZONES ====================

BUFFER_ZONES = {
    "safety_buffer": {
        "low_speed": 20,   # meters for 40-70 km/h
        "high_speed": 30,  # meters for 80-110 km/h
    },
    "tc_distance": {
        "from_workzone": 15,  # meters
    },
    "longitudinal_buffer": {
        "low_speed": 5,    # meters minimum
        "high_speed": 20,  # meters minimum
    },
}

# ==================== LATERAL SHIFT MARKERS ====================

LATERAL_SHIFT_SPACING = {
    # Worker proximity (m): Required spacing (m)
    "0-1.2": {"spacing": 15, "speed_limit": 40},
    "1.2-3.0": {"spacing": 25, "speed_limit": 40},
    "3.0-6.0": {"spacing": 30, "speed_limit": 60},
    "6.0-9.0": {"spacing": 35, "speed_limit": 80},
    "above_9.0": {"spacing": 45, "speed_limit": "posted"},
}

# ==================== SIGN PLACEMENT RULES ====================

SIGN_PLACEMENT_RULES = {
    # Speed limit based distances
    "40-50": {
        "advance_warning_1": 50,
        "advance_warning_2": 15,
        "prepare_to_stop_1": 70,
        "speed_reduction": 15,
        "tc_position": 45,
    },
    "60-70": {
        "advance_warning_1": 80,
        "advance_warning_2": 80,
        "prepare_to_stop_1": 160,
        "speed_reduction": 80,
        "tc_position": 90,
    },
    "80-90": {
        "advance_warning_1": 160,
        "advance_warning_2": 80,
        "prepare_to_stop_1": 160,
        "speed_reduction": 80,
        "tc_position": 90,
    },
    "100-110": {
        "advance_warning_1": 160,
        "advance_warning_2": 160,
        "prepare_to_stop_1": 160,
        "speed_reduction": 80,
        "tc_position": 90,
    },
}

# ==================== SPEED LIMIT REPEATER RULES ====================

SPEED_REPEATER_RULES = {
    "spacing_m": 200,  # Speed limit signs every 200m
    "within_workzone": True,
}

# ==================== DEVICE TYPES ====================

DEVICE_TYPES = {
    "warning_signs": ["T1-1", "T1-2", "T1-3", "T1-5", "T1-11", "T1-25"],
    "regulatory_signs": ["R4-1", "R4-201", "R4-5"],
    "guide_signs": ["G9-79", "G9-84"],
    "delineation": ["TC1", "TC2", "Bollard", "Water Barrier"],
    "arrow_boards": ["Arrow Board Left", "Arrow Board Right", "Arrow Board Split"],
    "other": ["Truck Attenuator", "VMS", "Speed Radar"],
}

# ==================== WORKZONE LENGTH REQUIREMENTS ====================

def get_minimum_workzone_length(work_type: str) -> int:
    """Get minimum workzone length based on work type"""
    minimums = {
        "pothole_repair": 20,
        "line_marking": 50,
        "utility_work": 30,
        "road_resurfacing": 100,
        "construction": 200,
        "default": 40,
    }
    return minimums.get(work_type, minimums["default"])

# ==================== TGS GENERATION HELPER ====================

def get_tgs_configuration(
    tgs_type: str,
    speed_limit: int,
    workzone_length: float,
    lane_width: float = 3.5
) -> Dict[str, Any]:
    """
    Get complete TGS configuration based on type and parameters
    
    Args:
        tgs_type: Type of TGS (from TGS_TYPES keys)
        speed_limit: Posted speed limit in km/h
        workzone_length: Length of work zone in meters
        lane_width: Lane width in meters (default 3.5m)
    
    Returns:
        Dictionary with complete TGS configuration
    """
    
    # Determine speed category
    if speed_limit <= 70:
        speed_category = "low_speed"
        sign_sequence = SIGN_SEQUENCE_STOP_SLOW_LOW if "STOP_SLOW" in tgs_type else SIGN_SEQUENCE_LANE_CLOSURE_LOW
    else:
        speed_category = "high_speed"
        sign_sequence = SIGN_SEQUENCE_STOP_SLOW_HIGH if "STOP_SLOW" in tgs_type else SIGN_SEQUENCE_LANE_CLOSURE_HIGH
    
    # Calculate taper length
    taper_length = calculate_taper_length(lane_width, speed_limit)
    
    # Get taper configuration
    if speed_limit <= 50:
        taper_config = TAPER_CONFIGS["low_speed"]
    elif speed_limit <= 80:
        taper_config = TAPER_CONFIGS["medium_speed"]
    elif speed_limit <= 100:
        taper_config = TAPER_CONFIGS["high_speed"]
    else:
        taper_config = TAPER_CONFIGS["very_high_speed"]
    
    # Get buffer zones
    buffer = BUFFER_ZONES["safety_buffer"][speed_category]
    
    return {
        "tgs_type": tgs_type,
        "tgs_info": TGS_TYPES.get(tgs_type, {}),
        "speed_limit": speed_limit,
        "speed_category": speed_category,
        "workzone_length": workzone_length,
        "taper_length": max(taper_length, taper_config["taper_length_m"]),
        "taper_config": taper_config,
        "safety_buffer": buffer,
        "sign_sequence": sign_sequence,
        "end_signs": SIGN_SEQUENCE_END,
        "speed_repeater_spacing": SPEED_REPEATER_RULES["spacing_m"],
    }


# ==================== CONE PLACEMENT GENERATOR ====================

def generate_taper_cones(
    start_lat: float,
    start_lng: float,
    bearing: float,
    taper_length: float,
    lane_width: float,
    speed_limit: int
) -> List[Dict]:
    """
    Generate cone positions for a taper
    
    Args:
        start_lat: Starting latitude
        start_lng: Starting longitude
        bearing: Road bearing in degrees
        taper_length: Length of taper in meters
        lane_width: Width of lane being closed
        speed_limit: Speed limit for cone spacing
    
    Returns:
        List of cone positions with lat/lng
    """
    import math
    
    # Determine cone spacing based on speed
    if speed_limit <= 50:
        spacing = 3
    elif speed_limit <= 80:
        spacing = 5
    else:
        spacing = 10
    
    num_cones = int(taper_length / spacing) + 1
    cones = []
    
    for i in range(num_cones):
        # Calculate position along taper
        distance_along = i * spacing
        progress = distance_along / taper_length  # 0 to 1
        
        # Linear taper: lateral offset decreases from lane_width to 0
        lateral_offset = lane_width * (1 - progress)
        
        # Calculate lat/lng (simplified - assumes flat earth for small distances)
        # In production, use proper geodesic calculations
        lat_offset = (distance_along * math.cos(math.radians(bearing))) / 111320
        lng_offset = (distance_along * math.sin(math.radians(bearing))) / (111320 * math.cos(math.radians(start_lat)))
        
        # Add lateral offset
        lat_lateral = (lateral_offset * math.cos(math.radians(bearing + 90))) / 111320
        lng_lateral = (lateral_offset * math.sin(math.radians(bearing + 90))) / (111320 * math.cos(math.radians(start_lat)))
        
        cones.append({
            "id": f"taper_cone_{i}",
            "device_name": "Traffic Cone 700mm",
            "device_type": "delineation",
            "position_lat": start_lat + lat_offset + lat_lateral,
            "position_lng": start_lng + lng_offset + lng_lateral,
            "distance_along_taper": distance_along,
            "lateral_offset": lateral_offset,
            "taper_position": f"{int(progress * 100)}%"
        })
    
    return cones


# For testing
if __name__ == "__main__":
    # Test configuration generation
    config = get_tgs_configuration(
        tgs_type="LANE_CLOSURE_NO_MEDIAN",
        speed_limit=60,
        workzone_length=100
    )
    
    import json
    print(json.dumps(config, indent=2, default=str))
