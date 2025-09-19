// Austroads Traffic Management Device Placement Rules
// Enhanced with Bilateral Signage Placement
// Based on AGTTM (Austroads Guide to Temporary Traffic Management)

import bilateralPlacement from './bilateralSignagePlacement.js';

export class AustroadDevicePlacement {
  constructor() {
    // Speed-based advance warning distances (meters)
    this.warningDistances = {
      '≤50': { advance1: 100, advance2: 50, advance3: 25 },
      '60': { advance1: 150, advance2: 75, advance3: 50 },
      '70': { advance1: 200, advance2: 100, advance3: 75 },
      '80': { advance1: 250, advance2: 125, advance3: 100 },
      '≥90': { advance1: 500, advance2: 200, advance3: 100 }
    };

    // Enhanced bilateral placement requirements
    this.bilateralRequirements = true;
    this.bilateralPlacement = bilateralPlacement;
  }

  /**
   * Calculate automatic device placement with enhanced bilateral positioning
   * @param {Object} workData - Work zone details
   * @param {Object} roadData - Road characteristics with geometry
   * @param {Array} coordinates - Start and end coordinates
   * @returns {Array} - Array of positioned devices with bilateral placement
   */
  calculateDevicePlacement(workData, roadData, coordinates) {
    // Enhanced road geometry analysis
    const roadGeometry = this.analyzeRoadGeometry(roadData, coordinates);
    
    // Use enhanced bilateral placement system
    const workZoneData = {
      startLat: coordinates.start.lat,
      startLng: coordinates.start.lng,
      endLat: coordinates.end.lat,
      endLng: coordinates.end.lng,
      bearing: this.calculateBearing(
        coordinates.start.lat, coordinates.start.lng,
        coordinates.end.lat, coordinates.end.lng
      ),
      work_details: workData.work_details,
      road_occupancy: workData.road_occupancy,
      control_measures: workData.control_measures,
      road_data: roadData
    };
    
    // Generate devices with proper bilateral placement
    const bilateralDevices = this.bilateralPlacement.calculateBilateralPlacement(
      workZoneData, roadGeometry
    );
    
    // Add any additional devices based on specific work requirements
    const additionalDevices = this.addSpecializedDevices(workData, roadData, coordinates);
    
    // Combine and validate all devices
    const allDevices = [...bilateralDevices, ...additionalDevices];
    
    // Validate placement and add warnings
    return this.validateAndEnhanceDevicePlacement(allDevices, roadGeometry);
  }

  analyzeRoadGeometry(roadData, coordinates) {
    // Enhanced road geometry analysis
    const workZoneLength = this.calculateDistance(
      coordinates.start.lat, coordinates.start.lng,
      coordinates.end.lat, coordinates.end.lng
    );
    
    return {
      // Basic geometry
      carriageway_width: this.estimateCarriagewayWidth(roadData),
      work_zone_length: workZoneLength,
      
      // Shoulder analysis
      left_shoulder_width: this.estimateShoulderWidth(roadData, 'left'),
      right_shoulder_width: this.estimateShoulderWidth(roadData, 'right'),
      
      // Verge analysis
      left_verge_width: this.estimateVergeWidth(roadData, 'left'),
      right_verge_width: this.estimateVergeWidth(roadData, 'right'),
      
      // Traffic characteristics
      speed_limit: roadData.speed_limit || 60,
      traffic_volume: roadData.traffic_volume || 15000,
      road_classification: roadData.road_classification,
      
      // Environmental constraints
      constraints: this.identifyConstraints(roadData, coordinates),
      
      // Median information
      median_present: this.hasMedian(roadData),
      median_width: this.estimateMedianWidth(roadData)
    };
  }

  estimateCarriagewayWidth(roadData) {
    const classification = roadData.road_classification;
    
    if (classification?.includes('Highway')) return 7.0;
    if (classification?.includes('Arterial')) return 6.5;
    if (classification?.includes('Collector')) return 6.0;
    return 5.5; // Local roads
  }

  estimateShoulderWidth(roadData, side) {
    const classification = roadData.road_classification;
    
    if (classification?.includes('Highway')) return 2.5;
    if (classification?.includes('Arterial')) return 1.5;
    if (classification?.includes('Collector')) return 1.0;
    return 0.5; // Local roads often have minimal shoulders
  }

