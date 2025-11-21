"""
Road Geometry Processor
Extracts precise road edge coordinates from OpenStreetMap data
Ensures traffic control devices are placed at exact road edges
"""

import requests
import math
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RoadGeometryProcessor:
    """Process road geometry to calculate precise edge positions"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
    
    def get_road_geometry(self, lat: float, lng: float, radius: int = 50) -> Optional[Dict]:
        """
        Get detailed road geometry from OpenStreetMap
        
        Args:
            lat: Latitude of point on road
            lng: Longitude of point on road
            radius: Search radius in meters (default 50m)
        
        Returns:
            Dict with road geometry data including edges, width, lanes
        """
        try:
            # Overpass query to get road geometry
            query = f"""
            [out:json];
            (
              way["highway"](around:{radius},{lat},{lng});
            );
            out geom;
            """
            
            response = requests.post(
                self.overpass_url,
                data={"data": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('elements'):
                    # Get the closest road way
                    road_way = data['elements'][0]
                    
                    # Extract road properties
                    tags = road_way.get('tags', {})
                    geometry = road_way.get('geometry', [])
                    
                    # Calculate road width from lanes or default values
                    road_width = self._calculate_road_width(tags)
                    
                    # Get road centerline points
                    centerline = [(node['lat'], node['lon']) for node in geometry]
                    
                    # Calculate road edges (left and right from centerline)
                    edges = self._calculate_road_edges(centerline, road_width)
                    
                    return {
                        'road_name': tags.get('name', 'Unknown Road'),
                        'highway_type': tags.get('highway', 'road'),
                        'lanes': int(tags.get('lanes', 2)),
                        'width': road_width,
                        'surface': tags.get('surface', 'asphalt'),
                        'maxspeed': tags.get('maxspeed', '50'),
                        'centerline': centerline,
                        'left_edge': edges['left'],
                        'right_edge': edges['right'],
                        'bearing': self._calculate_bearing(centerline[0], centerline[-1]) if len(centerline) >= 2 else 0
                    }
            
            logger.warning(f"No road geometry found at {lat}, {lng}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching road geometry: {str(e)}")
            return None
    
    def _calculate_road_width(self, tags: Dict) -> float:
        """
        Calculate road width from OSM tags
        
        Standard lane widths:
        - Urban roads: 3.0-3.5m per lane
        - Rural roads: 3.5m per lane
        - Highways: 3.5-3.75m per lane
        """
        # Check if width is explicitly tagged
        if 'width' in tags:
            try:
                return float(tags['width'].replace('m', '').strip())
            except:
                pass
        
        # Calculate from number of lanes
        lanes = int(tags.get('lanes', 2))
        highway_type = tags.get('highway', 'road')
        
        # Lane width standards
        if highway_type in ['motorway', 'trunk']:
            lane_width = 3.75
        elif highway_type in ['primary', 'secondary']:
            lane_width = 3.5
        else:
            lane_width = 3.0
        
        # Total carriageway width
        carriageway_width = lanes * lane_width
        
        # Add shoulders/verges if major road
        if highway_type in ['motorway', 'trunk', 'primary']:
            # Add 1.5m shoulders on each side
            return carriageway_width + 3.0
        elif highway_type in ['secondary', 'tertiary']:
            # Add 1m verges on each side
            return carriageway_width + 2.0
        else:
            # Residential roads - just carriageway
            return carriageway_width
    
    def _calculate_road_edges(self, centerline: List[Tuple[float, float]], width: float) -> Dict:
        """
        Calculate left and right road edges from centerline
        
        Args:
            centerline: List of (lat, lon) tuples representing road center
            width: Total road width in meters
        
        Returns:
            Dict with 'left' and 'right' edge coordinates
        """
        if not centerline or len(centerline) < 2:
            return {'left': [], 'right': []}
        
        left_edge = []
        right_edge = []
        half_width = width / 2
        
        for i in range(len(centerline)):
            lat, lon = centerline[i]
            
            # Calculate bearing at this point
            if i < len(centerline) - 1:
                # Use next point
                bearing = self._calculate_bearing(
                    (lat, lon),
                    centerline[i + 1]
                )
            elif i > 0:
                # Use previous point
                bearing = self._calculate_bearing(
                    centerline[i - 1],
                    (lat, lon)
                )
            else:
                bearing = 0
            
            # Calculate perpendicular offsets (90 degrees left and right)
            left_lat, left_lon = self._offset_position(lat, lon, bearing - 90, half_width)
            right_lat, right_lon = self._offset_position(lat, lon, bearing + 90, half_width)
            
            left_edge.append((left_lat, left_lon))
            right_edge.append((right_lat, right_lon))
        
        return {
            'left': left_edge,
            'right': right_edge
        }
    
    def get_device_position_on_road_edge(
        self, 
        road_geometry: Dict, 
        distance_along_road: float, 
        side: str,
        lateral_offset: float = 2.0
    ) -> Tuple[float, float]:
        """
        Get precise position for a device at specified distance along road edge
        
        Args:
            road_geometry: Road geometry data from get_road_geometry()
            distance_along_road: Distance in meters from start of road segment
            side: 'left' or 'right' side of road
            lateral_offset: Additional offset from road edge (verge placement)
        
        Returns:
            (latitude, longitude) tuple for device position
        """
        centerline = road_geometry['centerline']
        
        if not centerline or len(centerline) < 2:
            # Fallback to first point
            return (centerline[0][0], centerline[0][1]) if centerline else (0, 0)
        
        # Find point along centerline at specified distance
        cumulative_distance = 0
        target_index = 0
        
        for i in range(len(centerline) - 1):
            segment_distance = self._calculate_distance(
                centerline[i][0], centerline[i][1],
                centerline[i + 1][0], centerline[i + 1][1]
            )
            
            if cumulative_distance + segment_distance >= distance_along_road:
                # This segment contains our target distance
                target_index = i
                break
            
            cumulative_distance += segment_distance
        
        # Get the point on centerline
        center_lat, center_lon = centerline[target_index]
        
        # Calculate bearing at this point
        if target_index < len(centerline) - 1:
            bearing = self._calculate_bearing(
                (center_lat, center_lon),
                centerline[target_index + 1]
            )
        else:
            bearing = self._calculate_bearing(
                centerline[target_index - 1],
                (center_lat, center_lon)
            )
        
        # Calculate position at road edge + lateral offset
        total_offset = (road_geometry['width'] / 2) + lateral_offset
        
        # Left side = bearing - 90, Right side = bearing + 90
        perpendicular_bearing = bearing - 90 if side == 'left' else bearing + 90
        
        device_lat, device_lon = self._offset_position(
            center_lat, center_lon, 
            perpendicular_bearing, 
            total_offset
        )
        
        return (device_lat, device_lon)
    
    def _calculate_bearing(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate bearing between two points in degrees"""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlon = lon2 - lon1
        
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(x, y)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters using Haversine formula"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _offset_position(self, lat: float, lon: float, bearing: float, distance: float) -> Tuple[float, float]:
        """
        Calculate new position given start point, bearing and distance
        
        Args:
            lat: Starting latitude
            lon: Starting longitude
            bearing: Bearing in degrees
            distance: Distance in meters
        
        Returns:
            (new_lat, new_lon) tuple
        """
        R = 6371000  # Earth radius in meters
        
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Calculate new position
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance/R) +
            math.cos(lat_rad) * math.sin(distance/R) * math.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance/R) * math.cos(lat_rad),
            math.cos(distance/R) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        return (math.degrees(new_lat_rad), math.degrees(new_lon_rad))


# Global instance
road_geometry_processor = RoadGeometryProcessor()
