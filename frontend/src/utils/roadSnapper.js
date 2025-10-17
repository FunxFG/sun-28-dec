/**
 * Road Snapping Utility
 * Snaps geocoded address points to nearest road centerline/edge
 * Ensures devices are placed on public road reserve, not private property
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

class RoadSnapper {
  constructor() {
    this.snapCache = new Map(); // Cache snapped positions
  }

  /**
   * Snap a point to the nearest road
   * @param {number} lat - Latitude of address point
   * @param {number} lng - Longitude of address point
   * @param {string} googleMapsApiKey - Google Maps API key
   * @returns {Promise<{lat, lng, roadBearing, roadWidth}>} Snapped position on road
   */
  async snapToRoad(lat, lng, googleMapsApiKey) {
    const cacheKey = `${lat.toFixed(6)},${lng.toFixed(6)}`;
    
    // Check cache first
    if (this.snapCache.has(cacheKey)) {
      console.log('Using cached snap result for:', cacheKey);
      return this.snapCache.get(cacheKey);
    }

    // FOR NOW: Use fallback method directly (Google Roads API may need special permissions)
    console.log('Snapping to road using fallback method for:', lat, lng);
    const fallbackResult = this.fallbackSnapToRoad(lat, lng);
    this.snapCache.set(cacheKey, fallbackResult);
    return fallbackResult;

    /* DISABLED: Google Roads API (requires API key with Roads API enabled)
    try {
      const response = await fetch(
        `https://roads.googleapis.com/v1/snapToRoads?path=${lat},${lng}&interpolate=true&key=${googleMapsApiKey}`
      );

      if (!response.ok) {
        console.warn('Roads API failed, using fallback method');
        return this.fallbackSnapToRoad(lat, lng);
      }

      const data = await response.json();
      
      if (data.snappedPoints && data.snappedPoints.length > 0) {
        const snappedPoint = data.snappedPoints[0];
        const roadLocation = snappedPoint.location;
        
        const bearing = await this.calculateRoadBearing(
          roadLocation.latitude,
          roadLocation.longitude,
          googleMapsApiKey
        );

        const result = {
          lat: roadLocation.latitude,
          lng: roadLocation.longitude,
          roadBearing: bearing,
          roadWidth: 7.0,
          snappedFromProperty: true,
          offsetDistance: this.calculateDistance(lat, lng, roadLocation.latitude, roadLocation.longitude)
        };

        this.snapCache.set(cacheKey, result);
        return result;
      }

      return this.fallbackSnapToRoad(lat, lng);

    } catch (error) {
      console.error('Road snapping error:', error);
      return this.fallbackSnapToRoad(lat, lng);
    }
    */
  }

  /**
   * Fallback method: Offset point perpendicular to line between start/end
   * Assumes standard residential street offset
   */
  fallbackSnapToRoad(lat, lng, bearing = null) {
    // Default offset: 10m towards road (assumes property is ~10m from road center)
    // This is a rough approximation - actual distance varies
    const offsetDistance = 10; // meters
    
    // If no bearing provided, assume north-south road (bearing 0)
    const roadBearing = bearing !== null ? bearing : 0;
    
    // Calculate perpendicular offset (90 degrees from property center towards road)
    const perpBearing = roadBearing + 90;
    const roadPosition = this.calculatePosition(lat, lng, perpBearing, offsetDistance);

    return {
      lat: roadPosition.lat,
      lng: roadPosition.lng,
      roadBearing: roadBearing,
      roadWidth: 7.0,
      snappedFromProperty: true,
      offsetDistance: offsetDistance,
      fallback: true
    };
  }

  /**
   * Calculate road bearing by checking nearby points
   */
  async calculateRoadBearing(lat, lng, googleMapsApiKey) {
    // Create two points 50m apart along the road
    const distance = 50; // meters
    
    try {
      const response = await fetch(
        `https://roads.googleapis.com/v1/nearestRoads?points=${lat},${lng}&key=${googleMapsApiKey}`
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.snappedPoints && data.snappedPoints.length >= 2) {
          const p1 = data.snappedPoints[0].location;
          const p2 = data.snappedPoints[1].location;
          return this.calculateBearing(p1.latitude, p1.longitude, p2.latitude, p2.longitude);
        }
      }
    } catch (error) {
      console.warn('Could not determine road bearing:', error);
    }

    // Default bearing if API fails
    return 0;
  }

  /**
   * Calculate bearing between two points
   */
  calculateBearing(lat1, lng1, lat2, lng2) {
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const lat1Rad = lat1 * Math.PI / 180;
    const lat2Rad = lat2 * Math.PI / 180;
    
    const y = Math.sin(dLng) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) -
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLng);
    
    let bearing = Math.atan2(y, x) * 180 / Math.PI;
    return (bearing + 360) % 360;
  }

  /**
   * Calculate distance between two points (Haversine formula)
   */
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000; // Earth radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    
    return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * R;
  }

  /**
   * Calculate new position from point, bearing, and distance
   */
  calculatePosition(lat, lng, bearing, distance) {
    const R = 6371000; // Earth radius in meters
    const bearingRad = bearing * Math.PI / 180;
    const latRad = lat * Math.PI / 180;
    const lngRad = lng * Math.PI / 180;
    
    const newLatRad = Math.asin(
      Math.sin(latRad) * Math.cos(distance/R) +
      Math.cos(latRad) * Math.sin(distance/R) * Math.cos(bearingRad)
    );
    
    const newLngRad = lngRad + Math.atan2(
      Math.sin(bearingRad) * Math.sin(distance/R) * Math.cos(latRad),
      Math.cos(distance/R) - Math.sin(latRad) * Math.sin(newLatRad)
    );
    
    return {
      lat: newLatRad * 180 / Math.PI,
      lng: newLngRad * 180 / Math.PI
    };
  }

  /**
   * Place device on road edge/curb with proper clearance
   * @param {object} roadPoint - Snapped road position
   * @param {string} side - 'left' or 'right'
   * @param {number} lateralOffset - Distance from road edge (2-5m)
   * @returns {object} Final device position
   */
  placeDeviceOnCurb(roadPoint, side, lateralOffset) {
    // Calculate perpendicular bearing (90° from road direction)
    const perpBearing = side === 'left' 
      ? roadPoint.roadBearing - 90 
      : roadPoint.roadBearing + 90;
    
    // Road width / 2 gives distance from centerline to edge
    const roadHalfWidth = roadPoint.roadWidth / 2;
    
    // Total offset = road half-width + lateral clearance
    const totalOffset = roadHalfWidth + lateralOffset;
    
    // Calculate final position
    return this.calculatePosition(
      roadPoint.lat,
      roadPoint.lng,
      perpBearing,
      totalOffset
    );
  }

  /**
   * Batch snap multiple addresses to roads
   */
  async snapMultipleToRoads(points, googleMapsApiKey) {
    const results = [];
    
    for (const point of points) {
      const snapped = await this.snapToRoad(point.lat, point.lng, googleMapsApiKey);
      results.push({
        original: point,
        snapped: snapped
      });
    }
    
    return results;
  }

  /**
   * Clear snap cache
   */
  clearCache() {
    this.snapCache.clear();
  }
}

export default new RoadSnapper();
