/**
 * Special Device Placement Rules
 * Handles exceptions to standard bilateral placement:
 * 1. Road closure signs - center of road, singular
 * 2. Stop Here on Red signs - road edge, 20m from signals
 */

export class SpecialPlacementRules {
  constructor() {
    this.specialDevices = {
      road_closure: {
        placement_type: 'center_road_singular',
        bilateral: false,
        devices: ['Road Closed', 'No Entry', 'No Through Road'],
        codes: ['T1-2', 'R2-1', 'G2-3']
      },
      detour_assembly: {
        placement_type: 'center_or_paired',
        bilateral: false, // Can be singular or paired with detour signs
        devices: ['Road Closed', 'Detour', 'Local Traffic Only'],
        codes: ['T1-2', 'G2-1', 'R5-1']
      },
      traffic_light_stop: {
        placement_type: 'road_edge_singular',
        bilateral: false,
        device: 'Stop Here on Red',
        code: 'R1-5',
        distance_from_signal: 20, // meters
        position: 'safest_stopping_point'
      }
    };
  }

  /**
   * Place road closure sign assembly at center of road
   * Multi-sign assembly: Road Closed + No Entry + No Through Road
   */
  placeRoadClosureAssembly(closurePoint, roadGeometry) {
    const devices = [];
    const closureLat = closurePoint.lat;
    const closureLng = closurePoint.lng;
    const bearing = roadGeometry.bearing || 0;
    
    // SINGULAR CENTER PLACEMENT - not bilateral
    // Stack signs vertically at closure point
    
    // 1. Road Closed (top sign)
    devices.push({
      id: `road_closed_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Road Closed',
      device_code: 'T1-2',
      position_lat: closureLat,
      position_lng: closureLng,
      properties: {
        placement_type: 'center_road_singular',
        position_in_assembly: 'top',
        mounting_height: 2.8, // Higher for visibility
        bilateral: false,
        special_placement: 'road_closure',
        as1742_reference: 'AS 1742.3 Section 6.3',
        auto_placed: true
      }
    });
    
    // 2. No Entry (middle sign - slightly offset vertically)
    devices.push({
      id: `no_entry_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'No Entry',
      device_code: 'R2-1',
      position_lat: closureLat,
      position_lng: closureLng,
      properties: {
        placement_type: 'center_road_singular',
        position_in_assembly: 'middle',
        mounting_height: 2.1, // Standard height
        bilateral: false,
        special_placement: 'road_closure',
        as1742_reference: 'AS 1742.2 Section 4.5',
        auto_placed: true
      }
    });
    
    // 3. No Through Road (bottom sign)
    devices.push({
      id: `no_through_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'No Through Road',
      device_code: 'G2-3',
      position_lat: closureLat,
      position_lng: closureLng,
      properties: {
        placement_type: 'center_road_singular',
        position_in_assembly: 'bottom',
        mounting_height: 1.5, // Lower for readability
        bilateral: false,
        special_placement: 'road_closure',
        as1742_reference: 'AS 1742.3 Section 6.3',
        auto_placed: true
      }
    });
    
    // Add barrier protection around closure point
    devices.push(...this.addClosureBarriers(closurePoint, bearing));
    
    return devices;
  }

  /**
   * Place road closure with detour signage
   * Can be singular or paired depending on detour direction
   */
  placeRoadClosureWithDetour(closurePoint, detourDirection, roadGeometry) {
    const devices = [];
    
    // Road Closed sign (center)
    devices.push(...this.placeRoadClosureAssembly(closurePoint, roadGeometry));
    
    // Detour sign(s) - positioned to indicate direction
    if (detourDirection === 'both') {
      // Paired detour signs (left and right)
      const leftDetour = this.calculatePosition(
        closurePoint.lat, closurePoint.lng, 
        roadGeometry.bearing - 90, 3.0
      );
      const rightDetour = this.calculatePosition(
        closurePoint.lat, closurePoint.lng,
        roadGeometry.bearing + 90, 3.0
      );
      
      devices.push({
        id: `detour_left_${Date.now()}`,
        device_type: 'guidance',
        device_name: 'Detour Left',
        device_code: 'G2-1',
        position_lat: leftDetour.lat,
        position_lng: leftDetour.lng,
        properties: {
          placement_type: 'paired_with_closure',
          direction: 'left',
          bilateral: false,
          special_placement: 'road_closure_detour',
          auto_placed: true
        }
      });
      
      devices.push({
        id: `detour_right_${Date.now()}`,
        device_type: 'guidance',
        device_name: 'Detour Right',
        device_code: 'G2-1',
        position_lat: rightDetour.lat,
        position_lng: rightDetour.lng,
        properties: {
          placement_type: 'paired_with_closure',
          direction: 'right',
          bilateral: false,
          special_placement: 'road_closure_detour',
          auto_placed: true
        }
      });
    } else {
      // Singular detour sign
      const detourOffset = detourDirection === 'left' ? -90 : 90;
      const detourPos = this.calculatePosition(
        closurePoint.lat, closurePoint.lng,
        roadGeometry.bearing + detourOffset, 3.0
      );
      
      devices.push({
        id: `detour_${detourDirection}_${Date.now()}`,
        device_type: 'guidance',
        device_name: `Detour ${detourDirection}`,
        device_code: 'G2-1',
        position_lat: detourPos.lat,
        position_lng: detourPos.lng,
        properties: {
          placement_type: 'singular_with_closure',
          direction: detourDirection,
          bilateral: false,
          special_placement: 'road_closure_detour',
          auto_placed: true
        }
      });
    }
    
    return devices;
  }

  /**
   * Place "Stop Here on Red" sign for temporary traffic lights
   * Positioned ON road edge, ~20m from signal, at safest stopping point
   */
  placeStopHereOnRedSign(signalPosition, approachBearing, roadGeometry) {
    const devices = [];
    
    // Calculate position 20m BEFORE the traffic signal
    // This is where vehicles should stop and wait
    const stopPosition = this.calculatePosition(
      signalPosition.lat,
      signalPosition.lng,
      approachBearing + 180, // Opposite direction (before signal)
      20 // 20 meters
    );
    
    // Adjust for safest stopping point
    // Check if 20m is appropriate or needs adjustment
    const safeStopPosition = this.calculateSafestStoppingPoint(
      stopPosition,
      signalPosition,
      roadGeometry
    );
    
    devices.push({
      id: `stop_here_red_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'Stop Here on Red',
      device_code: 'R1-5',
      position_lat: safeStopPosition.lat,
      position_lng: safeStopPosition.lng,
      properties: {
        placement_type: 'road_edge_singular',
        position: 'road_edge', // RIGHT ON THE ROAD EDGE
        lateral_offset: 0.3, // Minimal offset - on road edge
        distance_from_signal: safeStopPosition.actual_distance,
        nominal_distance: 20,
        bilateral: false,
        special_placement: 'traffic_signal_stop',
        signal_id: `signal_${Date.now()}`,
        shuttle_flow: true, // For alternating traffic
        mounting_height: 1.5, // Lower for driver visibility
        as1742_reference: 'AS 1742.3 Section 8.4',
        auto_placed: true,
        purpose: 'Temporary traffic light stop line'
      }
    });
    
    // Add road marking indicator (stop line position)
    devices.push({
      id: `stop_line_marker_${Date.now()}`,
      device_type: 'marking',
      device_name: 'Stop Line Position',
      position_lat: safeStopPosition.lat,
      position_lng: safeStopPosition.lng,
      properties: {
        type: 'stop_line_indicator',
        purpose: 'Vehicle stopping position for red signal',
        auto_placed: true
      }
    });
    
    return devices;
  }

