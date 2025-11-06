"""
TGS Documentation Generator
Creates comprehensive TGS documentation including signage schedules and specifications
"""

from typing import List, Dict
from pathlib import Path
from datetime import datetime


def generate_signage_schedule(
    placed_devices: List[Dict],
    plan_name: str,
    output_dir: Path = Path("/app/tmp_outputs")
) -> str:
    """
    Generate signage schedule document listing all signs with positions and specifications
    
    Returns:
        Path to saved file
    """
    output_dir.mkdir(exist_ok=True)
    
    clean_plan_name = plan_name.replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{clean_plan_name}_{timestamp}_Signage_Schedule.txt"
    file_path = output_dir / filename
    
    with open(file_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(f"SIGNAGE SCHEDULE - {plan_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Signs: {len(placed_devices)}\n\n")
        
        # Table header
        f.write(f"{'#':<4} {'Sign Code':<15} {'Sign Name':<40} {'Distance (m)':<12} {'Side':<8}\n")
        f.write("-" * 80 + "\n")
        
        # Sort by distance
        sorted_devices = sorted(placed_devices, key=lambda x: x.get('distance_from_start', 0))
        
        for idx, device in enumerate(sorted_devices, 1):
            sign_code = device.get('device_code', 'N/A')
            sign_name = device.get('device_name', 'Unknown Sign')[:40]
            distance = device.get('distance_from_start', 0)
            side = device.get('side', 'Both')
            
            f.write(f"{idx:<4} {sign_code:<15} {sign_name:<40} {distance:<12.1f} {side:<8}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("NOTES:\n")
        f.write("- All distances measured from work zone start point\n")
        f.write("- Signs must be installed according to AS 1742.3 specifications\n")
        f.write("- Bilateral signage required where indicated\n")
        f.write("- All signs must be maintained in clean, reflective condition\n")
        f.write("=" * 80 + "\n")
    
    return str(file_path)


def generate_tgs_specifications(
    placed_devices: List[Dict],
    plan_name: str,
    work_zone_details: Dict,
    output_dir: Path = Path("/app/tmp_outputs")
) -> str:
    """
    Generate TGS specifications document with detailed requirements
    
    Returns:
        Path to saved file
    """
    output_dir.mkdir(exist_ok=True)
    
    clean_plan_name = plan_name.replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{clean_plan_name}_{timestamp}_TGS_Specifications.txt"
    file_path = output_dir / filename
    
    with open(file_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(f"TRAFFIC GUIDANCE SCHEME SPECIFICATIONS\n")
        f.write(f"Plan: {plan_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Work Zone Details
        f.write("1. WORK ZONE DETAILS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Location: {work_zone_details.get('location', 'N/A')}\n")
        f.write(f"Work Type: {work_zone_details.get('work_type', 'N/A')}\n")
        f.write(f"Speed Limit: {work_zone_details.get('speed_limit', 'N/A')} km/h\n")
        f.write(f"Road Classification: {work_zone_details.get('road_classification', 'N/A')}\n")
        f.write(f"Traffic Volume (AADT): {work_zone_details.get('aadt', 'N/A')}\n\n")
        
        # Signage Summary
        f.write("2. SIGNAGE SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Signs Required: {len(placed_devices)}\n")
        
        # Count sign types
        sign_types = {}
        for device in placed_devices:
            sign_code = device.get('device_code', 'Unknown')
            sign_types[sign_code] = sign_types.get(sign_code, 0) + 1
        
        f.write("\nSign Types:\n")
        for sign_code, count in sorted(sign_types.items()):
            f.write(f"  {sign_code}: {count} unit(s)\n")
        
        f.write("\n3. INSTALLATION REQUIREMENTS\n")
        f.write("-" * 80 + "\n")
        f.write("- All signs must comply with AS 1742.3-2019\n")
        f.write("- Signs must be Class 1 retroreflective (minimum)\n")
        f.write("- Mounting height: 1.2m to 2.5m to bottom of sign\n")
        f.write("- Signs must be perpendicular to traffic flow\n")
        f.write("- Offset from edge of carriageway: minimum 0.6m (urban), 1.5m (rural)\n")
        f.write("- All sign faces must be clean and clearly visible\n\n")
        
        f.write("4. ADVANCE WARNING DISTANCES\n")
        f.write("-" * 80 + "\n")
        
        speed_limit = work_zone_details.get('speed_limit', 60)
        if speed_limit <= 60:
            f.write("Speed ≤60 km/h: 50m minimum advance warning\n")
        elif speed_limit <= 80:
            f.write("Speed 70-80 km/h: 90m minimum advance warning\n")
        elif speed_limit <= 100:
            f.write("Speed 90-100 km/h: 150m minimum advance warning\n")
        else:
            f.write("Speed >100 km/h: 250m minimum advance warning\n")
        
        f.write("\n5. BILATERAL SIGNAGE REQUIREMENTS\n")
        f.write("-" * 80 + "\n")
        f.write("Bilateral signage required for:\n")
        f.write("- All lane closures\n")
        f.write("- Work zone advance warning signs\n")
        f.write("- Road works ahead signs\n")
        f.write("- End of works signs\n")
        f.write("- Side street approaches within work zone\n\n")
        
        f.write("6. MAINTENANCE AND INSPECTION\n")
        f.write("-" * 80 + "\n")
        f.write("- Daily inspection of all signs required\n")
        f.write("- Damaged or dirty signs must be replaced/cleaned immediately\n")
        f.write("- Non-reflective signs must be replaced\n")
        f.write("- Document all inspections and maintenance\n\n")
        
        f.write("7. REMOVAL PROCEDURE\n")
        f.write("-" * 80 + "\n")
        f.write("- Remove end of works signs first\n")
        f.write("- Work backwards from end of works to start\n")
        f.write("- Remove bilateral signs simultaneously\n")
        f.write("- Ensure no signs remain after works complete\n\n")
        
        f.write("8. COMPLIANCE STATEMENT\n")
        f.write("-" * 80 + "\n")
        f.write("This TGS has been prepared in accordance with:\n")
        f.write("- AS 1742.3-2019 Manual of Uniform Traffic Control Devices\n")
        f.write("- Austroads Guide to Temporary Traffic Management\n")
        f.write("- SA Government Traffic Management Guidelines\n")
        f.write("- Work Health and Safety Regulations 2012\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("END OF SPECIFICATIONS\n")
        f.write("=" * 80 + "\n")
    
    return str(file_path)


def generate_master_summary(
    plan_name: str,
    comprehensive_data: Dict,
    placed_devices: List[Dict],
    output_dir: Path = Path("/app/tmp_outputs")
) -> str:
    """
    Generate master summary document with all comprehensive data
    
    Returns:
        Path to saved file
    """
    output_dir.mkdir(exist_ok=True)
    
    clean_plan_name = plan_name.replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{clean_plan_name}_{timestamp}_MASTER_SUMMARY.txt"
    file_path = output_dir / filename
    
    with open(file_path, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write(f"TRAFFIC MANAGEMENT PLAN - MASTER SUMMARY\n")
        f.write(f"Plan: {plan_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}\n")
        f.write("=" * 100 + "\n\n")
        
        # SA Traffic Intelligence
        if comprehensive_data.get('sa_traffic_intelligence'):
            f.write("SA TRAFFIC INTELLIGENCE\n")
            f.write("-" * 100 + "\n")
            sa_traffic = comprehensive_data['sa_traffic_intelligence']
            
            top_40_road = sa_traffic.get('top_40_road_analysis', {})
            if top_40_road.get('is_top_40_road'):
                f.write(f"⚠️  TOP 40 ROAD DETECTED - RANK #{top_40_road.get('rank')}\n")
                f.write(f"   AADT: {top_40_road.get('traffic_volume', 0):,}\n")
                f.write(f"   Message: {top_40_road.get('message', 'N/A')}\n\n")
            
            top_40_int = sa_traffic.get('top_40_intersection_analysis', {})
            if top_40_int.get('is_top_40_intersection'):
                f.write(f"⚠️  TOP 40 INTERSECTION DETECTED - RANK #{top_40_int.get('rank')}\n")
                f.write(f"   Vehicle Exposure: {top_40_int.get('vehicle_exposure', 0):,}\n")
                f.write(f"   Location: {top_40_int.get('intersection_match', {}).get('location', 'N/A')}\n\n")
            
            f.write(f"Overall Traffic Level: {sa_traffic.get('overall_traffic_level', 'N/A')}\n")
            
            recommendations = sa_traffic.get('recommendations', [])
            if recommendations:
                f.write("\nRecommendations:\n")
                for rec in recommendations:
                    f.write(f"  - {rec}\n")
            f.write("\n")
        
        # Crash Statistics
        if comprehensive_data.get('crash_statistics'):
            f.write("CRASH HISTORY\n")
            f.write("-" * 100 + "\n")
            crash = comprehensive_data['crash_statistics']
            f.write(f"Total Crashes (5yr): {crash.get('total_crashes_5yr', 0)}\n")
            f.write(f"Risk Level: {crash.get('risk_assessment', {}).get('risk_level', 'N/A')}\n\n")
        
        # Pedestrian Controls
        if comprehensive_data.get('pedestrian_control_measures'):
            f.write("PEDESTRIAN CONTROL MEASURES\n")
            f.write("-" * 100 + "\n")
            ped = comprehensive_data['pedestrian_control_measures']
            barriers = ped.get('barriers_required', [])
            if barriers:
                f.write(f"Barriers Required: {len(barriers)} location(s)\n")
            
            dda = ped.get('dda_compliance', {})
            if dda:
                f.write(f"DDA Compliance: Width {dda.get('width_requirements', 'N/A')}, ")
                f.write(f"Grade {dda.get('grade_requirements', 'N/A')}\n")
            f.write("\n")
        
        # School Zones
        if comprehensive_data.get('school_zones'):
            schools = comprehensive_data['school_zones']
            if schools.get('nearby_schools'):
                f.write("SCHOOL ZONES\n")
                f.write("-" * 100 + "\n")
                f.write(f"Nearby Schools: {len(schools['nearby_schools'])}\n")
                f.write(f"Enhanced Restrictions: {schools.get('enhanced_restrictions', False)}\n")
                f.write(f"School Zone Speed: {schools.get('speed_limit_school_zone', 'N/A')}\n\n")
        
        # Device Summary
        f.write("TRAFFIC CONTROL DEVICES\n")
        f.write("-" * 100 + "\n")
        f.write(f"Total Devices: {len(placed_devices)}\n\n")
        
        f.write("=" * 100 + "\n")
        f.write("END OF MASTER SUMMARY\n")
        f.write("=" * 100 + "\n")
    
    return str(file_path)
