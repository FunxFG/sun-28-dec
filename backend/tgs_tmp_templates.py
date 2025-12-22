"""
Complete TMP Templates for All 17 TGS Patterns
Based on GENERIC TGS PACKAGE 2026

Each TGS pattern has a corresponding TMP template that can be:
1. Used standalone
2. Combined with other patterns
3. Customized by user
"""

from typing import Dict, List, Any
from datetime import datetime


class TGSTMPTemplates:
    """Generate complete TMP content for each TGS pattern"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize all 17 TGS pattern TMP templates"""
        
        return {
            # ==================== STOP-SLOW OPERATIONS ====================
            
            "STOP_SLOW_LOW_TRAFFIC_LANE": {
                "name": "Stop-Slow 40-70km (Traffic Lane)",
                "generic_code": "Generic 1",
                "work_type": "Work in Traffic Lane",
                "description": "Work undertaken within a traffic lane on low-speed roads (40-70 km/h) with traffic controllers managing flow using Stop/Slow bats.",
                "requires_tc": True,
                "tc_count": 2,
                "speed_reduction": 40,
                "key_risks": [
                    "Worker struck by vehicle",
                    "Traffic controller struck by vehicle",
                    "Rear-end collision in queue",
                    "Public confusion at control point"
                ],
                "control_measures": [
                    "Qualified traffic controllers with current tickets",
                    "High-visibility PPE for all workers",
                    "Advance warning signs at 195m, 145m, 130m, 60m",
                    "Speed reduction to 40 km/h minimum 45m before work",
                    "15m safety buffer between workers and passing traffic",
                    "Prepare to Stop signs at 130m and 60m",
                    "Stop Here When Directed sign at control point"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 15,
                "work_zone_length_range": [15, 40]
            },
            
            "STOP_SLOW_HIGH_TRAFFIC_LANE": {
                "name": "Stop-Slow 80-110km (Traffic Lane)",
                "generic_code": "Generic 2",
                "work_type": "Work in Traffic Lane (High Speed)",
                "description": "Work undertaken within a traffic lane on high-speed roads (80-110 km/h) with traffic controllers.",
                "requires_tc": True,
                "tc_count": 2,
                "speed_reduction": 60,
                "key_risks": [
                    "Worker struck by vehicle at high speed",
                    "Traffic controller struck by vehicle",
                    "Rear-end collision in extended queue",
                    "Inadequate stopping distance"
                ],
                "control_measures": [
                    "Qualified traffic controllers with high-speed training",
                    "High-visibility PPE and additional reflective gear",
                    "Extended advance warning signs at 400m, 320m, 240m, 80m",
                    "Speed reduction to 60 km/h minimum 60m before work",
                    "30m safety buffer between workers and passing traffic",
                    "Prepare to Stop signs at 240m and 80m",
                    "Arrow board for additional visibility",
                    "Consider Truck Mounted Attenuator for high-speed protection"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [15, 40]
            },
            
            "STOP_SLOW_LOW_SHOULDER": {
                "name": "Stop-Slow 40-70km (Shoulder)",
                "generic_code": "Generic 3",
                "work_type": "Shoulder Works",
                "description": "Work in road shoulder or verge on low-speed roads with traffic control.",
                "requires_tc": True,
                "tc_count": 2,
                "speed_reduction": 40,
                "key_risks": [
                    "Worker struck by errant vehicle",
                    "Vehicle encroachment into shoulder",
                    "Traffic controller exposure"
                ],
                "control_measures": [
                    "Traffic controllers managing vehicle proximity",
                    "Advance warning at 195m, 145m",
                    "Delineation between work area and traffic",
                    "Speed reduction to 40 km/h",
                    "Lateral shift markers if work within 1.2m of traffic"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 20,
                "work_zone_length_range": [10, 30]
            },
            
            "STOP_SLOW_HIGH_SHOULDER": {
                "name": "Stop-Slow 80-110km (Shoulder)",
                "generic_code": "Generic 4",
                "work_type": "Shoulder Works (High Speed)",
                "description": "Work in road shoulder on high-speed roads with traffic control.",
                "requires_tc": True,
                "tc_count": 2,
                "speed_reduction": 60,
                "key_risks": [
                    "Worker struck by high-speed vehicle",
                    "Vehicle loss of control entering shoulder",
                    "Inadequate separation from traffic"
                ],
                "control_measures": [
                    "Traffic controllers with high-speed training",
                    "Extended advance warnings at 400m, 320m",
                    "Robust delineation and barriers",
                    "Speed reduction to 60 km/h",
                    "30m minimum safety buffer",
                    "Consider TMA for additional protection"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [15, 40]
            },
            
            # ==================== INTERSECTION PATTERNS ====================
            
            "ROUNDABOUT_LOW": {
                "name": "Roundabout 40-70km",
                "generic_code": "Generic 5",
                "work_type": "Roundabout Works",
                "description": "Traffic management for works at or near roundabouts on low-speed roads.",
                "requires_tc": True,
                "tc_count": 3,
                "speed_reduction": 40,
                "key_risks": [
                    "Multi-directional traffic conflicts",
                    "Reduced visibility at roundabout",
                    "Pedestrian/cyclist exposure",
                    "Side road traffic entering work zone"
                ],
                "control_measures": [
                    "Traffic controllers at key approach points",
                    "Advance warning on ALL approaches",
                    "'ON SIDE ROAD' signs on all side roads within work area",
                    "Speed reduction on all approaches",
                    "Additional signage for circulating traffic",
                    "Heightened pedestrian control measures"
                ],
                "special_requirements": [
                    "ON SIDE ROAD signs mandatory on all side roads",
                    "Consider all traffic movements through roundabout",
                    "Maintain sight distances"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 20,
                "work_zone_length_range": [15, 30]
            },
            
            "ROUNDABOUT_HIGH": {
                "name": "Roundabout 80-110km",
                "generic_code": "Generic 6",
                "work_type": "Roundabout Works (High Speed)",
                "description": "Traffic management for works at high-speed roundabouts.",
                "requires_tc": True,
                "tc_count": 3,
                "speed_reduction": 60,
                "key_risks": [
                    "High-speed approach conflicts",
                    "Extended stopping distances",
                    "Complex traffic movements",
                    "Side road traffic at speed"
                ],
                "control_measures": [
                    "Multiple traffic controllers coordinated via radio",
                    "Extended advance warnings at 400m, 320m on all approaches",
                    "'ON SIDE ROAD' signs on all side roads",
                    "Substantial speed reduction to 60 km/h",
                    "Enhanced delineation and visibility",
                    "Consider temporary traffic signals if feasible"
                ],
                "special_requirements": [
                    "ON SIDE ROAD signs mandatory",
                    "Radio communication between TCs essential",
                    "Extended setup area"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [15, 30]
            },
            
            "T_INTERSECTION_LOW": {
                "name": "T-Intersection 40-70km",
                "generic_code": "Generic 7",
                "work_type": "T-Intersection Works",
                "description": "Traffic management at T-intersections on low-speed roads.",
                "requires_tc": True,
                "tc_count": 2,
                "speed_reduction": 40,
                "key_risks": [
                    "Turning vehicle conflicts",
                    "Reduced visibility for turning traffic",
                    "Pedestrian conflicts at intersection",
                    "Queue spillback blocking intersection"
                ],
                "control_measures": [
                    "Traffic controllers on main and side road approaches",
                    "Advance warning on main road at 70m, 45m",
                    "Warning on perpendicular road approach",
                    "Speed reduction to 40 km/h",
                    "Maintain intersection sight lines",
                    "Consider pedestrian holding areas"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 20,
                "work_zone_length_range": [15, 30]
            },
            
            "T_INTERSECTION_HIGH": {
                "name": "T-Intersection 80-110km",
                "generic_code": "Generic 8",
                "work_type": "T-Intersection Works (High Speed)",
                "description": "Traffic management at T-intersections on high-speed roads.",
                "requires_tc": True,
                "tc_count": 3,
                "speed_reduction": 60,
                "key_risks": [
                    "High-speed turning movements",
                    "Extended sight distance requirements",
                    "Severe collision potential",
                    "Complex traffic control coordination"
                ],
                "control_measures": [
                    "Multiple coordinated traffic controllers",
                    "Extended advance warnings at 160m, 80m on main road",
                    "Advance warning on side road at 80m",
                    "Speed reduction to 60 km/h on all approaches",
                    "Enhanced delineation and arrow boards",
                    "Radio communication between TCs mandatory"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [15, 40]
            },
            
            # ==================== LANE CLOSURES ====================
            
            "LANE_CLOSURE_LOW_NO_MEDIAN": {
                "name": "Lane Closure 40-70km (No Median)",
                "generic_code": "Generic 9",
                "work_type": "Lane Closure - Undivided Road",
                "description": "Single lane closure on multi-lane undivided road with low speed limit.",
                "requires_tc": False,
                "uses_arrow_board": True,
                "speed_reduction": 40,
                "taper_length_range": [15, 110],
                "key_risks": [
                    "Merge conflicts at taper",
                    "Inadequate taper length causing sudden lane change",
                    "Worker exposure to passing traffic",
                    "Side swipe collisions in merge area"
                ],
                "control_measures": [
                    "Advance warning signs at 160m, 80m",
                    "Lane Status/Merge sign at 60m before taper",
                    "Speed reduction to 40 km/h at 45m",
                    "Arrow board showing merge direction at 30m",
                    "Taper length 15-110m depending on speed and proximity",
                    "Cone spacing 3-5m in taper",
                    "Work zone delineation at 10m intervals",
                    "End Road Work sign 50m after work zone"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [20, 100]
            },
            
            "LANE_CLOSURE_HIGH_NO_MEDIAN": {
                "name": "Lane Closure 80-110km (No Median)",
                "generic_code": "Generic 10",
                "work_type": "Lane Closure - Undivided Road (High Speed)",
                "description": "Single lane closure on high-speed undivided road.",
                "requires_tc": False,
                "uses_arrow_board": True,
                "uses_tma": True,
                "speed_reduction": 60,
                "taper_length_range": [145, 180],
                "key_risks": [
                    "High-speed merge conflicts",
                    "Inadequate advance warning",
                    "Collision with work zone at high speed",
                    "TMA impact events"
                ],
                "control_measures": [
                    "Extended advance warnings at 320m, 240m",
                    "Prepare to Stop signs at 160m, 80m",
                    "Lane Status/Merge sign at 80m",
                    "Speed reduction to 60 km/h at 60m",
                    "Arrow board at 45m",
                    "Extended taper 145-180m",
                    "Truck Mounted Attenuator (TMA) recommended",
                    "10m cone spacing in taper",
                    "Enhanced delineation throughout work zone"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [30, 150]
            },
            
            "LANE_CLOSURE_LOW_MEDIAN": {
                "name": "Lane Closure 40-70km (Raised Median)",
                "generic_code": "Generic 11",
                "work_type": "Lane Closure - Divided Road",
                "description": "Single lane closure on divided road with raised median.",
                "requires_tc": False,
                "uses_arrow_board": True,
                "speed_reduction": 40,
                "taper_length_range": [15, 110],
                "key_risks": [
                    "Merge conflicts in divided road environment",
                    "Reduced escape options due to median",
                    "Worker exposure with limited egress routes"
                ],
                "control_measures": [
                    "Advance warnings at 160m, 80m",
                    "Lane Status/Merge sign at 60m",
                    "Speed reduction to 40 km/h",
                    "Arrow board indicating merge direction",
                    "Taper length 15-110m",
                    "Median protection if work near median",
                    "Emergency egress plan required"
                ],
                "special_requirements": [
                    "Median barrier considerations",
                    "Limited emergency access - plan carefully"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [20, 100]
            },
            
            "LANE_CLOSURE_HIGH_MEDIAN": {
                "name": "Lane Closure 80-110km (Raised Median)",
                "generic_code": "Generic 10 (Median Variant)",
                "work_type": "Lane Closure - Divided Road (High Speed)",
                "description": "Single lane closure on high-speed divided road.",
                "requires_tc": False,
                "uses_arrow_board": True,
                "uses_tma": True,
                "speed_reduction": 60,
                "taper_length_range": [145, 180],
                "key_risks": [
                    "High-speed merge on divided road",
                    "Limited egress with median barrier",
                    "TMA deployment in constrained space",
                    "Extended queue management"
                ],
                "control_measures": [
                    "Extended advance warnings at 320m, 240m, 160m, 80m",
                    "Speed reduction to 60 km/h at 60m",
                    "Long taper 145-180m",
                    "TMA protection recommended",
                    "Enhanced arrow board visibility",
                    "Emergency access plan with median considerations"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [30, 150]
            },
            
            # ==================== CONTRA FLOW ====================
            
            "CONTRA_FLOW_LOW": {
                "name": "Contra Flow 40-70km",
                "generic_code": "Generic 12",
                "work_type": "Contra Flow Operations",
                "description": "Two-way traffic operating in single lane due to lane closure.",
                "requires_tc": True,
                "tc_count": 4,
                "speed_reduction": 40,
                "key_risks": [
                    "Head-on collision in contra flow section",
                    "Driver confusion navigating unfamiliar traffic pattern",
                    "Inadequate separation between opposing flows",
                    "TC coordination failure"
                ],
                "control_measures": [
                    "Traffic controllers at both ends coordinated via radio",
                    "Two-Way Traffic Ahead signs at 145m",
                    "Speed reduction to 40 km/h maximum",
                    "Centerline delineation with bollards",
                    "Minimum 3m width per direction",
                    "Limited contra flow section length",
                    "Clear sight lines through section mandatory"
                ],
                "special_requirements": [
                    "Radio communication between TCs essential",
                    "Maximum contra flow length: 100m for low speed",
                    "Both TCs must have clear sight lines"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [20, 100]
            },
            
            "CONTRA_FLOW_HIGH": {
                "name": "Contra Flow 80-110km",
                "generic_code": "Generic 13",
                "work_type": "Contra Flow Operations (High Speed)",
                "description": "Contra flow on high-speed roads - highest risk TGS pattern.",
                "requires_tc": True,
                "tc_count": 4,
                "speed_reduction": 60,
                "key_risks": [
                    "High-speed head-on collision potential - CRITICAL RISK",
                    "Extended stopping distances",
                    "Driver panic in unfamiliar arrangement",
                    "Complex TC coordination requirements"
                ],
                "control_measures": [
                    "Minimum 4 qualified traffic controllers with radio communication",
                    "Extended advance warnings at 400m, 320m, 160m",
                    "Two-Way Traffic Ahead signs prominently displayed",
                    "Mandatory speed reduction to 60 km/h maximum",
                    "Robust centerline delineation",
                    "Enhanced lighting if any night work",
                    "Supervisor on site during operation",
                    "Minimize contra flow section length"
                ],
                "special_requirements": [
                    "Maximum contra flow length: 50m for high speed",
                    "Consider alternative arrangements (full closure) if possible",
                    "Supervisor presence mandatory"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "work_zone_length_range": [20, 50]
            },
            
            # ==================== ROAD CLOSURES ====================
            
            "ROAD_CLOSURE_DETOUR": {
                "name": "Road Closure with Detour",
                "generic_code": "Generic 14",
                "work_type": "Complete Road Closure",
                "description": "Full road closure with detour route for through traffic.",
                "requires_tc": True,
                "tc_count": 2,
                "speed_reduction": 40,
                "key_risks": [
                    "Driver non-compliance with closure",
                    "Inadequate detour signage causing confusion",
                    "Local access conflicts",
                    "Emergency vehicle access delays"
                ],
                "control_measures": [
                    "ROAD CLOSED signs at closure point",
                    "Road Closed Ahead signs at 195m, 145m",
                    "DETOUR signs showing alternative route",
                    "LOCAL TRAFFIC ONLY where applicable",
                    "Physical barriers preventing vehicle entry",
                    "Speed reductions on detour route if required",
                    "Emergency access plan documented",
                    "Local resident notification"
                ],
                "special_requirements": [
                    "Detour route capacity assessment required",
                    "Emergency service notification mandatory",
                    "Consider impact on local businesses",
                    "Maintain pedestrian access where possible"
                ],
                "work_zone_length_range": [10, 500]
            },
            
            "ROAD_CLOSURE_COURT_BOWL": {
                "name": "Court Bowl Closure",
                "generic_code": "Generic 15",
                "work_type": "Cul-de-sac/Court Bowl Closure",
                "description": "Closure of cul-de-sac or court bowl with local access management.",
                "requires_tc": False,
                "speed_reduction": 40,
                "key_risks": [
                    "Local resident access restrictions",
                    "Emergency vehicle access limitations",
                    "Service vehicle disruption",
                    "Resident non-compliance"
                ],
                "control_measures": [
                    "ROAD CLOSED sign at entry",
                    "LOCAL TRAFFIC ONLY signage",
                    "Advance notification to all residents minimum 48 hours",
                    "Maintain pedestrian access",
                    "Emergency vehicle access maintained or alternative provided",
                    "Temporary vehicle access windows if required"
                ],
                "special_requirements": [
                    "Resident notification mandatory",
                    "Emergency service consultation",
                    "Access windows for residents/services",
                    "Complaint management process"
                ],
                "work_zone_length_range": [20, 100]
            },
            
            # ==================== PEDESTRIAN ====================
            
            "FOOTPATH_CLOSURE": {
                "name": "Footpath Works",
                "generic_code": "Generic 16",
                "work_type": "Footpath/Pedestrian Management",
                "description": "Footpath closure with DDA-compliant pedestrian management.",
                "requires_tc": False,
                "key_risks": [
                    "Pedestrian forced into traffic",
                    "DDA non-compliance",
                    "Trip hazards in alternative route",
                    "Inadequate pedestrian protection"
                ],
                "control_measures": [
                    "FOOTPATH CLOSED signage at closure point",
                    "Advance warning 20m before closure",
                    "DDA-compliant alternative route provided",
                    "Pedestrian barriers along closure",
                    "2m minimum width for pedestrian detour",
                    "PEDESTRIANS WATCH YOUR STEP signs",
                    "Tactile indicators for vision-impaired",
                    "Ensure alternative route is accessible, well-lit, and safe"
                ],
                "special_requirements": [
                    "DDA compliance mandatory",
                    "Alternative route assessment required",
                    "Consider mobility-impaired users",
                    "Maintain access to key destinations (shops, bus stops, crossings)"
                ],
                "work_zone_length_range": [5, 50]
            },
            
            # ==================== LATERAL SHIFT ====================
            
            "LATERAL_SHIFT_LOW": {
                "name": "Lateral Shift 40-70km",
                "generic_code": "Lateral Shift (Low Speed)",
                "work_type": "Lateral Traffic Shift",
                "description": "Traffic shifted sideways using Lateral Shift Markers (LSM) to create work space without closing lanes.",
                "requires_tc": False,
                "uses_arrow_board": False,
                "speed_reduction": 40,
                "key_risks": [
                    "Vehicle encroachment into work area during shift",
                    "Driver confusion with shifted lane alignment",
                    "Insufficient lateral clearance to workers",
                    "LSM marker strike by vehicles",
                    "Inadequate shift taper causing sudden movement"
                ],
                "control_measures": [
                    "Advance warning signs at 160m, 80m",
                    "Lateral Shift Markers (LSM) at 15m spacing",
                    "Gradual shift taper over 30m",
                    "Speed reduction to 40 km/h",
                    "Minimum 1.5m lateral shift distance",
                    "Maintain minimum 3m lane width during shift",
                    "Enhanced delineation throughout shift section",
                    "Worker positioning outside shifted traffic path",
                    "End Road Work sign after shift returns to normal"
                ],
                "special_requirements": [
                    "LSM spacing based on worker-to-traffic proximity per AS 1742.3 Table",
                    "Minimum shift distance: 0.5m at 40km/h, 1.0m at 60km/h",
                    "Gradual shift and return tapers mandatory",
                    "Maintain sight lines through shift"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 20,
                "lateral_shift_distance": 1.5,
                "lsm_spacing": 15,
                "shift_taper_length": 30,
                "work_zone_length_range": [30, 150]
            },
            
            "LATERAL_SHIFT_HIGH": {
                "name": "Lateral Shift 80-110km",
                "generic_code": "Lateral Shift (High Speed)",
                "work_type": "Lateral Traffic Shift (High Speed)",
                "description": "High-speed lateral shift using LSM - requires extended tapers and increased shift distance.",
                "requires_tc": False,
                "uses_arrow_board": True,
                "speed_reduction": 60,
                "key_risks": [
                    "High-speed vehicle loss of control in shift",
                    "Inadequate shift taper length for speed",
                    "Worker exposure at high-speed proximity",
                    "LSM strike at high speed causing injury",
                    "Extended shift section causing driver fatigue/inattention"
                ],
                "control_measures": [
                    "Extended advance warnings at 320m, 160m",
                    "Arrow board showing shift direction at 80m",
                    "Lateral Shift Markers (LSM) at 25m spacing minimum",
                    "Extended shift taper over 60m minimum",
                    "Speed reduction to 60 km/h",
                    "Minimum 2.0m lateral shift for high-speed separation",
                    "Enhanced LSM reflectivity for visibility",
                    "Maintain minimum 3m lane width",
                    "Longer shift sections require additional warnings",
                    "End shift with gradual return taper"
                ],
                "special_requirements": [
                    "LSM spacing: 25m minimum for high-speed",
                    "Shift distance: 1.0m minimum at speeds over 60km/h",
                    "Extended taper lengths: 60m+ for speeds over 80km/h",
                    "Arrow board recommended for high-speed shifts",
                    "Consider safety barriers for shifts > 2m",
                    "Limit shift section length on high-speed roads"
                ],
                "minimum_lane_width": 3.0,
                "safety_buffer": 30,
                "lateral_shift_distance": 2.0,
                "lsm_spacing": 25,
                "shift_taper_length": 60,
                "work_zone_length_range": [50, 200]
            },
        }
    
    def get_template(self, tgs_pattern_id: str) -> Dict[str, Any]:
        """Get TMP template for a specific TGS pattern"""
        return self.templates.get(tgs_pattern_id, {})
    
    def combine_templates(self, tgs_pattern_ids: List[str]) -> Dict[str, Any]:
        """
        Combine multiple TMP templates into a single comprehensive TMP
        
        Args:
            tgs_pattern_ids: List of TGS pattern IDs to combine
        
        Returns:
            Combined TMP with merged risks, controls, and requirements
        """
        if not tgs_pattern_ids:
            return {}
        
        combined = {
            "patterns_included": [],
            "combined_name": "",
            "combined_description": "",
            "requires_tc": False,
            "tc_count_total": 0,
            "speed_reduction_minimum": 110,  # Will be reduced to lowest required
            "all_risks": [],
            "all_control_measures": [],
            "all_special_requirements": [],
            "uses_arrow_board": False,
            "uses_tma": False,
            "minimum_lane_width": 3.0,
            "safety_buffer_maximum": 0,
            "work_zone_length_range": [0, 0]
        }
        
        for pattern_id in tgs_pattern_ids:
            template = self.get_template(pattern_id)
            if not template:
                continue
            
            combined["patterns_included"].append({
                "id": pattern_id,
                "name": template.get("name"),
                "generic_code": template.get("generic_code")
            })
            
            # Combine requirements
            if template.get("requires_tc"):
                combined["requires_tc"] = True
                combined["tc_count_total"] += template.get("tc_count", 0)
            
            if template.get("uses_arrow_board"):
                combined["uses_arrow_board"] = True
            
            if template.get("uses_tma"):
                combined["uses_tma"] = True
            
            # Use most restrictive speed reduction
            if template.get("speed_reduction"):
                combined["speed_reduction_minimum"] = min(
                    combined["speed_reduction_minimum"],
                    template["speed_reduction"]
                )
            
            # Use maximum safety buffer
            if template.get("safety_buffer"):
                combined["safety_buffer_maximum"] = max(
                    combined["safety_buffer_maximum"],
                    template["safety_buffer"]
                )
            
            # Combine risks (deduplicate)
            for risk in template.get("key_risks", []):
                if risk not in combined["all_risks"]:
                    combined["all_risks"].append(risk)
            
            # Combine control measures (deduplicate)
            for control in template.get("control_measures", []):
                if control not in combined["all_control_measures"]:
                    combined["all_control_measures"].append(control)
            
            # Combine special requirements
            for req in template.get("special_requirements", []):
                if req not in combined["all_special_requirements"]:
                    combined["all_special_requirements"].append(req)
            
            # Expand work zone length range
            template_range = template.get("work_zone_length_range", [0, 0])
            if combined["work_zone_length_range"][0] == 0:
                combined["work_zone_length_range"] = template_range
            else:
                combined["work_zone_length_range"] = [
                    min(combined["work_zone_length_range"][0], template_range[0]),
                    max(combined["work_zone_length_range"][1], template_range[1])
                ]
        
        # Create combined name and description
        pattern_names = [p["name"] for p in combined["patterns_included"]]
        combined["combined_name"] = " + ".join(pattern_names)
        combined["combined_description"] = f"Multi-pattern TMP combining {len(pattern_names)} TGS patterns: " + ", ".join([p["generic_code"] for p in combined["patterns_included"]])
        
        return combined


# API Endpoint Helper Functions

def generate_tmp_for_tgs_pattern(
    tgs_pattern_id: str,
    location: str,
    work_details: Dict[str, Any],
    company_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate complete TMP content for a single TGS pattern
    
    Args:
        tgs_pattern_id: ID of the TGS pattern (e.g., 'LANE_CLOSURE_LOW_NO_MEDIAN')
        location: Work site location
        work_details: User's work details
        company_details: User's company information
    
    Returns:
        Complete TMP sections ready for PDF generation
    """
    templates = TGSTMPTemplates()
    template = templates.get_template(tgs_pattern_id)
    
    if not template:
        return {"error": "TGS pattern not found"}
    
    # Build TMP sections
    tmp_content = {
        "pattern_info": {
            "name": template["name"],
            "generic_code": template["generic_code"],
            "description": template["description"]
        },
        "work_description": {
            "work_type": template["work_type"],
            "location": location,
            "typical_duration": work_details.get("duration", "Variable")
        },
        "traffic_control_requirements": {
            "requires_traffic_controllers": template.get("requires_tc", False),
            "number_of_tcs": template.get("tc_count", 0),
            "uses_arrow_board": template.get("uses_arrow_board", False),
            "uses_tma": template.get("uses_tma", False),
            "speed_reduction_to": template.get("speed_reduction"),
            "minimum_lane_width_m": template.get("minimum_lane_width"),
            "safety_buffer_m": template.get("safety_buffer")
        },
        "risk_assessment": {
            "key_risks": template.get("key_risks", []),
            "control_measures": template.get("control_measures", []),
            "residual_risk_rating": "Medium" if template.get("requires_tc") else "Low"
        },
        "special_requirements": template.get("special_requirements", []),
        "device_schedule": {
            "taper_length_range_m": template.get("taper_length_range"),
            "work_zone_length_range_m": template.get("work_zone_length_range")
        }
    }
    
    return tmp_content


def generate_combined_tmp_for_multiple_patterns(
    tgs_pattern_ids: List[str],
    location: str,
    work_details: Dict[str, Any],
    company_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate combined TMP for multiple TGS patterns
    
    This intelligently merges TMPs from multiple patterns into a single
    comprehensive TMP document.
    """
    templates = TGSTMPTemplates()
    combined = templates.combine_templates(tgs_pattern_ids)
    
    if not combined:
        return {"error": "No valid TGS patterns provided"}
    
    tmp_content = {
        "pattern_info": {
            "name": combined["combined_name"],
            "patterns_count": len(combined["patterns_included"]),
            "patterns": combined["patterns_included"],
            "description": combined["combined_description"]
        },
        "work_description": {
            "work_type": "Multi-Pattern Traffic Management",
            "location": location,
            "patterns_applied": [p["generic_code"] for p in combined["patterns_included"]]
        },
        "traffic_control_requirements": {
            "requires_traffic_controllers": combined["requires_tc"],
            "total_tcs_required": combined["tc_count_total"],
            "uses_arrow_board": combined["uses_arrow_board"],
            "uses_tma": combined["uses_tma"],
            "speed_reduction_to": combined["speed_reduction_minimum"],
            "minimum_lane_width_m": combined["minimum_lane_width"],
            "safety_buffer_m": combined["safety_buffer_maximum"]
        },
        "risk_assessment": {
            "total_identified_risks": len(combined["all_risks"]),
            "key_risks": combined["all_risks"],
            "total_control_measures": len(combined["all_control_measures"]),
            "control_measures": combined["all_control_measures"],
            "residual_risk_rating": "High" if combined["requires_tc"] and len(tgs_pattern_ids) > 2 else "Medium"
        },
        "special_requirements": combined["all_special_requirements"],
        "complexity_assessment": {
            "patterns_combined": len(tgs_pattern_ids),
            "complexity_level": "High" if len(tgs_pattern_ids) >= 3 else "Medium" if len(tgs_pattern_ids) == 2 else "Standard",
            "recommendation": "Multi-pattern TMPs require experienced traffic management personnel and comprehensive site induction" if len(tgs_pattern_ids) >= 2 else "Standard TMP procedures apply"
        }
    }
    
    return tmp_content