  /**
   * Calculate safest stopping point for vehicles
   * Adjusts 20m nominal distance based on road conditions
   */
  calculateSafestStoppingPoint(nominalPosition, signalPosition, roadGeometry) {
    let adjustedDistance = 20; // Start with nominal 20m
    
    // Adjust for speed - higher speed needs more distance
    const speedLimit = roadGeometry.speed_limit || 60;
    if (speedLimit >= 80) {
      adjustedDistance = 25; // Extra distance for high speed
    } else if (speedLimit <= 40) {
      adjustedDistance = 15; // Can be closer for low speed
    }
    
    // Adjust for sight distance and road conditions
    // In practice, this would check for:
    // - Clear line of sight to signal
    // - No obstruction (curves, vegetation)
    // - Adequate queue storage
    
    return {
      lat: nominalPosition.lat,
      lng: nominalPosition.lng,
      actual_distance: adjustedDistance,
      adjustment_reason: speedLimit >= 80 ? 'high_speed' : 
                        speedLimit <= 40 ? 'low_speed' : 'standard'
    };
  }

  /**
   * Add barrier protection around road closure point
   */
  addClosureBarriers(closurePoint, bearing) {
    const barriers = [];
    const barrierSpacing = 2.0; // 2m apart
    
    // Create barrier line across road
    for (let i = -3; i <= 3; i++) {
      const offset = i * barrierSpacing;
      const barrierPos = this.calculatePosition(
        closurePoint.lat,
        closurePoint.lng,
        bearing + 90, // Perpendicular to road
        offset
      );
      
      barriers.push({
        id: `closure_barrier_${i}_${Date.now()}`,
        device_type: 'barrier',
        device_name: 'Water-Filled Barrier',
        device_code: 'B1-1',
        position_lat: barrierPos.lat,
        position_lng: barrierPos.lng,
        properties: {
          purpose: 'Road closure protection',
          sequence_number: i + 3,
          auto_placed: true
        }
      });
    }
    
    return barriers;
  }

  /**
   * Check if device requires special placement rules
   */
  isSpecialPlacementDevice(deviceName, deviceCode) {
    const specialNames = [
      'Road Closed',
      'No Entry', 
      'No Through Road',
      'Stop Here on Red',
      'Detour'
    ];
    
    const specialCodes = [
      'T1-2', // Road Closed
      'R2-1', // No Entry
      'G2-3', // No Through Road
      'R1-5', // Stop Here on Red
      'G2-1'  // Detour
    ];
    
    return specialNames.includes(deviceName) || specialCodes.includes(deviceCode);
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
}

export default new SpecialPlacementRules();
