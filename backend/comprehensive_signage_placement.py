"""
Comprehensive Signage Placement System
Implements Austroads and SA standards for:
1. Bilateral signage (both sides of road)
2. Side street signage
3. Intersection signage
4. Proper device codes and specifications
"""

class ComprehensiveSignagePlacement:
    """
    Austroads Guide to Temporary Traffic Management (AGTTM) Part 3
    SA Department for Infrastructure and Transport Standards
    AS 1742.3 - Traffic Control Devices for Works on Roads
    """
    
    def __init__(self):
        # SA-specific signage codes (Austroads compliant)
        self.sa_sign_codes = {
            # Warning Signs (W-series)
            'road_work_ahead': {
                'code': 'W1-1',
                'description': 'Road Work Ahead',
                'size_urban': '1200x1200mm',
                'size_rural': '1500x1500mm',
                'bilateral': True,
                'reflective': 'Class 1',
                'color': 'Yellow/Black'
            },
            'lane_closure_ahead': {
                'code': 'W1-2',
                'description': 'Lane Closure Ahead',
                'size_urban': '1200x1200mm',
                'size_rural': '1500x1500mm',
                'bilateral': True,
                'reflective': 'Class 1'
            },
            'road_closed_ahead': {
                'code': 'W1-3',
                'description': 'Road Closed Ahead',
                'size': '2000x2000mm',
                'bilateral': True,
                'reflective': 'Class 1'
            },
            'detour_ahead': {
                'code': 'W1-4',
                'description': 'Detour Ahead',
                'size_urban': '1200x1200mm',
                'bilateral': True
            },
            'pedestrian_crossing_ahead': {
                'code': 'W5-1',
                'description': 'Pedestrian Crossing Ahead',
                'size': '900x900mm',
                'bilateral': True
            },
            
            # Regulatory Signs (R-series)
            'road_closed': {
                'code': 'R2-1',
                'description': 'Road Closed',
                'size': '900mm diameter',
                'bilateral': True,
                'reflective': 'Class 1',
                'color': 'Red/White'
            },
            'speed_limit_40': {
                'code': 'R4-1(40)',
                'description': 'Speed Limit 40',
                'size': '900mm diameter',
                'bilateral': True,
                'reflective': 'Class 1'
            },
            'speed_limit_end_40': {
                'code': 'R4-3(40)',
                'description': 'End Speed Limit 40',
                'size': '900mm diameter',
                'bilateral': True
            },
            'no_entry': {
                'code': 'R2-2',
                'description': 'No Entry',
                'size': '900mm diameter',
                'bilateral': True
            },
            'local_traffic_only': {
                'code': 'R8-4',
                'description': 'Local Traffic Only',
                'size': '900x600mm',
                'bilateral': True
            },
            
            # Guidance Signs (G-series)
            'detour_arrow_left': {
                'code': 'G9-6(L)',
                'description': 'Detour Arrow Left',
                'size': '1800x900mm',
                'bilateral': False,
                'side': 'left'
            },
            'detour_arrow_right': {
                'code': 'G9-6(R)',
                'description': 'Detour Arrow Right',
                'size': '1800x900mm',
                'bilateral': False,
                'side': 'right'
            },
            'end_road_work': {
                'code': 'G2-4',
                'description': 'End Road Work',
                'size': '1200x600mm',
                'bilateral': True,
                'reflective': 'Class 1'
            },
            
            # Supplementary Plates (S-series)
            'distance_marker': {
                'code': 'S1-1',
                'description': 'Distance to Work',
                'size': '1200x300mm',
                'text_format': 'XXX m'
            },
            'use_detour': {
                'code': 'S8-1',
                'description': 'Use Detour',
                'size': '900x300mm'
            },
            'local_access_only': {
                'code': 'S8-2',
                'description': 'Local Access Only',
                'size': '900x300mm'
            }
        }
        
        # Side street signage requirements
        self.side_street_requirements = {
            'within_workzone': {
                'required_signs': [
                    'road_work_ahead',
                    'road_closed' # if applicable
                ],
                'placement': 'at_intersection',
                'distance_from_intersection': 10,  # meters before intersection
                'bilateral': True
            },
            'adjacent_to_workzone': {
                'required_signs': [
                    'road_work_ahead'
                ],
                'placement': 'at_intersection',
                'distance_from_intersection': 10,
                'bilateral': False,  # Only on approach side
                'approach_side_only': True
            },
            'detour_route': {
                'required_signs': [
                    'detour_arrow',
                    'distance_marker'
                ],
                'placement': 'at_intersection',
                'spacing': 200,  # meters between direction signs
                'bilateral': False
            }
        }
        
        # Bilateral placement rules (SA standards)
        self.bilateral_rules = {
            'urban_roads': {
                'speed_limit': 60,  # km/h threshold
                'mandatory_bilateral': [
                    'advance_warning',
                    'regulatory',
                    'speed_limits'
                ],
                'offset_between_signs': 2.0,  # meters
                'lateral_offset': 1.0,  # meters (staggered)
            },
            'rural_roads': {
                'speed_limit': 60,
                'mandatory_bilateral': [
                    'advance_warning',
                    'regulatory',
                    'speed_limits',
                    'guidance'
                ],
                'offset_between_signs': 5.0,
                'lateral_offset': 2.0
            },
            'divided_roads': {
                'median_present': True,
                'mandatory_bilateral': [
                    'advance_warning',
                    'regulatory'
                ],
                'placement': 'each_carriageway',
                'offset_between_signs': 2.0
            }
        }
    
    def generate_comprehensive_signage_plan(self, workzone_data, road_data, side_streets):
        """
        Generate complete signage plan including:
        - Main road bilateral signage
        - Side street signage
        - Intersection signage
        - Detour route signage
        """
        signage_plan = {
            'main_road_signage': [],
            'side_street_signage': [],
            'intersection_signage': [],
            'detour_signage': []
        }
        
        # 1. Main road bilateral signage
        signage_plan['main_road_signage'] = self._generate_main_road_signage(
            workzone_data, road_data
        )
        
        # 2. Side street signage
        if side_streets:
            signage_plan['side_street_signage'] = self._generate_side_street_signage(
                workzone_data, road_data, side_streets
            )
        
        # 3. Intersection signage
        signage_plan['intersection_signage'] = self._generate_intersection_signage(
            workzone_data, road_data, side_streets
        )
        
        # 4. Detour route signage (if applicable)
        if workzone_data.get('complete_closure'):
            signage_plan['detour_signage'] = self._generate_detour_signage(
                workzone_data, road_data
            )
        
        return signage_plan
    
    def _generate_main_road_signage(self, workzone_data, road_data):
        """Generate bilateral signage for main road"""
        devices = []
        speed = road_data.get('speed_limit', 60)
        lanes = road_data.get('lanes', 2)
        
        # Determine advance warning distances (AS 1742.3 Table 4.1)
        if speed <= 60:
            advance_distances = [90, 45]  # meters
        elif speed <= 80:
            advance_distances = [150, 75]
        else:
            advance_distances = [200, 100]
        
        # Sign size based on speed and environment
        sign_size = '1200x1200mm' if speed <= 60 else '1500x1500mm'
        
        # Position 1: First advance warning (bilateral)
        devices.append({
            'position': -advance_distances[0],
            'sign_code': 'W1-1',
            'description': 'Road Work Ahead',
            'size': sign_size,
            'placement': 'bilateral',
            'left_side': {
                'lat_offset': -3.5,  # meters left of centerline
                'clearance': 2.0
            },
            'right_side': {
                'lat_offset': 3.5 + (lanes * 3.5),  # right of all lanes
                'clearance': 2.0
            },
            'height': 2.1,  # meters above ground
            'reflective_class': 'Class 1',
            'mounting': 'Portable frame with sandbags',
            'quantity': 2  # Both sides
        })
        
        # Position 2: Second advance warning with distance (bilateral)
        devices.append({
            'position': -advance_distances[1],
            'sign_code': 'W1-2',
            'description': 'Lane Closure Ahead',
            'size': sign_size,
            'supplementary': {
                'code': 'S1-1',
                'text': f'{advance_distances[1]}m',
                'size': '1200x300mm'
            },
            'placement': 'bilateral',
            'left_side': {
                'lat_offset': -3.5,
                'clearance': 2.0
            },
            'right_side': {
                'lat_offset': 3.5 + (lanes * 3.5),
                'clearance': 2.0
            },
            'height': 2.1,
            'quantity': 2
        })
        
        # Position 3: Regulatory speed limit (bilateral)
        devices.append({
            'position': -advance_distances[1] + 10,
            'sign_code': 'R4-1(40)',
            'description': 'Speed Limit 40',
            'size': '900mm diameter',
            'placement': 'bilateral',
            'left_side': {
                'lat_offset': -3.5,
                'clearance': 2.0
            },
            'right_side': {
                'lat_offset': 3.5 + (lanes * 3.5),
                'clearance': 2.0
            },
            'height': 2.1,
            'quantity': 2,
            'mandatory': True  # Regulatory signs are mandatory bilateral
        })
        
        # Position 4: End of work zone (bilateral)
        workzone_end = workzone_data.get('workzone_length', 100)
        devices.append({
            'position': workzone_end + 15,  # 15m after work zone
            'sign_code': 'G2-4',
            'description': 'End Road Work',
            'size': '1200x600mm',
            'placement': 'bilateral',
            'left_side': {
                'lat_offset': -3.5,
                'clearance': 2.0
            },
            'right_side': {
                'lat_offset': 3.5 + (lanes * 3.5),
                'clearance': 2.0
            },
            'height': 2.1,
            'quantity': 2
        })
        
        # Position 5: End speed limit (bilateral)
        devices.append({
            'position': workzone_end + 20,
            'sign_code': 'R4-3(40)',
            'description': 'End Speed Limit 40',
            'size': '900mm diameter',
            'placement': 'bilateral',
            'left_side': {
                'lat_offset': -3.5,
                'clearance': 2.0
            },
            'right_side': {
                'lat_offset': 3.5 + (lanes * 3.5),
                'clearance': 2.0
            },
            'height': 2.1,
            'quantity': 2
        })
        
        return devices
    
    def _generate_side_street_signage(self, workzone_data, road_data, side_streets):
        """Generate signage for side streets intersecting or near work zone"""
        devices = []
        
        for street in side_streets:
            street_name = street.get('name', 'Unknown Street')
            distance_to_workzone = street.get('distance_to_workzone', 0)
            intersection_type = street.get('type', 'T-intersection')
            
            # Determine if side street is within or adjacent to work zone
            if distance_to_workzone < 10:  # Within work zone
                # Place Road Work Ahead on side street approach
                devices.append({
                    'location': f"{street_name} intersection",
                    'position': -10,  # 10m before intersection
                    'sign_code': 'W1-1',
                    'description': 'Road Work Ahead',
                    'size': '1200x1200mm',
                    'placement': 'side_street_approach',
                    'side_street': street_name,
                    'offset': 2.0,
                    'height': 2.1,
                    'quantity': 1,
                    'notes': f'Place on {street_name} approach to main road'
                })
                
                # If work zone blocks side street, add Road Closed
                if workzone_data.get('blocks_side_street', False):
                    devices.append({
                        'location': f"{street_name} intersection",
                        'position': -5,
                        'sign_code': 'R2-1',
                        'description': 'Road Closed',
                        'size': '900mm diameter',
                        'supplementary': {
                            'code': 'S8-2',
                            'text': 'Local Access Only'
                        },
                        'placement': 'side_street_approach',
                        'side_street': street_name,
                        'quantity': 1
                    })
            
            # Add direction signs at intersections within work zone
            devices.append({
                'location': f"{street_name} intersection",
                'position': 0,  # At intersection
                'sign_code': 'G9-1',
                'description': 'Direction Arrow',
                'size': '600x600mm',
                'placement': 'at_intersection',
                'side_street': street_name,
                'quantity': 1,
                'notes': 'Guide traffic through/around work zone'
            })
        
        return devices
    
    def _generate_intersection_signage(self, workzone_data, road_data, side_streets):
        """Generate specific signage for intersections"""
        devices = []
        
        # For each intersection, ensure proper advance warning on BOTH approaches
        for street in side_streets:
            street_name = street.get('name', 'Unknown Street')
            
            # Main road approach to intersection (both directions)
            devices.append({
                'location': f"Main road approach to {street_name}",
                'position': -50,  # 50m before intersection
                'sign_code': 'W1-1',
                'description': 'Road Work Ahead',
                'size': '1200x1200mm',
                'placement': 'bilateral',  # BOTH sides
                'left_side': {'lat_offset': -3.5},
                'right_side': {'lat_offset': 3.5 + (road_data.get('lanes', 2) * 3.5)},
                'quantity': 2,
                'notes': f'50m before {street_name} intersection on BOTH sides'
            })
            
            # Side street approach to main road
            devices.append({
                'location': f"{street_name} approach to main road",
                'position': -20,
                'sign_code': 'W1-1',
                'description': 'Road Work Ahead',
                'size': '1200x1200mm',
                'placement': 'single',
                'quantity': 1,
                'notes': f'On {street_name} 20m before main road'
            })
        
        return devices
    
    def _generate_detour_signage(self, workzone_data, road_data):
        """Generate comprehensive detour route signage"""
        devices = []
        detour_route = workzone_data.get('detour_route', [])
        
        # Advance warning of detour (bilateral)
        devices.append({
            'position': -200,
            'sign_code': 'W1-4',
            'description': 'Detour Ahead',
            'size': '1200x1200mm',
            'placement': 'bilateral',
            'quantity': 2,
            'notes': '200m before closure point, both sides'
        })
        
        # Direction arrows at closure point
        devices.append({
            'position': -50,
            'sign_code': 'G9-6(R)',
            'description': 'Detour Arrow Right',
            'size': '1800x900mm',
            'placement': 'directional',
            'quantity': 1,
            'notes': 'Large arrow board directing to detour route'
        })
        
        # Road Closed sign (bilateral)
        devices.append({
            'position': -10,
            'sign_code': 'R2-1',
            'description': 'Road Closed',
            'size': '900mm diameter',
            'supplementary': {
                'code': 'S8-1',
                'text': 'Use Detour'
            },
            'placement': 'bilateral',
            'quantity': 2
        })
        
        # Detour route confirmation signs every 200m
        for i, segment in enumerate(detour_route):
            devices.append({
                'location': f"Detour route - {segment.get('street_name')}",
                'position': i * 200,
                'sign_code': 'G9-6',
                'description': f"Detour - Continue {segment.get('direction')}",
                'size': '1800x900mm',
                'placement': 'single',
                'quantity': 1,
                'notes': f"Every 200m along detour route"
            })
        
        return devices
    
    def generate_device_schedule_report(self, signage_plan):
        """Generate comprehensive device schedule for documentation"""
        report = []
        report.append("=" * 100)
        report.append("COMPREHENSIVE SIGNAGE SCHEDULE - AUSTROADS & SA STANDARDS COMPLIANT")
        report.append("=" * 100)
        report.append("")
        
        # Main Road Signage
        report.append("1. MAIN ROAD SIGNAGE (Bilateral Placement)")
        report.append("-" * 100)
        for i, device in enumerate(signage_plan.get('main_road_signage', []), 1):
            report.append(f"\nDevice {i}:")
            report.append(f"  Position: {device['position']}m from work zone start")
            report.append(f"  Sign Code: {device['sign_code']} - {device['description']}")
            report.append(f"  Size: {device['size']}")
            report.append(f"  Placement: {device['placement'].upper()}")
            if device['placement'] == 'bilateral':
                report.append(f"  Quantity: 2 (LEFT side + RIGHT side)")
                report.append(f"    LEFT: {device['left_side']['lat_offset']}m offset, {device['left_side']['clearance']}m clearance")
                report.append(f"    RIGHT: {device['right_side']['lat_offset']}m offset, {device['right_side']['clearance']}m clearance")
            report.append(f"  Height: {device['height']}m above ground")
            report.append(f"  Reflective: {device.get('reflective_class', 'Class 1')}")
            if 'supplementary' in device:
                report.append(f"  Supplementary: {device['supplementary']['code']} - {device['supplementary']['text']}")
        
        # Side Street Signage
        if signage_plan.get('side_street_signage'):
            report.append("\n\n2. SIDE STREET SIGNAGE")
            report.append("-" * 100)
            for i, device in enumerate(signage_plan['side_street_signage'], 1):
                report.append(f"\nDevice S{i}:")
                report.append(f"  Location: {device['location']}")
                report.append(f"  Sign Code: {device['sign_code']} - {device['description']}")
                report.append(f"  Size: {device['size']}")
                report.append(f"  Placement: {device['placement']}")
                report.append(f"  Side Street: {device['side_street']}")
                report.append(f"  Quantity: {device['quantity']}")
                report.append(f"  Notes: {device.get('notes', 'N/A')}")
        
        # Intersection Signage
        if signage_plan.get('intersection_signage'):
            report.append("\n\n3. INTERSECTION SIGNAGE")
            report.append("-" * 100)
            for i, device in enumerate(signage_plan['intersection_signage'], 1):
                report.append(f"\nDevice I{i}:")
                report.append(f"  Location: {device['location']}")
                report.append(f"  Sign Code: {device['sign_code']} - {device['description']}")
                report.append(f"  Placement: {device['placement']}")
                if device['placement'] == 'bilateral':
                    report.append(f"  Quantity: 2 (BOTH sides of road)")
                report.append(f"  Notes: {device.get('notes', 'N/A')}")
        
        # Detour Signage
        if signage_plan.get('detour_signage'):
            report.append("\n\n4. DETOUR ROUTE SIGNAGE")
            report.append("-" * 100)
            for i, device in enumerate(signage_plan['detour_signage'], 1):
                report.append(f"\nDevice D{i}:")
                report.append(f"  Position/Location: {device.get('position', device.get('location'))}")
                report.append(f"  Sign Code: {device['sign_code']} - {device['description']}")
                report.append(f"  Size: {device['size']}")
                report.append(f"  Quantity: {device['quantity']}")
                report.append(f"  Notes: {device.get('notes', 'N/A')}")
        
        report.append("\n\n" + "=" * 100)
        report.append("TOTAL SIGNAGE COUNT:")
        total = (
            len(signage_plan.get('main_road_signage', [])) +
            len(signage_plan.get('side_street_signage', [])) +
            len(signage_plan.get('intersection_signage', [])) +
            len(signage_plan.get('detour_signage', []))
        )
        report.append(f"  Main Road: {len(signage_plan.get('main_road_signage', []))} device types")
        report.append(f"  Side Streets: {len(signage_plan.get('side_street_signage', []))} devices")
        report.append(f"  Intersections: {len(signage_plan.get('intersection_signage', []))} devices")
        report.append(f"  Detour Route: {len(signage_plan.get('detour_signage', []))} devices")
        report.append(f"  TOTAL: {total} device installations")
        report.append("=" * 100)
        
        return "\n".join(report)
