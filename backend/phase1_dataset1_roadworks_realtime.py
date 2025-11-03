"""
Phase 1 - Dataset #1: Real-Time Roadworks, Incidents & Road Closures
CRITICAL PRIORITY - Prevents TMP conflicts with existing roadworks
Resource ID: 8d75dfcc-cc95-4be3-8747-ff273e8c53db
"""

import httpx
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

SA_DATA_API = "https://data.sa.gov.au/data/api/3/action/datastore_search"
ROADWORKS_RESOURCE_ID = "8d75dfcc-cc95-4be3-8747-ff273e8c53db"


async def fetch_realtime_roadworks_incidents(lat: float, lng: float, radius_km: float = 5.0) -> Dict[str, Any]:
    """
    Fetch real-time roadworks, incidents, road closures and detours from Traffic SA
    
    Args:
        lat: Work site latitude
        lng: Work site longitude
        radius_km: Search radius in kilometers
        
    Returns:
        Dict with active roadworks, incidents, closures, and conflict analysis
    """
    
    result = {
        'active_roadworks': [],
        'active_incidents': [],
        'road_closures': [],
        'detours': [],
        'conflicts_detected': False,
        'conflict_details': [],
        'total_items': 0,
        'search_radius_km': radius_km,
        'data_source': 'Traffic SA Real-Time Data (data.sa.gov.au)',
        'last_updated': datetime.now().isoformat(),
        'warning': None
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch roadworks data
            params = {
                'resource_id': ROADWORKS_RESOURCE_ID,
                'limit': 1000  # Get all records
            }
            
            response = await client.get(SA_DATA_API, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('result', {}).get('records'):
                    records = data['result']['records']
                    logger.info(f"Fetched {len(records)} roadworks/incidents records")
                    
                    # Process each record
                    for record in records:
                        # Try to get location data (different field names possible)
                        record_lat = None
                        record_lng = None
                        
                        # Try various field name combinations
                        for lat_field in ['Latitude', 'latitude', 'LAT', 'lat', 'LATITUDE']:
                            if lat_field in record and record[lat_field]:
                                try:
                                    record_lat = float(record[lat_field])
                                    break
                                except:
                                    pass
                        
                        for lng_field in ['Longitude', 'longitude', 'LON', 'lng', 'LONGITUDE', 'Long']:
                            if lng_field in record and record[lng_field]:
                                try:
                                    record_lng = float(record[lng_field])
                                    break
                                except:
                                    pass
                        
                        # Calculate distance if coordinates available
                        if record_lat and record_lng:
                            distance_km = calculate_distance(lat, lng, record_lat, record_lng)
                            
                            if distance_km <= radius_km:
                                # Determine item type
                                item_type = (record.get('Type') or record.get('type') or 
                                           record.get('EVENT_TYPE') or 'Unknown').lower()
                                
                                item = {
                                    'type': item_type,
                                    'description': record.get('Description') or record.get('description') or 'No description',
                                    'location': record.get('Location') or record.get('location') or f"{record_lat:.4f}, {record_lng:.4f}",
                                    'distance_km': round(distance_km, 2),
                                    'status': record.get('Status') or record.get('status') or 'Active',
                                    'start_date': record.get('StartDate') or record.get('start_date'),
                                    'end_date': record.get('EndDate') or record.get('end_date'),
                                    'impact': record.get('Impact') or record.get('impact'),
                                    'coordinates': {'lat': record_lat, 'lng': record_lng}
                                }
                                
                                # Categorize
                                if 'roadwork' in item_type or 'maintenance' in item_type or 'construction' in item_type:
                                    result['active_roadworks'].append(item)
                                    
                                    # Check for conflicts (within 1km)
                                    if distance_km < 1.0:
                                        result['conflicts_detected'] = True
                                        result['conflict_details'].append({
                                            'type': 'ROADWORK_CONFLICT',
                                            'severity': 'HIGH' if distance_km < 0.5 else 'MEDIUM',
                                            'message': f"Active roadwork within {distance_km}km: {item['description']}",
                                            'recommendation': 'Coordinate with existing works or consider alternative timing'
                                        })
                                
                                elif 'closure' in item_type or 'closed' in item_type:
                                    result['road_closures'].append(item)
                                    
                                    if distance_km < 2.0:
                                        result['conflicts_detected'] = True
                                        result['conflict_details'].append({
                                            'type': 'CLOSURE_CONFLICT',
                                            'severity': 'CRITICAL' if distance_km < 1.0 else 'HIGH',
                                            'message': f"Road closure within {distance_km}km: {item['location']}",
                                            'recommendation': 'Check detour routes and traffic diversion impact'
                                        })
                                
                                elif 'detour' in item_type:
                                    result['detours'].append(item)
                                
                                elif 'incident' in item_type or 'accident' in item_type:
                                    result['active_incidents'].append(item)
                                else:
                                    # Add to roadworks as default
                                    result['active_roadworks'].append(item)
                    
                    result['total_items'] = (len(result['active_roadworks']) + 
                                           len(result['active_incidents']) + 
                                           len(result['road_closures']))
                    
                    logger.info(f"Found {result['total_items']} items within {radius_km}km")
                    
                else:
                    result['warning'] = 'No roadworks data available from API'
                    
            else:
                result['warning'] = f'API returned status {response.status_code}'
                
    except Exception as e:
        logger.error(f"Error fetching roadworks data: {str(e)}")
        result['warning'] = f'Error accessing real-time data: {str(e)}'
    
    return result


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth radius in km
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def analyze_conflict_severity(conflicts: List[Dict]) -> Dict[str, Any]:
    """Analyze overall conflict severity"""
    if not conflicts:
        return {
            'overall_severity': 'NONE',
            'can_proceed': True,
            'recommendations': ['No conflicts detected - proceed with TMP planning']
        }
    
    # Check for critical conflicts
    critical = [c for c in conflicts if c['severity'] == 'CRITICAL']
    high = [c for c in conflicts if c['severity'] == 'HIGH']
    medium = [c for c in conflicts if c['severity'] == 'MEDIUM']
    
    if critical:
        return {
            'overall_severity': 'CRITICAL',
            'can_proceed': False,
            'recommendations': [
                '⚠️ CRITICAL CONFLICTS DETECTED',
                'Mandatory coordination with DIT Traffic Management',
                'Consider alternative location or timing',
                'Contact Traffic SA: 1300 794 880'
            ]
        }
    elif high:
        return {
            'overall_severity': 'HIGH',
            'can_proceed': 'WITH_CONDITIONS',
            'recommendations': [
                '⚠️ High impact conflicts detected',
                'Coordinate with nearby roadworks teams',
                'Enhanced traffic management required',
                'Notify Traffic SA of planned works'
            ]
        }
    elif medium:
        return {
            'overall_severity': 'MEDIUM',
            'can_proceed': True,
            'recommendations': [
                'Medium conflicts detected',
                'Awareness of nearby works required',
                'Standard traffic management adequate',
                'Monitor traffic conditions closely'
            ]
        }
    
    return {
        'overall_severity': 'LOW',
        'can_proceed': True,
        'recommendations': ['Minimal conflicts - proceed with standard TMP']
    }


# Test function
if __name__ == "__main__":
    async def test():
        # Test with Adelaide CBD
        result = await fetch_realtime_roadworks_incidents(
            lat=-34.9285,
            lng=138.6007,
            radius_km=5.0
        )
        
        import json
        print(json.dumps(result, indent=2))
        
        if result['conflicts_detected']:
            analysis = analyze_conflict_severity(result['conflict_details'])
            print("\nCONFLICT ANALYSIS:")
            print(json.dumps(analysis, indent=2))
    
    asyncio.run(test())
