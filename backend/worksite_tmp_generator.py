"""
Worksite Traffic Management Generator
Based on VicRoads Traffic Management Note No. 33 and AS 1742.3:2019

Generates specialized TMPs for:
- Lane closure works with merge tapers
- Lateral shift operations
- Speed reduction zones
- Sign spacing calculations
- Worker safety zones
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime


def calculate_sign_spacing_and_tapers(
    posted_speed: int,
    reduced_speed: Optional[int] = None,
    road_type: str = "arterial",
    lane_closure: bool = False,
    workers_present: bool = True,
    traffic_control_required: bool = False
) -> Dict:
    """
    Calculate sign spacing and taper lengths based on speed zones and work type
    
    Args:
        posted_speed: Posted speed limit (km/h)
        reduced_speed: Reduced worksite speed limit (km/h), if None, calculated automatically
        road_type: Type of road (arterial, freeway, local, etc.)
        lane_closure: Whether lane closure is required
        workers_present: Whether workers will be present
        traffic_control_required: Whether traffic controllers are needed
    
    Returns:
        Complete sign spacing and taper length specifications
    """
    
    # Determine appropriate reduced speed if not specified
    if reduced_speed is None:
        reduced_speed = _calculate_reduced_speed(posted_speed, workers_present)
    
    # Calculate advance warning sign distances
    advance_distances = _calculate_advance_warning_distances(posted_speed, reduced_speed)
    
    # Calculate taper lengths
    taper_lengths = _calculate_taper_lengths(posted_speed, reduced_speed, lane_closure)
    
    return {
        "calculation_id": f"SIGNSPACE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "posted_speed": posted_speed,
        "reduced_speed": reduced_speed,
        "road_type": road_type,
        
        "advance_warning_signs": {
            "roadwork_ahead": {
                "sign_code": "TC-2601",
                "distance_to_worksite": advance_distances["roadwork_ahead"],
                "placement": "Both sides of carriageway",
                "size": "1200mm x 900mm (minimum)",
                "mandatory": True
            },
            "speed_limit_ahead": {
                "sign_code": "TC-2602",
                "text": f"{reduced_speed} km/h AHEAD",
                "distance_to_worksite": advance_distances["speed_limit_ahead"],
                "placement": "Both sides of carriageway",
                "size": "900mm x 600mm",
                "mandatory": True if reduced_speed <= 60 else False
            },
            "prepare_to_stop": {
                "sign_code": "TC-2605",
                "distance_to_worksite": advance_distances.get("prepare_to_stop"),
                "placement": "Both sides of carriageway",
                "size": "1200mm x 900mm",
                "mandatory": traffic_control_required,
                "note": "Required when traffic will be stopped"
            }
        },
        
        "worksite_signage": {
            "reduced_speed_limit": {
                "sign_code": "TC-2610",
                "speed": reduced_speed,
                "placement": "Both sides of carriageway at worksite entry",
                "size": "900mm diameter",
                "mandatory": True,
                "repeater_spacing": 200 if reduced_speed == 40 else 500,
                "repeater_note": f"Repeater signs every {200 if reduced_speed == 40 else 500}m"
            },
            "symbolic_workers": {
                "sign_code": "TC-2615",
                "placement": "Visible throughout work area",
                "size": "900mm x 900mm",
                "mandatory": workers_present,
                "note": "Must be displayed whenever workers are on-site"
            },
            "symbolic_traffic_controller": {
                "sign_code": "TC-2620",
                "placement": "Where traffic controller stationed",
                "size": "900mm x 900mm",
                "mandatory": traffic_control_required
            }
        },
        
        "taper_specifications": taper_lengths,
        
        "safety_buffer": {
            "distance": _calculate_safety_buffer(posted_speed, reduced_speed),
            "description": "Clear zone between traffic and work area",
            "marking": "Delineator cones or barriers at recommended spacing"
        },
        
        "end_of_works": {
            "end_speed_limit": {
                "sign_code": "TC-2630",
                "placement": "At end of worksite",
                "size": "900mm diameter",
                "note": "Return to previous speed limit"
            },
            "distance_beyond_works": 50,
            "description": "Signs placed 50m beyond last work activity"
        },
        
        "modifications_required": _generate_site_modifications(
            posted_speed, reduced_speed, workers_present, traffic_control_required
        ),
        
        "worker_safety_requirements": _generate_worker_safety_requirements(
            posted_speed, reduced_speed, workers_present
        ),
        
        "compliance": {
            "standards": [
                "AS 1742.3:2019 - Manual of uniform traffic control devices, Part 3",
                "Victorian Worksite Safety - Traffic Management Code of Practice (2010)",
                "VicRoads Traffic Management Note No. 33"
            ],
            "regulations": [
                "Road Safety (Traffic Management) Regulations 2009"
            ]
        }
    }


def generate_worksite_tmp(
    location: str,
    work_type: str,
    posted_speed: int,
    reduced_speed: Optional[int] = None,
    lane_closure: bool = False,
    lane_closure_type: str = "merge",  # merge or lateral_shift
    work_duration_days: int = 1,
    work_hours: str = "7am-5pm",
    workers_present: bool = True,
    traffic_control_required: bool = False,
    night_works: bool = False
) -> Dict:
    """
    Generate a complete worksite traffic management plan
    
    Args:
        location: Work location
        work_type: Type of work (e.g., "Road Resurfacing", "Utility Works")
        posted_speed: Posted speed limit
        reduced_speed: Reduced worksite speed (auto-calculated if None)
        lane_closure: Whether lane closure required
        lane_closure_type: Type of closure (merge or lateral_shift)
        work_duration_days: Duration of works
        work_hours: Working hours
        workers_present: Whether workers will be on-site
        traffic_control_required: Whether traffic controllers needed
        night_works: Whether works occur at night
    """
    
    # Calculate sign spacing and tapers
    sign_spacing = calculate_sign_spacing_and_tapers(
        posted_speed=posted_speed,
        reduced_speed=reduced_speed,
        lane_closure=lane_closure,
        workers_present=workers_present,
        traffic_control_required=traffic_control_required
    )
    
    plan = {
        "plan_type": "Worksite Traffic Management Plan",
        "plan_id": f"WORKSITE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "location": location,
        "work_type": work_type,
        "generated_date": datetime.now().isoformat(),
        
        "work_details": {
            "duration_days": work_duration_days,
            "work_hours": work_hours,
            "night_works": night_works,
            "workers_present": workers_present,
            "traffic_control_required": traffic_control_required
        },
        
        "speed_management": {
            "posted_speed": posted_speed,
            "reduced_speed": sign_spacing["reduced_speed"],
            "speed_reduction_reason": _get_speed_reduction_reason(
                posted_speed, sign_spacing["reduced_speed"], workers_present
            ),
            "40kmh_zone_restrictions": {
                "maximum_length": 200,
                "note": "40 km/h worksite speed zones must not exceed 200m in length",
                "applicable": sign_spacing["reduced_speed"] == 40
            }
        },
        
        "sign_spacing_and_tapers": sign_spacing,
        
        "lane_management": {
            "lane_closure_required": lane_closure,
            "closure_type": lane_closure_type if lane_closure else None,
            "merge_taper": sign_spacing["taper_specifications"].get("merge_taper") if lane_closure else None,
            "lateral_shift_taper": sign_spacing["taper_specifications"].get("lateral_shift_taper") if lane_closure and lane_closure_type == "lateral_shift" else None,
            "lane_closure_signs": _get_lane_closure_signage(lane_closure_type) if lane_closure else []
        },
        
        "traffic_control": {
            "controllers_required": traffic_control_required,
            "controller_positions": _get_controller_positions_worksite(traffic_control_required, lane_closure),
            "stop_slow_bats_required": traffic_control_required,
            "two_way_radio_required": traffic_control_required,
            "responsibilities": [
                "Manage traffic flow safely through worksite",
                "Display STOP/SLOW bat as required",
                "Maintain clear communication with other controllers",
                "Ensure worker safety",
                "Adjust to changing site conditions",
                "Wear high-visibility clothing at all times"
            ] if traffic_control_required else []
        },
        
        "delineation_and_barriers": {
            "delineator_spacing": _calculate_delineator_spacing(sign_spacing["reduced_speed"]),
            "barrier_type": "Temporary concrete barriers" if posted_speed > 80 else "Safety barriers or delineators",
            "placement": "Along work zone edge, parallel to traffic flow",
            "reflectivity": "All delineators must have reflective elements for night visibility"
        },
        
        "lighting_requirements": {
            "required": night_works or work_hours != "7am-5pm",
            "specifications": {
                "work_area": "Adequate task lighting for workers",
                "signage": "All signs must be illuminated or reflective (Class 1 or 2)",
                "delineators": "Reflective or active lighting on barriers/cones",
                "minimum_lux": 20
            } if night_works else {}
        },
        
        "site_modifications": sign_spacing["modifications_required"],
        
        "worker_safety": sign_spacing["worker_safety_requirements"],
        
        "setup_and_removal": {
            "setup_sequence": [
                {
                    "step": 1,
                    "action": "Install advance warning signs",
                    "distance": "As per sign spacing calculations",
                    "time": "30 minutes"
                },
                {
                    "step": 2,
                    "action": "Install reduced speed limit signs",
                    "location": "Worksite entry (both sides)",
                    "time": "15 minutes"
                },
                {
                    "step": 3,
                    "action": "Install taper delineation (if lane closure)",
                    "specification": "As per taper length calculations",
                    "time": "30 minutes" if lane_closure else "N/A"
                },
                {
                    "step": 4,
                    "action": "Install work zone barriers/delineators",
                    "specification": "Safety buffer zone",
                    "time": "30 minutes"
                },
                {
                    "step": 5,
                    "action": "Position traffic controllers (if required)",
                    "location": "As per traffic control plan",
                    "time": "Ongoing" if traffic_control_required else "N/A"
                },
                {
                    "step": 6,
                    "action": "Display symbolic workers signs",
                    "requirement": "Mandatory when workers on-site",
                    "time": "5 minutes"
                }
            ],
            "removal_note": "Remove in reverse order. Ensure site is safe before removing speed restrictions."
        },
        
        "emergency_procedures": {
            "site_evacuation": "All workers to designated safe zone immediately",
            "incident_reporting": "Report all incidents to site supervisor and relevant authorities",
            "first_aid": "Qualified first aid officer on-site",
            "emergency_contacts": {
                "emergency_services": "000",
                "site_supervisor": "TBC",
                "traffic_management_company": "TBC"
            }
        },
        
        "compliance": sign_spacing["compliance"]
    }
    
    return plan


def _calculate_reduced_speed(posted_speed: int, workers_present: bool) -> int:
    """Calculate appropriate reduced speed based on posted speed and worker presence"""
    
    # Worker proximity rules (from VicRoads Note 33)
    if workers_present:
        if posted_speed >= 90:
            return 60
        elif posted_speed >= 70:
            return 40
        elif posted_speed >= 50:
            return 40
        else:
            return max(40, posted_speed - 20)
    else:
        # No workers - less aggressive reduction
        if posted_speed >= 100:
            return 80
        elif posted_speed >= 80:
            return 60
        else:
            return max(40, posted_speed - 20)


def _calculate_advance_warning_distances(posted_speed: int, reduced_speed: int) -> Dict:
    """Calculate advance warning sign distances based on speed differential"""
    
    # Base distances from AS 1742.3 and VicRoads Note 33
    distance_map = {
        110: {"roadwork_ahead": 500, "speed_limit_ahead": 300, "prepare_to_stop": 200},
        100: {"roadwork_ahead": 400, "speed_limit_ahead": 250, "prepare_to_stop": 150},
        90: {"roadwork_ahead": 350, "speed_limit_ahead": 200, "prepare_to_stop": 150},
        80: {"roadwork_ahead": 300, "speed_limit_ahead": 180, "prepare_to_stop": 120},
        70: {"roadwork_ahead": 250, "speed_limit_ahead": 150, "prepare_to_stop": 100},
        60: {"roadwork_ahead": 200, "speed_limit_ahead": 120, "prepare_to_stop": 80},
        50: {"roadwork_ahead": 150, "speed_limit_ahead": 100, "prepare_to_stop": 60},
        40: {"roadwork_ahead": 100, "speed_limit_ahead": 60, "prepare_to_stop": 50}
    }
    
    # Get closest speed or interpolate
    return distance_map.get(posted_speed, distance_map[60])


def _calculate_taper_lengths(posted_speed: int, reduced_speed: int, lane_closure: bool) -> Dict:
    """Calculate merge and lateral shift taper lengths"""
    
    if not lane_closure:
        return {"merge_taper": None, "lateral_shift_taper": None}
    
    # Taper lengths from AS 1742.3:2019
    taper_map = {
        110: {"merge": 90, "lateral_shift": 60},
        100: {"merge": 80, "lateral_shift": 50},
        90: {"merge": 70, "lateral_shift": 45},
        80: {"merge": 60, "lateral_shift": 40},
        70: {"merge": 50, "lateral_shift": 35},
        60: {"merge": 40, "lateral_shift": 30},
        50: {"merge": 30, "lateral_shift": 25},
        40: {"merge": 20, "lateral_shift": 20}
    }
    
    tapers = taper_map.get(posted_speed, taper_map[60])
    
    return {
        "merge_taper": {
            "length_meters": tapers["merge"],
            "description": "Linear taper for lane closure merge",
            "delineator_spacing": "6-10m intervals",
            "note": "Taper begins at reduced speed limit sign location"
        },
        "lateral_shift_taper": {
            "length_meters": tapers["lateral_shift"],
            "description": "Taper for lateral movement (no lane closure)",
            "delineator_spacing": "6-10m intervals",
            "note": "Use when shifting traffic laterally without reducing lane count"
        }
    }


def _calculate_safety_buffer(posted_speed: int, reduced_speed: int) -> int:
    """Calculate safety buffer distance between traffic and work area"""
    
    if reduced_speed <= 40:
        return 5  # 5m buffer at 40 km/h
    elif reduced_speed <= 60:
        return 10  # 10m buffer at 60 km/h
    else:
        return 15  # 15m buffer at higher speeds


def _calculate_delineator_spacing(reduced_speed: int) -> str:
    """Calculate spacing between delineators/cones"""
    
    if reduced_speed <= 40:
        return "6-10m spacing"
    elif reduced_speed <= 60:
        return "10-15m spacing"
    else:
        return "15-20m spacing"


def _get_speed_reduction_reason(posted_speed: int, reduced_speed: int, workers_present: bool) -> str:
    """Generate explanation for speed reduction"""
    
    reasons = []
    
    if workers_present:
        reasons.append("Workers present in proximity to traffic")
    
    speed_diff = posted_speed - reduced_speed
    if speed_diff >= 50:
        reasons.append("Significant hazard or constrained work area")
    elif speed_diff >= 30:
        reasons.append("Active work zone with safety concerns")
    else:
        reasons.append("Minor works with reduced clearances")
    
    return "; ".join(reasons)


def _generate_site_modifications(posted_speed: int, reduced_speed: int, 
                                 workers_present: bool, traffic_control: bool) -> List[Dict]:
    """Generate list of required site-specific modifications"""
    
    modifications = [
        {
            "condition": "Sight obstructions present",
            "modification": "Move advance warning signs earlier to ensure visibility",
            "minimum_sight_distance": f"{posted_speed * 2}m"
        },
        {
            "condition": "Queue formation expected",
            "modification": "Place advance warning signs before queue tail position",
            "note": "Adjust based on peak traffic volumes"
        }
    ]
    
    if not workers_present:
        modifications.append({
            "condition": "No workers on-site",
            "modification": "Remove 'Symbolic Workers' signs",
            "note": "Replace when workers return to site"
        })
    
    if not traffic_control:
        modifications.append({
            "condition": "No traffic controllers present",
            "modification": "Remove 'Prepare to Stop' and 'Symbolic Traffic Controller' signs",
            "note": "These signs only required when traffic will be stopped"
        })
    
    return modifications


def _generate_worker_safety_requirements(posted_speed: int, reduced_speed: int, 
                                         workers_present: bool) -> Dict:
    """Generate worker safety requirements based on proximity to traffic"""
    
    return {
        "high_visibility_clothing": {
            "required": True,
            "specification": "AS/NZS 4602.1:2011 Class D/N",
            "note": "Day/night visibility required"
        },
        "proximity_to_traffic": {
            "reduced_speed": reduced_speed,
            "maximum_proximity": _calculate_worker_proximity(reduced_speed),
            "barrier_required": reduced_speed > 40,
            "note": "Workers must not be closer to traffic than specified distance"
        },
        "symbolic_workers_display": {
            "required": workers_present,
            "placement": "Visible to approaching traffic",
            "quantity": "Sufficient to cover entire work zone"
        },
        "safety_briefing": {
            "required": True,
            "topics": [
                "Site-specific hazards",
                "Traffic management layout",
                "Emergency procedures",
                "PPE requirements",
                "Communication protocols"
            ]
        }
    }


def _calculate_worker_proximity(reduced_speed: int) -> str:
    """Calculate minimum safe distance between workers and traffic"""
    
    if reduced_speed <= 40:
        return "0.5m with barriers, 1.0m without barriers"
    elif reduced_speed <= 60:
        return "1.0m with barriers, 2.0m without barriers"
    else:
        return "2.0m with barriers, workers should not be within traffic lanes"


def _get_lane_closure_signage(closure_type: str) -> List[Dict]:
    """Get signage requirements for lane closures"""
    
    base_signs = [
        {
            "sign_code": "TC-2640",
            "sign_name": "LANE CLOSED",
            "quantity": 2,
            "placement": "Before and at taper start",
            "size": "1200mm x 900mm"
        },
        {
            "sign_code": "TC-2641",
            "sign_name": "MERGE LEFT/RIGHT",
            "quantity": 1,
            "placement": "At merge taper",
            "size": "1200mm x 900mm",
            "with_arrow": True
        }
    ]
    
    if closure_type == "lateral_shift":
        base_signs.append({
            "sign_code": "TC-2645",
            "sign_name": "SHIFT LEFT/RIGHT",
            "quantity": 1,
            "placement": "At lateral shift taper",
            "size": "900mm x 600mm",
            "with_arrow": True
        })
    
    return base_signs


def _get_controller_positions_worksite(traffic_control: bool, lane_closure: bool) -> List[str]:
    """Determine traffic controller positions"""
    
    if not traffic_control:
        return []
    
    positions = [
        "Upstream position (advance of taper)" if lane_closure else "Upstream of work zone",
        "Work zone edge (managing traffic flow)"
    ]
    
    if lane_closure:
        positions.append("Downstream position (after merge)")
    
    return positions
