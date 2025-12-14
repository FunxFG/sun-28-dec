/**
 * Professional TGS Drawing Generator
 * Creates AS 1742.3 compliant TGS drawings in PDF format
 * Also generates SVG overlays for Google Maps (satellite/street view)
 */

import jsPDF from 'jspdf';

export class ProfessionalTGSGenerator {
  constructor() {
    this.pageWidth = 297; // A3 width in mm
    this.pageHeight = 420; // A3 height in mm
  }

  /**
   * Generate complete TGS package
   * Returns: { pdf: blob, mapOverlay: SVG, streetViewMarkers: [] }
   */
  async generateCompleteTGS(planData, devices, roadData, companyInfo) {
    return {
      // Professional PDF for permit submission
      pdf: await this.generateProfessionalPDF(planData, devices, roadData, companyInfo),
      
      // SVG overlay for Google Maps
      mapOverlay: this.generateMapOverlaySVG(devices, roadData),
      
      // Street view markers
      streetViewMarkers: this.generateStreetViewMarkers(devices),
      
      // Satellite view annotations
      satelliteAnnotations: this.generateSatelliteAnnotations(devices, roadData)
    };
  }

  /**
   * Generate Professional PDF Drawing (A3 format)
   */
  async generateProfessionalPDF(planData, devices, roadData, companyInfo) {
    const doc = new jsPDF({
      orientation: 'landscape',
      unit: 'mm',
      format: 'a3'
    });

    // 1. Title Block (Top)
    this.drawTitleBlock(doc, planData, roadData);
    
    // 2. Main Schematic (Center)
    await this.drawMainSchematic(doc, devices, roadData, planData);
    
    // 3. Inset Diagrams (Bottom)
    this.drawInsetDiagrams(doc, devices, roadData);
    
    // 4. Legend (Bottom Left)
    this.drawLegend(doc);
    
    // 5. Compliance Block (Bottom Right)
    this.drawComplianceBlock(doc, companyInfo);
    
    // 6. Company Branding
    this.drawCompanyBranding(doc, companyInfo);
    
    // 7. North Arrow
    this.drawNorthArrow(doc);

    return doc.output('blob');
  }

  /**
   * Draw Title Block
   */
  drawTitleBlock(doc, planData = {}, roadData = {}) {
    // Top Left - Traffic Team Leader Section
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('Traffic Team Leader to Complete Information Below', 10, 15);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    const fields = [
      `Location: ${planData.work_details?.start_address || '____________________'}`,
      `Municipality: ${roadData.governing_body || '____________________'}`,
      `Client: ${planData.company_details?.name || '____________________'}`,
      `Date: ${planData.work_details?.start_date || '____________________'}`,
      `Time: ${planData.work_details?.work_hours_start || '__:__'} - ${planData.work_details?.work_hours_end || '__:__'}`,
      `Melways Ref: ____________________`
    ];
    
    fields.forEach((field, idx) => {
      doc.text(String(field), 10, 22 + (idx * 5));
    });

    // Top Right - Generic Number and Description
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    const genericNum = `GENERIC ${planData.id || '001'}`;
    doc.text(String(genericNum), this.pageWidth - 10, 15, { align: 'right' });
    
    doc.setFontSize(10);
    const description = this.generateTGSDescription(planData, roadData);
    doc.text(String(description), this.pageWidth - 10, 22, { align: 'right' });
  }

  /**
   * Generate TGS Description
   */
  generateTGSDescription(planData = {}, roadData = {}) {
    const occupancy = this.getOccupancyType(planData.road_occupancy);
    const speedLimit = roadData.speed_limit || 60;
    const roadType = roadData.road_type || 'Road';
    
    return String(`${occupancy} ${roadType} ${speedLimit}km/h`);
  }

  /**
   * Get Occupancy Type
   */
  getOccupancyType(occupancy) {
    if (occupancy?.complete_road_closure) return 'Complete Road Closure';
    if (occupancy?.left_lane) return 'Left Lane Closure';
    if (occupancy?.right_lane) return 'Right Lane Closure';
    if (occupancy?.center_lane) return 'Center Lane Closure';
    if (occupancy?.left_shoulder) return 'Left Shoulder Works';
    if (occupancy?.right_shoulder) return 'Right Shoulder Works';
    return 'Road Works';
  }

