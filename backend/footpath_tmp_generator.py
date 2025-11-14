"""
Footpath Closure and Pedestrian Management TMP Generator
Based on SA DIT Field Guide and analyzed footpath closure plans

Generates specialized TMPs for:
- Footpath closure with pedestrian detours
- Pedestrian access retained scenarios
- DDA compliant pedestrian management
"""

from typing import Dict, List, Optional
from datetime import datetime


def generate_footpath_closure_plan(
    location: str,
    work_type: str,
    closure_type: str = "full",  # "full" or "partial"
    detour_width: float = 1.2,  # minimum 1.2m as per standards
    dda_compliant: bool = True,
    duration_days: int = 1,
    work_hours: str = "7am-5pm",
    traffic_controllers_required: int = 2
) -> Dict:
    """
    Generate a comprehensive footpath closure and pedestrian management plan
    
    Args:
        location: Work site location
        work_type: Type of work being performed
        closure_type: "full" (detour required) or "partial" (access retained)
        detour_width: Width of detour path (minimum 1.2m)
        dda_compliant: Whether DDA compliant ramps/access required
        duration_days: Duration of works
        work_hours: Working hours
        traffic_controllers_required: Number of traffic controllers needed
    """
    
    # Validate minimum detour width
    if detour_width < 1.2:
        detour_width = 1.2
    
    plan = {
        "plan_type": "Footpath Closure and Pedestrian Management",
        "plan_id": f"FOOTPATH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "location": location,
        "work_type": work_type,
        "closure_type": closure_type,
        "generated_date": datetime.now().isoformat(),
        
        "pedestrian_management": {
            "closure_type": closure_type,
            "detour_required": closure_type == "full",
            "detour_specifications": {
                "minimum_width": detour_width,
                "dda_compliant": dda_compliant,
                "surface_type": "Temporary footpath matting or existing hard surface",
                "gradient": "Maximum 1:14 for DDA compliance" if dda_compliant else "As per site conditions",
                "delineation": "Safety barriers and/or crowd control barriers"
            } if closure_type == "full" else {
                "access_retained": True,
                "minimum_clear_width": 1.2,
                "description": "Pedestrian access maintained with safe passage alongside work zone"
            }
        },
        
        "signage_requirements": _generate_footpath_signage(closure_type, dda_compliant),
        
        "traffic_control": {
            "controllers_required": traffic_controllers_required,
            "positions": _get_controller_positions(closure_type),
            "responsibilities": [
                "Guide pedestrians to detour or around work area",
                "Maintain safety of pedestrians and workers",
                "Ensure clear signage visibility",
                "Assist mobility-impaired pedestrians",
                "Monitor footpath conditions",
                "Manage conflicts between pedestrians and vehicles (if applicable)"
            ]
        },
        
        "safety_measures": {
            "work_site_delineation": "MANDATORY - Work site must be fully delineated and closed off for pedestrian access",
            "safety_zones": [
                {
                    "zone_name": "Work Zone",
                    "description": "Area closed to all pedestrian access",
                    "barriers": "Temporary fencing or safety barriers"
                },
                {
                    "zone_name": "Safety Buffer",
                    "description": "Minimum 0.5m clearance between work zone and pedestrian route",
                    "marking": "Delineator cones or barriers"
                }
            ],
            "lighting": "Adequate lighting required for night works" if work_hours != "7am-5pm" else "Standard daylight visibility",
            "accessibility": {
                "dda_compliance": dda_compliant,
                "requirements": [
                    "DDA compliant pedestrian ramps at kerb transitions",
                    "Minimum 1.2m clear width maintained throughout",
                    "Tactile ground surface indicators (TGSI) where required",
                    "Clear signage at decision points",
                    "Assistance available from traffic controllers"
                ] if dda_compliant else ["Basic pedestrian access maintained"]
            }
        },
        
        "duration_and_staging": {
            "total_duration_days": duration_days,
            "work_hours": work_hours,
            "staging": [
                {
                    "stage": 1,
                    "description": "Set up signage and barriers",
                    "duration": "0.5 hours"
                },
                {
                    "stage": 2,
                    "description": "Establish detour route/retained access",
                    "duration": "1 hour"
                },
                {
                    "stage": 3,
                    "description": "Commence works",
                    "duration": f"{duration_days} days"
                },
                {
                    "stage": 4,
                    "description": "Remove traffic management and restore",
                    "duration": "1 hour"
                }
            ]
        },
        
        "compliance": {
            "standards": [
                "AS 1742.3:2019 - Manual of uniform traffic control devices, Part 3: Traffic control for works on roads",
                "SA DIT Field Guide Version 9.1 2021",
                "Disability Discrimination Act 1992 (DDA)",
                "Work Health and Safety Act 2012"
            ],
            "approvals_required": [
                "Local Council/Road Authority permit",
                "Public liability insurance",
                "Traffic controller accreditation (all personnel)"
            ]
        },
        
        "emergency_procedures": {
            "emergency_access": "Maintain clear emergency vehicle access at all times",
            "incident_response": [
                "Immediately notify site supervisor",
                "Call 000 for emergencies",
                "Provide first aid if qualified",
                "Preserve incident scene",
                "Complete incident report"
            ],
            "emergency_contacts": {
                "site_supervisor": "TBC",
                "traffic_management_company": "TBC",
                "local_council": "TBC",
                "emergency_services": "000"
            }
        },
        
        "alternative_signage": {
            "note": "If standard multi-message signs unavailable, use framed signs",
            "alternatives": [
                {"standard": "FOOTPATH CLOSED", "alternative": "Framed sign: FOOTPATH CLOSED"},
                {"standard": "USE OTHER FOOTPATH", "alternative": "Framed sign: USE OTHER FOOTPATH with arrow"},
                {"standard": "PEDESTRIANS WATCH YOUR STEP", "alternative": "Framed sign: WATCH YOUR STEP"}
            ]
        }
    }
    
    return plan


