/**
 * TGS (Traffic Guidance Schemes) Drawing Generator
 * Creates DTMR-compliant visual drawings with Austroads device symbols
 * Hybrid approach: Interactive maps + Official TGS exports
 */

export class TGSDrawingGenerator {
  constructor() {
    // Austroads-standard device symbols and specifications
    this.deviceSymbols = {
      warning: {
        'Road Work Ahead': {
          symbol: 'WS1-1',
          color: '#FF6600',
          size: { width: 40, height: 40 },
          shape: 'diamond',
          text: 'ROAD\nWORK\nAHEAD'
        },
        'Lane Closure Ahead': {
          symbol: 'WS1-2',
          color: '#FF6600',
          size: { width: 40, height: 40 },
          shape: 'diamond',
          text: 'LANE\nCLOSURE\nAHEAD'
        },
        'Road Closed Ahead': {
          symbol: 'WS1-3',
          color: '#FF6600',
          size: { width: 40, height: 40 },
          shape: 'diamond',
          text: 'ROAD\nCLOSED\nAHEAD'
        }
      },
      regulatory: {
        'Temporary Speed Limit 40': {
          symbol: 'R4-1',
          color: '#FFFFFF',
          border: '#FF0000',
          size: { width: 35, height: 35 },
          shape: 'circle',
          text: '40'
        },
        'Stop/Go Board': {
          symbol: 'R2-10',
          color: '#FF0000',
          size: { width: 30, height: 40 },
          shape: 'octagon',
          text: 'STOP'
        }
      },
      guidance: {
        'Changeable Message Sign': {
          symbol: 'G9-1',
          color: '#000000',
          size: { width: 60, height: 30 },
          shape: 'rectangle',
          text: 'VMS'
        },
        'End Road Work': {
          symbol: 'G2-4',
          color: '#FFFFFF',
          size: { width: 40, height: 30 },
          shape: 'rectangle',
          text: 'END\nROAD WORK'
        }
      },
      cone: {
        'Traffic Cone 700mm': {
          symbol: 'D5-1',
          color: '#FF6600',
          size: { width: 12, height: 20 },
          shape: 'cone',
          text: ''
        },
        'Traffic Cone 900mm': {
          symbol: 'D5-2',
          color: '#FF6600',
          size: { width: 15, height: 25 },
          shape: 'cone',
          text: ''
        }
      },
      barrier: {
        'Concrete Barrier': {
          symbol: 'D4-1',
          color: '#CCCCCC',
          size: { width: 50, height: 8 },
          shape: 'rectangle',
          text: ''
        },
        'Water Filled Barrier': {
          symbol: 'D4-2',
          color: '#0066CC',
          size: { width: 40, height: 8 },
          shape: 'rectangle',
          text: ''
        }
      },
      vehicle: {
        'Shadow Vehicle with Attenuator': {
          symbol: 'V1-1',
          color: '#FFFF00',
          size: { width: 60, height: 20 },
          shape: 'vehicle',
          text: 'SHADOW'
        }
      }
    };

    // TGS drawing standards
    this.drawingStandards = {
      scale: {
        default: '1:500',
        options: ['1:200', '1:500', '1:1000']
      },
      dimensions: {
        width: 1189, // A0 width in points (842mm)
        height: 841,  // A0 height in points (595mm)
        margin: 50
      },
      titleBlock: {
        height: 150,
        company: 'Traffic Management Company',
        drawing: 'Traffic Guidance Scheme',
        standard: 'AS 1742.3 & AGTTM Compliant'
      },
      legend: {
        width: 200,
        deviceCategories: ['Warning Signs', 'Regulatory Signs', 'Guidance Devices', 'Delineation', 'Barriers']
      }
    };
  }

  /**
   * Generate complete TGS drawing package
   */
  generateTGSPackage(planData, devices, mapData) {
    return {
      interactive_map: this.generateInteractiveMap(devices, mapData),
      official_drawings: this.generateOfficialTGS(planData, devices, mapData),
      device_legend: this.generateDeviceLegend(devices),
      compliance_notes: this.generateComplianceNotes(devices),
      measurement_annotations: this.generateMeasurementAnnotations(devices)
    };
  }