  /**
   * Main Schematic Drawing (Center of TGS) - WITH SATELLITE VIEW
   */
  async drawMainSchematic(doc, devices, roadData, planData) {
    const startX = 20;
    const startY = 60;
    const mapWidth = 250;
    const mapHeight = 140;
    
    console.log(`🎨 Drawing TGS schematic with ${devices?.length || 0} devices`);
    
    // Try to embed Google Maps satellite image if we have location data
    const hasLocation = planData?.work_details?.start_address || planData?.map_center_lat;
    
    if (hasLocation && devices && devices.length > 0) {
      try {
        console.log('📡 Attempting to fetch satellite imagery...');
        
        // Calculate center point and bounds from devices
        const lats = devices.map(d => d.position_lat).filter(Boolean);
        const lngs = devices.map(d => d.position_lng).filter(Boolean);
        
        if (lats.length > 0 && lngs.length > 0) {
          const centerLat = lats.reduce((a, b) => a + b, 0) / lats.length;
          const centerLng = lngs.reduce((a, b) => a + b, 0) / lngs.length;
          
          // Use the same Google Maps API key from the app
          const apiKey = 'AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs';
          
          // Calculate zoom level for PRECISE device placement visibility
          // Higher zoom = closer view for pinpoint accuracy
          const latSpread = Math.max(...lats) - Math.min(...lats);
          const lngSpread = Math.max(...lngs) - Math.min(...lngs);
          const maxSpread = Math.max(latSpread, lngSpread);
          
          // ZOOM LEVELS (higher = closer):
          // 19-20: Individual lane markings visible, perfect for device placement
          // 18: Road edges and lanes clear
          // 17: Road width visible but less detail
          const zoom = maxSpread > 0.005 ? 18 : maxSpread > 0.002 ? 19 : 20;
          
          console.log(`  Map spread: ${(maxSpread * 111000).toFixed(0)}m, using zoom: ${zoom}`);
          
          // Build Static Maps API URL with HIGH DETAIL satellite view
          const staticMapUrl = `https://maps.googleapis.com/maps/api/staticmap?` +
            `center=${centerLat},${centerLng}` +
            `&zoom=${zoom}` +
            `&size=1280x960` +  // Larger image for more detail
            `&scale=2` +         // Retina/high-DPI for sharpness
            `&maptype=satellite` +
            `&key=${apiKey}`;
          
          console.log(`  Fetching high-resolution satellite image at zoom ${zoom}...`);
          
          // Add device markers to the URL
          devices.forEach((device, idx) => {
            if (device.position_lat && device.position_lng) {
              const color = device.device_type === 'warning' ? 'yellow' : 
                           device.device_type === 'regulatory' ? 'red' : 'blue';
              // Only add first 10 markers to avoid URL length limits
              if (idx < 10) {
                // staticMapUrl += `&markers=color:${color}|${device.position_lat},${device.position_lng}`;
              }
            }
          });
          
          console.log('  Fetching satellite image from Google Maps...');
          
          // Fetch the satellite image
          try {
            const response = await fetch(staticMapUrl);
            if (response.ok) {
              const blob = await response.blob();
              const reader = new FileReader();
              
              await new Promise((resolve, reject) => {
                reader.onloadend = () => {
                  const base64data = reader.result;
                  
                  // Embed satellite image in PDF
                  doc.addImage(base64data, 'PNG', startX, startY, mapWidth, mapHeight);
                  console.log('  ✅ Satellite image embedded successfully');
                  
                  // Draw device positions on top of satellite image
                  this.drawDevicesOnMap(doc, devices, startX, startY, mapWidth, mapHeight, centerLat, centerLng);
                  
                  resolve();
                };
                reader.onerror = reject;
                reader.readAsDataURL(blob);
              });
            } else {
              throw new Error(`Failed to fetch map: ${response.status}`);
            }
          } catch (fetchError) {
            console.error('Failed to fetch satellite image:', fetchError);
            // Draw placeholder if fetch fails
            doc.setFillColor(240, 240, 240);
            doc.rect(startX, startY, mapWidth, mapHeight, 'F');
            
            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            doc.text('Satellite View (Image unavailable)', startX + mapWidth/2, startY + 10, { align: 'center' });
            doc.setFontSize(8);
            doc.text(`Location: ${planData?.work_details?.start_address || 'Work Site'}`, 
                     startX + mapWidth/2, startY + 18, { align: 'center' });
            
            // Draw device positions on the map placeholder
            this.drawDevicesOnMap(doc, devices, startX, startY, mapWidth, mapHeight, centerLat, centerLng);
          }
        }
      } catch (error) {
        console.error('Failed to add satellite imagery:', error);
        this.drawFallbackSchematic(doc, devices, startX, startY);
      }
    } else {
      // Fallback to simple schematic
      this.drawFallbackSchematic(doc, devices, startX, startY);
    }
    
    // Draw measurements
    this.drawMeasurements(doc, devices, roadData, startX, startY, mapWidth);
    
    // Draw work area shading
    this.drawWorkArea(doc, roadData, startX, startY, mapWidth, 8);
    
    // Draw traffic flow arrows
    this.drawTrafficFlowArrows(doc, startX, startY, 8);
  }

