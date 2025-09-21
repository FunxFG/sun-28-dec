// Enhanced Austroads Traffic Management Device Placement Rules
// Based on AGTTM rules extraction and AS 1742.3 standards
// Implements EXACT AGTTM compliance for DTMR approval

import agttmCompliantRules from './agttmCompliantRules.js';

export class AustroadDevicePlacement {
  constructor() {
    // Use AGTTM-compliant placement system
    this.agttmSystem = agttmCompliantRules;
    
    // Fallback specifications for legacy compatibility
    this.fallbackSpecs = {
      warningDistances: {
        '≤50': { advance1: 100, advance2: 50 },
        '60': { advance1: 150, advance2: 75 },
        '70': { advance1: 200, advance2: 100 },
        '80': { advance1: 250, advance2: 125 },
        '≥90': { advance1: 500, advance2: 200, advance3: 100 }
      }
    };
  }

  /**
   * Calculate device placement using EXACT AGTTM compliance
   * @param {Object} workData - Work zone details
   * @param {Object} roadData - Road characteristics with enhanced geometry
   * @param {Array} coordinates - Start and end coordinates
   * @returns {Array} - Array of AGTTM-compliant positioned devices
   */
  calculateDevicePlacement(workData, roadData, coordinates) {
    // Prepare enhanced work zone data for AGTTM system
    const enhancedWorkZoneData = {
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
      control_measures: workData.control_measures
    };

    // Enhanced road geometry with bilateral placement analysis
    const enhancedRoadGeometry = {
      ...roadData,
      // Estimate geometry if not provided
      carriageway_width: this.estimateCarriagewayWidth(roadData),
      left_shoulder_width: this.estimateShoulderWidth(roadData, 'left'),
      right_shoulder_width: this.estimateShoulderWidth(roadData, 'right'),
      left_verge_width: this.estimateVergeWidth(roadData, 'left'),
      right_verge_width: this.estimateVergeWidth(roadData, 'right'),
      // Use provided or default values
      speed_limit: roadData.speed_limit || 60,
      traffic_volume: roadData.traffic_volume || 15000,
      road_classification: roadData.road_classification || 'Urban Arterial'
    };

    // Generate AGTTM-compliant bilateral placement
    const agttmDevices = this.agttmSystem.calculateAGTTMCompliantPlacement(
      enhancedWorkZoneData, 
      enhancedRoadGeometry
    );

    // Add any specialized devices based on work requirements
    const specializedDevices = this.addSpecializedDevices(workData, roadData, coordinates);

    // Combine all devices
    const allDevices = [...agttmDevices, ...specializedDevices];

    // Final validation and enhancement
    return this.enhanceDevicesWithMetadata(allDevices, enhancedRoadGeometry);
  }

  estimateCarriagewayWidth(roadData) {
    const classification = roadData.road_classification || '';
    
    if (classification.includes('Highway')) return 7.5;
    if (classification.includes('Major') || classification.includes('Arterial')) return 7.0;
    if (classification.includes('Collector')) return 6.5;
    return 6.0; // Local roads
  }

  estimateShoulderWidth(roadData, side) {
    const classification = roadData.road_classification || '';
    const environment = roadData.environment || 'Urban';
    
    if (environment === 'Rural') {
      if (classification.includes('Highway')) return 3.0;
      if (classification.includes('Arterial')) return 2.5;
      return 1.5;
    } else {
      if (classification.includes('Highway')) return 2.5;
      if (classification.includes('Arterial')) return 1.5;
      return 1.0;
    }
  }

  estimateVergeWidth(roadData, side) {
    const environment = roadData.environment || 'Urban';
    const classification = roadData.road_classification || '';
    
    if (environment === 'Rural') {
      return 4.0; // Rural roads typically have wider verges
    } else {
      // Urban verge widths vary significantly
      if (classification.includes('Highway')) return 3.0;
      if (classification.includes('Arterial')) return 2.5;
      return 2.0;
    }
  }

