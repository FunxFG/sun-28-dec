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
  generateCompleteTGS(planData, devices, roadData, companyInfo) {
    return {
      // Professional PDF for permit submission
      pdf: this.generateProfessionalPDF(planData, devices, roadData, companyInfo),
      
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
  generateProfessionalPDF(planData, devices, roadData, companyInfo) {
    const doc = new jsPDF({
      orientation: 'landscape',
      unit: 'mm',
      format: 'a3'
    });

    // 1. Title Block (Top)
    this.drawTitleBlock(doc, planData, roadData);
    
    // 2. Main Schematic (Center)
    this.drawMainSchematic(doc, devices, roadData);
    
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
  drawTitleBlock(doc, planData, roadData) {
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
      doc.text(field, 10, 22 + (idx * 5));
    });

    // Top Right - Generic Number and Description
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    const genericNum = `GENERIC ${planData.id || '001'}`;
    doc.text(genericNum, this.pageWidth - 10, 15, { align: 'right' });
    
    doc.setFontSize(10);
    const description = this.generateTGSDescription(planData, roadData);
    doc.text(description, this.pageWidth - 10, 22, { align: 'right' });
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
   * Draw Main Schematic (Bird's Eye View)
   */
  drawMainSchematic(doc, devices, roadData) {
    const startX = 80;
    const startY = 60;
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
    devices.forEach(device => {
      this.drawDeviceSymbol(doc, device, startX, startY, roadLength, laneWidth);
    });
    
    // Draw measurements
    this.drawMeasurements(doc, devices, roadData, startX, startY, roadLength);
    
    // Draw work area shading
    this.drawWorkArea(doc, roadData, startX, startY, roadLength, laneWidth);
    
    // Draw traffic flow arrows
    this.drawTrafficFlowArrows(doc, startX, startY, laneWidth);
  }

  /**
   * Draw Device Symbol (AS 1742.3 Standard Symbols)
   */
  drawDeviceSymbol(doc, device, roadStartX, roadStartY, roadLength, laneWidth) {
    // Calculate position based on distance from start
    const distanceFromStart = parseFloat(device.measurements?.distance_from_workzone_start || 0);
    const xPos = roadStartX + (distanceFromStart / 1000) * roadLength;
    
    // Lateral offset
    const lateralOffset = parseFloat(device.measurements?.lateral_offset_from_centerline || 0);
    const yPos = roadStartY + laneWidth + (lateralOffset / 10) * laneWidth;
    
    // Device type determines symbol
    if (device.device_type === 'sign') {
      this.drawSignSymbol(doc, xPos, yPos, device.device_name);
    } else if (device.device_type === 'cone') {
      this.drawConeSymbol(doc, xPos, yPos);
    } else if (device.device_type === 'arrow_board') {
      this.drawArrowBoardSymbol(doc, xPos, yPos);
    } else if (device.device_type === 'controller') {
      this.drawControllerSymbol(doc, xPos, yPos);
    }
    
    // Add distance annotation
    doc.setFontSize(6);
    doc.text(`${distanceFromStart.toFixed(0)}m`, xPos, yPos - 3, { align: 'center' });
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
}

export default ProfessionalTGSGenerator;
