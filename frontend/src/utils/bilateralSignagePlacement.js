/**
 * Enhanced Bilateral Signage Placement System
 * Implements Austroads requirements for proper sign positioning
 */

export class BilateralSignagePlacement {
  constructor() {
    // Austroads clearance requirements
    this.clearanceRequirements = {
      'verge_placement': {
        'lateral_clearance': 2.0,  // 2m from edge of carriageway
        'min_verge_width': 3.0,    // Minimum verge width required
        'height_clearance': 2.1    // Height above ground
      },
      'shoulder_placement': {
        'lateral_clearance': 0.5,  // 0.5m from edge of travel lane
        'min_shoulder_width': 2.5, // Minimum shoulder width required
        'height_clearance': 2.1
      },
      'sign_spacing': {
        'minimum_spacing': 60,     // 60m minimum between signs
        'bilateral_offset': 1.0    // Offset between left/right bilateral signs
      }
    };

    // Device placement requirements by type
    this.devicePlacementRules = {
      'advance_warning': {
        'bilateral_required': true,
        'preferred_location': 'verge',
        'fallback_location': 'shoulder'
      },
      'regulatory_signs': {
        'bilateral_required': true,
        'preferred_location': 'verge',
        'fallback_location': 'shoulder'
      },
      'delineation_devices': {
        'bilateral_required': false,
        'preferred_location': 'shoulder',
        'fallback_location': 'verge'
      },
      'barriers': {
        'bilateral_required': false,
        'preferred_location': 'shoulder',
        'fallback_location': null
      }
    };
  }

  /**
   * Calculate bilateral device placement with proper positioning
   */
  calculateBilateralPlacement(workZoneData, roadGeometry) {
    const devices = [];
    const { startLat, startLng, endLat, endLng, bearing } = workZoneData;
    
    // Analyze road geometry and constraints
    const roadAnalysis = this.analyzeRoadGeometry(roadGeometry);
    
    // Place advance warning signs (bilateral)
    devices.push(...this.placeAdvanceWarningSigns(
      startLat, startLng, bearing, roadAnalysis
    ));
    
    // Place regulatory signs (bilateral)
    devices.push(...this.placeRegulatorySigns(
      startLat, startLng, bearing, roadAnalysis, workZoneData
    ));
    
    // Place delineation devices
    devices.push(...this.placeDelineationDevices(
      startLat, startLng, endLat, endLng, bearing, roadAnalysis, workZoneData
    ));
    
    // Place end-of-work signs (bilateral)
    devices.push(...this.placeEndOfWorkSigns(
      endLat, endLng, bearing, roadAnalysis
    ));
    
    return devices;
  }

  analyzeRoadGeometry(roadGeometry) {
    return {
      carriageway_width: roadGeometry.carriageway_width || 7.0,
      left_shoulder_width: roadGeometry.left_shoulder_width || 1.5,
      right_shoulder_width: roadGeometry.right_shoulder_width || 1.5,
      left_verge_width: roadGeometry.left_verge_width || 2.0,
      right_verge_width: roadGeometry.right_verge_width || 2.0,
      median_present: roadGeometry.median_present || false,
      median_width: roadGeometry.median_width || 0,
      constraints: roadGeometry.constraints || []
    };
  }