  estimateVergeWidth(roadData, side) {
    const environment = roadData.environment || 'Urban';
    
    if (environment === 'Rural') return 3.0;
    if (environment === 'Urban') {
      const classification = roadData.road_classification;
      if (classification?.includes('Highway')) return 2.5;
      if (classification?.includes('Arterial')) return 2.0;
      return 1.5; // Urban local roads
    }
    return 2.0; // Default
  }

  identifyConstraints(roadData, coordinates) {
    const constraints = [];
    
    // Add common urban constraints
    if (roadData.environment === 'Urban') {
      constraints.push('utility_poles', 'street_furniture', 'property_boundaries');
    }
    
    // Add traffic volume constraints
    if (roadData.traffic_volume > 25000) {
      constraints.push('high_traffic_volume');
    }
    
    // Add speed-related constraints
    if (roadData.speed_limit >= 80) {
      constraints.push('high_speed_environment');
    }
    
    return constraints;
  }

  hasMedian(roadData) {
    return roadData.road_classification?.includes('Highway') || 
           roadData.road_classification?.includes('Divided');
  }

  estimateMedianWidth(roadData) {
    if (this.hasMedian(roadData)) {
      if (roadData.road_classification?.includes('Highway')) return 4.0;
      return 2.0;
    }
    return 0;
  }

  addSpecializedDevices(workData, roadData, coordinates) {
    const devices = [];
    
    // Add arrow boards for lane changes
    if (workData.road_occupancy.left_lane || workData.road_occupancy.right_lane) {
      const arrowBoardPos = this.calculatePosition(
        coordinates.start.lat, coordinates.start.lng,
        this.calculateBearing(
          coordinates.start.lat, coordinates.start.lng,
          coordinates.end.lat, coordinates.end.lng
        ) + 180,
        150
      );
      
      devices.push({
        id: `arrow_board_${Date.now()}`,
        device_type: 'guidance',
        device_name: 'Changeable Message Sign',
        position_lat: arrowBoardPos.lat,
        position_lng: arrowBoardPos.lng,
        properties: {
          message: workData.road_occupancy.left_lane ? 'MERGE RIGHT' : 'MERGE LEFT',
          placement_type: 'centralized',
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.5.3 - Lane Change Guidance'
        }
      });
    }
    
    // Add shadow vehicles for high-risk work
    if (workData.work_details.work_type === 'emergency' || 
        roadData.speed_limit >= 80) {
      devices.push({
        id: `shadow_vehicle_${Date.now()}`,
        device_type: 'vehicle',
        device_name: 'Shadow Vehicle with Attenuator',
        position_lat: coordinates.start.lat,
        position_lng: coordinates.start.lng,
        properties: {
          placement_type: 'mobile',
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.7.2 - Mobile Protection'
        }
      });
    }
    
    return devices;
  }

  validateAndEnhanceDevicePlacement(devices, roadGeometry) {
    return devices.map(device => {
      // Add placement validation
      const validation = this.validateDevicePlacement(device, roadGeometry);
      
      // Enhance device properties with validation results
      return {
        ...device,
        properties: {
          ...device.properties,
          placement_valid: validation.valid,
          placement_warnings: validation.warnings,
          clearance_analysis: validation.clearances,
          // Add visual styling based on placement quality
          marker_style: this.getMarkerStyle(device, validation)
        }
      };
    });
  }

  validateDevicePlacement(device, roadGeometry) {
    const warnings = [];
    const clearances = {};
    
    // Check lateral clearance
    const side = device.properties.side;
    if (side) {
      const availableWidth = side === 'left' ? 
        roadGeometry.left_verge_width : roadGeometry.right_verge_width;
      
      if (availableWidth < 2.0) {
        warnings.push('Limited lateral clearance');
      }
      
      clearances[`${side}_clearance`] = availableWidth;
    }
    
    // Check bilateral pairing
    if (device.properties.bilateral_pair && !device.properties.pair_placed) {
      warnings.push('Bilateral pair may be incomplete');
    }
    
    // Check sight distance
    if (roadGeometry.speed_limit >= 80 && device.device_type === 'warning') {
      clearances.sight_distance = 'High speed environment - extended sight lines required';
    }
    
    return {
      valid: warnings.length === 0,
      warnings,
      clearances
    };
  }

