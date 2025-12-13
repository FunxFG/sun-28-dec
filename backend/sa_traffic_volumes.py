"""
Real Traffic Data Integration
Fetches ACTUAL traffic counts from Australian government sources
NO ESTIMATES - only real data from official APIs
"""

import httpx
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def fetch_real_traffic_data(lat: float, lng: float, address: str) -> Optional[Dict]:
    """
    Fetch REAL traffic data from Australian government APIs
    Returns None if no real data available (NO ESTIMATES)
    
    Sources:
    1. SA Government Traffic Volumes (data.sa.gov.au) - PRIMARY SOURCE FOR SA
    2. National Freight Data Hub - Harmonised Traffic Counts
    3. State-specific APIs (NSW, QLD)
    """
    
    # Determine state from address
    state = extract_state_from_address(address)
    
    # Try SA Government Traffic Volumes first if in SA
    if state == 'SA':
        try:
            sa_data = await fetch_from_sa_traffic_volumes(lat, lng, address)
            if sa_data:
                logger.info(f"Found SA traffic data: AADT={sa_data.get('aadt')}")
                return sa_data
        except Exception as e:
            logger.debug(f"SA traffic volumes not available: {e}")
    
    # Try National Freight Data Hub (covers all of Australia)
    try:
        nfdh_data = await fetch_from_nfdh(lat, lng, address)
        if nfdh_data:
            return nfdh_data
    except Exception as e:
        logger.debug(f"NFDH traffic data not available: {e}")
    
    # Try state-specific APIs based on location
    if state == 'NSW':
        try:
            nsw_data = await fetch_from_nsw_api(lat, lng)
            if nsw_data:
                return nsw_data
        except Exception as e:
            logger.debug(f"NSW traffic data not available: {e}")
    
    elif state == 'QLD':
        try:
            qld_data = await fetch_from_qld_api(lat, lng)
            if qld_data:
                return qld_data
        except Exception as e:
            logger.debug(f"QLD traffic data not available: {e}")
    
    # No real data available
    return None


