// Austroads Traffic Management Device Placement Rules
// Based on AGTTM (Austroads Guide to Temporary Traffic Management)

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

    // Cone spacing based on speed limit (meters)
    this.coneSpacing = {
      '≤50': 10,
      '60': 15,
      '70': 20,
      '80': 25,
      '≥90': 30
    };

    // Device specifications
    this.devices = {
      warning: {
        'roadwork_ahead': { name: 'Road Work Ahead', priority: 1 },
        'lane_closure': { name: 'Lane Closure Ahead', priority: 2 },
        'detour': { name: 'Detour', priority: 3 },
        'speed_reduction': { name: 'Reduce Speed', priority: 4 }
      },
      regulatory: {
        'speed_limit': { name: 'Temporary Speed Limit', priority: 1 },
        'stop_go': { name: 'Stop/Go', priority: 2 },
        'no_overtaking': { name: 'No Overtaking', priority: 3 }
      },
      guidance: {
        'traffic_cones': { name: 'Traffic Cones', priority: 1 },
        'arrow_board': { name: 'Arrow Board', priority: 2 },
        'barriers': { name: 'Safety Barriers', priority: 3 }
      }
    };
  }

  /**
   * Calculate automatic device placement based on Austroads rules
   * @param {Object} workData - Work zone details
   * @param {Object} roadData - Road characteristics
   * @param {Array} coordinates - Start and end coordinates
   * @returns {Array} - Array of positioned devices
   */
  calculateDevicePlacement(workData, roadData, coordinates) {
    const devices = [];
    const speedLimit = this.getSpeedCategory(roadData.speed_limit || 60);
    const distances = this.warningDistances[speedLimit];
    const coneSpacing = this.coneSpacing[speedLimit];

    // Calculate work zone direction vector
    const startLat = coordinates.start.lat;
    const startLng = coordinates.start.lng;
    const endLat = coordinates.end.lat;
    const endLng = coordinates.end.lng;

    // Calculate bearing and distances
    const bearing = this.calculateBearing(startLat, startLng, endLat, endLng);
    const workZoneLength = this.calculateDistance(startLat, startLng, endLat, endLng);

    // 1. ADVANCE WARNING SIGNS
    devices.push(...this.placeAdvanceWarnings(startLat, startLng, bearing, distances, workData, roadData));

    // 2. REGULATORY SIGNS
    devices.push(...this.placeRegulatoryDevices(startLat, startLng, bearing, distances, workData, roadData));

    // 3. TRAFFIC GUIDANCE DEVICES
    devices.push(...this.placeGuidanceDevices(
      startLat, startLng, endLat, endLng, 
      bearing, workZoneLength, coneSpacing, workData, roadData
    ));

    // 4. END OF WORK ZONE SIGNS
    devices.push(...this.placeEndOfWorkZone(endLat, endLng, bearing, workData, roadData));

    return devices;
  }

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