  getMarkerStyle(device, validation) {
    let color = '#3B82F6'; // Default blue for auto-placed
    
    if (!validation.valid) {
      color = '#EF4444'; // Red for validation issues
    } else if (validation.warnings.length > 0) {
      color = '#F59E0B'; // Yellow/orange for warnings
    }
    
    return {
      color,
      bilateral_indicator: device.properties.bilateral_pair,
      placement_type: device.properties.placement_type
    };
  }

  // Existing utility methods remain the same...
  calculateBearing(lat1, lng1, lat2, lng2) {
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const lat1Rad = lat1 * Math.PI / 180;
    const lat2Rad = lat2 * Math.PI / 180;
    
    const y = Math.sin(dLng) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - 
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLng);
    
    return Math.atan2(y, x) * 180 / Math.PI;
  }

  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000; // Earth's radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    
    return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * R;
  }

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
}

// Export default instance
export default new AustroadDevicePlacement();

  placeAdvanceWarnings(startLat, startLng, bearing, distances, workData, roadData) {
    const devices = [];
    
    // Primary advance warning (furthest from work zone)
    const advance1Pos = this.calculatePosition(startLat, startLng, bearing + 180, distances.advance1);
    devices.push({
      id: `warning_advance_1_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Road Work Ahead',
      position_lat: advance1Pos.lat,
      position_lng: advance1Pos.lng,
      properties: {
        distance: `${distances.advance1}m`,
        auto_placed: true,
        austroads_rule: 'AGTTM Section 4.2.1'
      }
    });

    // Secondary advance warning
    const advance2Pos = this.calculatePosition(startLat, startLng, bearing + 180, distances.advance2);
    devices.push({
      id: `warning_advance_2_${Date.now() + 1}`,
      device_type: 'warning',
      device_name: workData.road_occupancy.complete_road_closure 
        ? 'Road Closed Ahead' 
        : 'Lane Closure Ahead',
      position_lat: advance2Pos.lat,
      position_lng: advance2Pos.lng,
      properties: {
        distance: `${distances.advance2}m`,
        auto_placed: true,
        austroads_rule: 'AGTTM Section 4.2.2'
      }
    });

    // Speed reduction warning if required
    if (workData.control_measures.speed_reduction) {
      const speedPos = this.calculatePosition(startLat, startLng, bearing + 180, distances.advance3);
      devices.push({
        id: `speed_reduction_${Date.now() + 2}`,
        device_type: 'regulatory',
        device_name: 'Temporary Speed Limit 40',
        position_lat: speedPos.lat,
        position_lng: speedPos.lng,
        properties: {
          distance: `${distances.advance3}m`,
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.3.1',
          speed_limit: 40
        }
      });
    }

    return devices;
  }

  placeRegulatoryDevices(startLat, startLng, bearing, distances, workData, roadData) {
    const devices = [];

    // Stop/Go boards for single lane closure
    if (workData.control_measures.twenty_min_rule || 
        (workData.road_occupancy.left_lane && workData.road_occupancy.right_lane)) {
      
      // Stop board at start
      devices.push({
        id: `stop_go_start_${Date.now()}`,
        device_type: 'regulatory',
        device_name: 'Stop/Go Board',
        position_lat: startLat,
        position_lng: startLng,
        properties: {
          type: 'start_position',
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.4.1'
        }
      });
    }

    // No overtaking signs for mobile works
    if (workData.work_details.work_style === 'mobile') {
      const noOvertakePos = this.calculatePosition(startLat, startLng, bearing + 180, 50);
      devices.push({
        id: `no_overtaking_${Date.now()}`,
        device_type: 'regulatory',
        device_name: 'No Overtaking',
        position_lat: noOvertakePos.lat,
        position_lng: noOvertakePos.lng,
        properties: {
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.3.3'
        }
      });
    }

    return devices;
  }

  placeGuidanceDevices(startLat, startLng, endLat, endLng, bearing, workZoneLength, coneSpacing, workData, roadData) {
    const devices = [];

    // Traffic cones along the work zone
    const numCones = Math.floor(workZoneLength / coneSpacing);
    
    for (let i = 0; i <= numCones; i++) {
      const distance = (workZoneLength / numCones) * i;
      const conePos = this.calculatePositionAlongPath(startLat, startLng, endLat, endLng, distance / workZoneLength);
      
      // Offset cones to the side based on lane occupancy
      const offset = this.getConeOffset(workData.road_occupancy);
      const offsetPos = this.calculatePosition(conePos.lat, conePos.lng, bearing + 90, offset);
      
      devices.push({
        id: `cone_${i}_${Date.now()}`,
        device_type: 'cone',
        device_name: 'Traffic Cone 700mm',
        position_lat: offsetPos.lat,
        position_lng: offsetPos.lng,
        properties: {
          spacing: `${coneSpacing}m`,
          sequence: i,
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.5.1'
        }
      });
    }

    // Arrow boards for lane changes
    if (workData.road_occupancy.left_lane || workData.road_occupancy.right_lane) {
      const arrowPos = this.calculatePosition(startLat, startLng, bearing + 180, 75);
      devices.push({
        id: `arrow_board_${Date.now()}`,
        device_type: 'guidance',
        device_name: 'Changeable Message Sign',
        position_lat: arrowPos.lat,
        position_lng: arrowPos.lng,
        properties: {
          message: workData.road_occupancy.left_lane ? 'MERGE RIGHT' : 'MERGE LEFT',
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.5.3'
        }
      });
    }

    // Safety barriers for high-risk work
    if (workData.work_details.work_type === 'construction' || 
        roadData.traffic_volume > 20000) {
      
      const barrierSpacing = 50; // 50m spacing for barriers
      const numBarriers = Math.floor(workZoneLength / barrierSpacing);
      
      for (let i = 0; i <= numBarriers; i++) {
        const distance = (workZoneLength / numBarriers) * i;
        const barrierPos = this.calculatePositionAlongPath(startLat, startLng, endLat, endLng, distance / workZoneLength);
        
        devices.push({
          id: `barrier_${i}_${Date.now()}`,
          device_type: 'barrier',
          device_name: 'Concrete Barrier',
          position_lat: barrierPos.lat,
          position_lng: barrierPos.lng,
          properties: {
            auto_placed: true,
            austroads_rule: 'AGTTM Section 4.6.1'
          }
        });
      }
    }

    return devices;
  }

  placeEndOfWorkZone(endLat, endLng, bearing, workData, roadData) {
    const devices = [];

    // End of work zone sign
    const endPos = this.calculatePosition(endLat, endLng, bearing, 50);
    devices.push({
      id: `end_work_zone_${Date.now()}`,
      device_type: 'guide',
      device_name: 'End Road Work',
      position_lat: endPos.lat,
      position_lng: endPos.lng,
      properties: {
        auto_placed: true,
        austroads_rule: 'AGTTM Section 4.2.4'
      }
    });

    // Speed limit resumption
    if (workData.control_measures.speed_reduction) {
      const speedResumePos = this.calculatePosition(endLat, endLng, bearing, 100);
      devices.push({
        id: `speed_resume_${Date.now()}`,
        device_type: 'regulatory',
        device_name: 'End Temporary Speed Limit',
        position_lat: speedResumePos.lat,
        position_lng: speedResumePos.lng,
        properties: {
          auto_placed: true,
          austroads_rule: 'AGTTM Section 4.3.2'
        }
      });
    }

    return devices;
  }

  // Utility methods
  getSpeedCategory(speed) {
    if (speed <= 50) return '≤50';
    if (speed === 60) return '60';
    if (speed === 70) return '70';
    if (speed === 80) return '80';
    return '≥90';
  }

  getConeOffset(roadOccupancy) {
    // Determine which side to place cones based on occupancy
    if (roadOccupancy.left_lane) return -3; // 3m to the left
    if (roadOccupancy.right_lane) return 3;  // 3m to the right
    return 0; // Center placement
  }

  calculateBearing(lat1, lng1, lat2, lng2) {
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const lat1Rad = lat1 * Math.PI / 180;
    const lat2Rad = lat2 * Math.PI / 180;
    
    const y = Math.sin(dLng) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) - 
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLng);
    
    return Math.atan2(y, x) * 180 / Math.PI;
  }

  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000; // Earth's radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    
    return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * R;
  }

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

  calculatePositionAlongPath(startLat, startLng, endLat, endLng, ratio) {
    return {
      lat: startLat + (endLat - startLat) * ratio,
      lng: startLng + (endLng - startLng) * ratio
    };
  }
}

// Export default instance
export default new AustroadDevicePlacement();