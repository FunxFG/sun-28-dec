"""
Field Guide Placement Engine
SA DIT Field Guide compliant device placement calculator
Implements exact zone definitions and spacing requirements
"""

from typing import Dict, List, Tuple
import math


def calculate_field_guide_zones(
    speed_limit: int,
    work_length: int,
    lane_closure: bool = False
) -> Dict:
    """
    Calculate all Field Guide zones based on speed limit
    
    Args:
        speed_limit: Posted speed limit (km/h)
        work_length: Length of work area (meters)
        lane_closure: Whether lane closure is required
        
    Returns:
        Complete zone layout with distances
    """
    
    # Get zone lengths based on speed
    zones = get_zone_lengths_by_speed(speed_limit)
    
    # Calculate cumulative distances from start
    layout = {
        'buffer_zone': {
            'code': 'BZ',
            'name': 'Buffer Zone',
            'start': 0,
            'end': zones['buffer_zone'],
            'length': zones['buffer_zone'],
            'description': 'Safety buffer before advance warning'
        },
        'advance_warning': {
            'code': 'AW',
            'name': 'Advance Warning Area',
            'start': zones['buffer_zone'],
            'end': zones['buffer_zone'] + zones['advance_warning'],
            'length': zones['advance_warning'],
            'description': 'Driver alert zone',
            'sign_position': zones['buffer_zone'] + 5  # 5m into AW zone
        },
        'taper_area': {
            'code': 'TA',
            'name': 'Taper Area',
            'start': zones['buffer_zone'] + zones['advance_warning'],
            'end': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'],
            'length': zones['taper_length'],
            'description': 'Gradual lane shift/closure',
            'taper_type': 'merge' if lane_closure else 'lateral_shift'
        },
        'safety_buffer': {
            'code': 'SB',
            'name': 'Safety Buffer',
            'start': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'],
            'end': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'] + zones['safety_buffer'],
            'length': zones['safety_buffer'],
            'description': 'Buffer between taper and work'
        },
        'work_area': {
            'code': 'WA',
            'name': 'Work Area',
            'start': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'] + zones['safety_buffer'],
            'end': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'] + zones['safety_buffer'] + work_length,
            'length': work_length,
            'description': 'Actual work zone'
        },
        'termination': {
            'code': 'ML',
            'name': 'Termination Area',
            'start': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'] + zones['safety_buffer'] + work_length,
            'end': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'] + zones['safety_buffer'] + work_length + zones['termination'],
            'length': zones['termination'],
            'description': 'End road work signage',
            'sign_position': zones['buffer_zone'] + zones['advance_warning'] + zones['taper_length'] + zones['safety_buffer'] + work_length + 5
        }
    }
    
    # Total length
    total_length = layout['termination']['end']
    
    # Calculate cone positions for taper
    cone_spacing = get_cone_spacing(speed_limit)
    taper_cones = calculate_taper_cone_positions(
        layout['taper_area']['start'],
        layout['taper_area']['length'],
        cone_spacing
    )
    
    return {
        'speed_limit': speed_limit,
        'work_length': work_length,
        'total_setup_length': total_length,
        'zones': layout,
        'cone_spacing': cone_spacing,
        'taper_cones': taper_cones,
        'compliance': 'SA DIT Field Guide Version 9.1 2021'
    }


def get_zone_lengths_by_speed(speed_limit: int) -> Dict:
    """Get zone lengths based on speed limit"""
    
    # Speed categories as per Field Guide
    if speed_limit <= 45:
        return {
            'buffer_zone': 20,
            'advance_warning': 5,
            'taper_length': 15,
            'safety_buffer': 25,  # Mid-range of 20-30m
            'termination': 10
        }
    elif speed_limit <= 65:
        return {
            'buffer_zone': 20,
            'advance_warning': 50,
            'taper_length': 30,
            'safety_buffer': 40,  # Mid-range of 30-50m
            'termination': 10
        }
    elif speed_limit <= 85:
        return {
            'buffer_zone': 20,
            'advance_warning': 90,
            'taper_length': 70,  # Lateral shift taper
            'safety_buffer': 62,  # Mid-range of 50-75m
            'termination': 15
        }
    else:  # > 85 km/h
        return {
            'buffer_zone': 20,
            'advance_warning': 150,
            'taper_length': 100,  # Lateral shift taper
            'safety_buffer': 87,  # Mid-range of 75-100m
            'termination': 15
        }