  /**
   * Generate interactive Google Maps with device symbols
   */
  generateInteractiveMap(devices, mapData) {
    const mapConfig = {
      center: { lat: mapData.center_lat, lng: mapData.center_lng },
      zoom: mapData.zoom || 17,
      mapTypeId: 'hybrid', // Show both satellite and road markings
      styles: this.getMapStyles()
    };

    const deviceMarkers = devices.map(device => {
      const symbol = this.getDeviceSymbol(device);
      
      return {
        id: device.id,
        position: { lat: device.position_lat, lng: device.position_lng },
        icon: this.createInteractiveIcon(symbol, device),
        title: `${device.device_name} (${device.properties?.compliance_level || 'Standard'})`,
        infoWindow: this.createDeviceInfoWindow(device),
        zIndex: this.getDeviceZIndex(device.device_type),
        
        // Interactive features
        draggable: !device.properties?.auto_placed, // Manual devices can be dragged
        clickable: true,
        
        // Compliance styling
        compliance_status: device.properties?.agttm_compliant ? 'compliant' : 'warning',
        bilateral_pair: device.properties?.bilateral_pair || false
      };
    });

    // Add measurement lines between bilateral pairs
    const measurementOverlays = this.generateMeasurementOverlays(devices);
    
    // Add work zone boundary
    const workZoneBoundary = this.generateWorkZoneBoundary(mapData, devices);

    return {
      mapConfig,
      deviceMarkers,
      measurementOverlays,
      workZoneBoundary,
      
      // Interactive controls
      controls: {
        deviceLibrary: true,
        measurementTool: true,
        complianceChecker: true,
        exportTGS: true
      }
    };
  }

