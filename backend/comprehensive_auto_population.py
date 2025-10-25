"""
Comprehensive Auto-Population System
Fetches and deduces ALL possible information to minimize user input
"""
import httpx
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

async def fetch_osm_road_data(lat: float, lng: float) -> Dict[str, Any]:
    """Fetch road data from OpenStreetMap Overpass API"""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json][timeout:10];
        (
          way(around:50,{lat},{lng})["highway"]["name"];
        );
        out body;
        >;
        out skel qt;
        """
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            data = response.json()
        
        # Extract road information
        road_info = {
            'speed_limit': 60,
            'lanes': 2,
            'road_name': 'Unknown Road',
            'highway_type': 'residential',
            'surface': 'asphalt',
            'has_footpath': False,
            'has_cycleway': False,
            'has_parking': False
        }
        
        for element in data.get('elements', []):
            if element.get('type') == 'way':
                tags = element.get('tags', {})
                
                if 'name' in tags:
                    road_info['road_name'] = tags['name']
                
                if 'highway' in tags:
                    road_info['highway_type'] = tags['highway']
                
                if 'maxspeed' in tags:
                    try:
                        road_info['speed_limit'] = int(tags['maxspeed'].replace(' km/h', '').replace('km/h', ''))
                    except:
                        pass
                
                if 'lanes' in tags:
                    try:
                        road_info['lanes'] = int(tags['lanes'])
                    except:
                        pass
                
                if 'surface' in tags:
                    road_info['surface'] = tags['surface']
                
                if 'footway' in tags or 'sidewalk' in tags:
                    road_info['has_footpath'] = True
                
                if 'cycleway' in tags:
                    road_info['has_cycleway'] = True
                
                if 'parking' in tags:
                    road_info['has_parking'] = True
                
                break  # Use first matching way
        
        return road_info
        
    except Exception as e:
        logger.error(f"Error fetching OSM road data: {str(e)}")
        return {
            'speed_limit': 60,
            'lanes': 2,
            'road_name': 'Unknown Road',
            'highway_type': 'residential',
            'surface': 'asphalt',
            'has_footpath': False,
            'has_cycleway': False,
            'has_parking': False
        }

async def get_comprehensive_auto_population(lat: float, lng: float, start_address: str, end_address: str, work_type: str = None):
    """
    Master function to auto-populate ALL possible TMP fields
    Returns complete data package ready to populate forms
    """
    
    result = {
        'road_data': {},
        'traffic_assessment': {},
        'site_assessment': {},
        'side_streets': [],
        'intersections': [],
        'control_measures': [],
        'pedestrian_control_measures': [],  # NEW: Pedestrian control
        'recommended_devices': [],
        'suggested_risks': [],
        'governing_body_details': {},
        'notification_requirements': {},
        'environmental_constraints': {},
        'staging_recommendations': {},
        'public_facilities': {},
        'signage_plan': {}  # NEW: Detailed signage plan with distances
    }
    
    try:
        # 0. FETCH OSM ROAD DATA (foundational)
        osm_data = await fetch_osm_road_data(lat, lng)
        result['road_data'] = osm_data
        
        # 1. SIDE STREETS AND INTERSECTIONS (OSM)
        result['side_streets'] = await fetch_side_streets(lat, lng)
        result['intersections'] = await fetch_intersections(lat, lng)
        
        # 2. GOVERNING BODY CONTACT DETAILS
        result['governing_body_details'] = await fetch_governing_body_contacts(lat, lng, start_address)
        
        # 3. PUBLIC FACILITIES (schools, hospitals, businesses)
        result['public_facilities'] = await fetch_public_facilities(lat, lng)
        
        # 4. SUGGESTED CONTROL MEASURES (based on work type and road)
        result['control_measures'] = suggest_control_measures(work_type, osm_data)
        
        # 5. PEDESTRIAN CONTROL MEASURES (NEW)
        result['pedestrian_control_measures'] = suggest_pedestrian_controls(work_type, osm_data, result['public_facilities'])
        
        # 6. RECOMMENDED DEVICES (from device library)
        result['recommended_devices'] = recommend_devices(work_type, osm_data)
        
        # 7. SIGNAGE PLAN with bilateral and side street requirements (NEW)
        result['signage_plan'] = generate_signage_plan(work_type, osm_data, result['side_streets'], result['intersections'])
        
        # 8. SUGGESTED RISKS (from 106-risk register)
        result['suggested_risks'] = suggest_risks_for_scenario(work_type, osm_data)
        
        # 9. NOTIFICATION REQUIREMENTS
        result['notification_requirements'] = determine_notifications(osm_data)
        
        # 10. ENVIRONMENTAL CONSTRAINTS
        result['environmental_constraints'] = await assess_environmental_constraints(lat, lng, start_address)
        
        # 11. STAGING RECOMMENDATIONS
        result['staging_recommendations'] = generate_staging_plan(osm_data, start_address, end_address)
        
        # 12. DETOUR ROUTES (if road closure)
        if work_type and 'closure' in work_type.lower():
            result['detour_routes'] = await calculate_detour_routes(lat, lng, start_address)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in comprehensive auto-population: {str(e)}")
        return result

async def fetch_side_streets(lat: float, lng: float):
    """Fetch all side streets within workzone using OSM"""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json][timeout:10];
        (
          way(around:200,{lat},{lng})["highway"]["name"];
        );
        out body;
        """
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            data = response.json()
        
        streets = []
        seen_names = set()
        
        for element in data.get('elements', []):
            name = element.get('tags', {}).get('name')
            highway_type = element.get('tags', {}).get('highway')
            
            if name and name not in seen_names:
                streets.append({
                    'name': name,
                    'type': highway_type,
                    'ref': element.get('tags', {}).get('ref', '')
                })
                seen_names.add(name)
        
        return streets[:10]  # Limit to 10 nearest streets
        
    except Exception as e:
        logger.error(f"Error fetching side streets: {str(e)}")
        return []