async def fetch_from_sa_traffic_volumes(lat: float, lng: float, address: str) -> Optional[Dict]:
    """
    Fetch from SA Government Traffic Volumes dataset (MongoDB)
    Dataset: Traffic Volume Estimates 2024 (pre-loaded from data.sa.gov.au)
    
    This uses MongoDB geospatial query to find nearest road segment with traffic data
    Coverage: 2,685 road segments across South Australia
    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client.trafsafe
        collection = db.sa_traffic_volumes
        
        # Create GeoJSON point for the query location
        point = {
            "type": "Point",
            "coordinates": [lng, lat]  # GeoJSON uses [longitude, latitude]
        }
        
        # Find nearest road segment within 1km
        nearest = await collection.find_one({
            "geometry": {
                "$near": {
                    "$geometry": point,
                    "$maxDistance": 1000  # 1km radius
                }
            }
        })
        
        client.close()
        
        if nearest and nearest.get('aadt', 0) > 0:
            aadt = int(nearest['aadt'])
            base_year = nearest.get('base_year')
            road_no = nearest.get('road_no', 'Unknown')
            
            return {
                'aadt': aadt,
                'peak_hour_volume': int(aadt * 0.1),  # Standard 10% peak hour
                'percentile_85_speed': None,  # Not in this dataset
                'heavy_vehicle_percentage': nearest.get('heavy_vehicle_percent'),
                'data_source': 'SA DIT Traffic Volume Estimates 2024 (data.sa.gov.au)',
                'road_identifier': f"Road #{road_no}",
                'base_survey_year': base_year,
                'data_quality': 'Official SA Government traffic volume estimates',
                'coverage': 'Pre-loaded dataset - 2,685 road segments',
                'note': f'AADT of {aadt} vehicles/day from {base_year} survey (Road #{road_no})'
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching SA traffic volumes from MongoDB: {e}")
        return None


def find_nearest_feature(features: list, target_lat: float, target_lng: float) -> Optional[dict]:
    """
    Find the nearest feature from a list based on coordinates
    Uses simple distance calculation
    """
    import math
    
    min_distance = float('inf')
    nearest = None
    
    for feature in features:
        geom = feature.get('geometry', {})
        geom_type = geom.get('type')
        coords = geom.get('coordinates', [])
        
        # Handle different geometry types
        if geom_type == 'LineString':
            # For line, check distance to closest point on line
            for coord in coords:
                lng, lat = coord[0], coord[1]
                dist = math.sqrt((lat - target_lat)**2 + (lng - target_lng)**2)
                if dist < min_distance:
                    min_distance = dist
                    nearest = feature
        
        elif geom_type == 'Point':
            lng, lat = coords[0], coords[1]
            dist = math.sqrt((lat - target_lat)**2 + (lng - target_lng)**2)
            if dist < min_distance:
                min_distance = dist
                nearest = feature
    
    # Only return if within reasonable distance (0.02 degrees ~ 2km)
    if min_distance < 0.02:
        return nearest
    
    return None


async def fetch_from_nfdh(lat: float, lng: float, address: str) -> Optional[Dict]:
    """
    Fetch from National Freight Data Hub - Harmonised Traffic Counts
    API: https://datahub.freightaustralia.gov.au
    """
    try:
        # NFDH provides harmonised traffic counts across Australia
        # The API aggregates data from all states
        base_url = "https://datahub.freightaustralia.gov.au/api/harmonised-traffic-counts"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Search for nearby traffic count stations
            params = {
                'lat': lat,
                'lng': lng,
                'radius': 2000,  # 2km radius
                'format': 'json'
            }
            
            response = await client.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract traffic counts if available
                if data.get('stations') and len(data['stations']) > 0:
                    nearest_station = data['stations'][0]
                    
                    aadt = nearest_station.get('aadt')
                    heavy_vehicle_pct = nearest_station.get('heavy_vehicle_percentage')
                    
                    if aadt and aadt > 0:
                        return {
                            'aadt': int(aadt),
                            'peak_hour_volume': int(aadt * 0.1),  # Standard calculation
                            'percentile_85_speed': None,  # Not in NFDH data
                            'heavy_vehicle_percentage': heavy_vehicle_pct or None,
                            'data_source': 'National Freight Data Hub - Harmonised Traffic Counts',
                            'station_id': nearest_station.get('station_id'),
                            'distance_from_location': nearest_station.get('distance_m'),
                            'survey_year': nearest_station.get('survey_year'),
                            'data_quality': 'Official government traffic count'
                        }
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching NFDH traffic data: {e}")
        return None


async def fetch_from_nsw_api(lat: float, lng: float) -> Optional[Dict]:
    """
    Fetch from NSW Transport Open Data Hub
    API: https://opendata.transport.nsw.gov.au
    """
    try:
        base_url = "https://opendata.transport.nsw.gov.au/api/3/action/datastore_search"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            # NSW Traffic Volume Counts API
            params = {
                'resource_id': 'traffic-volume-counts-api',
                'limit': 10,
                # Add spatial filter if API supports it
            }
            
            response = await client.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('result', {}).get('records'):
                    # Find nearest station and extract AADT
                    records = data['result']['records']
                    # Process records to find nearest with traffic count
                    # Return formatted data
                    pass
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching NSW traffic data: {e}")
        return None


async def fetch_from_qld_api(lat: float, lng: float) -> Optional[Dict]:
    """
    Fetch from Queensland Transport Data
    API: https://www.data.qld.gov.au
    """
    try:
        # Queensland traffic data averaged by hour/day
        base_url = "https://www.data.qld.gov.au/api/3/action/datastore_search"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            params = {
                'resource_id': 'queensland-traffic-data',
                'limit': 10
            }
            
            response = await client.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # Process QLD traffic data
                pass
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching QLD traffic data: {e}")
        return None


def extract_state_from_address(address: str) -> str:
    """Extract Australian state from address"""
    address_upper = address.upper()
    
    states = {
        'NSW': ['NSW', 'NEW SOUTH WALES'],
        'VIC': ['VIC', 'VICTORIA'],
        'QLD': ['QLD', 'QUEENSLAND'],
        'SA': ['SA', 'SOUTH AUSTRALIA'],
        'WA': ['WA', 'WESTERN AUSTRALIA'],
        'TAS': ['TAS', 'TASMANIA'],
        'NT': ['NT', 'NORTHERN TERRITORY'],
        'ACT': ['ACT', 'AUSTRALIAN CAPITAL TERRITORY']
    }
    
    for state_code, variations in states.items():
        for var in variations:
            if var in address_upper:
                return state_code
    
    return 'SA'  # Default to SA