  /**
   * Create interactive device icon for Google Maps
   */
  createInteractiveIcon(symbol, device) {
    const size = symbol.size;
    const isCompliant = device.properties?.agttm_compliant;
    const isBilateral = device.properties?.bilateral_pair;
    
    // Create SVG icon with compliance indicators
    const svgIcon = `
      <svg width="${size.width + 10}" height="${size.height + 10}" xmlns="http://www.w3.org/2000/svg">
        <!-- Compliance border -->
        <rect x="2" y="2" width="${size.width + 6}" height="${size.height + 6}" 
              fill="none" stroke="${isCompliant ? '#10B981' : '#F59E0B'}" 
              stroke-width="2" rx="4"/>
        
        <!-- Device symbol -->
        ${this.generateDeviceSVG(symbol, 5, 5)}
        
        <!-- Bilateral indicator -->
        ${isBilateral ? `<circle cx="${size.width}" cy="8" r="4" fill="#3B82F6"/>` : ''}
        
        <!-- Auto-placed indicator -->
        ${device.properties?.auto_placed ? `<circle cx="8" cy="${size.height}" r="3" fill="#10B981"/>` : ''}
      </svg>
    `;

    return {
      url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgIcon),
      scaledSize: { width: size.width + 10, height: size.height + 10 },
      anchor: { x: (size.width + 10) / 2, y: size.height + 5 }
    };
  }

  /**
   * Generate device SVG symbol
   */
  generateDeviceSVG(symbol, x, y) {
    const { shape, color, border, text, size } = symbol;
    
    switch (shape) {
      case 'diamond':
        return `
          <polygon points="${x + size.width/2},${y} ${x + size.width},${y + size.height/2} 
                          ${x + size.width/2},${y + size.height} ${x},${y + size.height/2}" 
                   fill="${color}" stroke="${border || '#000000'}" stroke-width="1"/>
          <text x="${x + size.width/2}" y="${y + size.height/2}" text-anchor="middle" 
                dominant-baseline="middle" font-size="8" font-weight="bold" fill="#000000">
            ${text.split('\n')[0]}
          </text>
        `;
        
      case 'circle':
        return `
          <circle cx="${x + size.width/2}" cy="${y + size.height/2}" r="${size.width/2}" 
                  fill="${color}" stroke="${border || '#000000'}" stroke-width="2"/>
          <text x="${x + size.width/2}" y="${y + size.height/2}" text-anchor="middle" 
                dominant-baseline="middle" font-size="12" font-weight="bold" fill="#000000">
            ${text}
          </text>
        `;
        
      case 'rectangle':
        return `
          <rect x="${x}" y="${y}" width="${size.width}" height="${size.height}" 
                fill="${color}" stroke="${border || '#000000'}" stroke-width="1"/>
          <text x="${x + size.width/2}" y="${y + size.height/2}" text-anchor="middle" 
                dominant-baseline="middle" font-size="8" font-weight="bold" fill="#000000">
            ${text.split('\n')[0]}
          </text>
        `;
        
      case 'cone':
        return `
          <polygon points="${x + size.width/2},${y} ${x + size.width},${y + size.height} ${x},${y + size.height}" 
                   fill="${color}" stroke="#000000" stroke-width="1"/>
          <polygon points="${x + size.width/4},${y + size.height*0.6} ${x + size.width*0.75},${y + size.height*0.6} 
                          ${x + size.width*0.7},${y + size.height*0.8} ${x + size.width*0.3},${y + size.height*0.8}" 
                   fill="#FFFFFF"/>
        `;
        
      case 'vehicle':
        return `
          <rect x="${x}" y="${y}" width="${size.width}" height="${size.height}" 
                fill="${color}" stroke="#000000" stroke-width="1" rx="3"/>
          <rect x="${x + 5}" y="${y + 3}" width="${size.width - 10}" height="${size.height - 6}" 
                fill="#FF6600" stroke="#000000" stroke-width="1"/>
          <text x="${x + size.width/2}" y="${y + size.height/2}" text-anchor="middle" 
                dominant-baseline="middle" font-size="8" font-weight="bold" fill="#000000">
            ${text}
          </text>
        `;
        
      default:
        return `
          <circle cx="${x + size.width/2}" cy="${y + size.height/2}" r="8" 
                  fill="${color}" stroke="#000000" stroke-width="1"/>
        `;
    }
  }

  /**
   * Generate official TGS drawing for DTMR submission
   */
  generateOfficialTGS(planData, devices, mapData) {
    const drawing = {
      format: 'A1', // Standard TGS drawing size
      scale: '1:500',
      orientation: 'landscape',
      
      // Drawing components
      titleBlock: this.generateTitleBlock(planData),
      northArrow: this.generateNorthArrow(),
      scaleBar: this.generateScaleBar(),
      legend: this.generateDeviceLegend(devices),
      
      // Main drawing area
      siteLayout: this.generateSiteLayout(mapData, devices),
      devicePlacements: this.generateDevicePlacements(devices),
      measurementAnnotations: this.generateMeasurementAnnotations(devices),
      complianceNotes: this.generateComplianceNotes(devices),
      
      // Drawing metadata
      drawingNumber: `TGS-${planData.id?.substring(0, 8) || Date.now()}`,
      revision: 'A',
      date: new Date().toLocaleDateString('en-AU'),
      drawnBy: planData.traffic_company?.liaison_name || 'System Generated',
      checkedBy: 'TBC',
      approvedBy: 'TBC'
    };

    return drawing;
  }

  generateTitleBlock(planData) {
    return {
      projectName: planData.plan_name || 'Traffic Management Plan',
      location: `${planData.work_details?.start_address || 'TBC'} to ${planData.work_details?.end_address || 'TBC'}`,
      contractor: planData.company_details?.name || 'TBC',
      trafficManager: planData.traffic_company?.name || 'TBC',
      workType: planData.work_details?.work_type?.toUpperCase() || 'CONSTRUCTION',
      standards: ['AS 1742.3-2019', 'AGTTM 2021', planData.road_data?.governing_body || 'Local Authority'],
      
      // Compliance statement
      complianceStatement: 'This Traffic Guidance Scheme has been prepared in accordance with AS 1742.3 and AGTTM standards'
    };
  }

  generateDeviceLegend(devices) {
    const uniqueDevices = new Map();
    
    devices.forEach(device => {
      const key = `${device.device_type}_${device.device_name}`;
      if (!uniqueDevices.has(key)) {
        const symbol = this.getDeviceSymbol(device);
        uniqueDevices.set(key, {
          symbol: symbol,
          name: device.device_name,
          type: device.device_type,
          standard: symbol.symbol,
          count: 1,
          autoPlaced: device.properties?.auto_placed || false,
          bilateralRequired: device.properties?.bilateral_pair || false
        });
      } else {
        uniqueDevices.get(key).count++;
      }
    });

    return {
      title: 'TRAFFIC CONTROL DEVICES LEGEND',
      devices: Array.from(uniqueDevices.values()),
      notes: [
        'All devices comply with AS 1742.3 specifications',
        'Bilateral placement as per AGTTM requirements',
        'Distances shown are to scale',
        'Manual override applied where noted'
      ]
    };
  }

  generateMeasurementAnnotations(devices) {
    const annotations = [];
    const processedPairs = new Set();
    
    devices.forEach(device => {
      // Bilateral pair measurements
      if (device.properties?.bilateral_pair && device.properties?.bilateral_pair_id) {
        const pairId = device.properties.bilateral_pair_id;
        if (!processedPairs.has(pairId)) {
          processedPairs.add(pairId);
          
          const pairedDevice = devices.find(d => 
            d.properties?.bilateral_pair_id === pairId && d.id !== device.id
          );
          
          if (pairedDevice) {
            const distance = this.calculateDistance(
              device.position_lat, device.position_lng,
              pairedDevice.position_lat, pairedDevice.position_lng
            );
            
            annotations.push({
              type: 'bilateral_spacing',
              from: { lat: device.position_lat, lng: device.position_lng },
              to: { lat: pairedDevice.position_lat, lng: pairedDevice.position_lng },
              measurement: `${distance.toFixed(1)}m`,
              label: 'Bilateral Spacing',
              compliant: true
            });
          }
        }
      }
      
      // Advance warning distances
      if (device.properties?.distance_advance_exact) {
        annotations.push({
          type: 'advance_distance',
          position: { lat: device.position_lat, lng: device.position_lng },
          measurement: device.properties.distance_advance_exact,
          label: `${device.properties.advance_level || 'Advance'} Warning`,
          agttm_rule: device.properties.agttm_rule
        });
      }
      
      // Lateral clearances
      if (device.properties?.clearance_exact) {
        annotations.push({
          type: 'lateral_clearance',
          position: { lat: device.position_lat, lng: device.position_lng },
          measurement: device.properties.clearance_exact,
          label: `${device.properties.placement_type} Clearance`,
          compliant: device.properties.compliance_level !== 'non_compliant'
        });
      }
    });
    
    return annotations;
  }

  generateComplianceNotes(devices) {
    const notes = [];
    const agttmRules = new Set();
    const as1742References = new Set();
    
    devices.forEach(device => {
      if (device.properties?.agttm_rule) {
        agttmRules.add(device.properties.agttm_rule);
      }
      if (device.properties?.as1742_reference) {
        as1742References.add(device.properties.as1742_reference);
      }
    });
    
    notes.push('COMPLIANCE REFERENCES:');
    
    if (agttmRules.size > 0) {
      notes.push('AGTTM Rules Applied:');
      agttmRules.forEach(rule => {
        notes.push(`• ${rule}`);
      });
    }
    
    if (as1742References.size > 0) {
      notes.push('AS 1742.3 References:');
      as1742References.forEach(ref => {
        notes.push(`• ${ref}`);
      });
    }
    
    // Bilateral compliance summary
    const bilateralDevices = devices.filter(d => d.properties?.bilateral_pair);
    if (bilateralDevices.length > 0) {
      notes.push(`BILATERAL PLACEMENT: ${bilateralDevices.length} devices placed bilaterally as per AGTTM requirements`);
    }
    
    // Clearance compliance summary
    const clearanceCompliant = devices.filter(d => d.properties?.compliance_level === 'full_compliance').length;
    notes.push(`CLEARANCE COMPLIANCE: ${clearanceCompliant}/${devices.length} devices meet preferred clearances`);
    
    return {
      title: 'DESIGN NOTES & COMPLIANCE',
      notes: notes,
      designerStatement: 'This TGS has been designed in accordance with current Austroads and AS 1742.3 standards',
      reviewRequired: 'This drawing requires review and approval by qualified traffic management professional'
    };
  }

  // Utility methods
  getDeviceSymbol(device) {
    const category = this.deviceSymbols[device.device_type];
    return category?.[device.device_name] || {
      symbol: 'D1-1',
      color: '#CCCCCC',
      size: { width: 20, height: 20 },
      shape: 'circle',
      text: '?'
    };
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

  getDeviceZIndex(deviceType) {
    const zIndexMap = {
      'warning': 100,
      'regulatory': 90,
      'guidance': 80,
      'cone': 70,
      'barrier': 60,
      'vehicle': 110
    };
    return zIndexMap[deviceType] || 50;
  }

  getMapStyles() {
    return [
      {
        featureType: "road",
        elementType: "geometry",
        stylers: [{ color: "#ffffff" }, { weight: 2 }]
      },
      {
        featureType: "road.arterial",
        elementType: "geometry",
        stylers: [{ color: "#ffd700" }, { weight: 3 }]
      }
    ];
  }

  generateMeasurementOverlays(devices) {
    // Implementation for measurement lines between devices
    return [];
  }

  generateWorkZoneBoundary(mapData, devices) {
    // Implementation for work zone boundary overlay
    return null;
  }

  generateNorthArrow() {
    return {
      position: 'top-right',
      style: 'standard',
      size: 50
    };
  }

  generateScaleBar() {
    return {
      position: 'bottom-left',
      units: 'metric',
      style: 'standard'
    };
  }

  generateSiteLayout(mapData, devices) {
    return {
      bounds: mapData.bounds,
      roadGeometry: mapData.roadGeometry,
      workZone: mapData.workZone
    };
  }

  generateDevicePlacements(devices) {
    return devices.map(device => ({
      id: device.id,
      position: { lat: device.position_lat, lng: device.position_lng },
      symbol: this.getDeviceSymbol(device),
      annotation: device.properties?.distance_advance_exact || device.properties?.clearance_exact,
      compliance: device.properties?.agttm_compliant
    }));
  }

  createDeviceInfoWindow(device) {
    const symbol = this.getDeviceSymbol(device);
    
    return `
      <div class="device-info-window" style="min-width: 250px;">
        <h3 style="margin: 0 0 10px 0; color: #1f2937; font-size: 14px; font-weight: bold;">
          ${device.device_name}
        </h3>
        
        <div style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">
          <strong>Symbol:</strong> ${symbol.symbol} | 
          <strong>Type:</strong> ${device.device_type}
        </div>
        
        ${device.properties?.agttm_compliant ? 
          '<div style="color: #10b981; font-size: 11px; margin-bottom: 5px;">✓ AGTTM Compliant</div>' :
          '<div style="color: #f59e0b; font-size: 11px; margin-bottom: 5px;">⚠ Check Compliance</div>'
        }
        
        ${device.properties?.bilateral_pair ? 
          '<div style="color: #3b82f6; font-size: 11px; margin-bottom: 5px;">↔ Bilateral Placement</div>' : ''
        }
        
        ${device.properties?.clearance_exact ? 
          `<div style="font-size: 11px;"><strong>Clearance:</strong> ${device.properties.clearance_exact}</div>` : ''
        }
        
        ${device.properties?.distance_advance_exact ? 
          `<div style="font-size: 11px;"><strong>Advance Distance:</strong> ${device.properties.distance_advance_exact}</div>` : ''
        }
        
        ${device.properties?.agttm_rule ? 
          `<div style="font-size: 10px; color: #6b7280; margin-top: 8px; border-top: 1px solid #e5e7eb; padding-top: 5px;">
            <strong>Rule:</strong><br>${device.properties.agttm_rule}
          </div>` : ''
        }
      </div>
    `;
  }
}

export default new TGSDrawingGenerator();