async def fetch_intersections(lat: float, lng: float):
    """Identify major intersections within workzone"""
    streets = await fetch_side_streets(lat, lng)
    
    # Major streets are intersections
    intersections = [
        {
            'name': street['name'],
            'signage_required': True,
            'type': 'T-intersection' if 'terrace' in street['name'].lower() or 'street' in street['name'].lower() else 'crossroad'
        }
        for street in streets if street['type'] in ['primary', 'secondary', 'tertiary', 'residential']
    ]
    
    return intersections[:5]

async def fetch_governing_body_contacts(lat: float, lng: float, address: str):
    """Get contact details for road authority"""
    
    # SA DIT (Department for Infrastructure and Transport) contacts
    contacts = {
        'authority_name': 'SA Department for Infrastructure and Transport',
        'main_phone': '1300 794 880',
        'email': 'DIT.TMApprovals@sa.gov.au',
        'website': 'www.dit.sa.gov.au',
        'notification_email': 'DIT.RoadworkNotifications@sa.gov.au',
        'emergency_phone': '1800 018 313',
        'office_hours': 'Monday to Friday, 8:30am - 5:00pm'
    }
    
    # Check if it's a council road
    if 'street' in address.lower() or 'road' in address.lower():
        # Could be local council - add fallback
        contacts['local_council_note'] = 'If local road, contact relevant council'
    
    return contacts