  placeAdvanceWarningSigns(startLat, startLng, bearing, roadAnalysis) {
    const devices = [];
    const distances = [500, 200, 100]; // Advance warning distances
    
    distances.forEach((distance, index) => {
      const signPosition = this.calculatePosition(startLat, startLng, bearing + 180, distance);
      
      // Determine optimal placement locations
      const placementOptions = this.determinePlacementOptions(roadAnalysis, 'advance_warning');
      
      // Place bilateral signs
      if (placementOptions.left_side.feasible) {
        const leftPosition = this.calculateOffset(
          signPosition.lat, signPosition.lng, bearing - 90, 
          placementOptions.left_side.offset
        );
        
        devices.push({
          id: `warning_left_${distance}_${Date.now()}`,
          device_type: 'warning',
          device_name: 'Road Work Ahead',
          position_lat: leftPosition.lat,
          position_lng: leftPosition.lng,
          properties: {
            distance: `${distance}m`,
            side: 'left',
            placement_type: placementOptions.left_side.type,
            bilateral_pair: true,
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.2.1 - Bilateral Placement',
            clearance_met: true
          }
        });
      }
      
      if (placementOptions.right_side.feasible) {
        const rightPosition = this.calculateOffset(
          signPosition.lat, signPosition.lng, bearing + 90, 
          placementOptions.right_side.offset
        );
        
        devices.push({
          id: `warning_right_${distance}_${Date.now()}`,
          device_type: 'warning',
          device_name: 'Road Work Ahead',
          position_lat: rightPosition.lat,
          position_lng: rightPosition.lng,
          properties: {
            distance: `${distance}m`,
            side: 'right',
            placement_type: placementOptions.right_side.type,
            bilateral_pair: true,
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.2.1 - Bilateral Placement',
            clearance_met: true
          }
        });
      }
      
      // Warning if bilateral placement not possible
      if (!placementOptions.left_side.feasible || !placementOptions.right_side.feasible) {
        console.warn(`Bilateral placement constraints at ${distance}m warning position`);
      }
    });
    
    return devices;
  }

  placeRegulatorySign
    const devices = [];
    
    // Speed limit signs (bilateral if speed reduction required)
    if (workZoneData.control_measures?.speed_reduction) {
      const speedSignPosition = this.calculatePosition(startLat, startLng, bearing + 180, 75);
      const placementOptions = this.determinePlacementOptions(roadAnalysis, 'regulatory_signs');
      
      // Left side speed sign
      if (placementOptions.left_side.feasible) {
        const leftPosition = this.calculateOffset(
          speedSignPosition.lat, speedSignPosition.lng, bearing - 90,
          placementOptions.left_side.offset
        );
        
        devices.push({
          id: `speed_left_${Date.now()}`,
          device_type: 'regulatory',
          device_name: 'Temporary Speed Limit 40',
          position_lat: leftPosition.lat,
          position_lng: leftPosition.lng,
          properties: {
            side: 'left',
            placement_type: placementOptions.left_side.type,
            bilateral_pair: true,
            speed_limit: 40,
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.3.1 - Bilateral Speed Signs'
          }
        });
      }
      
      // Right side speed sign
      if (placementOptions.right_side.feasible) {
        const rightPosition = this.calculateOffset(
          speedSignPosition.lat, speedSignPosition.lng, bearing + 90,
          placementOptions.right_side.offset
        );
        
        devices.push({
          id: `speed_right_${Date.now()}`,
          device_type: 'regulatory',
          device_name: 'Temporary Speed Limit 40',
          position_lat: rightPosition.lat,
          position_lng: rightPosition.lng,
          properties: {
            side: 'right',
            placement_type: placementOptions.right_side.type,
            bilateral_pair: true,
            speed_limit: 40,
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.3.1 - Bilateral Speed Signs'
          }
        });
      }
    }
    
