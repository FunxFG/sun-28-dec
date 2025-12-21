/**
 * TGS Placement Engine - AS 1742.3:2019 Compliant
 * 
 * This module implements accurate TGS (Traffic Guidance Scheme) device placement
 * based on ADVANCED Traffic Management Generic TGS Package 2026 standards.
 * 
 * Key Features:
 * - Multiple TGS patterns (Lane Closure, Road Closure, Stop-Slow, etc.)
 * - Accurate distance calculations per AS 1742.3
 * - Road edge snapping for precise device placement
 * - Side street signing (double gating)
 * - Speed-based configurations
 */

class TGSPlacementEngine {
  
  constructor() {
    // Earth radius for geodesic calculations
    this.EARTH_RADIUS_M = 6371000;
  }

  /**
   * Main entry point - supports MULTIPLE TGS patterns
   * @param {Object} workZoneData - Work zone coordinates and details
   * @param {String|Array} tgsTypes - Single TGS type or array of multiple types
   * @param {Number} speedLimit - Speed limit in km/h
   * @param {Object} roadEdgeGeometry - Road edge points for snapping
   * @param {Array} sideStreets - Side street locations
   * @returns {Array} Combined devices from all selected TGS patterns
   */
  placeTGSDevices(workZoneData, tgsTypes, speedLimit, roadEdgeGeometry = null, sideStreets = []) {
    console.log('🏗️ TGS Placement Engine Initializing...');
    
    // Handle single or multiple TGS types
    const typesArray = Array.isArray(tgsTypes) ? tgsTypes : [tgsTypes];
    console.log(`  TGS Types Selected: ${typesArray.join(', ')}`);
    console.log(`  Speed Limit: ${speedLimit} km/h`);
    console.log(`  Road Edge Data: ${roadEdgeGeometry ? 'Available' : 'Not Available'}`);
    
    let allDevices = [];
    
    // Place devices for each selected TGS type
    typesArray.forEach((tgsType, index) => {
      console.log(`\n📋 Processing TGS Pattern ${index + 1}/${typesArray.length}: ${tgsType}`);
      
      let devices = [];
      
      switch(tgsType) {
        // STOP-SLOW PATTERNS
        case 'STOP_SLOW_LOW_TRAFFIC_LANE':
        case 'STOP_SLOW_HIGH_TRAFFIC_LANE':
        case 'STOP_SLOW_LOW_SHOULDER':
        case 'STOP_SLOW_HIGH_SHOULDER':
        case 'STOP_SLOW_LOW_SPEED':
        case 'STOP_SLOW_HIGH_SPEED':
          devices = this.placeStopSlowTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        // LANE CLOSURE PATTERNS
        case 'LANE_CLOSURE_LOW_NO_MEDIAN':
        case 'LANE_CLOSURE_HIGH_NO_MEDIAN':
        case 'LANE_CLOSURE_LOW_MEDIAN':
        case 'LANE_CLOSURE_HIGH_MEDIAN':
        case 'LANE_CLOSURE':
        case 'LANE_CLOSURE_NO_MEDIAN':
        case 'LANE_CLOSURE_RAISED_MEDIAN':
          devices = this.placeLaneClosureTGS(workZoneData, speedLimit, roadEdgeGeometry, sideStreets);
          break;
        
        // INTERSECTION PATTERNS
        case 'ROUNDABOUT_LOW':
        case 'ROUNDABOUT_HIGH':
          devices = this.placeRoundaboutTGS(workZoneData, speedLimit, roadEdgeGeometry, sideStreets);
          break;
        
        case 'T_INTERSECTION_LOW':
        case 'T_INTERSECTION_HIGH':
          devices = this.placeTIntersectionTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        // CONTRA FLOW PATTERNS
        case 'CONTRA_FLOW_LOW':
        case 'CONTRA_FLOW_HIGH':
        case 'CONTRA_FLOW':
          devices = this.placeContraFlowTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        // ROAD CLOSURE PATTERNS
        case 'ROAD_CLOSURE_DETOUR':
        case 'ROAD_CLOSURE':
          devices = this.placeRoadClosureTGS(workZoneData, speedLimit, roadEdgeGeometry, sideStreets);
          break;
        
        case 'ROAD_CLOSURE_COURT_BOWL':
          devices = this.placeCourtBowlClosureTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        // PEDESTRIAN/SHOULDER PATTERNS
        case 'SHOULDER_WORK':
          devices = this.placeShoulderWorkTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        case 'FOOTPATH_CLOSURE':
          devices = this.placeFootpathClosureTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        case 'PEDESTRIAN_DETOUR':
          devices = this.placePedestrianDetourTGS(workZoneData, speedLimit, roadEdgeGeometry);
          break;
        
        default:
          console.warn(`⚠️ Unknown TGS type: ${tgsType}, skipping`);
          devices = [];
      }
      
      // Tag devices with their TGS pattern
      devices = devices.map(device => ({
        ...device,
        properties: {
          ...device.properties,
          tgs_pattern: tgsType
        }
      }));
      
      allDevices = [...allDevices, ...devices];
      console.log(`  ✅ Added ${devices.length} devices from ${tgsType}`);
    });
    
    console.log(`\n🎯 Total Devices from All Patterns: ${allDevices.length}`);
    return allDevices;
  }