async def fetch_public_facilities(lat: float, lng: float):
    """Find schools, hospitals, and major businesses nearby"""
    facilities = {
        'schools': [],
        'hospitals': [],
        'businesses': [],
        'special_zones': []
    }
    
    try:
        # Query OSM for facilities
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json][timeout:10];
        (
          node(around:500,{lat},{lng})["amenity"="school"];
          node(around:500,{lat},{lng})["amenity"="hospital"];
          way(around:500,{lat},{lng})["amenity"="school"];
          way(around:500,{lat},{lng})["amenity"="hospital"];
        );
        out body;
        """
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            data = response.json()
        
        for element in data.get('elements', []):
            amenity = element.get('tags', {}).get('amenity')
            name = element.get('tags', {}).get('name', 'Unnamed')
            
            if amenity == 'school':
                facilities['schools'].append({
                    'name': name,
                    'notification_required': True,
                    'peak_times': '8:00-9:00am, 3:00-4:00pm'
                })
            elif amenity == 'hospital':
                facilities['hospitals'].append({
                    'name': name,
                    'emergency_access_critical': True,
                    'notification_required': True
                })
        
        # Add special considerations
        if facilities['schools']:
            facilities['special_zones'].append({
                'type': 'School Zone',
                'restrictions': 'Avoid peak drop-off/pick-up times',
                'additional_signage': 'Children Crossing signs may be required'
            })
        
        if facilities['hospitals']:
            facilities['special_zones'].append({
                'type': 'Hospital Zone',
                'restrictions': 'Emergency vehicle access MUST be maintained 24/7',
                'additional_signage': 'Hospital Access Maintained signs required'
            })
        
    except Exception as e:
        logger.error(f"Error fetching public facilities: {str(e)}")
    
    return facilities

def suggest_control_measures(work_type: str, osm_data: dict):
    """Intelligently suggest control measures based on scenario"""
    
    measures = {
        'temporal': [],
        'speed': [],
        'lane_management': [],
        'safety': [],
        'communication': []
    }
    
    speed = osm_data.get('speed_limit', 60) if osm_data else 60
    lanes = osm_data.get('lanes', 2) if osm_data else 2
    
    # Temporal controls
    if speed <= 60:
        measures['temporal'].append('off_peak_hours')
    measures['temporal'].append('staged_works')
    
    # Speed management
    if speed > 50:
        measures['speed'].append('temporary_speed_limit_40')
    measures['speed'].append('speed_reduction')
    
    # Lane management
    if lanes >= 2:
        measures['lane_management'].append('lane_closure')
        measures['lane_management'].append('merge_taper')
    
    # Safety
    measures['safety'].extend([
        'static_signs',
        'delineation_devices',
        'water_filled_barriers',
        'traffic_controllers',
        'lighting_systems'
    ])
    
    # Communication
    measures['communication'].extend([
        'public_notification',
        'stakeholder_consultation',
        'emergency_services_notification'
    ])
    
    return measures

def recommend_devices(work_type: str, osm_data: dict):
    """Recommend devices from library based on scenario"""
    
    devices = []
    speed = osm_data.get('speed_limit', 60) if osm_data else 60
    
    # Advance warning distance
    if speed <= 60:
        adv_dist = 90
    else:
        adv_dist = 150
    
    devices.append({
        'code': 'W1-1',
        'name': 'Road Work Ahead',
        'position': f'-{adv_dist}m',
        'placement': 'bilateral',
        'quantity': 2
    })
    
    devices.append({
        'code': 'W1-2',
        'name': 'Lane Closure Ahead',
        'position': f'-{int(adv_dist/2)}m',
        'placement': 'bilateral',
        'quantity': 2
    })
    
    devices.append({
        'code': 'R4-1(40)',
        'name': 'Speed Limit 40',
        'position': f'-{int(adv_dist/2)+10}m',
        'placement': 'bilateral',
        'quantity': 2
    })
    
    devices.append({
        'code': 'D5-1',
        'name': 'Traffic Cones 700mm',
        'position': 'taper',
        'quantity': 20
    })
    
    devices.append({
        'code': 'G2-4',
        'name': 'End Road Work',
        'position': '+50m after workzone',
        'placement': 'bilateral',
        'quantity': 2
    })
    
    return devices

def suggest_risks_for_scenario(work_type: str, osm_data: dict):
    """Pre-select relevant risks from 106-risk register"""
    
    # Common risks for all scenarios
    suggested = ['TF1', 'TF2', 'TF3', 'WS1', 'WS2', 'PC1', 'SD1', 'EM1']
    
    # Add scenario-specific risks
    if work_type:
        if 'closure' in work_type.lower():
            suggested.extend(['TF4', 'PB1', 'IF1'])
        if 'utility' in work_type.lower():
            suggested.extend(['WS3', 'PE1', 'IF2'])
    
    return suggested

def determine_notifications(osm_data: dict):
    """Determine who needs to be notified"""
    
    notifications = {
        'road_authority': {
            'required': True,
            'timeframe': '5 business days minimum',
            'method': 'Online portal or email'
        },
        'emergency_services': {
            'required': True,
            'timeframe': '48 hours before works',
            'contacts': ['SA Police', 'SA Ambulance', 'SA Fire']
        },
        'public_transport': {
            'required': False,
            'timeframe': '7 days before',
            'authority': 'Adelaide Metro'
        },
        'adjacent_properties': {
            'required': True,
            'timeframe': '3 days before',
            'method': 'Letter box drop or door knock'
        }
    }
    
    return notifications

async def assess_environmental_constraints(lat: float, lng: float, address: str):
    """Assess environmental and heritage constraints"""
    
    constraints = {
        'heritage_areas': [],
        'environmental_zones': [],
        'tree_protection': False,
        'noise_restrictions': {},
        'dust_management': True
    }
    
    # Check for heritage (would need heritage database API)
    if 'adelaide' in address.lower() and ('north terrace' in address.lower() or 'king william' in address.lower()):
        constraints['heritage_areas'].append({
            'area': 'Adelaide CBD Heritage Zone',
            'restrictions': 'State Heritage approval may be required',
            'contact': 'Heritage SA'
        })
    
    # Standard noise restrictions
    constraints['noise_restrictions'] = {
        'weekday_evening': '6pm - 7am (>5dB above background)',
        'weekend': 'Saturday 1pm - Monday 7am',
        'public_holidays': 'No noisy works'
    }
    
    return constraints

def generate_staging_plan(osm_data: dict, start_addr: str, end_addr: str):
    """Generate staging recommendations"""
    
    lanes = osm_data.get('lanes', 2) if osm_data else 2
    
    staging = {
        'recommended_stages': [],
        'rationale': ''
    }
    
    if lanes >= 3:
        staging['recommended_stages'] = [
            {
                'stage': 1,
                'description': 'Close left lane, maintain center and right lanes',
                'duration': '50% of project',
                'traffic_impact': 'Minor delays'
            },
            {
                'stage': 2,
                'description': 'Switch to right lane closure, maintain left and center',
                'duration': '50% of project',
                'traffic_impact': 'Minor delays'
            }
        ]
        staging['rationale'] = 'Multi-lane road allows staged approach maintaining 2 lanes open'
    else:
        staging['recommended_stages'] = [
            {
                'stage': 1,
                'description': 'Single lane closure with traffic control',
                'duration': 'Full project',
                'traffic_impact': 'Moderate delays expected'
            }
        ]
        staging['rationale'] = '2-lane road requires single stage with traffic controllers'
    
    return staging

async def calculate_detour_routes(lat: float, lng: float, address: str):
    """Calculate detour routes for road closures"""
    
    # This would use Google Directions API with waypoints
    # For now, provide template
    


def suggest_pedestrian_controls(work_type: str, osm_data: dict, public_facilities: dict):
    """
    Suggest pedestrian control measures based on scenario
    Includes pedestrian detours, barriers, signage, and safety measures
    """
    
    pedestrian_measures = {
        'barriers_required': [],
        'pedestrian_detours': [],
        'signage': [],
        'safety_measures': [],
        'access_requirements': []
    }
    
    has_footpath = osm_data.get('has_footpath', False)
    has_schools = len(public_facilities.get('schools', [])) > 0
    has_hospitals = len(public_facilities.get('hospitals', [])) > 0
    
    # Barriers
    if has_footpath:
        pedestrian_measures['barriers_required'].extend([
            {
                'type': 'Pedestrian Barrier Fencing',
                'location': 'Along workzone perimeter adjacent to footpath',
                'specification': 'AS 1742.3 compliant, minimum 1.2m high',
                'quantity_estimate': 'Per meter of workzone length'
            },
            {
                'type': 'Pedestrian Mesh Fencing',
                'location': 'Separation between workzone and pedestrian path',
                'specification': '2.0m high chain mesh or solid hoarding',
                'visibility': 'Must maintain sight lines for pedestrians'
            }
        ])
    
    # Pedestrian Detours
    if work_type and ('closure' in work_type.lower() or 'excavation' in work_type.lower()):
        pedestrian_measures['pedestrian_detours'].append({
            'type': 'Pedestrian Detour Route',
            'description': 'Alternative pedestrian path around workzone',
            'requirements': [
                'Minimum 1.0m clear width (DDA compliant)',
                'Maximum grade 1:14 (7.1%) for DDA compliance',
                'Tactile ground surface indicators at decision points',
                'Handrails if grade exceeds 1:20',
                'Clear signage at diversion points'
            ],
            'signage_required': [
                'Pedestrians Use Other Side',
                'Pedestrian Detour',
                'Directional arrows'
            ]
        })
    
    # Signage for Pedestrians
    pedestrian_measures['signage'].extend([
        {
            'code': 'P1-1',
            'name': 'Pedestrian Detour',
            'location': 'At start of pedestrian diversion',
            'placement': 'Both sides if bilateral footpaths'
        },
        {
            'code': 'P1-2',
            'name': 'Footpath Closed',
            'location': 'At closure point',
            'placement': 'Directly at closed footpath entrance'
        },
        {
            'code': 'P1-3',
            'name': 'Pedestrians Use Other Side',
            'location': 'Before workzone',
            'placement': 'With directional arrow'
        }
    ])
    
    # Safety Measures
    pedestrian_measures['safety_measures'].extend([
        {
            'measure': 'Separation Distance',
            'requirement': 'Minimum 1.2m clearance between traffic and pedestrian path',
            'standard': 'AS 1742.3 Table 5.2'
        },
        {
            'measure': 'Lighting',
            'requirement': 'Adequate lighting for night works',
            'specification': 'Minimum 20 lux at pedestrian level'
        },
        {
            'measure': 'Visibility',
            'requirement': 'High visibility bollards and delineators',
            'spacing': 'Every 2-3 meters along pedestrian path'
        }
    ])
    
    # Access Requirements
    if has_schools:
        pedestrian_measures['access_requirements'].append({
            'facility': 'Schools',
            'requirement': 'Maintain safe pedestrian access during school hours',
            'peak_times': '8:00-9:00am, 3:00-4:00pm',
            'special_consideration': 'Additional supervision may be required during peak times'
        })
    
    if has_hospitals:
        pedestrian_measures['access_requirements'].append({
            'facility': 'Hospital',
            'requirement': 'Maintain 24/7 pedestrian emergency access',
            'special_consideration': 'Clear signage to emergency department entrance'
        })
    
    # DDA Compliance
    pedestrian_measures['access_requirements'].append({
        'compliance': 'DDA (Disability Discrimination Act)',
        'requirements': [
            'Minimum 1.0m clear path width',
            'Maximum cross-fall 1:40 (2.5%)',
            'Maximum grade 1:14 (7.1%)',
            'Tactile ground surface indicators',
            'No protruding objects above 680mm or below 2000mm'
        ]
    })
    
    return pedestrian_measures


def generate_signage_plan(work_type: str, osm_data: dict, side_streets: list, intersections: list):
    """
    Generate comprehensive signage plan with:
    - Austroads-compliant advance warning distances
    - Bilateral signage requirements
    - Side street signing (double gating)
    - All distances documented
    """
    
    speed = osm_data.get('speed_limit', 60)
    lanes = osm_data.get('lanes', 2)
    
    signage_plan = {
        'advance_warning_signs': [],
        'workzone_signs': [],
        'side_street_signs': [],
        'end_of_works_signs': [],
        'bilateral_requirements': {},
        'distances_documented': {}
    }
    
    # Calculate Austroads advance warning distances based on speed
    # AS 1742.3 - Table 6.2
    if speed <= 60:
        adv_warning_dist = 90  # meters
        intermediate_dist = 50  # meters
    elif speed <= 80:
        adv_warning_dist = 150  # meters
        intermediate_dist = 90  # meters
    elif speed <= 100:
        adv_warning_dist = 250  # meters
        intermediate_dist = 150  # meters
    else:
        adv_warning_dist = 350  # meters
        intermediate_dist = 250  # meters
    
    # Document distances
    signage_plan['distances_documented'] = {
        'speed_limit': f'{speed} km/h',
        'advance_warning_distance': f'{adv_warning_dist}m (AS 1742.3 Table 6.2)',
        'intermediate_distance': f'{intermediate_dist}m',
        'taper_length': f'{calculate_taper_length(speed, lanes)}m',
        'buffer_zone': f'{calculate_buffer_zone(speed)}m',
        'standard_reference': 'AS 1742.3:2019 - Manual of uniform traffic control devices, Part 3: Traffic control for works on roads'
    }
    
    # Advance Warning Signs (BILATERAL)
    signage_plan['advance_warning_signs'].append({
        'sign_code': 'T1-1',
        'name': 'Road Work Ahead',
        'position': f'-{adv_warning_dist}m from workzone start',
        'placement': 'BILATERAL (both sides of road)',
        'quantity': 2,
        'mounting_height': '2.0-2.5m (AS 1742.3)',
        'lateral_offset': '0.5-1.0m from edge of carriageway',
        'notes': 'Must be on both sides for multi-lane roads'
    })
    
    if lanes > 1:
        signage_plan['advance_warning_signs'].append({
            'sign_code': 'T1-2',
            'name': 'Lane Closure Ahead',
            'position': f'-{intermediate_dist}m from lane closure',
            'placement': 'BILATERAL (both sides of road)',
            'quantity': 2,
            'mounting_height': '2.0-2.5m',
            'lateral_offset': '0.5-1.0m from edge of carriageway'
        })
    
    # Speed Reduction Signs (BILATERAL)
    if speed > 40:
        signage_plan['advance_warning_signs'].append({
            'sign_code': 'R4-1(40)',
            'name': 'Speed Limit 40',
            'position': f'-{intermediate_dist + 20}m from workzone',
            'placement': 'BILATERAL (both sides of road)',
            'quantity': 2,
            'mounting_height': '2.0-2.5m',
            'compliance': 'Regulatory sign - enforceable by law'
        })
    
    # Workzone Signs
    signage_plan['workzone_signs'].extend([
        {
            'sign_code': 'T1-3',
            'name': 'Work Zone',
            'position': 'At start of workzone',
            'placement': 'BILATERAL',
            'quantity': 2
        },
        {
            'sign_code': 'D5-1',
            'name': 'Traffic Cones 700mm',
            'position': 'Taper and workzone perimeter',
            'spacing': f'{calculate_cone_spacing(speed)}m spacing',
            'quantity': 'Variable based on workzone length',
            'specification': '700mm high, retroreflective, weighted base'
        }
    ])
    
    # Side Street Signs (DOUBLE GATING)
    for side_street in side_streets[:5]:  # Limit to 5 nearest
        signage_plan['side_street_signs'].append({
            'side_street_name': side_street['name'],
            'requirement': 'DOUBLE GATING - Signs on both approaches to intersection',
            'signs': [
                {
                    'sign_code': 'T1-1',
                    'name': 'Road Work Ahead',
                    'position': f'On {side_street["name"]} approaching main road',
                    'placement': 'Both approaches (north & south, or east & west)',
                    'quantity': 2,
                    'distance_from_intersection': '50-90m depending on visibility',
                    'notes': 'AS 1742.3 requires warning on all approaches to workzone'
                },
                {
                    'sign_code': 'T1-5',
                    'name': 'Expect Delays',
                    'position': f'On {side_street["name"]} 20m before intersection',
                    'placement': 'Both approaches',
                    'quantity': 2
                }
            ]
        })
    
    # Intersection Signs
    for intersection in intersections[:3]:
        signage_plan['side_street_signs'].append({
            'intersection_name': intersection['name'],
            'type': intersection['type'],
            'requirement': 'BILATERAL WARNING on all approaches',
            'signs': [
                {
                    'sign_code': 'T1-4',
                    'name': 'Road Work at Intersection',
                    'placement': 'All intersection approaches (4-way or 3-way)',
                    'quantity': 3 if intersection['type'] == 'T-intersection' else 4,
                    'distance_from_intersection': '50-90m on each approach'
                }
            ]
        })
    
    # End of Works Signs (BILATERAL)
    signage_plan['end_of_works_signs'].append({
        'sign_code': 'G2-4',
        'name': 'End Road Work',
        'position': '+50m after workzone end',
        'placement': 'BILATERAL (both sides of road)',
        'quantity': 2,
        'mounting_height': '2.0-2.5m',
        'notes': 'Indicates return to normal conditions'
    })
    
    if speed > 40:
        signage_plan['end_of_works_signs'].append({
            'sign_code': 'R4-1(60)',
            'name': f'Speed Limit {speed}',
            'position': '+55m after workzone end',
            'placement': 'BILATERAL (both sides of road)',
            'quantity': 2,
            'notes': 'Reinstates normal speed limit'
        })
    
    # Bilateral Requirements Summary
    signage_plan['bilateral_requirements'] = {
        'applies_to': 'Multi-lane roads and roads with speed limits >60 km/h',
        'definition': 'Signs must be placed on BOTH sides of the road',
        'standard': 'AS 1742.3 Clause 6.3.2',
        'total_bilateral_signs': sum([
            len(signage_plan['advance_warning_signs']),
            len(signage_plan['workzone_signs']) if 'BILATERAL' in str(signage_plan['workzone_signs']) else 0,
            len(signage_plan['end_of_works_signs'])
        ]),
        'compliance_note': 'All regulatory and warning signs in workzone MUST be bilateral for roads with >1 lane per direction'
    }
    
    return signage_plan


def calculate_taper_length(speed: int, lanes: int) -> int:
    """Calculate taper length per AS 1742.3 formula: L = W * S / 2"""
    lane_width = 3.5  # Standard lane width in meters
    if speed <= 60:
        return int(lane_width * speed / 2)
    else:
        return int(lane_width * speed / 1.5)


def calculate_buffer_zone(speed: int) -> int:
    """Calculate buffer zone per AS 1742.3"""
    if speed <= 60:
        return 30
    elif speed <= 80:
        return 50
    else:
        return 80


def calculate_cone_spacing(speed: int) -> int:
    """Calculate cone spacing per AS 1742.3"""
    if speed <= 60:
        return 5  # 5m spacing
    elif speed <= 80:
        return 10  # 10m spacing
    else:
        return 20  # 20m spacing

    detour = {
        'northbound': {
            'route': 'Via alternative streets',
            'distance_added': '~2km',
            'time_added': '~5 minutes',
            'signage_points': []
        },
        'southbound': {
            'route': 'Via alternative streets',
            'distance_added': '~2km',
            'time_added': '~5 minutes',
            'signage_points': []
        },
        'notes': 'Detailed detour route to be confirmed with road authority'
    }
    
    return detour