  addSpecializedDevices(workData, roadData, coordinates) {
    const devices = [];
    
    // Shadow vehicles for high-speed or emergency work
    if (workData.work_details.work_type === 'emergency' || 
        (roadData.speed_limit || 60) >= 80) {
      devices.push({
        id: `shadow_vehicle_${Date.now()}`,
        device_type: 'vehicle',
        device_name: 'Shadow Vehicle with Attenuator',
        position_lat: coordinates.start.lat,
        position_lng: coordinates.start.lng,
        properties: {
          agttm_rule: 'agttm4_mobile_shadow_vehicle',
          placement_type: 'mobile',
          vehicle_type: 'shadow_with_attenuator',
          auto_placed: true,
          agttm_compliant: true,
          specialized_device: true
        }
      });
    }

    // Variable Message Signs for major disruptions
    if (workData.road_occupancy.complete_road_closure || 
        (roadData.traffic_volume || 15000) > 20000) {
      const vmsPosition = this.calculatePosition(
        coordinates.start.lat, coordinates.start.lng,
        this.calculateBearing(
          coordinates.start.lat, coordinates.start.lng,
          coordinates.end.lat, coordinates.end.lng
        ) + 180,
        300 // 300m advance warning for VMS
      );
      
      devices.push({
        id: `vms_${Date.now()}`,
        device_type: 'guidance',
        device_name: 'Variable Message Sign',
        position_lat: vmsPosition.lat,
        position_lng: vmsPosition.lng,
        properties: {
          agttm_rule: 'sa_wz_023_vms_location_clearance',
          message: workData.road_occupancy.complete_road_closure ? 
            'ROAD CLOSED AHEAD - USE ALTERNATE ROUTE' :
            'LANE CLOSURE AHEAD - MERGE WITH CARE',
          placement_type: 'centralized',
          auto_placed: true,
          agttm_compliant: true,
          specialized_device: true
        }
      });
    }

    return devices;
  }

  enhanceDevicesWithMetadata(devices, roadGeometry) {
    return devices.map(device => {
      // Add enhanced metadata for better visualization and reporting
      const enhanced = {
        ...device,
        properties: {
          ...device.properties,
          // Add placement metadata
          road_classification: roadGeometry.road_classification,
          speed_environment: roadGeometry.speed_limit,
          traffic_environment: roadGeometry.traffic_volume,
          
          // Add visual styling hints
          marker_style: this.getEnhancedMarkerStyle(device),
          
          // Add compliance summary
          compliance_summary: this.generateComplianceSummary(device),
          
          // Add placement timestamp
          placed_at: new Date().toISOString()
        }
      };

      return enhanced;
    });
  }

  getEnhancedMarkerStyle(device) {
    const isAutoPlaced = device.properties.auto_placed;
    const complianceScore = device.properties.agttm_compliance_score || 100;
    const isBilateral = device.properties.bilateral_pair;
    
    let color = '#3B82F6'; // Default blue
    
    if (complianceScore < 80) {
      color = '#EF4444'; // Red for non-compliance
    } else if (complianceScore < 95) {
      color = '#F59E0B'; // Orange for warnings
    } else if (isAutoPlaced) {
      color = '#10B981'; // Green for compliant auto-placed
    }
    
    return {
      color: color,
      bilateral_indicator: isBilateral,
      compliance_indicator: complianceScore >= 95,
      size: device.device_type === 'guidance' ? 'large' : 'standard',
      agttm_compliant: device.properties.agttm_compliant || false
    };
  }

  generateComplianceSummary(device) {
    const props = device.properties;
    
    return {
      agttm_rule: props.agttm_rule || 'Not specified',
      as1742_reference: props.as1742_reference || 'Not specified',
      bilateral_compliant: props.bilateral_pair || false,
      clearance_compliant: props.compliance_status === 'compliant',
      work_zone_category: props.work_zone_category || 'Not categorized',
      overall_status: props.agttm_compliant ? 'AGTTM Compliant' : 'Non-compliant'
    };
  }

  // Existing utility methods
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
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    
    return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * R;
  }

  calculatePosition(lat, lng, bearing, distance) {
    const R = 6371000;
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