  /**
   * Draw Device Symbol (AS 1742.3 Standard Symbols)
   */
  drawDeviceSymbol(doc, device, roadStartX, roadStartY, roadLength, laneWidth) {
    // Calculate position based on distance from start
    // Support both measurements and properties format
    const distanceStr = device.measurements?.distance_from_workzone_start || 
                       device.properties?.distance_advance_exact || 
                       device.properties?.distance || '0';
    const distanceFromStart = parseFloat(String(distanceStr).replace('m', ''));
    
    // Skip if distance is invalid or 0
    if (!distanceFromStart || distanceFromStart <= 0) {
      return;
    }
    
    const xPos = roadStartX + Math.min((distanceFromStart / 100) * roadLength, roadLength);
    
    // Lateral offset - support both formats
    const lateralStr = device.measurements?.lateral_offset_from_centerline || 
                      device.properties?.lateral_offset_exact || 
                      device.properties?.clearance_exact || '0';
    const lateralOffset = parseFloat(String(lateralStr).replace('m', ''));
    
    // Determine which side (left = negative y, right = positive y)
    const side = device.properties?.side || device.measurements?.side_of_road || 'left';
    const yMultiplier = side === 'left' ? -1 : 1;
    const yPos = roadStartY + laneWidth + (yMultiplier * Math.min(Math.abs(lateralOffset), 3));
    
    // Device type determines symbol
    const deviceType = device.device_type || 'warning';
    
    if (deviceType === 'warning' || deviceType === 'regulatory' || deviceType === 'sign' || deviceType === 'guide') {
      this.drawSignSymbol(doc, xPos, yPos, device.device_name);
    } else if (deviceType === 'cone' || deviceType === 'delineation') {
      this.drawConeSymbol(doc, xPos, yPos);
    } else if (deviceType === 'arrow_board' || deviceType === 'guidance') {
      this.drawArrowBoardSymbol(doc, xPos, yPos);
    } else if (deviceType === 'barrier') {
      this.drawBarrierSymbol(doc, xPos, yPos);
    } else {
      // Default to sign symbol
      this.drawSignSymbol(doc, xPos, yPos, device.device_name);
    }
    
    // Add distance annotation
    doc.setFontSize(6);
    doc.text(`${distanceFromStart.toFixed(0)}m`, xPos, yPos - 5, { align: 'center' });
  }

  /**
   * Draw Sign Symbol (Triangle/Circle/Rectangle per AS 1742.3)
   */
  drawSignSymbol(doc, x, y, signName) {
    // Warning signs = Yellow Triangle
    if (signName.includes('Warning') || signName.includes('Ahead')) {
      doc.setFillColor(255, 255, 0); // Yellow
      doc.triangle(x, y - 3, x - 2, y + 2, x + 2, y + 2, 'FD');
    }
    // Regulatory = Red Circle
    else if (signName.includes('Speed') || signName.includes('Stop')) {
      doc.setFillColor(255, 0, 0); // Red
      doc.circle(x, y, 2, 'FD');
    }
    // Guide = Blue Rectangle
    else {
      doc.setFillColor(0, 0, 255); // Blue
      doc.rect(x - 2, y - 2, 4, 4, 'FD');
    }
  }