    return devices;
  }

  placeDelineationDevices(startLat, startLng, endLat, endLng, bearing, roadAnalysis, workZoneData) {
    const devices = [];
    const workZoneLength = this.calculateDistance(startLat, startLng, endLat, endLng);
    const coneSpacing = this.getConeSpacing(workZoneData.road_data?.speed_limit || 60);
    
    const numPositions = Math.floor(workZoneLength / coneSpacing);
    
    for (let i = 0; i <= numPositions; i++) {
      const progress = i / numPositions;
      const conePosition = this.calculatePositionAlongPath(
        startLat, startLng, endLat, endLng, progress
      );
      
      // Determine which side needs delineation based on work zone occupancy
      const delineationSides = this.determineDelineationSides(workZoneData.road_occupancy);
      
      delineationSides.forEach(side => {
        const offset = side === 'left' ? -3.0 : 3.0; // 3m offset from centerline
        const devicePosition = this.calculateOffset(
          conePosition.lat, conePosition.lng, bearing + 90, offset
        );
        
        devices.push({
          id: `cone_${side}_${i}_${Date.now()}`,
          device_type: 'cone',
          device_name: 'Traffic Cone 700mm',
          position_lat: devicePosition.lat,
          position_lng: devicePosition.lng,
          properties: {
            side: side,
            spacing: `${coneSpacing}m`,
            sequence: i,
            placement_type: 'shoulder',
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.5.1 - Delineation'
          }
        });
      });
    }
    
    return devices;
  }

  placeEndOfWorkSigns(endLat, endLng, bearing, roadAnalysis) {
    const devices = [];
    const endPosition = this.calculatePosition(endLat, endLng, bearing, 50);
    const placementOptions = this.determinePlacementOptions(roadAnalysis, 'advance_warning');
    
    // End of roadwork signs (bilateral)
    ['left', 'right'].forEach(side => {
      const sideOption = placementOptions[`${side}_side`];
      if (sideOption.feasible) {
        const signOffset = side === 'left' ? -sideOption.offset : sideOption.offset;
        const signPosition = this.calculateOffset(
          endPosition.lat, endPosition.lng, bearing + 90, signOffset
        );
        
        devices.push({
          id: `end_work_${side}_${Date.now()}`,
          device_type: 'guide',
          device_name: 'End Road Work',
          position_lat: signPosition.lat,
          position_lng: signPosition.lng,
          properties: {
            side: side,
            placement_type: sideOption.type,
            bilateral_pair: true,
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.2.4 - End of Work Zone'
          }
        });
      }
    });
    
    return devices;
  }

  determinePlacementOptions(roadAnalysis, deviceType) {
    const rules = this.devicePlacementRules[deviceType];
    const clearances = this.clearanceRequirements;
    
    return {
      left_side: this.assessPlacementFeasibility(roadAnalysis, 'left', rules, clearances),
      right_side: this.assessPlacementFeasibility(roadAnalysis, 'right', rules, clearances)
    };
  }

  assessPlacementFeasibility(roadAnalysis, side, rules, clearances) {
    const vergeWidth = roadAnalysis[`${side}_verge_width`];
    const shoulderWidth = roadAnalysis[`${side}_shoulder_width`];
    
    let placement = {
      feasible: false,
      type: null,
      offset: 0,
      constraints: []
    };
    
    // Check verge placement first (preferred)
    if (rules.preferred_location === 'verge' && 
        vergeWidth >= clearances.verge_placement.min_verge_width) {
      placement = {
        feasible: true,
        type: 'verge',
        offset: (roadAnalysis.carriageway_width / 2) + clearances.verge_placement.lateral_clearance,
        constraints: []
      };
    }
    // Check shoulder placement as fallback
    else if (rules.fallback_location === 'shoulder' && 
             shoulderWidth >= clearances.shoulder_placement.min_shoulder_width) {
      placement = {
        feasible: true,
        type: 'shoulder',
        offset: (roadAnalysis.carriageway_width / 2) + clearances.shoulder_placement.lateral_clearance,
        constraints: ['limited_shoulder_width']
      };
    }
    // Check specific constraints
    else {
      placement.constraints = [];
      if (vergeWidth < clearances.verge_placement.min_verge_width) {
        placement.constraints.push('insufficient_verge_width');
      }
      if (shoulderWidth < clearances.shoulder_placement.min_shoulder_width) {
        placement.constraints.push('insufficient_shoulder_width');
      }
    }
    
    return placement;
  }

  determineDelineationSides(roadOccupancy) {
    const sides = [];
    
    if (roadOccupancy.left_lane || roadOccupancy.left_shoulder) {
      sides.push('left');
    }
    if (roadOccupancy.right_lane || roadOccupancy.right_shoulder) {
      sides.push('right');
    }
    if (roadOccupancy.complete_road_closure) {
      sides.push('left', 'right');
    }
    
    return sides.length > 0 ? sides : ['left']; // Default to left side
  }

  getConeSpacing(speedLimit) {
    if (speedLimit <= 50) return 10;
    if (speedLimit <= 60) return 15;
    if (speedLimit <= 70) return 20;
    if (speedLimit <= 80) return 25;
    return 30;
  }

  // Utility methods
  calculatePosition(lat, lng, bearing, distance) {
    const R = 6371000; // Earth's radius in meters
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

  calculateOffset(lat, lng, bearing, offset) {
    return this.calculatePosition(lat, lng, bearing, offset);
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

  calculatePositionAlongPath(startLat, startLng, endLat, endLng, ratio) {
    return {
      lat: startLat + (endLat - startLat) * ratio,
      lng: startLng + (endLng - startLng) * ratio
    };
  }
}

export default new BilateralSignagePlacement();