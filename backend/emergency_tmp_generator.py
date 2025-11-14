"""
Emergency Traffic Management Plan Generator
Based on SA State Emergency Management Plan (SEMP) Part 2

Generates specialized TMPs for emergency situations including:
- Natural disasters (bushfires, floods, storms)
- Road accidents and incidents
- Utility emergencies
- Tiered access control systems
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class EmergencyTier(Enum):
    """Emergency access tiers based on risk levels"""
    TIER_1 = "Emergency Services Only (Extreme Risk)"
    TIER_2 = "Essential Services, Media with escort (High Risk)"
    TIER_3 = "Bona Fide Residents/Landowners, Relief/Recovery Services, Media (Medium Risk)"
    TIER_4 = "Residents, Relief/Recovery Services, Media (Low Risk)"
    TIER_5 = "Road Open with Caution (Very Low Risk)"


def generate_emergency_tmp(
    emergency_type: str,
    location: str,
    initial_tier: EmergencyTier = EmergencyTier.TIER_1,
    affected_roads: List[str] = None,
    control_agency: str = "TBC",
    incident_controller: str = "TBC"
) -> Dict:
    """
    Generate an Emergency Traffic Management Plan
    
    Args:
        emergency_type: Type of emergency (bushfire, flood, accident, etc.)
        location: Location of emergency
        initial_tier: Initial access tier (default: TIER_1 - Emergency Services Only)
        affected_roads: List of affected roads
        control_agency: Primary control agency (e.g., CFS, SES, SAPOL)
        incident_controller: Name of incident controller
    """
    
    affected_roads = affected_roads or []
    
    plan = {
        "plan_type": "Emergency Traffic Management Plan",
        "plan_id": f"EMERGENCY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "emergency_type": emergency_type,
        "location": location,
        "generated_date": datetime.now().isoformat(),
        "incident_details": {
            "control_agency": control_agency,
            "incident_controller": incident_controller,
            "affected_roads": affected_roads,
            "current_access_tier": initial_tier.value
        },
        
        "guiding_principles": {
            "primacy_of_life": "Safety of responders and the public is the highest priority",
            "risk_based_approach": "All decisions based on continual risk assessment",
            "flexibility": "Plans must be promptly implemented and adaptable to changing circumstances",
            "community_safety": "Balance between public safety and community access needs"
        },
        
        "access_tier_system": _generate_tier_system(),
        
        "road_closure_management": {
            "closure_authority": {
                "primary": control_agency,
                "support": "SA Police (SAPOL)",
                "consultation_required": [
                    "Traffic Management Centre (TMC)",
                    "Relevant Local Councils",
                    "Department of Infrastructure and Transport (DIT)"
                ]
            },
            "closure_procedures": [
                {
                    "step": 1,
                    "action": "Determine need for road closure based on risk assessment",
                    "responsible": "Control Agency / Incident Controller"
                },
                {
                    "step": 2,
                    "action": "Advise SAPOL and request support for road closures",
                    "responsible": "Control Agency"
                },
                {
                    "step": 3,
                    "action": "Implement physical closures using appropriate signage and barriers",
                    "responsible": "Control Agency with SAPOL support",
                    "standards": "AS 1742.3:2019, WHS requirements"
                },
                {
                    "step": 4,
                    "action": "Notify TMC and relevant councils of closures",
                    "responsible": "Control Agency / SAPOL"
                },
                {
                    "step": 5,
                    "action": "Communicate closures to public via multiple channels",
                    "responsible": "Public Information FSG"
                },
                {
                    "step": 6,
                    "action": "Record closure details in Incident Log",
                    "responsible": "IMT Logistics"
                }
            ],
            "signage_requirements": _get_emergency_closure_signage(),
            "heavy_vehicle_management": {
                "requirement": "Consultation with councils required before detouring heavy vehicles onto local roads",
                "detour_planning": "Must consider bridge capacities, road widths, and load limits"
            }
        },
        
        "controlled_access_management": {
            "purpose": "Facilitate community recovery while maintaining safety",
            "authorization_process": [
                "Access request submitted to Control Agency",
                "Bona fide reasons must be provided",
                "Control Agency reviews against current risk tier",
                "Consultation with Functional Support Groups and Road Authorities",
                "Authorization granted/denied with documentation"
            ],
            "authorized_access_categories": _get_authorized_access_categories(),
            "media_access": {
                "tier_allowed": "Tier 2 and above",
                "requirements": [
                    "Accreditation required",
                    "Appropriate PPE mandatory",
                    "Escort required at Tier 2",
                    "Authorization from Incident Controller",
                    "Consideration of resident access fairness"
                ]
            }
        },
        
        "risk_assessment_framework": {
            "process": [
                "Identify hazards (primary and secondary)",
                "Analyze risk level (likelihood x consequence)",
                "Evaluate against risk matrix",
                "Implement treatment/mitigation",
                "Monitor and review continually"
            ],
            "primary_hazards": _get_primary_hazards(emergency_type),
            "secondary_hazards": [
                "Fallen trees and vegetation",
                "Downed power lines",
                "Damaged road infrastructure (bridges, culverts, signs)",
                "Road surface damage (washouts, debris, erosion)",
                "Reduced visibility (smoke, dust, heavy rain)",
                "Flooding and water over roads",
                "Unstable ground conditions",
                "Wildlife hazards"
            ],
            "risk_matrix": _generate_risk_matrix()
        },
        
        "reopening_procedures": {
            "goal": "Reopen roads to community as soon as safe",
            "staged_approach": True,
            "key_considerations": [
                "Has the risk reduced to acceptable levels?",
                "Weather forecast (consult Bureau of Meteorology)",
                "Road structural integrity",
                "Clearance of hazards (trees, power lines, debris)",
                "Bridge and culvert condition",
                "Road furniture status (signs, barriers, line marking)",
                "Day vs night safety considerations",
                "Temporary speed restrictions required?",
                "Traffic control measures needed?"
            ],
            "assessment_checklist": [
                {"item": "Emergency risk reduced", "verified_by": "Control Agency"},
                {"item": "Weather conditions favorable", "verified_by": "BoM consultation"},
                {"item": "Road traversed by emergency services", "verified_by": "Emergency Services"},
                {"item": "Road surface sound", "verified_by": "DIT/Council"},
                {"item": "Hazards cleared", "verified_by": "Control Agency"},
                {"item": "Temporary controls in place", "verified_by": "SAPOL/TMC"},
                {"item": "Public advised of restrictions", "verified_by": "Public Information FSG"}
            ],
            "handover": "Formal advice from Incident Controller to relevant road authority (DIT/Council) when roads are safe to reopen"
        },
        
        "responsibilities": {
            "control_agency": [
                "Determine need for road closures",
                "Implement closures (with SAPOL if available)",
                "Provide ongoing advice on closures and openings",
                "Advise appropriate Tier of Road Closure",
                "Provide predictive information about emergency",
                "Provide information to community",
                "Authorize controlled access",
                "Liaise with IMT, SAPOL, TMC, councils"
            ],
            "sapol": [
                "Attend emergencies when requested",
                "Support road closures",
                "Provide liaison officer to IMT and TMC",
                "Determine need for additional closures",
                "Record and share road closure information",
                "Independent authority to close roads and divert traffic"
            ],
            "tmc": [
                "Overall management of road network",
                "Collate and display road closures",
                "Share information with SAPOL",
                "Optimize traffic flow during emergency"
            ],
            "councils": [
                "Advise TMC of implemented closures",
                "Advise TMC of road works",
                "Provide local road condition information",
                "Participate in reopening assessments"
            ]
        },
        
        "communication_strategy": {
            "channels": [
                "Public Information Functional Support Group",
                "SA Police website",
                "Control Agency websites",
                "Department of Infrastructure and Transport website",
                "Social media (Facebook, Twitter)",
                "Mainstream media (TV, radio, print)",
                "Community meetings",
                "Direct resident contact (door-knock if safe)"
            ],
            "mapping": {
                "purpose": "Provide visual information on road status",
                "color_coding": {
                    "Red": "Closed (Safety Issues - Tier 1)",
                    "Orange": "Access being assessed (Tier 2)",
                    "Yellow": "Approved access allowed (Tier 3)",
                    "Green": "Open to access, caution required (Tier 4)",
                    "No Color": "Open with caution (Tier 5)"
                },
                "update_frequency": "As conditions change, minimum every 4 hours"
            },
            "residual_risk_advice": [
                "Hazardous trees may fall",
                "Downed or damaged power lines present",
                "Road signs may be damaged or missing",
                "Conditions may worsen",
                "Flooding or water over roads",
                "Ground may be unstable",
                "Smoke or poor visibility",
                "Wildlife on roads",
                "Emergency vehicles may be present"
            ]
        },
        
        "incident_management_team": {
            "structure": "Established under SEMP",
            "key_positions": [
                "Incident Controller",
                "Operations Officer",
                "Logistics Officer",
                "Planning Officer",
                "Public Information Officer",
                "SAPOL Liaison",
                "TMC Liaison",
                "Council Liaison"
            ],
            "meetings": "Regular situation reports and decision-making meetings"
        },
        
        "compliance": {
            "legislation": [
                "Emergency Management Act 2004",
                "Fire and Emergency Services Act 2005",
                "Australian Road Rules",
                "Work Health and Safety Act 2012"
            ],
            "standards": [
                "AS 1742.3:2019 - Traffic control for works on roads",
                "State Emergency Management Plan (SEMP) Part 2"
            ],
            "powers": {
                "road_closure": "Fire and Emergency Services Act 2005 s27(1)(e), Australian Road Rules rule 305",
                "emergency_coordinator": "Emergency Management Act 2004 s25, s26"
            }
        },
        
        "documentation_requirements": {
            "incident_log": "All decisions, actions, and communications recorded",
            "closure_records": "Details of all road closures including time, location, tier, reason",
            "access_authorizations": "Record of all authorized access with names, times, purposes",
            "risk_assessments": "Documented risk assessments for closures and reopenings",
            "handovers": "Formal handover documentation when roads returned to authorities"
        }
    }
    
    return plan


def _generate_tier_system() -> Dict:
    """Generate the 5-tier access control system"""
    return {
        "tier_1": {
            "name": "Emergency Services Only",
            "risk_level": "Extreme",
            "color_code": "Red",
            "allowed_access": ["Emergency services only"],
            "description": "Road closed due to extreme safety risk. Only emergency response personnel allowed.",
            "typical_scenarios": [
                "Active bushfire impact",
                "Severe flooding over road",
                "Major structural failure",
                "Hazardous materials incident"
            ]
        },
        "tier_2": {
            "name": "Essential Services, Media with Escort",
            "risk_level": "High",
            "color_code": "Orange",
            "allowed_access": [
                "Emergency services",
                "Essential service crews (power, water, gas)",
                "Accredited media with escort"
            ],
            "description": "High risk - Essential services and escorted media only. Access being continually assessed.",
            "typical_scenarios": [
                "Post-emergency assessment phase",
                "Utility restoration in progress",
                "Hazards being cleared"
            ]
        },
        "tier_3": {
            "name": "Residents, Relief/Recovery, Media",
            "risk_level": "Medium",
            "color_code": "Yellow",
            "allowed_access": [
                "Emergency services",
                "Essential service crews",
                "Bona fide residents/landowners",
                "Relief and recovery services",
                "Accredited media"
            ],
            "description": "Medium risk - Residents can return. Approved access with authorization.",
            "typical_scenarios": [
                "Emergency contained, residual risks remain",
                "Resident return phase",
                "Recovery operations underway"
            ]
        },
        "tier_4": {
            "name": "Residents, Relief/Recovery, Media",
            "risk_level": "Low",
            "color_code": "Green",
            "allowed_access": [
                "All Tier 3 access",
                "Residents without restrictions",
                "Support services"
            ],
            "description": "Low risk - Road open to residents and support services. Caution required.",
            "typical_scenarios": [
                "Emergency resolved",
                "Minor hazards may remain",
                "Normal access resuming"
            ]
        },
        "tier_5": {
            "name": "Road Open with Caution",
            "risk_level": "Very Low",
            "color_code": "White/No Color",
            "allowed_access": ["General public"],
            "description": "Road open to all with caution advised. Minor residual risks may remain.",
            "typical_scenarios": [
                "Emergency fully resolved",
                "Normal conditions restored",
                "Advisory warnings only"
            ]
        }
    }


def _get_emergency_closure_signage() -> List[Dict]:
    """Generate emergency road closure signage requirements"""
    return [
        {
            "sign_code": "TC-2701",
            "sign_name": "ROAD CLOSED",
            "quantity": 2,
            "locations": ["Both ends of closure"],
            "size": "1200mm x 900mm (minimum)",
            "mounting": "On barricades or A-frame",
            "reflectivity": "Class 1 or 2 (emergency situations)",
            "mandatory": True
        },
        {
            "sign_code": "TC-2702",
            "sign_name": "EMERGENCY - ROAD CLOSED",
            "quantity": 2,
            "locations": ["Primary closure points"],
            "size": "1200mm x 900mm",
            "mounting": "Barricade or VMS board",
            "additional_info": "Tier level can be added",
            "mandatory": True
        },
        {
            "sign_code": "TC-2705",
            "sign_name": "DETOUR",
            "quantity": "As required",
            "locations": ["At detour route decision points"],
            "size": "900mm x 600mm",
            "mounting": "Temporary stand or VMS",
            "with_arrows": True
        },
        {
            "sign_code": "TC-2710",
            "sign_name": "AUTHORIZED VEHICLES ONLY",
            "quantity": 2,
            "locations": ["At controlled access points"],
            "size": "900mm x 600mm",
            "mounting": "With barricade",
            "supplementary": "TIER [X] ACCESS"
        },
        {
            "sign_code": "VMS",
            "sign_name": "Variable Message Sign",
            "quantity": "As available",
            "locations": ["Approach routes to closure"],
            "messages": [
                "EMERGENCY AHEAD",
                "ROAD CLOSED",
                "USE ALTERNATE ROUTE",
                "EMERGENCY SERVICES ONLY"
            ],
            "preferred": True
        }
    ]


def _get_authorized_access_categories() -> Dict:
    """Define categories of authorized access"""
    return {
        "emergency_services": {
            "description": "Emergency response personnel",
            "includes": ["Police", "Fire", "Ambulance", "SES", "CFS", "Other emergency services"],
            "minimum_tier": 1,
            "identification_required": "Emergency services ID and uniform"
        },
        "essential_services": {
            "description": "Critical utility and infrastructure crews",
            "includes": ["SA Power Networks", "SA Water", "Gas crews", "Telecommunications"],
            "minimum_tier": 2,
            "identification_required": "Company ID and vehicle livery"
        },
        "accredited_media": {
            "description": "News media with appropriate accreditation",
            "includes": ["TV", "Radio", "Print", "Online news"],
            "minimum_tier": 2,
            "requirements": ["Accreditation", "PPE", "Escort (Tier 2)", "Incident Controller authorization"]
        },
        "residents_landowners": {
            "description": "Bona fide residents and property owners",
            "includes": ["Permanent residents", "Property owners", "Essential property managers"],
            "minimum_tier": 3,
            "identification_required": "Proof of residency or ownership"
        },
        "relief_recovery": {
            "description": "Relief and recovery service providers",
            "includes": ["Red Cross", "Salvation Army", "Council recovery teams", "Insurance assessors"],
            "minimum_tier": 3,
            "authorization": "Required from Control Agency"
        }
    }


def _get_primary_hazards(emergency_type: str) -> List[str]:
    """Get primary hazards based on emergency type"""
    hazard_map = {
        "bushfire": [
            "Active fire front",
            "Radiant heat",
            "Smoke and poor visibility",
            "Falling trees and embers",
            "Extreme fire weather conditions"
        ],
        "flood": [
            "Water over road",
            "Swift water currents",
            "Submerged hazards",
            "Road washouts and erosion",
            "Ongoing rainfall"
        ],
        "storm": [
            "High winds",
            "Falling trees and branches",
            "Flying debris",
            "Downed power lines",
            "Lightning"
        ],
        "accident": [
            "Vehicle debris on road",
            "Fuel or chemical spills",
            "Traffic congestion",
            "Secondary collision risk",
            "Distraction to motorists"
        ],
        "hazmat": [
            "Chemical contamination",
            "Toxic fumes or gases",
            "Explosion risk",
            "Fire risk",
            "Environmental contamination"
        ]
    }
    
    return hazard_map.get(emergency_type.lower(), [
        "Unspecified emergency hazard",
        "Road safety compromised",
        "Public safety risk"
    ])


def _generate_risk_matrix() -> Dict:
    """Generate risk assessment matrix"""
    return {
        "likelihood_levels": {
            "1": "Rare - May occur only in exceptional circumstances",
            "2": "Unlikely - Could occur at some time",
            "3": "Possible - Might occur at some time",
            "4": "Likely - Will probably occur in most circumstances",
            "5": "Almost Certain - Expected to occur in most circumstances"
        },
        "consequence_levels": {
            "1": "Insignificant - No injuries, minimal damage",
            "2": "Minor - First aid treatment, minor damage",
            "3": "Moderate - Medical treatment required, localized damage",
            "4": "Major - Extensive injuries, significant damage",
            "5": "Catastrophic - Death or permanent disability, widespread damage"
        },
        "risk_ratings": {
            "1-5": "Extreme - Immediate action required",
            "6-12": "High - Senior management attention needed",
            "13-15": "Medium - Management attention required",
            "16-25": "Low - Manage by routine procedures"
        },
        "tier_mapping": {
            "Extreme (1-5)": "Tier 1 - Emergency Services Only",
            "High (6-12)": "Tier 2 - Essential Services, Media with escort",
            "Medium (13-15)": "Tier 3 - Residents, Relief, Media",
            "Low (16-20)": "Tier 4 - Residents, Relief, Media",
            "Very Low (21-25)": "Tier 5 - Road Open with Caution"
        }
    }