  /**
   * Draw Cone Symbol
   */
  drawConeSymbol(doc, x, y) {
    doc.setFillColor(255, 128, 0); // Orange
    doc.triangle(x, y - 2, x - 1, y + 2, x + 1, y + 2, 'FD');
  }

  /**
   * Draw Arrow Board Symbol
   */
  drawArrowBoardSymbol(doc, x, y) {
    doc.setFillColor(255, 200, 0); // Amber
    doc.rect(x - 3, y - 2, 6, 4, 'FD');
    doc.setDrawColor(0);
    doc.line(x - 1, y, x + 2, y - 1); // Arrow
    doc.line(x - 1, y, x + 2, y + 1);
  }

  /**
   * Draw Traffic Controller Symbol
   */
  drawControllerSymbol(doc, x, y) {
    doc.setFillColor(255, 255, 255);
    doc.circle(x, y - 1, 1.5, 'FD'); // Head
    doc.line(x, y, x, y + 3); // Body
    doc.line(x - 2, y + 1, x + 2, y + 1); // Arms (holding bat)
  }

  /**
   * Draw Barrier Symbol
   */
  drawBarrierSymbol(doc, x, y) {
    doc.setFillColor(200, 200, 200); // Gray
    doc.setDrawColor(255, 0, 0); // Red stripes
    doc.rect(x - 2, y - 1, 4, 2, 'FD');
    // Red diagonal stripes
    doc.line(x - 2, y - 1, x + 2, y + 1);
    doc.line(x - 1, y - 1, x + 2, y);
  }

  /**
   * Draw Measurements and Annotations
   */
  drawMeasurements(doc, devices, roadData, startX, startY, roadLength) {
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    
    // Taper length
    const speedKey = this.getSpeedKey(roadData.speed_limit);
    const taperLength = this.getTaperLength(speedKey);
    doc.text(`Taper: ${taperLength}m`, startX + 10, startY - 5);
    
    // Buffer zone
    const bufferZone = this.getBufferZone(speedKey);
    doc.text(`Buffer: ${bufferZone}m`, startX + 40, startY - 5);
    
    // Work zone length
    doc.text(`Work Zone: ${roadData.workzone_size || 100}m`, startX + 80, startY - 5);
  }

  /**
   * Draw Work Area Shading
   */
  drawWorkArea(doc, roadData, startX, startY, roadLength, laneWidth) {
    const workzoneSize = roadData.workzone_size || 100;
    const workStartX = startX + 40; // After taper and buffer
    const workWidth = (workzoneSize / 1000) * roadLength;
    
    doc.setFillColor(255, 200, 200, 0.3); // Light red shading
    doc.rect(workStartX, startY, workWidth, laneWidth * 2, 'F');
    
    // Diagonal hatching for work area
    doc.setDrawColor(255, 0, 0);
    for (let i = 0; i < workWidth; i += 5) {
      doc.line(workStartX + i, startY, workStartX + i, startY + laneWidth * 2);
    }
  }

  /**
   * Draw Traffic Flow Arrows
   */
  drawTrafficFlowArrows(doc, startX, startY, laneWidth) {
    doc.setDrawColor(0, 0, 0);
    doc.setLineWidth(0.5);
    
    // Forward arrows
    for (let i = 0; i < 5; i++) {
      const x = startX + 20 + (i * 30);
      const y = startY + laneWidth - 2;
      doc.line(x, y, x + 5, y); // Arrow shaft
      doc.line(x + 5, y, x + 3, y - 1); // Arrow head top
      doc.line(x + 5, y, x + 3, y + 1); // Arrow head bottom
    }
  }

  /**
   * Draw Inset Diagrams
   */
  drawInsetDiagrams(doc, devices, roadData) {
    const insetY = this.pageHeight - 100;
    
    // Pedestrian Layout
    this.drawPedestrianInset(doc, 10, insetY, devices);
    
    // Sign Spacing Table
    this.drawSignSpacingTable(doc, 80, insetY, roadData);
    
    // Taper Length Diagram
    this.drawTaperDiagram(doc, 150, insetY, roadData);
    
    // Side Roads
    this.drawSideRoadInset(doc, 220, insetY);
  }