def _generate_footpath_signage(closure_type: str, dda_compliant: bool) -> List[Dict]:
    """Generate required signage based on closure type"""
    
    base_signage = [
        {
            "sign_code": "TC-2850",
            "sign_name": "PEDESTRIANS",
            "quantity": 2,
            "locations": ["Start of detour", "Decision points"],
            "size": "600mm x 600mm",
            "mounting": "Temporary stand or existing post"
        }
    ]
    
    if closure_type == "full":
        signage = base_signage + [
            {
                "sign_code": "TC-2851",
                "sign_name": "FOOTPATH CLOSED",
                "quantity": 2,
                "locations": ["At closure points (both ends)"],
                "size": "600mm x 450mm",
                "mounting": "Temporary stand"
            },
            {
                "sign_code": "TC-2852",
                "sign_name": "USE OTHER FOOTPATH",
                "quantity": 2,
                "locations": ["Directing to detour route"],
                "size": "600mm x 450mm",
                "mounting": "Temporary stand with directional arrow"
            }
        ]
    else:
        signage = base_signage + [
            {
                "sign_code": "TC-2855",
                "sign_name": "PEDESTRIANS WATCH YOUR STEP",
                "quantity": 2,
                "locations": ["At work zone edges"],
                "size": "600mm x 450mm",
                "mounting": "Temporary stand"
            }
        ]
    
    if dda_compliant:
        signage.append({
            "sign_code": "CUSTOM",
            "sign_name": "DDA ACCESSIBLE ROUTE",
            "quantity": 1,
            "locations": ["At detour entry point"],
            "size": "600mm x 450mm",
            "mounting": "Temporary stand",
            "note": "International Symbol of Access (ISA) wheelchair symbol"
        })
    
    return signage


def _get_controller_positions(closure_type: str) -> List[str]:
    """Determine traffic controller positions based on closure type"""
    
    if closure_type == "full":
        return [
            "At detour entry point (north/upstream end)",
            "At detour exit point (south/downstream end)",
            "Roving position for pedestrian assistance"
        ]
    else:
        return [
            "At work zone edge (managing pedestrian flow)",
            "Roving position for assistance and monitoring"
        ]


def generate_pedestrian_detour_diagram_data(
    location: str,
    detour_length: float,
    detour_width: float,
    road_name: str,
    intersecting_street: Optional[str] = None
) -> Dict:
    """
    Generate data for creating a pedestrian detour diagram
    
    Returns structured data that can be used to render a visual diagram
    """
    
    return {
        "diagram_type": "pedestrian_detour",
        "location": location,
        "road_name": road_name,
        "intersecting_street": intersecting_street,
        "detour_specifications": {
            "length": detour_length,
            "width": detour_width,
            "route_description": f"Detour via {intersecting_street}" if intersecting_street else "On-road detour"
        },
        "elements": {
            "work_zone": {
                "type": "polygon",
                "fill_color": "#FFD700",
                "border_color": "#FF0000",
                "label": "WORK AREA"
            },
            "footpath_closed": {
                "type": "line",
                "color": "#FF0000",
                "style": "dashed",
                "width": 3,
                "label": "CLOSED FOOTPATH"
            },
            "detour_route": {
                "type": "line",
                "color": "#00FF00",
                "style": "solid",
                "width": 4,
                "arrows": True,
                "label": "PEDESTRIAN DETOUR"
            },
            "dda_ramps": {
                "type": "marker",
                "symbol": "ramp",
                "color": "#0000FF",
                "locations": ["detour_entry", "detour_exit"]
            },
            "safety_barriers": {
                "type": "line",
                "color": "#FFA500",
                "style": "solid",
                "width": 2,
                "label": "SAFETY BARRIERS"
            }
        },
        "legend": {
            "Traffic Controller": {"symbol": "person", "color": "#FFFF00"},
            "Pedestrian Route": {"symbol": "arrow", "color": "#00FF00"},
            "DDA Compliant Ramp": {"symbol": "ramp", "color": "#0000FF"},
            "Safety Zone": {"symbol": "hatched", "color": "#FFA500"},
            "Work Area": {"symbol": "solid", "color": "#FFD700"},
            "Closed Footpath": {"symbol": "dashed_line", "color": "#FF0000"}
        }
    }
