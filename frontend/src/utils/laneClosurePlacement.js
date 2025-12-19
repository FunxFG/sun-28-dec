/**
 * AS 1742.3 Compliant Lane Closure Device Placement
 * Based on ADVANCED Traffic Management Generic TGS Package 2026
 * 
 * This module implements proper TGS-compliant device placement with:
 * - Correct sign sequences at proper distances
 * - Proper taper formations with correct cone spacing
 * - Devices placed ON the road edge (not scattered)
 * - Buffer zones and safety areas
 */

class LaneClosurePlacement {
  
  // ==================== TGS SIGN SEQUENCES ====================
  
  // Sign sequence for approach side (low speed 40-70 km/h)
  getApproachSignsLowSpeed() {
    return [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 195, side: 'left' },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 145, side: 'left' },
      { code: 'T1-25', name: 'Lane Status / Merge Left', distance: 100, side: 'left' },
      { code: 'R4-1', name: 'Speed Limit 40', distance: 60, side: 'left' },
      { code: 'Arrow', name: 'Arrow Board Left', distance: 45, side: 'left' },
    ];
  }
  
  // Sign sequence for approach side (high speed 80-110 km/h)
  getApproachSignsHighSpeed() {
    return [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 400, side: 'left' },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 320, side: 'left' },
      { code: 'T1-2', name: 'Prepare to Stop', distance: 240, side: 'left' },
      { code: 'T1-25', name: 'Lane Status / Merge Left', distance: 160, side: 'left' },
      { code: 'R4-1', name: 'Speed Limit 60', distance: 100, side: 'left' },
      { code: 'Arrow', name: 'Arrow Board Left', distance: 60, side: 'left' },
    ];
  }
  
  // Sign sequence for departure side (after work zone)
  getDepartureSignsLowSpeed() {
    return [
      { code: 'T1-11', name: 'End Road Work', distance: -50, side: 'left' },
    ];
  }
  
  getDepartureSignsHighSpeed() {
    return [
      { code: 'T1-11', name: 'End Road Work', distance: -80, side: 'left' },
    ];
  }

  // ==================== TAPER CONFIGURATIONS ====================
  
  getTaperConfig(speedLimit) {
    if (speedLimit <= 50) {
      return { length: 15, coneSpacing: 3, numCones: 6 };
    } else if (speedLimit <= 70) {
      return { length: 30, coneSpacing: 5, numCones: 7 };
    } else if (speedLimit <= 90) {
      return { length: 90, coneSpacing: 10, numCones: 10 };
    } else {
      return { length: 145, coneSpacing: 15, numCones: 10 };
    }
  }
  
  // Buffer zone sizes
  getBufferZone(speedLimit) {
    return speedLimit <= 70 ? 20 : 30; // meters
  }

  // ==================== MAIN PLACEMENT FUNCTION ====================
  
  placeLaneClosureDevices(workZoneData, speedLimit, sideStreets = [], trafficDirection = 'West', roadEdgeGeometry = null) {
    console.log('🚧 ====== TGS-COMPLIANT DEVICE PLACEMENT ======');
    console.log('  Speed limit:', speedLimit, 'km/h');
    console.log('  Traffic direction:', trafficDirection);
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    // Validate coordinates
    if (!start_lat || !start_lng || isNaN(start_lat) || isNaN(start_lng)) {
      console.error('❌ Invalid start coordinates');
      return [];
    }
    
    // Calculate road bearing if not provided
    let bearing = road_bearing;
    if (!bearing || isNaN(bearing)) {
      bearing = this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
      if (isNaN(bearing)) bearing = 90; // Default to east-west
    }
    console.log('  Road bearing:', bearing.toFixed(1), '°');
    
    // Determine approach bearing based on traffic direction
    const approachBearing = this.getApproachBearing(bearing, trafficDirection);
    console.log('  Approach bearing:', approachBearing.toFixed(1), '°');
    
    // Get road edge for device placement (devices go on LEFT edge of travel lane)
    const roadEdge = this.getRoadEdgePoints(roadEdgeGeometry, start_lat, start_lng, bearing);
    console.log('  Road edge available:', roadEdge.length > 0 ? 'Yes' : 'No (using calculated)');
    
    // ==================== 1. APPROACH SIGNS ====================
    console.log('📍 Placing approach signs...');
    const approachSigns = speedLimit <= 70 ? this.getApproachSignsLowSpeed() : this.getApproachSignsHighSpeed();
    
    approachSigns.forEach((sign, idx) => {
      // Calculate position BEFORE the work zone (positive distance = upstream)
      const signPos = this.calculatePosition(start_lat, start_lng, approachBearing + 180, sign.distance);
      
      // Offset to road edge (left side for approach traffic)
      const edgeOffset = 1.0; // 1m from road edge
      const finalPos = this.offsetToRoadEdge(signPos.lat, signPos.lng, bearing, edgeOffset, roadEdge);
      
      devices.push({
        id: `approach_sign_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: finalPos.lat,
        position_lng: finalPos.lng,
        properties: {
          side: 'left',
          distance_from_workzone: sign.distance,
          placement: 'approach',
          sequence: idx + 1,
          auto_placed: true
        }
      });
      console.log(`    ${sign.code} - ${sign.name} at ${sign.distance}m`);
    });
    
    // ==================== 2. TAPER CONES ====================
    console.log('📍 Placing taper cones...');
    const taperConfig = this.getTaperConfig(speedLimit);
    const taperStartDistance = 30; // Taper starts 30m before work zone
    
    // Lane width (standard 3.5m)
    const laneWidth = 3.5;
    
    for (let i = 0; i <= taperConfig.numCones; i++) {
      const progress = i / taperConfig.numCones; // 0 to 1
      const distanceAlongTaper = i * taperConfig.coneSpacing;
      
      // Position along the road (from taper start toward work zone)
      const conePos = this.calculatePosition(
        start_lat, start_lng, 
        approachBearing + 180, 
        taperStartDistance - distanceAlongTaper
      );
      
      // LINEAR TAPER: Lateral offset decreases from lane edge (3.5m) to road edge (0.3m)
      const lateralOffset = laneWidth - (progress * (laneWidth - 0.3));
      
      // Apply lateral offset perpendicular to road
      const finalPos = this.offsetPerpendicular(conePos.lat, conePos.lng, bearing, lateralOffset);
      
      devices.push({
        id: `taper_cone_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: 'Traffic Cone 700mm',
        device_code: 'TC1',
        position_lat: finalPos.lat,
        position_lng: finalPos.lng,
        properties: {
          side: 'left',
          distance_along_taper: distanceAlongTaper,
          lateral_offset: lateralOffset.toFixed(2),
          taper_position: `${(progress * 100).toFixed(0)}%`,
          in_taper: true,
          auto_placed: true
        }
      });
    }
    console.log(`    Placed ${taperConfig.numCones + 1} taper cones over ${taperConfig.length}m`);
    
    // ==================== 3. WORK ZONE DELINEATION ====================
    console.log('📍 Placing work zone delineation...');
    const workzoneLength = this.calculateDistance(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng) || 50;
    const delineationSpacing = 10; // 10m spacing along work zone
    const numDelineators = Math.max(3, Math.floor(workzoneLength / delineationSpacing));
    
    for (let i = 0; i <= numDelineators; i++) {
      const distanceAlong = i * delineationSpacing;
      
      // Position along work zone
      const delinPos = this.calculatePosition(start_lat, start_lng, bearing, distanceAlong);
      
      // Place on road edge (0.3m offset)
      const finalPos = this.offsetPerpendicular(delinPos.lat, delinPos.lng, bearing, 0.3);
      
      devices.push({
        id: `workzone_delin_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: i === 0 || i === numDelineators ? 'Bollard' : 'Traffic Cone 700mm',
        device_code: i === 0 || i === numDelineators ? 'Bollard' : 'TC1',
        position_lat: finalPos.lat,
        position_lng: finalPos.lng,
        properties: {
          side: 'left',
          distance_from_start: distanceAlong,
          in_workzone: true,
          auto_placed: true
        }
      });
    }
    console.log(`    Placed ${numDelineators + 1} work zone delineators over ${workzoneLength}m`);
    
    // ==================== 4. DEPARTURE SIGNS ====================
    console.log('📍 Placing departure signs...');
    const departureSigns = speedLimit <= 70 ? this.getDepartureSignsLowSpeed() : this.getDepartureSignsHighSpeed();
    
    departureSigns.forEach((sign, idx) => {
      // Calculate position AFTER the work zone (negative distance = downstream)
      const endLat = end_lat || start_lat;
      const endLng = end_lng || start_lng;
      const signPos = this.calculatePosition(endLat, endLng, bearing, Math.abs(sign.distance));
      
      // Offset to road edge
      const finalPos = this.offsetPerpendicular(signPos.lat, signPos.lng, bearing, 1.0);
      
      devices.push({
        id: `departure_sign_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: finalPos.lat,
        position_lng: finalPos.lng,
        properties: {
          side: 'left',
          distance_from_workzone_end: Math.abs(sign.distance),
          placement: 'departure',
          auto_placed: true
        }
      });
      console.log(`    ${sign.code} - ${sign.name} at +${Math.abs(sign.distance)}m after work zone`);
    });
    
    // ==================== 5. SIDE STREET SIGNS (if any) ====================
    if (sideStreets && sideStreets.length > 0) {
      console.log('📍 Placing side street warning signs...');
      sideStreets.forEach((street, idx) => {
        if (street.lat && street.lng) {
          // Place "Road Work Ahead" on side street approach
          const sideSignPos = this.calculatePosition(street.lat, street.lng, street.bearing || 0, 50);
          
          devices.push({
            id: `side_street_sign_${idx}_${Date.now()}`,
            device_type: 'warning',
            device_name: 'Road Work Ahead',
            device_code: 'T1-1',
            position_lat: sideSignPos.lat,
            position_lng: sideSignPos.lng,
            properties: {
              side_street: street.name || `Side Street ${idx + 1}`,
              distance_from_intersection: 50,
              auto_placed: true
            }
          });
        }
      });
    }
    
    console.log(`✅ TGS Placement Complete: ${devices.length} devices placed`);
    console.log('   - Approach signs:', approachSigns.length);
    console.log('   - Taper cones:', taperConfig.numCones + 1);
    console.log('   - Work zone delineation:', numDelineators + 1);
    console.log('   - Departure signs:', departureSigns.length);
    
    return devices;
  }

  // ==================== HELPER FUNCTIONS ====================
  
  getApproachBearing(roadBearing, trafficDirection) {
    // Traffic direction determines which way vehicles approach
    const directionMap = {
      'North': 0,
      'South': 180,
      'East': 90,
      'West': 270,
      'northbound': 0,
      'southbound': 180,
      'eastbound': 90,
      'westbound': 270,
    };
    
    if (directionMap[trafficDirection] !== undefined) {
      return directionMap[trafficDirection];
    }
    
    // Default to road bearing
    return roadBearing;
  }
  
  calculatePosition(lat, lng, bearing, distanceMeters) {
    // Calculate new position given bearing and distance
    const R = 6371000; // Earth radius in meters
    const d = distanceMeters / R;
    const brng = bearing * Math.PI / 180;
    const lat1 = lat * Math.PI / 180;
    const lng1 = lng * Math.PI / 180;
    
    const lat2 = Math.asin(
      Math.sin(lat1) * Math.cos(d) +
      Math.cos(lat1) * Math.sin(d) * Math.cos(brng)
    );
    
    const lng2 = lng1 + Math.atan2(
      Math.sin(brng) * Math.sin(d) * Math.cos(lat1),
      Math.cos(d) - Math.sin(lat1) * Math.sin(lat2)
    );
    
    return {
      lat: lat2 * 180 / Math.PI,
      lng: lng2 * 180 / Math.PI
    };
  }
  
  offsetPerpendicular(lat, lng, bearing, offsetMeters) {
    // Offset position perpendicular to bearing (positive = left side)
    const perpBearing = bearing - 90;
    return this.calculatePosition(lat, lng, perpBearing, offsetMeters);
  }
  
  offsetToRoadEdge(lat, lng, bearing, edgeOffset, roadEdgePoints) {
    // If we have road edge data, snap to nearest edge point
    if (roadEdgePoints && roadEdgePoints.length > 0) {
      return this.snapToNearestEdge(lat, lng, roadEdgePoints);
    }
    // Otherwise use calculated offset
    return this.offsetPerpendicular(lat, lng, bearing, edgeOffset);
  }
  
  snapToNearestEdge(lat, lng, edgePoints) {
    if (!edgePoints || edgePoints.length === 0) {
      return { lat, lng };
    }
    
    let minDist = Infinity;
    let nearestPoint = { lat, lng };
    
    for (const point of edgePoints) {
      const pointLat = Array.isArray(point) ? point[0] : point.lat;
      const pointLng = Array.isArray(point) ? point[1] : point.lng;
      
      if (typeof pointLat !== 'number' || typeof pointLng !== 'number') continue;
      
      const dist = this.calculateDistance(lat, lng, pointLat, pointLng);
      if (dist < minDist) {
        minDist = dist;
        nearestPoint = { lat: pointLat, lng: pointLng };
      }
    }
    
    return nearestPoint;
  }
  
  getRoadEdgePoints(roadEdgeGeometry, lat, lng, bearing) {
    if (roadEdgeGeometry?.start?.left_edge) {
      return roadEdgeGeometry.start.left_edge;
    }
    return [];
  }
  
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
  
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000; // Earth radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
}

export default new LaneClosurePlacement();