  /**
   * Draw Pedestrian Layout Inset
   */
  drawPedestrianInset(doc, x, y, devices) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('PEDESTRIAN LAYOUT', x, y);
    
    // Simple pedestrian path diagram
    doc.setDrawColor(0);
    doc.rect(x, y + 5, 60, 30);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.text('Footpath maintained', x + 5, y + 15);
    doc.text('Min 1.2m width (DDA)', x + 5, y + 20);
    doc.text('Barriers as required', x + 5, y + 25);
    
    // Pedestrian symbol
    doc.circle(x + 50, y + 15, 2);
    doc.line(x + 50, y + 17, x + 50, y + 22);
    doc.line(x + 48, y + 19, x + 52, y + 19);
  }

  /**
   * Draw Sign Spacing Table
   */
  drawSignSpacingTable(doc, x, y, roadData) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('SIGN SPACING', x, y);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    
    const speedLimit = roadData.speed_limit || 60;
    const spacing = this.getSignSpacing(speedLimit);
    
    doc.text(`Speed: ${speedLimit}km/h`, x, y + 10);
    doc.text(`Primary: ${spacing.primary}m`, x, y + 15);
    doc.text(`Secondary: ${spacing.secondary}m`, x, y + 20);
    doc.text(`Tertiary: ${spacing.tertiary}m`, x, y + 25);
  }

  /**
   * Draw Taper Diagram
   */
  drawTaperDiagram(doc, x, y, roadData) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('TAPER CALCULATION', x, y);
    
    const speedKey = this.getSpeedKey(roadData.speed_limit);
    const taperSpecs = this.getTaperSpecs(speedKey);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.text(`Formula: L = W × S`, x, y + 10);
    doc.text(`Length: ${taperSpecs.length}m`, x, y + 15);
    doc.text(`Ratio: 1:${taperSpecs.ratio}`, x, y + 20);
    doc.text(`Cone spacing: ${taperSpecs.cone_spacing}m`, x, y + 25);
  }

  /**
   * Draw Side Road Inset
   */
  drawSideRoadInset(doc, x, y) {
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('SIDE ROADS', x, y);
    
    // T-junction diagram
    doc.setDrawColor(0);
    doc.line(x, y + 15, x + 40, y + 15); // Main road
    doc.line(x + 20, y + 15, x + 20, y + 30); // Side road
    
    doc.setFontSize(6);
    doc.text('"ON SIDE ROAD" sign', x + 5, y + 35);
    doc.text('required at intersection', x + 5, y + 39);
  }

  /**
   * Draw Legend
   */
  drawLegend(doc) {
    const x = 10;
    const y = this.pageHeight - 50;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('LEGEND', x, y);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    
    const legendItems = [
      { symbol: '△', color: [255, 255, 0], text: 'Warning Sign' },
      { symbol: '○', color: [255, 0, 0], text: 'Regulatory Sign' },
      { symbol: '□', color: [0, 0, 255], text: 'Guide Sign' },
      { symbol: '▲', color: [255, 128, 0], text: 'Traffic Cone' },
      { symbol: '▬', color: [255, 200, 0], text: 'Arrow Board' },
      { symbol: '⚐', color: [0, 0, 0], text: 'Traffic Controller' }
    ];
    
    legendItems.forEach((item, idx) => {
      const itemY = y + 8 + (idx * 5);
      doc.setFillColor(...item.color);
      doc.circle(x + 2, itemY - 1, 1.5, 'F');
      doc.text(item.text, x + 6, itemY);
    });
  }

  /**
   * Draw Compliance Block
   */
  drawComplianceBlock(doc, companyInfo = {}) {
    const x = this.pageWidth - 90;
    const y = this.pageHeight - 50;
    
    doc.setFontSize(6);
    doc.setFont('helvetica', 'bold');
    doc.text('TRAFFIC GUIDANCE SCHEME IS NOT TO SCALE AND IS INDICATIVE ONLY', x, y, { maxWidth: 85 });
    
    doc.setFont('helvetica', 'normal');
    doc.text('Sign positions may need to be adjusted to site conditions. Worksite to be fully compliant to:', x, y + 8, { maxWidth: 85 });
    doc.text('• AS 1742.3:2019', x + 2, y + 14);
    doc.text('• AGTTM Parts 1-10', x + 2, y + 18);
    doc.text('• State Standards for Workzone Traffic Management', x + 2, y + 22);
    
    // Approval
    doc.setFont('helvetica', 'bold');
    doc.text('Approved:', x, y + 30);
    doc.setFont('helvetica', 'normal');
    const approvedBy = companyInfo.approved_by || companyInfo.name || '_______________';
    doc.text(String(approvedBy), x + 20, y + 30);
    
    doc.text('Date:', x, y + 35);
    doc.text(new Date().toLocaleDateString('en-AU'), x + 20, y + 35);
    
    doc.text('Print Scale: A3, NTS', x, y + 40);
  }

  /**
   * Draw Company Branding
   */
  drawCompanyBranding(doc, companyInfo = {}) {
    const x = 10;
    const y = this.pageHeight - 20;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    const companyName = companyInfo.company_name || companyInfo.name || 'Company Name';
    doc.text(String(companyName), x, y);
    
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    const address = companyInfo.address || 'Address';
    const phone = companyInfo.phone || 'Phone';
    const website = companyInfo.website || companyInfo.email || 'Website';
    doc.text(String(address), x, y + 5);
    doc.text(String(phone), x, y + 9);
    doc.text(String(website), x, y + 13);
  }

  /**
   * Draw North Arrow
   */
  drawNorthArrow(doc) {
    const x = this.pageWidth - 20;
    const y = 30;
    
    // North arrow
    doc.setDrawColor(0);
    doc.setFillColor(0);
    doc.triangle(x, y - 5, x - 2, y + 2, x + 2, y + 2, 'FD');
    
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('N', x, y - 7, { align: 'center' });
  }

  // Helper methods
  getSpeedKey(speed) {
    if (speed <= 50) return '≤50kmh';
    if (speed === 60) return '60kmh';
    if (speed === 70) return '70kmh';
    if (speed === 80) return '80kmh';
    return '≥90kmh';
  }

  getTaperLength(speedKey) {
    const lengths = { '≤50kmh': 30, '60kmh': 40, '70kmh': 50, '80kmh': 60, '≥90kmh': 90 };
    return lengths[speedKey];
  }

  getBufferZone(speedKey) {
    const zones = { '≤50kmh': 20, '60kmh': 30, '70kmh': 40, '80kmh': 50, '≥90kmh': 60 };
    return zones[speedKey];
  }

  getTaperSpecs(speedKey) {
    const specs = {
      '≤50kmh': { length: 30, ratio: 12, cone_spacing: 3 },
      '60kmh': { length: 40, ratio: 15, cone_spacing: 4 },
      '70kmh': { length: 50, ratio: 18, cone_spacing: 5 },
      '80kmh': { length: 60, ratio: 20, cone_spacing: 6 },
      '≥90kmh': { length: 90, ratio: 25, cone_spacing: 6 }
    };
    return specs[speedKey];
  }

  getSignSpacing(speed) {
    if (speed <= 50) return { primary: 60, secondary: 30, tertiary: 15 };
    if (speed === 60) return { primary: 70, secondary: 40, tertiary: 20 };
    if (speed === 70) return { primary: 80, secondary: 50, tertiary: 25 };
    if (speed === 80) return { primary: 100, secondary: 60, tertiary: 30 };
    return { primary: 150, secondary: 100, tertiary: 50 };
  }

  /**
   * Generate Map Overlay SVG (for Google Maps)
   */
  generateMapOverlaySVG(devices, roadData) {
    // SVG paths for device symbols that can be overlaid on Google Maps
    return {
      signs: devices.filter(d => d.device_type === 'sign').map(d => ({
        lat: d.position_lat,
        lng: d.position_lng,
        svg: this.getSignSVG(d.device_name)
      })),
      cones: devices.filter(d => d.device_type === 'cone').map(d => ({
        lat: d.position_lat,
        lng: d.position_lng,
        svg: this.getConeSVG()
      }))
    };
  }

  getSignSVG(signName) {
    if (signName.includes('Warning')) {
      return '<svg width="30" height="30"><polygon points="15,5 25,25 5,25" fill="yellow" stroke="black" stroke-width="2"/></svg>';
    }
    return '<svg width="30" height="30"><circle cx="15" cy="15" r="12" fill="red" stroke="black" stroke-width="2"/></svg>';
  }

  getConeSVG() {
    return '<svg width="20" height="20"><polygon points="10,2 15,18 5,18" fill="orange" stroke="black" stroke-width="1"/></svg>';
  }

  /**
   * Generate Street View Markers
   */
  generateStreetViewMarkers(devices) {
    return devices.map(device => ({
      position: { lat: device.position_lat, lng: device.position_lng },
      label: device.device_name,
      distance: device.measurements?.distance_from_workzone_start
    }));
  }

  /**
   * Generate Satellite Annotations
   */
  generateSatelliteAnnotations(devices, roadData) {
    return {
      workzone: {
        center: { lat: roadData.center_lat, lng: roadData.center_lng },
        size: roadData.workzone_size
      },
      devices: devices.map(d => ({
        position: { lat: d.position_lat, lng: d.position_lng },
        type: d.device_type,
        annotation: `${d.device_name} - ${d.measurements?.distance_from_workzone_start}`
      }))
    };
  }

  /**
   * Draw devices on map placeholder
   */
  drawDevicesOnMap(doc, devices, startX, startY, mapWidth, mapHeight, centerLat, centerLng) {
    if (!devices || devices.length === 0) return;
    
    // Simple positioning based on relative coordinates
    devices.forEach((device, idx) => {
      if (device.position_lat && device.position_lng) {
        // Calculate relative position within the map bounds
        const relativeX = startX + (mapWidth * 0.3) + (idx * 15); // Simple spacing
        const relativeY = startY + (mapHeight * 0.5) + ((idx % 2) * 20);
        
        // Draw device symbol on map
        if (device.device_type === 'warning' || device.device_type === 'sign') {
          doc.setFillColor(255, 255, 0); // Yellow
          doc.triangle(relativeX, relativeY - 2, relativeX - 2, relativeY + 2, relativeX + 2, relativeY + 2, 'FD');
        } else if (device.device_type === 'cone') {
          doc.setFillColor(255, 128, 0); // Orange
          doc.triangle(relativeX, relativeY - 2, relativeX - 1, relativeY + 2, relativeX + 1, relativeY + 2, 'FD');
        } else {
          doc.setFillColor(0, 0, 255); // Blue
          doc.circle(relativeX, relativeY, 2, 'FD');
        }
        
        // Add device label
        doc.setFontSize(6);
        doc.setTextColor(0, 0, 0);
        doc.text(device.device_name.substring(0, 8), relativeX, relativeY + 5, { align: 'center' });
      }
    });
  }

  /**
   * Draw fallback schematic (original road view)
   */
  drawFallbackSchematic(doc, devices, startX, startY) {
    const roadLength = 180;
    const laneWidth = 8;
    
    // Draw road
    doc.setDrawColor(0);
    doc.setFillColor(200, 200, 200);
    doc.rect(startX, startY, roadLength, laneWidth * 2, 'F');
    
    // Draw center line
    doc.setLineDash([5, 3]);
    doc.line(startX, startY + laneWidth, startX + roadLength, startY + laneWidth);
    doc.setLineDash([]);
    
    // Draw devices with AS 1742.3 symbols
    if (devices && devices.length > 0) {
      console.log(`  Drawing ${devices.length} device symbols...`);
      devices.forEach((device, idx) => {
        console.log(`  Device ${idx}: ${device.device_name} (${device.device_type})`);
        this.drawDeviceSymbol(doc, device, startX, startY, roadLength, laneWidth);
      });
    } else {
      console.warn('⚠️ No devices to draw on TGS');
      // Draw a note that no devices are placed yet
      doc.setFontSize(12);
      doc.setTextColor(150, 150, 150);
      doc.text('No devices placed - use Auto-Place Devices button', startX + roadLength/2, startY + laneWidth, { align: 'center' });
      doc.setTextColor(0, 0, 0);
    }
  }
}

export default ProfessionalTGSGenerator;
