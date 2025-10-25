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