def get_cone_spacing(speed_limit: int) -> int:
    """Get cone spacing based on speed (Field Guide)"""
    
    if speed_limit <= 45:
        return 6
    elif speed_limit <= 65:
        return 12
    elif speed_limit <= 85:
        return 18
    else:
        return 24


def calculate_taper_cone_positions(
    taper_start: float,
    taper_length: float,
    cone_spacing: int
) -> List[Dict]:
    """Calculate individual cone positions in taper"""
    
    positions = []
    current_distance = taper_start
    cone_number = 1
    
    while current_distance < (taper_start + taper_length):
        positions.append({
            'cone_number': cone_number,
            'distance_from_start': current_distance,
            'device_type': 'cone',
            'zone': 'TA - Taper Area'
        })
        current_distance += cone_spacing
        cone_number += 1
    
    return positions


def generate_device_schedule(
    zones: Dict,
    work_type: str,
    bilateral: bool = True
) -> List[Dict]:
    """
    Generate complete device schedule with Field Guide zones
    
    Args:
        zones: Zone layout from calculate_field_guide_zones
        work_type: Type of work
        bilateral: Whether bilateral signage required
        
    Returns:
        Complete device list with positions
    """
    
    devices = []
    device_id = 1
    
    # Advance Warning Signs (in AW zone)
    aw_position = zones['zones']['advance_warning']['sign_position']
    
    signs = [
        {
            'code': 'T1-1',
            'name': 'Road Work Ahead',
            'size': '600mm x 600mm',
            'zone': 'AW',
            'position': aw_position,
            'bilateral': bilateral
        }
    ]
    
    # Add lane closure sign if applicable
    if 'closure' in work_type.lower():
        signs.append({
            'code': 'T1-7',
            'name': 'Road Closed Ahead',
            'size': '900mm x 600mm',
            'zone': 'AW',
            'position': aw_position + 20,
            'bilateral': bilateral
        })
    
    # Convert to device list
    for sign in signs:
        if sign['bilateral']:
            # Left side
            devices.append({
                'id': device_id,
                'device_code': sign['code'],
                'device_name': sign['name'],
                'size': sign['size'],
                'zone': sign['zone'],
                'distance_from_start': sign['position'],
                'side': 'Left',
                'bilateral_pair': device_id + 1
            })
            device_id += 1
            
            # Right side
            devices.append({
                'id': device_id,
                'device_code': sign['code'],
                'device_name': sign['name'],
                'size': sign['size'],
                'zone': sign['zone'],
                'distance_from_start': sign['position'],
                'side': 'Right',
                'bilateral_pair': device_id - 1
            })
            device_id += 1
        else:
            devices.append({
                'id': device_id,
                'device_code': sign['code'],
                'device_name': sign['name'],
                'size': sign['size'],
                'zone': sign['zone'],
                'distance_from_start': sign['position'],
                'side': 'Center',
                'bilateral_pair': None
            })
            device_id += 1
    
    # Add cones in taper
    taper_cones = zones['taper_cones']
    for cone in taper_cones:
        devices.append({
            'id': device_id,
            'device_code': 'CONE',
            'device_name': f"Traffic Cone #{cone['cone_number']}",
            'size': '750mm',
            'zone': 'TA',
            'distance_from_start': cone['distance_from_start'],
            'side': 'Taper Line',
            'bilateral_pair': None
        })
        device_id += 1
    
    # End Road Work signs (in ML zone)
    ml_position = zones['zones']['termination']['sign_position']
    
    if bilateral:
        devices.extend([
            {
                'id': device_id,
                'device_code': 'T1-12',
                'device_name': 'End Road Work',
                'size': '600mm x 600mm',
                'zone': 'ML',
                'distance_from_start': ml_position,
                'side': 'Left',
                'bilateral_pair': device_id + 1
            },
            {
                'id': device_id + 1,
                'device_code': 'T1-12',
                'device_name': 'End Road Work',
                'size': '600mm x 600mm',
                'zone': 'ML',
                'distance_from_start': ml_position,
                'side': 'Right',
                'bilateral_pair': device_id
            }
        ])
    
    return devices


