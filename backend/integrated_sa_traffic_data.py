"""
Integration of Successfully Fetched SA Government Datasets into TMP System
Adds Top 40 Roads, Top 40 Intersections, and Travel Speed data to auto-population
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Successfully integrated resource IDs
TOP_40_ROADS_RESOURCE_ID = "16375bfa-0b0d-4fcd-8b79-ec97bdddb6b8"
TOP_40_INTERSECTIONS_RESOURCE_ID = "8bff8123-d93e-40ee-92a4-ab13137831b4"
TRAVEL_SPEED_RESOURCE_ID = "d0d3501e-1b87-4c1c-8d86-46ad18039500"

SA_DATA_API = "https://data.sa.gov.au/data/api/3/action/datastore_search"


async def fetch_top_40_roads() -> Dict[str, Any]:
    """
    Fetch Top 40 road sections with traffic volumes from SA Government
    """
    result = {
        'roads': [],
        'total_roads': 0,
        'data_source': 'DIT SA - Top 40 Road Sections',
        'success': False
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                'resource_id': TOP_40_ROADS_RESOURCE_ID,
                'limit': 40
            }
            
            response = await client.get(SA_DATA_API, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('result', {}).get('records'):
                    records = data['result']['records']
                    
                    for record in records:
                        road = {
                            'rank': record.get('Rank'),
                            'road_no': record.get('Road No'),
                            'road_name': record.get('Road Name'),
                            'start_location': record.get('Start RRD'),
                            'end_location': record.get('End RRD'),
                            'length_km': record.get('Length (km)'),
                            'aadt': record.get('AADT 2023'),  # Annual Average Daily Traffic
                            'description': f"{record.get('Road No')} {record.get('Road Name')}"
                        }
                        result['roads'].append(road)
                    
                    result['total_roads'] = len(result['roads'])
                    result['success'] = True
                    logger.info(f"Fetched {result['total_roads']} top roads")
                    
    except Exception as e:
        logger.error(f"Error fetching top 40 roads: {str(e)}")
    
    return result


async def match_location_to_top_roads(address: str, lat: float, lng: float) -> Dict[str, Any]:
    """
    Check if work site location matches any of the Top 40 roads
    """
    match_result = {
        'is_top_40_road': False,
        'road_match': None,
        'traffic_volume': None,
        'rank': None,
        'message': ''
    }
    
    try:
        # Fetch top 40 roads
        roads_data = await fetch_top_40_roads()
        
        if roads_data['success']:
            # Simple matching based on road name in address
            address_lower = address.lower()
            
            for road in roads_data['roads']:
                road_name = road.get('road_name', '').lower()
                road_no = str(road.get('road_no', '')).lower()
                
                if road_name and road_name in address_lower:
                    match_result['is_top_40_road'] = True
                    match_result['road_match'] = road
                    match_result['traffic_volume'] = road.get('aadt')
                    match_result['rank'] = road.get('rank')
                    match_result['message'] = f"⚠️ HIGH TRAFFIC LOCATION: Ranked #{road.get('rank')} busiest road in SA with {road.get('aadt'):,} AADT"
                    break
                elif road_no and road_no in address_lower:
                    match_result['is_top_40_road'] = True
                    match_result['road_match'] = road
                    match_result['traffic_volume'] = road.get('aadt')
                    match_result['rank'] = road.get('rank')
                    match_result['message'] = f"⚠️ HIGH TRAFFIC LOCATION: Ranked #{road.get('rank')} busiest road in SA with {road.get('aadt'):,} AADT"
                    break
            
            if not match_result['is_top_40_road']:
                match_result['message'] = 'Location not in Top 40 busiest SA roads'
                
    except Exception as e:
        logger.error(f"Error matching location to top roads: {str(e)}")
        match_result['message'] = 'Unable to check Top 40 roads'
    
    return match_result


async def fetch_top_40_intersections() -> Dict[str, Any]:
    """
    Fetch Top 40 intersections with vehicle exposure from SA Government
    """
    result = {
        'intersections': [],
        'total_intersections': 0,
        'data_source': 'DIT SA - Top 40 Intersections',
        'success': False
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                'resource_id': TOP_40_INTERSECTIONS_RESOURCE_ID,
                'limit': 40
            }
            
            response = await client.get(SA_DATA_API, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('result', {}).get('records'):
                    records = data['result']['records']
                    
                    for record in records:
                        intersection = {
                            'rank': record.get('Rank'),
                            'location': record.get('Location'),
                            'vehicle_exposure': record.get('Vehicle Exposure'),
                            'description': record.get('Location')
                        }
                        result['intersections'].append(intersection)
                    
                    result['total_intersections'] = len(result['intersections'])
                    result['success'] = True
                    logger.info(f"Fetched {result['total_intersections']} top intersections")
                    
    except Exception as e:
        logger.error(f"Error fetching top 40 intersections: {str(e)}")
    
    return result


async def match_location_to_top_intersections(address: str, lat: float, lng: float) -> Dict[str, Any]:
    """
    Check if work site location matches any of the Top 40 intersections
    """
    match_result = {
        'is_top_40_intersection': False,
        'intersection_match': None,
        'vehicle_exposure': None,
        'rank': None,
        'message': ''
    }
    
    try:
        # Fetch top 40 intersections
        intersections_data = await fetch_top_40_intersections()
        
        if intersections_data['success']:
            # Simple matching based on intersection location in address
            address_lower = address.lower()
            
            for intersection in intersections_data['intersections']:
                location = intersection.get('location', '').lower()
                
                # Check if key parts of intersection location are in address
                if location and any(part in address_lower for part in location.split() if len(part) > 3):
                    match_result['is_top_40_intersection'] = True
                    match_result['intersection_match'] = intersection
                    match_result['vehicle_exposure'] = intersection.get('vehicle_exposure')
                    match_result['rank'] = intersection.get('rank')
                    match_result['message'] = f"⚠️ MAJOR INTERSECTION: Ranked #{intersection.get('rank')} busiest intersection in SA"
                    break
            
            if not match_result['is_top_40_intersection']:
                match_result['message'] = 'Location not in Top 40 busiest SA intersections'
                
    except Exception as e:
        logger.error(f"Error matching location to top intersections: {str(e)}")
        match_result['message'] = 'Unable to check Top 40 intersections'
    
    return match_result


async def fetch_travel_speeds() -> Dict[str, Any]:
    """
    Fetch travel speed data for Metropolitan Adelaide
    """
    result = {
        'speed_data': [],
        'total_records': 0,
        'data_source': 'DIT SA - Travel Speed Metropolitan Adelaide',
        'success': False
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                'resource_id': TRAVEL_SPEED_RESOURCE_ID,
                'limit': 150
            }
            
            response = await client.get(SA_DATA_API, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('result', {}).get('records'):
                    records = data['result']['records']
                    result['speed_data'] = records
                    result['total_records'] = len(records)
                    result['success'] = True
                    logger.info(f"Fetched {result['total_records']} speed records")
                    
    except Exception as e:
        logger.error(f"Error fetching travel speeds: {str(e)}")
    
    return result


async def get_traffic_intelligence_for_location(address: str, lat: float, lng: float) -> Dict[str, Any]:
    """
    Main function to get all traffic intelligence data for a location
    Combines Top 40 roads, Top 40 intersections, and travel speed data
    """
    result = {
        'top_40_road_analysis': {},
        'top_40_intersection_analysis': {},
        'travel_speed_data': {},
        'overall_traffic_level': 'Unknown',
        'recommendations': []
    }
    
    try:
        # Run all fetches concurrently
        road_match, intersection_match, speed_data = await asyncio.gather(
            match_location_to_top_roads(address, lat, lng),
            match_location_to_top_intersections(address, lat, lng),
            fetch_travel_speeds()
        )
        
        result['top_40_road_analysis'] = road_match
        result['top_40_intersection_analysis'] = intersection_match
        result['travel_speed_data'] = speed_data
        
        # Determine overall traffic level
        if road_match['is_top_40_road']:
            rank = road_match['rank']
            if rank <= 10:
                result['overall_traffic_level'] = 'VERY HIGH'
                result['recommendations'].append('⚠️ Top 10 busiest road - Maximum traffic control required')
                result['recommendations'].append('Consider night/weekend works to minimize disruption')
                result['recommendations'].append('Multiple advance warning signs essential')
            elif rank <= 20:
                result['overall_traffic_level'] = 'HIGH'
                result['recommendations'].append('⚠️ Major traffic route - Enhanced traffic management required')
                result['recommendations'].append('Traffic management personnel recommended')
            else:
                result['overall_traffic_level'] = 'MEDIUM-HIGH'
                result['recommendations'].append('Busy road - Standard enhanced traffic control required')
        
        if intersection_match['is_top_40_intersection']:
            result['recommendations'].append('⚠️ Major intersection - Coordinate with DIT signal timing')
            result['recommendations'].append('Consider impacts on turning movements')
        
        if not road_match['is_top_40_road'] and not intersection_match['is_top_40_intersection']:
            result['overall_traffic_level'] = 'MODERATE'
            result['recommendations'].append('Standard traffic control measures appropriate')
        
    except Exception as e:
        logger.error(f"Error getting traffic intelligence: {str(e)}")
        result['error'] = str(e)
    
    return result


# Test function
if __name__ == "__main__":
    async def test():
        # Test with Adelaide CBD location (King William Street)
        result = await get_traffic_intelligence_for_location(
            "King William Street, Adelaide SA",
            -34.9285,
            138.6007
        )
        
        import json
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test())