  /**
   * Lane Closure TGS - M01.2A Pattern
   * For single lane closure on multi-lane roads
   */
  placeLaneClosureTGS(workZoneData, speedLimit, roadEdgeGeometry, sideStreets = []) {
    console.log('🚧 === LANE CLOSURE TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    // Validate inputs
    if (!start_lat || !start_lng) {
      console.error('❌ Invalid coordinates');
      return [];
    }
    
    // Calculate road bearing
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    console.log(`  Road bearing: ${bearing.toFixed(1)}°`);
    
    // Determine speed category
    const isLowSpeed = speedLimit <= 70;
    const speedCategory = isLowSpeed ? 'low' : 'high';
    console.log(`  Speed category: ${speedCategory} (${speedLimit} km/h)`);
    
    // Get road edge for snapping
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    console.log(`  Road edge points: ${roadEdge.length}`);
    
    // === 1. ADVANCE WARNING SIGNS ===
    console.log('\n📍 Placing Advance Warning Signs...');
    const advanceWarningSequence = isLowSpeed ? [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 195 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 145 }
    ] : [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 400 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 320 }
    ];
    
    advanceWarningSequence.forEach((sign, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, bearing + 180, sign.distance);
      const finalPos = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0); // 1m from edge
      
      devices.push({
        id: `advance_warning_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: finalPos.lat,
        position_lng: finalPos.lng,
        properties: {
          distance_from_workzone: sign.distance,
          placement: 'advance_warning',
          sequence: idx + 1,
          auto_placed: true,
          tgs_compliant: true
        }
      });
      console.log(`    ${sign.code} @ ${sign.distance}m: (${finalPos.lat.toFixed(6)}, ${finalPos.lng.toFixed(6)})`);
    });
    
    // === 2. LANE STATUS / MERGE SIGNS ===
    console.log('\n📍 Placing Lane Status Signs...');
    const mergeDistance = isLowSpeed ? 60 : 80;
    const mergePos = this.calculatePosition(start_lat, start_lng, bearing + 180, mergeDistance);
    const mergeSnapped = this.snapToRoadEdge(mergePos.lat, mergePos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `merge_sign_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Lane Status / Merge Left',
      device_code: 'T1-25',
      position_lat: mergeSnapped.lat,
      position_lng: mergeSnapped.lng,
      properties: {
        distance_from_workzone: mergeDistance,
        placement: 'lane_status',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    console.log(`    T1-25 @ ${mergeDistance}m: (${mergeSnapped.lat.toFixed(6)}, ${mergeSnapped.lng.toFixed(6)})`);
    
    // === 3. SPEED LIMIT REDUCTION SIGN ===
    console.log('\n📍 Placing Speed Reduction Sign...');
    const reducedSpeed = isLowSpeed ? 40 : 60;
    const speedSignDistance = isLowSpeed ? 45 : 60;
    const speedPos = this.calculatePosition(start_lat, start_lng, bearing + 180, speedSignDistance);
    const speedSnapped = this.snapToRoadEdge(speedPos.lat, speedPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `speed_limit_${Date.now()}`,
      device_type: 'regulatory',
      device_name: `Speed Limit ${reducedSpeed}`,
      device_code: 'R4-1',
      position_lat: speedSnapped.lat,
      position_lng: speedSnapped.lng,
      properties: {
        distance_from_workzone: speedSignDistance,
        placement: 'speed_reduction',
        speed_value: reducedSpeed,
        auto_placed: true,
        tgs_compliant: true
      }
    });
    console.log(`    R4-1 (${reducedSpeed} km/h) @ ${speedSignDistance}m: (${speedSnapped.lat.toFixed(6)}, ${speedSnapped.lng.toFixed(6)})`);
    
    // === 4. ARROW BOARD ===
    console.log('\n📍 Placing Arrow Board...');
    const arrowDistance = isLowSpeed ? 30 : 45;
    const arrowPos = this.calculatePosition(start_lat, start_lng, bearing + 180, arrowDistance);
    const arrowSnapped = this.snapToRoadEdge(arrowPos.lat, arrowPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `arrow_board_${Date.now()}`,
      device_type: 'arrow_board',
      device_name: 'Arrow Board Left',
      device_code: 'Arrow',
      position_lat: arrowSnapped.lat,
      position_lng: arrowSnapped.lng,
      properties: {
        distance_from_workzone: arrowDistance,
        placement: 'arrow_board',
        direction: 'left',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    console.log(`    Arrow Board @ ${arrowDistance}m: (${arrowSnapped.lat.toFixed(6)}, ${arrowSnapped.lng.toFixed(6)})`);
    
    // === 5. TAPER CONES ===
    console.log('\n📍 Placing Taper Cones...');
    const taperConfig = this.getTaperConfig(speedLimit);
    console.log(`    Taper: ${taperConfig.length}m, ${taperConfig.coneSpacing}m spacing, ${taperConfig.numCones} cones`);
    
    const taperStartDistance = isLowSpeed ? 25 : 35;
    const laneWidth = 3.5; // Standard lane width in meters
    
    for (let i = 0; i <= taperConfig.numCones; i++) {
      const progress = i / taperConfig.numCones; // 0 to 1
      const distanceAlongTaper = i * taperConfig.coneSpacing;
      const distanceFromWorkzone = taperStartDistance - distanceAlongTaper;
      
      // Position along road centerline
      const coneBasePos = this.calculatePosition(
        start_lat, start_lng,
        bearing + 180,
        distanceFromWorkzone
      );
      
      // LINEAR taper: lateral offset decreases from lane width to road edge
      const lateralOffset = laneWidth * (1 - progress) + 0.3; // 0.3m from edge at end
      
      // Apply lateral offset perpendicular to road bearing
      const conePos = this.calculatePosition(
        coneBasePos.lat, coneBasePos.lng,
        bearing - 90, // 90° left of bearing
        lateralOffset
      );
      
      // Snap to road edge
      const coneSnapped = this.snapToRoadEdge(conePos.lat, conePos.lng, roadEdge, 0.3);
      
      devices.push({
        id: `taper_cone_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: 'Traffic Cone 700mm',
        device_code: 'TC1',
        position_lat: coneSnapped.lat,
        position_lng: coneSnapped.lng,
        properties: {
          distance_from_workzone: distanceFromWorkzone,
          distance_along_taper: distanceAlongTaper,
          lateral_offset: lateralOffset.toFixed(2),
          taper_progress: `${(progress * 100).toFixed(0)}%`,
          placement: 'taper',
          auto_placed: true,
          tgs_compliant: true
        }
      });
      
      if (i === 0 || i === taperConfig.numCones) {
        console.log(`    Cone ${i}: @ ${distanceFromWorkzone.toFixed(1)}m, offset ${lateralOffset.toFixed(2)}m`);
      }
    }
    console.log(`    ... ${taperConfig.numCones + 1} total cones placed`);
    
    // === 6. WORK ZONE DELINEATION ===
    console.log('\n📍 Placing Work Zone Delineation...');
    const workzoneLength = this.calculateDistance(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng) || 50;
    const delineationSpacing = 10; // 10m spacing
    const numDelineators = Math.max(3, Math.floor(workzoneLength / delineationSpacing));
    
    for (let i = 0; i <= numDelineators; i++) {
      const distanceAlong = i * delineationSpacing;
      
      const delinBasePos = this.calculatePosition(start_lat, start_lng, bearing, distanceAlong);
      const delinOffsetPos = this.calculatePosition(delinBasePos.lat, delinBasePos.lng, bearing - 90, 0.3);
      const delinSnapped = this.snapToRoadEdge(delinOffsetPos.lat, delinOffsetPos.lng, roadEdge, 0.3);
      
      const isEnd = i === 0 || i === numDelineators;
      
      devices.push({
        id: `workzone_delin_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: isEnd ? 'Bollard' : 'Traffic Cone 700mm',
        device_code: isEnd ? 'Bollard' : 'TC1',
        position_lat: delinSnapped.lat,
        position_lng: delinSnapped.lng,
        properties: {
          distance_from_start: distanceAlong,
          placement: 'workzone_delineation',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    }
    console.log(`    ${numDelineators + 1} delineators placed over ${workzoneLength.toFixed(0)}m`);
    
    // === 7. END ROADWORK SIGN ===
    console.log('\n📍 Placing End Roadwork Sign...');
    const endSignDistance = isLowSpeed ? 50 : 80;
    const endLat = end_lat || start_lat;
    const endLng = end_lng || start_lng;
    const endPos = this.calculatePosition(endLat, endLng, bearing, endSignDistance);
    const endSnapped = this.snapToRoadEdge(endPos.lat, endPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `end_roadwork_${Date.now()}`,
      device_type: 'warning',
      device_name: 'End Road Work',
      device_code: 'T1-11',
      position_lat: endSnapped.lat,
      position_lng: endSnapped.lng,
      properties: {
        distance_from_workzone_end: endSignDistance,
        placement: 'end_roadwork',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    console.log(`    T1-11 @ +${endSignDistance}m after workzone: (${endSnapped.lat.toFixed(6)}, ${endSnapped.lng.toFixed(6)})`);
    
    // === 8. SIDE STREET SIGNS ===
    if (sideStreets && sideStreets.length > 0) {
      console.log('\n📍 Placing Side Street Signs (Double Gating)...');
      sideStreets.forEach((street, idx) => {
        if (street.lat && street.lng) {
          // Place "Road Work Ahead" on side street approach (50m back)
          const sideSignPos = this.calculatePosition(
            street.lat, street.lng,
            street.bearing || 0,
            -50 // 50m back from intersection
          );
          const sideSnapped = this.snapToRoadEdge(sideSignPos.lat, sideSignPos.lng, roadEdge, 1.0);
          
          devices.push({
            id: `side_street_${idx}_${Date.now()}`,
            device_type: 'warning',
            device_name: 'Road Work Ahead',
            device_code: 'T1-1',
            position_lat: sideSnapped.lat,
            position_lng: sideSnapped.lng,
            properties: {
              side_street: street.name || `Side Street ${idx + 1}`,
              distance_from_intersection: 50,
              placement: 'side_street_warning',
              auto_placed: true,
              tgs_compliant: true
            }
          });
          console.log(`    Side street "${street.name}" - T1-1 @ 50m approach`);
        }
      });
    }
    
    console.log(`\n✅ Lane Closure TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Road Closure with Detour TGS
   */
  placeRoadClosureTGS(workZoneData, speedLimit, roadEdgeGeometry, sideStreets = []) {
    console.log('🚧 === ROAD CLOSURE TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    const isLowSpeed = speedLimit <= 70;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // === ADVANCE WARNING ===
    const advanceSequence = isLowSpeed ? [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 195 },
      { code: 'T5-28', name: 'Road Closed Ahead', distance: 145 },
      { code: 'G9-79', name: 'Detour', distance: 100 }
    ] : [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 400 },
      { code: 'T5-28', name: 'Road Closed Ahead', distance: 240 },
      { code: 'G9-79', name: 'Detour', distance: 160 }
    ];
    
    advanceSequence.forEach((sign, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, bearing + 180, sign.distance);
      const snapped = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0);
      
      devices.push({
        id: `road_closure_advance_${idx}_${Date.now()}`,
        device_type: sign.code.startsWith('G') ? 'guide' : 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_closure: sign.distance,
          placement: 'advance_warning',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    });
    
    // === CLOSURE POINT ===
    const closurePos = this.snapToRoadEdge(start_lat, start_lng, roadEdge, 0.5);
    
    devices.push({
      id: `road_closed_sign_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'Road Closed',
      device_code: 'R2-1',
      position_lat: closurePos.lat,
      position_lng: closurePos.lng,
      properties: {
        distance_from_workzone: 0,
        placement: 'closure_point',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // Barrier at closure
    devices.push({
      id: `closure_barrier_${Date.now()}`,
      device_type: 'barrier',
      device_name: 'Water Filled Barrier',
      device_code: 'Barrier',
      position_lat: closurePos.lat,
      position_lng: closurePos.lng,
      properties: {
        placement: 'closure_barrier',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ Road Closure TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Stop-Slow TGS with Traffic Controllers
   */
  placeStopSlowTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === STOP-SLOW TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    const isLowSpeed = speedLimit <= 70;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // === ADVANCE WARNING ===
    const advanceSequence = isLowSpeed ? [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 195 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 145 },
      { code: 'T1-2', name: 'Prepare to Stop', distance: 130 },
      { code: 'T1-2', name: 'Prepare to Stop', distance: 60 }
    ] : [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 400 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 320 },
      { code: 'T1-2', name: 'Prepare to Stop', distance: 240 },
      { code: 'T1-2', name: 'Prepare to Stop', distance: 80 }
    ];
    
    advanceSequence.forEach((sign, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, bearing + 180, sign.distance);
      const snapped = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0);
      
      devices.push({
        id: `stop_slow_advance_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_workzone: sign.distance,
          placement: 'advance_warning',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    });
    
    // === SPEED REDUCTION ===
    const reducedSpeed = isLowSpeed ? 40 : 60;
    const speedDistance = isLowSpeed ? 45 : 60;
    const speedPos = this.calculatePosition(start_lat, start_lng, bearing + 180, speedDistance);
    const speedSnapped = this.snapToRoadEdge(speedPos.lat, speedPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `stop_slow_speed_${Date.now()}`,
      device_type: 'regulatory',
      device_name: `Speed Limit ${reducedSpeed}`,
      device_code: 'R4-1',
      position_lat: speedSnapped.lat,
      position_lng: speedSnapped.lng,
      properties: {
        distance_from_workzone: speedDistance,
        placement: 'speed_reduction',
        speed_value: reducedSpeed,
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // === TRAFFIC CONTROLLER POSITION ===
    const tcDistance = isLowSpeed ? 15 : 20;
    const tcPos = this.calculatePosition(start_lat, start_lng, bearing + 180, tcDistance);
    const tcSnapped = this.snapToRoadEdge(tcPos.lat, tcPos.lng, roadEdge, 2.0);
    
    devices.push({
      id: `tc_position_${Date.now()}`,
      device_type: 'tc_position',
      device_name: 'Stop Here When Directed',
      device_code: 'TC',
      position_lat: tcSnapped.lat,
      position_lng: tcSnapped.lng,
      properties: {
        distance_from_workzone: tcDistance,
        placement: 'traffic_controller',
        requires_tc: true,
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ Stop-Slow TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Shoulder Work TGS
   */
  placeShoulderWorkTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === SHOULDER WORK TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    const isLowSpeed = speedLimit <= 70;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // Simplified shoulder work - just warning signs and delineation
    const warnings = [
      { code: 'T1-1', name: 'Road Work Ahead', distance: isLowSpeed ? 100 : 200 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: isLowSpeed ? 50 : 100 }
    ];
    
    warnings.forEach((sign, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, bearing + 180, sign.distance);
      const snapped = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0);
      
      devices.push({
        id: `shoulder_warning_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_workzone: sign.distance,
          placement: 'advance_warning',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    });
    
    // Shoulder delineation
    const workzoneLength = this.calculateDistance(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng) || 30;
    const numCones = Math.max(5, Math.floor(workzoneLength / 5));
    
    for (let i = 0; i <= numCones; i++) {
      const distanceAlong = (i / numCones) * workzoneLength;
      const conePos = this.calculatePosition(start_lat, start_lng, bearing, distanceAlong);
      const coneOffsetPos = this.calculatePosition(conePos.lat, conePos.lng, bearing - 90, 0.5);
      const snapped = this.snapToRoadEdge(coneOffsetPos.lat, coneOffsetPos.lng, roadEdge, 0.3);
      
      devices.push({
        id: `shoulder_cone_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: 'Traffic Cone 700mm',
        device_code: 'TC1',
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_start: distanceAlong,
          placement: 'shoulder_delineation',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    }
    
    console.log(`✅ Shoulder Work TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Footpath Closure TGS
   * For footpath/sidewalk closures with pedestrian management
   */
  placeFootpathClosureTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === FOOTPATH CLOSURE TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // === FOOTPATH CLOSURE SIGNS ===
    // Place at start of closure
    const closureStartPos = this.snapToRoadEdge(start_lat, start_lng, roadEdge, 0.5);
    
    devices.push({
      id: `footpath_closed_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Footpath Closed',
      device_code: 'T5-6',
      position_lat: closureStartPos.lat,
      position_lng: closureStartPos.lng,
      properties: {
        placement: 'footpath_closure_start',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // Advance warning
    const warningPos = this.calculatePosition(start_lat, start_lng, bearing + 180, 20);
    const warningSnapped = this.snapToRoadEdge(warningPos.lat, warningPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `footpath_warning_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Footpath Closed Ahead',
      device_code: 'T5-6',
      position_lat: warningSnapped.lat,
      position_lng: warningSnapped.lng,
      properties: {
        distance_from_closure: 20,
        placement: 'footpath_advance_warning',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // === PEDESTRIAN BARRIERS ===
    const closureLength = this.calculateDistance(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng) || 20;
    const numBarriers = Math.max(3, Math.floor(closureLength / 3));
    
    for (let i = 0; i <= numBarriers; i++) {
      const distanceAlong = (i / numBarriers) * closureLength;
      const barrierPos = this.calculatePosition(start_lat, start_lng, bearing, distanceAlong);
      // Offset to footpath side (right side, 2m from road edge)
      const barrierOffsetPos = this.calculatePosition(barrierPos.lat, barrierPos.lng, bearing + 90, 2.0);
      const snapped = this.snapToRoadEdge(barrierOffsetPos.lat, barrierOffsetPos.lng, roadEdge, 0.5);
      
      devices.push({
        id: `footpath_barrier_${i}_${Date.now()}`,
        device_type: 'barrier',
        device_name: 'Pedestrian Barrier',
        device_code: 'Barrier',
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_start: distanceAlong,
          placement: 'footpath_barrier',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    }
    
    // === END OF CLOSURE SIGN ===
    const endLat = end_lat || start_lat;
    const endLng = end_lng || start_lng;
    const endPos = this.snapToRoadEdge(endLat, endLng, roadEdge, 0.5);
    
    devices.push({
      id: `footpath_end_${Date.now()}`,
      device_type: 'warning',
      device_name: 'End Footpath Closure',
      device_code: 'T5-6',
      position_lat: endPos.lat,
      position_lng: endPos.lng,
      properties: {
        placement: 'footpath_closure_end',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ Footpath Closure TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Roundabout TGS with Side Road Signing
   */
  placeRoundaboutTGS(workZoneData, speedLimit, roadEdgeGeometry, sideStreets = []) {
    console.log('🚧 === ROUNDABOUT TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || 0;
    const isLowSpeed = speedLimit <= 70;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // Advance warnings on all approaches (4 directions for roundabout)
    const approaches = [0, 90, 180, 270]; // N, E, S, W
    const warningDistance = isLowSpeed ? 70 : 160;
    
    approaches.forEach((approachBearing, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, approachBearing, warningDistance);
      const snapped = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0);
      
      devices.push({
        id: `roundabout_warning_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: 'Road Work Ahead',
        device_code: 'T1-1',
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          approach: ['North', 'East', 'South', 'West'][idx],
          distance_from_roundabout: warningDistance,
          placement: 'roundabout_approach',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    });
    
    // Side road signs ("ON SIDE ROAD" requirement)
    if (sideStreets && sideStreets.length > 0) {
      sideStreets.forEach((street, idx) => {
        if (street.lat && street.lng) {
          const sideSignPos = this.calculatePosition(street.lat, street.lng, street.bearing || 0, -30);
          const snapped = this.snapToRoadEdge(sideSignPos.lat, sideSignPos.lng, roadEdge, 1.0);
          
          devices.push({
            id: `side_road_sign_${idx}_${Date.now()}`,
            device_type: 'warning',
            device_name: 'Road Work Ahead (On Side Road)',
            device_code: 'T1-1',
            position_lat: snapped.lat,
            position_lng: snapped.lng,
            properties: {
              side_road: street.name,
              placement: 'on_side_road',
              auto_placed: true,
              tgs_compliant: true
            }
          });
        }
      });
    }
    
    console.log(`✅ Roundabout TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * T-Intersection TGS
   */
  placeTIntersectionTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === T-INTERSECTION TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || 0;
    const isLowSpeed = speedLimit <= 70;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // Warnings on main road approaches
    const mainRoadWarnings = isLowSpeed ? [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 70 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 45 }
    ] : [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 160 },
      { code: 'T1-1', name: 'Road Work Ahead', distance: 80 }
    ];
    
    mainRoadWarnings.forEach((sign, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, bearing + 180, sign.distance);
      const snapped = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0);
      
      devices.push({
        id: `t_int_warning_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_intersection: sign.distance,
          placement: 't_intersection_main',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    });
    
    // Warning on perpendicular road
    const perpPos = this.calculatePosition(start_lat, start_lng, bearing + 90, 50);
    const perpSnapped = this.snapToRoadEdge(perpPos.lat, perpPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `t_int_perp_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Road Work Ahead',
      device_code: 'T1-1',
      position_lat: perpSnapped.lat,
      position_lng: perpSnapped.lng,
      properties: {
        distance_from_intersection: 50,
        placement: 't_intersection_perpendicular',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ T-Intersection TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Court Bowl (Cul-de-sac) Closure TGS
   */
  placeCourtBowlClosureTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === COURT BOWL CLOSURE TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || 0;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // Road Closed sign at entrance
    const closurePos = this.snapToRoadEdge(start_lat, start_lng, roadEdge, 0.5);
    
    devices.push({
      id: `court_bowl_closed_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'Road Closed',
      device_code: 'R2-1',
      position_lat: closurePos.lat,
      position_lng: closurePos.lng,
      properties: {
        placement: 'court_bowl_entrance',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // Local Traffic Only sign
    const localTrafficPos = this.calculatePosition(start_lat, start_lng, bearing + 180, 20);
    const localSnapped = this.snapToRoadEdge(localTrafficPos.lat, localTrafficPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `local_traffic_${Date.now()}`,
      device_type: 'regulatory',
      device_name: 'Local Traffic Only',
      device_code: 'R2-2',
      position_lat: localSnapped.lat,
      position_lng: localSnapped.lng,
      properties: {
        distance_from_closure: 20,
        placement: 'local_traffic_warning',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // Barrier at closure point
    devices.push({
      id: `court_bowl_barrier_${Date.now()}`,
      device_type: 'barrier',
      device_name: 'Water Filled Barrier',
      device_code: 'Barrier',
      position_lat: closurePos.lat,
      position_lng: closurePos.lng,
      properties: {
        placement: 'closure_barrier',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ Court Bowl Closure TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

      position_lng: endPos.lng,
      properties: {
        placement: 'footpath_closure_end',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ Footpath Closure TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Pedestrian Detour TGS
   * For directing pedestrians around work zones (DDA compliant)
   */
  placePedestrianDetourTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === PEDESTRIAN DETOUR TGS (DDA Compliant) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // === DETOUR START SIGNS ===
    const detourStartPos = this.snapToRoadEdge(start_lat, start_lng, roadEdge, 1.5);
    
    devices.push({
      id: `ped_detour_start_${Date.now()}`,
      device_type: 'guide',
      device_name: 'Pedestrian Detour',
      device_code: 'G9-84',
      position_lat: detourStartPos.lat,
      position_lng: detourStartPos.lng,
      properties: {
        placement: 'pedestrian_detour_start',
        auto_placed: true,
        tgs_compliant: true,
        dda_compliant: true
      }
    });
    
    // Advance warning
    const warningPos = this.calculatePosition(start_lat, start_lng, bearing + 180, 15);
    const warningSnapped = this.snapToRoadEdge(warningPos.lat, warningPos.lng, roadEdge, 1.5);
    
    devices.push({
      id: `ped_detour_warning_${Date.now()}`,
      device_type: 'warning',
      device_name: 'Pedestrian Detour Ahead',
      device_code: 'G9-84',
      position_lat: warningSnapped.lat,
      position_lng: warningSnapped.lng,
      properties: {
        distance_from_detour: 15,
        placement: 'pedestrian_detour_advance',
        auto_placed: true,
        tgs_compliant: true,
        dda_compliant: true
      }
    });
    
    // === DETOUR PATH MARKERS ===
    // Create a simple detour path (offset from road)
    const detourLength = this.calculateDistance(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng) || 25;
    const numMarkers = Math.max(3, Math.floor(detourLength / 10));
    
    for (let i = 0; i <= numMarkers; i++) {
      const distanceAlong = (i / numMarkers) * detourLength;
      const markerPos = this.calculatePosition(start_lat, start_lng, bearing, distanceAlong);
      // Offset detour path 3m to the side
      const detourOffsetPos = this.calculatePosition(markerPos.lat, markerPos.lng, bearing + 90, 3.0);
      const snapped = this.snapToRoadEdge(detourOffsetPos.lat, detourOffsetPos.lng, roadEdge, 0.5);
      
      devices.push({
        id: `ped_detour_marker_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: 'Pedestrian Detour Marker',
        device_code: 'Bollard',
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_along_detour: distanceAlong,
          placement: 'pedestrian_detour_path',
          auto_placed: true,
          tgs_compliant: true,
          dda_compliant: true
        }
      });
    }
    
    // === END DETOUR SIGN ===
    const endLat = end_lat || start_lat;
    const endLng = end_lng || start_lng;
    const endPos = this.calculatePosition(endLat, endLng, bearing, 5);
    const endSnapped = this.snapToRoadEdge(endPos.lat, endPos.lng, roadEdge, 1.5);
    
    devices.push({
      id: `ped_detour_end_${Date.now()}`,
      device_type: 'guide',
      device_name: 'End Pedestrian Detour',
      device_code: 'G9-84',
      position_lat: endSnapped.lat,
      position_lng: endSnapped.lng,
      properties: {
        placement: 'pedestrian_detour_end',
        auto_placed: true,
        tgs_compliant: true,
        dda_compliant: true
      }
    });
    
    console.log(`✅ Pedestrian Detour TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  /**
   * Contra Flow TGS
   * For diverting traffic to opposing lane
   */
  placeContraFlowTGS(workZoneData, speedLimit, roadEdgeGeometry) {
    console.log('🚧 === CONTRA FLOW TGS (AS 1742.3) ===');
    
    const devices = [];
    const { start_lat, start_lng, end_lat, end_lng, road_bearing } = workZoneData;
    
    const bearing = road_bearing || this.calculateBearing(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng);
    const isLowSpeed = speedLimit <= 70;
    const roadEdge = this.extractRoadEdgePoints(roadEdgeGeometry);
    
    // === ADVANCE WARNING ===
    const warnings = isLowSpeed ? [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 195 },
      { code: 'T5-32', name: 'Two Way Traffic Ahead', distance: 145 },
      { code: 'T1-25', name: 'Lane Change', distance: 100 }
    ] : [
      { code: 'T1-1', name: 'Road Work Ahead', distance: 400 },
      { code: 'T5-32', name: 'Two Way Traffic Ahead', distance: 320 },
      { code: 'T1-25', name: 'Lane Change', distance: 160 }
    ];
    
    warnings.forEach((sign, idx) => {
      const signPos = this.calculatePosition(start_lat, start_lng, bearing + 180, sign.distance);
      const snapped = this.snapToRoadEdge(signPos.lat, signPos.lng, roadEdge, 1.0);
      
      devices.push({
        id: `contraflow_warning_${idx}_${Date.now()}`,
        device_type: 'warning',
        device_name: sign.name,
        device_code: sign.code,
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_workzone: sign.distance,
          placement: 'contraflow_advance',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    });
    
    // === SPEED REDUCTION ===
    const reducedSpeed = isLowSpeed ? 40 : 60;
    const speedDistance = isLowSpeed ? 60 : 80;
    const speedPos = this.calculatePosition(start_lat, start_lng, bearing + 180, speedDistance);
    const speedSnapped = this.snapToRoadEdge(speedPos.lat, speedPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `contraflow_speed_${Date.now()}`,
      device_type: 'regulatory',
      device_name: `Speed Limit ${reducedSpeed}`,
      device_code: 'R4-1',
      position_lat: speedSnapped.lat,
      position_lng: speedSnapped.lng,
      properties: {
        distance_from_workzone: speedDistance,
        placement: 'speed_reduction',
        speed_value: reducedSpeed,
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    // === DELINEATION FOR CONTRA FLOW SECTION ===
    const contraflowLength = this.calculateDistance(start_lat, start_lng, end_lat || start_lat, end_lng || start_lng) || 50;
    const numDelineators = Math.max(5, Math.floor(contraflowLength / 5));
    
    for (let i = 0; i <= numDelineators; i++) {
      const distanceAlong = (i / numDelineators) * contraflowLength;
      const delinPos = this.calculatePosition(start_lat, start_lng, bearing, distanceAlong);
      // Center line delineation
      const snapped = this.snapToRoadEdge(delinPos.lat, delinPos.lng, roadEdge, 0.3);
      
      devices.push({
        id: `contraflow_delin_${i}_${Date.now()}`,
        device_type: 'delineation',
        device_name: 'Bollard',
        device_code: 'Bollard',
        position_lat: snapped.lat,
        position_lng: snapped.lng,
        properties: {
          distance_from_start: distanceAlong,
          placement: 'contraflow_centerline',
          auto_placed: true,
          tgs_compliant: true
        }
      });
    }
    
    // === END CONTRA FLOW ===
    const endLat = end_lat || start_lat;
    const endLng = end_lng || start_lng;
    const endPos = this.calculatePosition(endLat, endLng, bearing, 20);
    const endSnapped = this.snapToRoadEdge(endPos.lat, endPos.lng, roadEdge, 1.0);
    
    devices.push({
      id: `contraflow_end_${Date.now()}`,
      device_type: 'warning',
      device_name: 'End Two Way Traffic',
      device_code: 'T5-32',
      position_lat: endSnapped.lat,
      position_lng: endSnapped.lng,
      properties: {
        distance_from_end: 20,
        placement: 'contraflow_end',
        auto_placed: true,
        tgs_compliant: true
      }
    });
    
    console.log(`✅ Contra Flow TGS Complete: ${devices.length} devices placed`);
    return devices;
  }

  // ==================== HELPER FUNCTIONS ====================

  /**
   * Get taper configuration based on speed limit
   */
  getTaperConfig(speedLimit) {
    if (speedLimit <= 50) {
      return { length: 15, coneSpacing: 3, numCones: 5 };
    } else if (speedLimit <= 70) {
      return { length: 30, coneSpacing: 5, numCones: 6 };
    } else if (speedLimit <= 90) {
      return { length: 90, coneSpacing: 10, numCones: 9 };
    } else {
      return { length: 145, coneSpacing: 15, numCones: 10 };
    }
  }

  /**
   * Extract road edge points from geometry data
   */
  extractRoadEdgePoints(roadEdgeGeometry) {
    if (!roadEdgeGeometry) return [];
    
    let points = [];
    
    // Handle different geometry formats
    if (roadEdgeGeometry.start && roadEdgeGeometry.start.left_edge) {
      points = [...roadEdgeGeometry.start.left_edge];
    }
    if (roadEdgeGeometry.end && roadEdgeGeometry.end.left_edge) {
      points = [...points, ...roadEdgeGeometry.end.left_edge];
    }
    
    // Normalize to {lat, lng} format
    return points.map(point => {
      if (Array.isArray(point)) {
        return { lat: point[0], lng: point[1] };
      }
      return point;
    }).filter(p => p.lat && p.lng);
  }

  /**
   * Snap a position to the nearest road edge point
   */
  snapToRoadEdge(lat, lng, roadEdgePoints, maxSnapDistance = 5.0) {
    if (!roadEdgePoints || roadEdgePoints.length === 0) {
      return { lat, lng };
    }
    
    let minDist = Infinity;
    let nearestPoint = { lat, lng };
    
    for (const point of roadEdgePoints) {
      const dist = this.calculateDistance(lat, lng, point.lat, point.lng);
      if (dist < minDist) {
        minDist = dist;
        nearestPoint = { lat: point.lat, lng: point.lng };
      }
    }
    
    // Only snap if within reasonable distance
    if (minDist < maxSnapDistance) {
      return nearestPoint;
    }
    
    return { lat, lng };
  }

  /**
   * Calculate new position given bearing and distance
   */
  calculatePosition(lat, lng, bearing, distanceMeters) {
    const R = this.EARTH_RADIUS_M;
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
    const R = this.EARTH_RADIUS_M;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
}

export default new TGSPlacementEngine();