def calculate_clearance_requirements(
    lane_width: float,
    work_width: float,
    road_width: float
) -> Dict:
    """
    Calculate clearance and determine if containment fencing required
    
    Args:
        lane_width: Width of travel lane (meters)
        work_width: Width of work area (meters)
        road_width: Total road width (meters)
        
    Returns:
        Clearance analysis and requirements
    """
    
    # Calculate available clearance
    clearance = (road_width - lane_width - work_width) / 2
    
    # Field Guide requirement: minimum 3m
    minimum_clearance = 3.0
    containment_required = clearance < minimum_clearance
    
    return {
        'available_clearance': round(clearance, 2),
        'minimum_required': minimum_clearance,
        'clearance_adequate': clearance >= minimum_clearance,
        'containment_fencing_required': containment_required,
        'recommendations': generate_clearance_recommendations(clearance),
        'compliance': 'SA DIT Field Guide - Minimum 3m clearance requirement'
    }


def generate_clearance_recommendations(clearance: float) -> List[str]:
    """Generate recommendations based on clearance"""
    
    recommendations = []
    
    if clearance < 2.0:
        recommendations.extend([
            'CRITICAL: Clearance < 2m - Enhanced protection required',
            'Install concrete barriers or rigid containment',
            'Deploy additional traffic controllers',
            'Consider full lane closure with stop/slow control',
            'Implement 25 km/h speed limit (high hazard)'
        ])
    elif clearance < 3.0:
        recommendations.extend([
            'WARNING: Clearance < 3m - Containment fencing MANDATORY',
            'Install chain mesh or similar physical barrier',
            'Enhanced high-vis PPE for all workers',
            'Regular safety briefings',
            'Implement 40 km/h speed limit in work zone'
        ])
    elif clearance < 4.0:
        recommendations.extend([
            'Standard clearance - Additional precautions recommended',
            'Physical delineation (cones/bollards)',
            'High-vis PPE mandatory',
            'Monitor for vehicle encroachment'
        ])
    else:
        recommendations.append('Adequate clearance - Standard traffic control measures')
    
    return recommendations


def calculate_traffic_controller_positions(
    zones: Dict,
    one_lane_operation: bool = False
) -> Dict:
    """Calculate optimal traffic controller positions"""
    
    if not one_lane_operation:
        return {
            'controllers_required': False,
            'reason': 'Not one-lane operation'
        }
    
    # For one-lane operations: controllers at both ends
    work_start = zones['zones']['work_area']['start']
    work_end = zones['zones']['work_area']['end']
    
    # Positions should allow good sight distance
    tc1_position = work_start - 20  # 20m before work area
    tc2_position = work_end + 20    # 20m after work area
    
    sight_distance = tc2_position - tc1_position
    
    return {
        'controllers_required': True,
        'minimum_controllers': 2,
        'positions': [
            {
                'controller_id': 'TC1',
                'position': tc1_position,
                'location': 'Approach end (before work area)',
                'equipment': ['Stop/Slow baton', 'UHF radio', 'High-vis vest'],
                'clearance_from_lane': 1.5,
                'escape_route': 'Required'
            },
            {
                'controller_id': 'TC2',
                'position': tc2_position,
                'location': 'Departure end (after work area)',
                'equipment': ['Stop/Slow baton', 'UHF radio', 'High-vis vest'],
                'clearance_from_lane': 1.5,
                'escape_route': 'Required'
            }
        ],
        'sight_distance': sight_distance,
        'sight_distance_adequate': sight_distance >= 150,
        'communication_method': 'UHF radio (preferred) or visual sight line',
        'breaks_required': 'Every 2 hours minimum',
        'compliance': 'SA DIT Field Guide Traffic Controller Requirements'
    }
