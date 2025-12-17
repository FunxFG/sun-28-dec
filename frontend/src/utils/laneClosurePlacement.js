/**
 * AS 1742.3 Compliant Lane Closure Device Placement
 * 
 * Implements proper sign sequencing for lane closures:
 * RWA/40 → Lane Merge → Buffer → Taper → Workzone → End Roadworks
 * Plus side street signage
 */

class LaneClosurePlacement {
  constructor() {
    // AS 1742.3 spacing requirements based on speed limit
    this.spacingRules = {
      40: { rwa_distance: 60, merge_distance: 40, buffer: 30, taper: 30 },
      50: { rwa_distance: 70, merge_distance: 50, buffer: 40, taper: 40 },
      60: { rwa_distance: 80, merge_distance: 60, buffer: 50, taper: 50 },
      70: { rwa_distance: 90, merge_distance: 70, buffer: 60, taper: 60 },
      80: { rwa_distance: 100, merge_distance: 80, buffer: 70, taper: 70 }
    };
  }

  /**
   * Calculate lane closure device placement
   * @param {Object} workZoneData - Work zone details (start/end lat/lng, bearing)
   * @param {Number} speedLimit - Posted speed limit
   * @param {Array} sideStreets - Array of side streets with coordinates
   * @returns {Array} - Array of device objects with positions
   */
  placeLaneClosureDevices(workZoneData, speedLimit = 60, sideStreets = [], trafficDirection = 'northbound', roadEdgeGeometry = null) {
    const devices = [];
    const spacing = this.spacingRules[speedLimit] || this.spacingRules[60];
    
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    console.log('🚧 Placing Lane Closure devices WITH REAL ROAD EDGES');
    console.log('  Speed limit:', speedLimit, 'km/h');
    console.log('  Traffic direction:', trafficDirection);
    console.log('  Spacing rules:', spacing);
    console.log('  Start coords:', start_lat, start_lng);
    console.log('  End coords:', end_lat, end_lng);
    console.log('  Road bearing:', road_bearing);
    console.log('  Real road edges available:', !!roadEdgeGeometry);
    
    // Check if we have REAL road edge data
    const hasRealEdges = roadEdgeGeometry && 
                        roadEdgeGeometry.start && 
                        roadEdgeGeometry.start.left_edge && 
                        roadEdgeGeometry.start.left_edge.length > 0;
    
    console.log('  Using real road geometry:', hasRealEdges);
    
    // Validate inputs
    if (!start_lat || !start_lng || !end_lat || !end_lng) {
      console.error('❌ Invalid coordinates provided to lane closure placement');
      return devices;
    }
    
    // Calculate road bearing if not provided
    let bearing = road_bearing;
    if (!bearing || isNaN(bearing)) {
      bearing = this.calculateBearing(start_lat, start_lng, end_lat, end_lng);
      console.log('  Calculated bearing:', bearing);
    }
    
    // Map traffic direction to compass bearing adjustment
    // Signs must be placed BEFORE the workzone from traffic's approach direction
    const directionMap = {
      'northbound': 180,  // Traffic going north, signs south (reverse bearing)
      'southbound': 0,    // Traffic going south, signs north (same bearing)
      'eastbound': 270,   // Traffic going east, signs west
      'westbound': 90     // Traffic going west, signs east
    };
    
    const approachAdjustment = directionMap[trafficDirection] || 180;
    const approachBearing = (bearing + approachAdjustment) % 360;
    
    console.log(`  Traffic ${trafficDirection}: signs placed at bearing ${approachBearing}° (${approachAdjustment}° from road bearing)`);
    
    // 1. RWA/40 Sign (bilateral) - SNAP TO REAL ROAD EDGE
    const rwaDistance = spacing.rwa_distance;
    const rwaPosition = this.calculatePosition(start_lat, start_lng, approachBearing, rwaDistance);
    
    // Calculate initial positions
    let rwaLeft = this.offsetPosition(rwaPosition, bearing - 90, 3); // 3m left
    let rwaRight = this.offsetPosition(rwaPosition, bearing + 90, 3); // 3m right
    
    // SNAP TO REAL ROAD EDGES if available
    if (hasRealEdges) {
      console.log('  🎯 Snapping RWA signs to REAL road edges');
      rwaLeft = this.snapToRoadEdge(rwaLeft.lat, rwaLeft.lng, roadEdgeGeometry.start.left_edge, 'left');
      rwaRight = this.snapToRoadEdge(rwaRight.lat, rwaRight.lng, roadEdgeGeometry.start.right_edge, 'right');
    }
    
    console.log('  RWA center:', rwaPosition);
    console.log('  RWA left (snapped):', rwaLeft);
    console.log('  RWA right (snapped):', rwaRight);
    
    devices.push({
      id: `rwa_left_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Road Work Ahead / 40',
      position_lat: rwaLeft.lat,
      position_lng: rwaLeft.lng,
      properties: {
        side: 'left',
        distance_from_start: rwaDistance,
        sign_code: 'RWA/40',
        auto_placed: true
      }
    });
    
    devices.push({
      id: `rwa_right_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Road Work Ahead / 40',
      position_lat: rwaRight.lat,
      position_lng: rwaRight.lng,
      properties: {
        side: 'right',
        distance_from_start: rwaDistance,
        sign_code: 'RWA/40',
        auto_placed: true
      }
    });
    
    // 2. Lane Merge Right (T1-15) - bilateral - SNAP TO REAL ROAD EDGE
    const mergeDistance = rwaDistance - spacing.merge_distance;
    const mergePosition = this.calculatePosition(start_lat, start_lng, approachBearing, mergeDistance);
    
    let mergeLeft = this.offsetPosition(mergePosition, bearing - 90, 3);
    let mergeRight = this.offsetPosition(mergePosition, bearing + 90, 3);
    
    // SNAP TO REAL ROAD EDGES if available
    if (hasRealEdges) {
      console.log('  🎯 Snapping Merge signs to REAL road edges');
      mergeLeft = this.snapToRoadEdge(mergeLeft.lat, mergeLeft.lng, roadEdgeGeometry.start.left_edge, 'left');
      mergeRight = this.snapToRoadEdge(mergeRight.lat, mergeRight.lng, roadEdgeGeometry.start.right_edge, 'right');
    }
    
    devices.push({
      id: `merge_left_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Lane Merge Right (T1-15)',
      position_lat: mergeLeft.lat,
      position_lng: mergeLeft.lng,
      properties: {
        side: 'left',
        distance_from_start: mergeDistance,
        sign_code: 'T1-15',
        auto_placed: true
      }
    });
    
    devices.push({
      id: `merge_right_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Lane Merge Right (T1-15)',
      position_lat: mergeRight.lat,
      position_lng: mergeRight.lng,
      properties: {
        side: 'right',
        distance_from_start: mergeDistance,
        sign_code: 'T1-15',
        auto_placed: true
      }
    });
    
    // 3. Buffer zone (no signs, just space)
    const bufferStart = mergeDistance - spacing.buffer;
    
    // 4. Taper with cones - PROPER GRADUATED TAPER
    const taperStart = bufferStart - spacing.taper;
    const coneSpacing = 5; // 5m between cones in taper
    const numCones = Math.floor(spacing.taper / coneSpacing);
    
    console.log(`  Creating ${numCones} taper cones over ${spacing.taper}m`);
    
    // Taper formula: gradually angle from full lane width to edge
    // Start: 3.5m from centerline (full lane position)
    // End: 0.3m from edge (workzone boundary)
    const taperStartOffset = 3.5; // Full lane width
    const taperEndOffset = 0.3;   // Edge of workzone
    
    for (let i = 0; i <= numCones; i++) {
      const progress = i / numCones; // 0 to 1
      const coneDistance = taperStart - (i * coneSpacing);
      const conePosition = this.calculatePosition(start_lat, start_lng, approachBearing, coneDistance);
      
      // Graduated taper: smooth curve from lane to edge
      // Using quadratic easing for smooth transition
      const easedProgress = progress * progress; // Accelerating taper
      const lateralOffset = taperStartOffset - (easedProgress * (taperStartOffset - taperEndOffset));
      
      let conePos = this.offsetPosition(conePosition, bearing - 90, lateralOffset);
      
      // SNAP TAPER CONES TO REAL ROAD EDGE (critical - keeps taper on road, not property!)
      if (hasRealEdges) {
        conePos = this.snapToRoadEdge(conePos.lat, conePos.lng, roadEdgeGeometry.start.left_edge, 'taper');
      }
      
      devices.push({
        id: `cone_taper_${i}_${Date.now() + i}`,
        device_type: 'delineation',
        device_name: 'Traffic Cone 700mm',
        position_lat: conePos.lat,
        position_lng: conePos.lng,
        properties: {
          side: 'left',
          distance_from_start: coneDistance,
          lateral_offset: lateralOffset.toFixed(1) + 'm',
          taper_position: `${(progress * 100).toFixed(0)}%`,
          in_taper: true,
          auto_placed: true
        }
      });
    }
    
    // 5. Workzone edge marking (more cones along workzone)
    const workzoneLength = this.calculateDistance(start_lat, start_lng, end_lat, end_lng);
    const workzoneCones = Math.floor(workzoneLength / 10); // 10m spacing
    
    for (let i = 0; i <= workzoneCones; i++) {
      const ratio = i / workzoneCones;
      const coneLat = start_lat + (end_lat - start_lat) * ratio;
      const coneLng = start_lng + (end_lng - start_lng) * ratio;
      
      let workzoneConePos = this.offsetPosition({lat: coneLat, lng: coneLng}, bearing - 90, 0.5);
      
      // SNAP WORKZONE EDGE CONES TO REAL ROAD EDGE
      if (hasRealEdges) {
        workzoneConePos = this.snapToRoadEdge(workzoneConePos.lat, workzoneConePos.lng, roadEdgeGeometry.start.left_edge, 'workzone');
      }
      
      devices.push({
        id: `cone_workzone_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: 'Traffic Cone 700mm',
        position_lat: workzoneConePos.lat,
        position_lng: workzoneConePos.lng,
        properties: {
          side: 'left',
          in_workzone: true,
          auto_placed: true
        }
      });
    }
    
    // 6. End Roadworks sign (bilateral) - after workzone
    const endDistance = 10; // 10m after end (forward direction)
    const endPosition = this.calculatePosition(end_lat, end_lng, bearing, endDistance);
    
    let endLeft = this.offsetPosition(endPosition, bearing - 90, 3);
    let endRight = this.offsetPosition(endPosition, bearing + 90, 3);
    
    // SNAP END SIGNS TO REAL ROAD EDGES
    if (hasRealEdges) {
      console.log('  🎯 Snapping End Roadworks signs to REAL road edges');
      endLeft = this.snapToRoadEdge(endLeft.lat, endLeft.lng, roadEdgeGeometry.end?.left_edge || roadEdgeGeometry.start.left_edge, 'left');
      endRight = this.snapToRoadEdge(endRight.lat, endRight.lng, roadEdgeGeometry.end?.right_edge || roadEdgeGeometry.start.right_edge, 'right');
    }
    
    devices.push({
      id: `end_left_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'End Roadworks',
      position_lat: endLeft.lat,
      position_lng: endLeft.lng,
      properties: {
        side: 'left',
        sign_code: 'END_RW',
        auto_placed: true
      }
    });
    
    devices.push({
      id: `end_right_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'End Roadworks',
      position_lat: endRight.lat,
      position_lng: endRight.lng,
      properties: {
        side: 'right',
        sign_code: 'END_RW',
        auto_placed: true
      }
    });
    
    // 7. Side street signage
    if (sideStreets && sideStreets.length > 0) {
      console.log(`  Processing ${sideStreets.length} side streets`);
      sideStreets.forEach((street, idx) => {
        if (!street.lat || !street.lng) return;
        
        // RWA on approach to main road
        const streetApproach = this.calculatePosition(street.lat, street.lng, street.bearing || 0, 20);
        
        devices.push({
          id: `side_rwa_${idx}_${Date.now()}`,
          device_type: 'warning',
          device_name: 'Road Work Ahead',
          position_lat: streetApproach.lat,
          position_lng: streetApproach.lng,
          properties: {
            side_street: true,
            street_name: street.name,
            sign_code: 'RWA',
            auto_placed: true
          }
        });
        
        // END ROADWORKS on back of same sign (same location, facing away)
        devices.push({
          id: `side_end_${idx}_${Date.now()}`,
          device_type: 'regulatory',
          device_name: 'End Roadworks (back of RWA)',
          position_lat: streetApproach.lat,
          position_lng: streetApproach.lng,
          properties: {
            side_street: true,
            street_name: street.name,
            back_of_sign: true,
            sign_code: 'END_RW',
            auto_placed: true
          }
        });
        
        // "Left Lane Closed" at intersection
        devices.push({
          id: `side_lane_closed_${idx}_${Date.now()}`,
          device_type: 'regulatory',
          device_name: 'Left Lane Closed',
          position_lat: street.lat,
          position_lng: street.lng,
          properties: {
            side_street: true,
            street_name: street.name,
            at_intersection: true,
            sign_code: 'LANE_CLOSED',
            auto_placed: true
          }
        });
      });
    }
    
    console.log(`✅ Placed ${devices.length} devices for lane closure`);
    return devices;
  }

  calculatePosition(lat, lng, bearing, distanceMeters) {
    const R = 6371000; // Earth radius in meters
    const bearingRad = bearing * Math.PI / 180;
    const latRad = lat * Math.PI / 180;
    
    const newLatRad = Math.asin(
      Math.sin(latRad) * Math.cos(distanceMeters / R) +
      Math.cos(latRad) * Math.sin(distanceMeters / R) * Math.cos(bearingRad)
    );
    
    const newLngRad = (lng * Math.PI / 180) + Math.atan2(
      Math.sin(bearingRad) * Math.sin(distanceMeters / R) * Math.cos(latRad),
      Math.cos(distanceMeters / R) - Math.sin(latRad) * Math.sin(newLatRad)
    );
    
    return {
      lat: newLatRad * 180 / Math.PI,
      lng: newLngRad * 180 / Math.PI
    };
  }

  offsetPosition(position, bearing, offsetMeters) {
    // Calculate lateral offset from a position (perpendicular to road)
    const result = this.calculatePosition(position.lat, position.lng, bearing, offsetMeters);
    return {
      lat: result.lat,
      lng: result.lng
    };
  }

  snapToRoadEdge(targetLat, targetLng, roadEdgePoints, side = 'left') {
    /**
     * Snap a device position to the nearest point on the ACTUAL road edge
     * Returns the coordinates of the closest road edge point
     * 
     * Road edge points can be either:
     * - Array format: [[lat, lng], [lat, lng], ...]
     * - Object format: [{lat, lng}, {lat, lng}, ...]
     */
    if (!roadEdgePoints || roadEdgePoints.length === 0) {
      console.log(`    ⚠️ No road edge points for ${side}, using original position`);
      return { lat: targetLat, lng: targetLng };
    }
    
    let minDistance = Infinity;
    let closestPoint = { lat: targetLat, lng: targetLng };
    
    // Find the closest point on the road edge
    for (const edgePoint of roadEdgePoints) {
      // Handle both array format [lat, lng] and object format {lat, lng}
      let pointLat, pointLng;
      
      if (Array.isArray(edgePoint)) {
        // Array format: [lat, lng]
        pointLat = edgePoint[0];
        pointLng = edgePoint[1];
      } else if (edgePoint && typeof edgePoint === 'object') {
        // Object format: {lat, lng}
        pointLat = edgePoint.lat;
        pointLng = edgePoint.lng;
      } else {
        console.warn('    Invalid edge point format:', edgePoint);
        continue;
      }
      
      // Validate coordinates
      if (typeof pointLat !== 'number' || typeof pointLng !== 'number' || 
          isNaN(pointLat) || isNaN(pointLng)) {
        console.warn('    Invalid coordinates:', pointLat, pointLng);
        continue;
      }
      
      const distance = this.calculateDistance(
        targetLat, targetLng,
        pointLat, pointLng
      );
      
      if (distance < minDistance) {
        minDistance = distance;
        closestPoint = { lat: pointLat, lng: pointLng };
      }
    }
    
    console.log(`    ✅ Snapped ${side} to road edge: distance ${minDistance.toFixed(1)}m`);
    console.log(`       Original: (${targetLat.toFixed(6)}, ${targetLng.toFixed(6)})`);
    console.log(`       Snapped:  (${closestPoint.lat.toFixed(6)}, ${closestPoint.lng.toFixed(6)})`);
    return closestPoint;
  }

  calculateBearing(lat1, lng1, lat2, lng2) {
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const lat1Rad = lat1 * Math.PI / 180;
    const lat2Rad = lat2 * Math.PI / 180;
    
    const y = Math.sin(dLng) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) -
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLng);
    
    let bearing = Math.atan2(y, x) * 180 / Math.PI;
    bearing = (bearing + 360) % 360; // Normalize to 0-360
    
    return bearing;
  }

  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    
    return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * R;
  }
}

export default new LaneClosurePlacement();
