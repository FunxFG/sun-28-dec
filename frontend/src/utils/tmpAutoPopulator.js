/**
 * TMP Auto-Populator
 * Intelligently fills TMP forms from minimal inputs
 */

export class TMPAutoPopulator {
  constructor() {
    this.templates = this.initializeTemplates();
  }

  /**
   * Auto-populate entire TMP from minimal inputs
   */
  async autoPopulateTMP(minimalInputs, userProfile, roadData) {
    const {
      work_type,
      work_style,
      start_address,
      end_address,
      start_date,
      end_date,
      road_occupancy
    } = minimalInputs;

    // Fetch traffic assessment from API
    const trafficAssessment = await this.fetchTrafficAssessment(start_address, roadData);
    
    // Fetch site assessment from API
    const siteAssessment = await this.fetchSiteAssessment(start_address, roadData);

    // Generate all sections
    const populated = {
      // Company details from user profile
      company_details: this.getCompanyDetails(userProfile),
      traffic_company: this.getTrafficCompanyDetails(userProfile),
      
      // Project overview
      project_overview: this.generateProjectOverview(minimalInputs, roadData),
      
      // Work details with smart defaults
      work_details: await this.generateWorkDetails(minimalInputs, roadData),
      
      // Traffic assessment (FROM API)
      traffic_assessment: trafficAssessment,
      
      // Site assessment (FROM API)
      site_assessment: siteAssessment,
      
      // Emergency contacts from profile + location
      emergency_contacts: await this.generateEmergencyContacts(userProfile, start_address),
      
      // Personnel from user's team
      personnel: this.getPersonnelDetails(userProfile),
      
      // Insurance from profile
      permits_insurance: this.getInsuranceDetails(userProfile),
      
      // Safety plan
      safety_plan: this.generateSafetyPlan(work_type, roadData),
      
      // Environmental based on date + location
      environmental_conditions: await this.generateEnvironmentalConditions(start_address, start_date),
      
      // Safety based on work type
      safety_communications: this.generateSafetyCommunications(work_type, work_style, roadData),
      
      // Implementation plan
      implementation: this.generateImplementationPlan(work_type, roadData),
      
      // Contingency templates
      contingency_plans: this.generateContingencyPlans(work_type, road_occupancy),
      
      // Monitoring
      monitoring: this.generateMonitoring(work_type),
      
      // Management review
      management_review: this.generateManagementReview(),
      
      // Auto-fill approval preparer
      approvals: this.generateApprovals(userProfile),
      
      // Road occupancy and control measures
      road_occupancy: road_occupancy,
      control_measures: this.inferControlMeasures(road_occupancy, work_type)
    };

    return populated;
  }

  /**
   * Fetch Traffic Assessment from Backend API
   */
  async fetchTrafficAssessment(address, roadData) {
    try {
      const lat = roadData.start_coords?.lat || -27.4698;
      const lng = roadData.start_coords?.lng || 153.0251;
      
      const response = await fetch(
        `https://traffix-manager-1.preview.emergentagent.com/api/traffic-assessment?lat=${lat}&lng=${lng}&address=${encodeURIComponent(address)}`
      );
      
      if (response.ok) {
        const data = await response.json();
        console.log('Traffic assessment fetched from API:', data);
        return data;
      }
      
      throw new Error('API call failed');
      
    } catch (error) {
      console.error('Error fetching traffic assessment:', error);
      // Fallback to estimation
      return {
        aadt: roadData.traffic_volume || 15000,
        peak_hour_volume: Math.round((roadData.traffic_volume || 15000) * 0.10),
        '85th_percentile_speed': `${(roadData.speed_limit || 60) + 8} km/h`,
        crash_history: 'Manual assessment required - contact local road authority',
        heavy_vehicle_percentage: '12%',
        assessment_method: 'Estimated based on road classification'
      };
    }
  }

  /**
   * Fetch Site Assessment from Backend API
   */
  async fetchSiteAssessment(address, roadData) {
    try {
      const lat = roadData.start_coords?.lat || -27.4698;
      const lng = roadData.start_coords?.lng || 153.0251;
      
      const response = await fetch(
        `https://traffix-manager-1.preview.emergentagent.com/api/site-assessment?lat=${lat}&lng=${lng}&address=${encodeURIComponent(address)}`
      );
      
      if (response.ok) {
        const data = await response.json();
        console.log('Site assessment fetched from API:', data);
        return data;
      }
      
      throw new Error('API call failed');
      
    } catch (error) {
      console.error('Error fetching site assessment:', error);
      // Fallback to estimation
      return {
        road_geometry: `${roadData.lanes || 2} lanes, 3.5m width each - verify on site`,
        sight_distances: 'Minimum 100m required - verify on site',
        parking_restrictions: 'Verify local parking controls',
        pedestrian_facilities: 'Footpaths present - assess accessibility',
        cyclist_facilities: 'Assess shared road usage',
        public_transport: 'Verify with local transport authority',
        utility_services: 'Dial Before You Dig (1100) required',
        environmental_factors: 'Standard environment - assess noise, dust, heritage'
      };
    }
  }

  /**
   * Generate Project Overview
   */
  generateProjectOverview(minimalInputs, roadData) {
    const { start_address, work_type } = minimalInputs;
    
    return {
      location_description: `${start_address} - ${roadData.road_classification || 'Urban road'}, ${roadData.speed_limit || 60}km/h speed limit`,
      project_purpose: `${work_type} works requiring temporary traffic management per AS 1742.3 and AGTTM standards`,
      site_constraints: 'Traffic volume, pedestrian access, business access - assess on site',
      special_requirements: roadData.road_classification === 'National Highway' ? 'Extended notification period, VMS signs required' : 'Standard traffic management',
      coordinated_by: roadData.governing_body || 'Local Road Authority'
    };
  }

  /**
   * Generate Safety Plan
   */
  generateSafetyPlan(work_type, roadData) {
    return {
      whs_manager: '',
      site_safety_officer: '',
      safety_responsibilities: 'Site supervisor: Overall safety. Traffic controllers: Vehicle/pedestrian management. Workers: Follow WHS procedures.',
      hazard_identification: 'Moving traffic, working near live lanes, night work, adverse weather, underground services',
      risk_controls: 'Hierarchy of controls applied: Eliminate (road closure if possible), Engineering controls (barriers, signage), Administrative (procedures, training), PPE (high-vis, hard hats)',
      emergency_procedures: '1. Secure scene 2. Call 000 if injuries 3. Notify supervisor 4. Document incident 5. Preserve evidence',
      incident_reporting: 'All incidents reported within 24 hours to WHS manager and road authority',
      safety_induction_required: true
    };
  }

  /**
   * Generate Implementation Plan
   */
  generateImplementationPlan(work_type, roadData) {
    const speedLimit = roadData.speed_limit || 60;
    
    return {
      installation_sequence: '1. Install advance warning signs 2. Install taper cones 3. Place work area delineation 4. Position traffic controllers 5. Commence works',
      staging_requirements: 'Progressive installation from upstream to downstream. Remove in reverse order.',
      tgs_drawing_numbers: 'TGS-001 (Main Layout), TGS-002 (Pedestrian Management)',
      device_setup_time: speedLimit >= 80 ? '45 minutes' : '30 minutes',
      removal_sequence: 'Reverse of installation - downstream to upstream',
      handover_procedures: 'Daily handover checklist: Device condition, incidents, variations, upcoming works'
    };
  }

  /**
   * Generate Monitoring Plan
   */
  generateMonitoring(work_type) {
    return {
      daily_inspection_required: true,
      inspection_frequency: work_type === 'construction' ? 'Start and end of each shift' : 'Daily',
      inspection_checklist: 'Device visibility and condition, correct positioning, damage/vandalism, cleanliness, reflectivity, stability',
      defect_rectification: 'Immediate rectification of safety-critical defects. Non-critical within 24 hours. Log all defects.',
      audit_schedule: work_type === 'construction' ? 'Weekly' : 'As required',
      responsible_person: 'Site Supervisor'
    };
  }

  /**
   * Generate Management Review
   */
  generateManagementReview() {
    return {
      review_frequency: 'Monthly or when conditions change',
      review_process: 'Assess effectiveness, incident review, device performance, stakeholder feedback',
      variation_procedures: 'Minor variations: Site supervisor approval. Major variations: New TMP required and submitted to road authority',
      approval_authority: 'Road authority for major variations, Site supervisor for minor',
      record_keeping: 'All TMP records retained for minimum 7 years. Includes inspections, incidents, variations, approvals'
    };
  }

  /**
   * Get company details from user profile
   */
  getCompanyDetails(userProfile) {
    return {
      name: userProfile?.company_name || '',
      address: userProfile?.company_address || '',
      abn: userProfile?.company_abn || '',
      phone: userProfile?.company_phone || '',
      liaison_name: userProfile?.liaison_name || userProfile?.name || '',
      liaison_phone: userProfile?.phone || '',
      liaison_email: userProfile?.email || ''
    };
  }

  /**
   * Get traffic company details (if separate)
   */
  getTrafficCompanyDetails(userProfile) {
    if (userProfile?.traffic_company) {
      return userProfile.traffic_company;
    }
    // Default to same as primary company
    return {
      name: userProfile?.company_name || '',
      address: userProfile?.company_address || '',
      phone: userProfile?.company_phone || '',
      liaison_name: '',
      liaison_phone: '',
      liaison_email: ''
    };
  }

  /**
   * Generate work details with smart defaults
   */
  async generateWorkDetails(minimalInputs, roadData) {
    const { work_type, work_style, start_date, end_date, start_address, end_address } = minimalInputs;
    
    // Determine work hours based on work type
    const { start_time, end_time, night_work, weekend_work } = this.determineWorkHours(work_type, start_date);
    
    return {
      work_type,
      work_style,
      description: this.generateWorkDescription(work_type, work_style, start_address, roadData),
      start_date,
      end_date,
      start_address,
      end_address,
      work_hours_start: start_time,
      work_hours_end: end_time,
      night_work,
      weekend_work
    };
  }

  /**
   * Determine work hours from work type
   */
  determineWorkHours(work_type, start_date) {
    const dayOfWeek = new Date(start_date).getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    
    const schedules = {
      emergency: { start: '00:00', end: '23:59', night: true, weekend: true },
      maintenance: { start: '07:00', end: '17:00', night: false, weekend: isWeekend },
      construction: { start: '07:00', end: '18:00', night: false, weekend: false }
    };
    
    const schedule = schedules[work_type?.toLowerCase()] || schedules.maintenance;
    
    return {
      start_time: schedule.start,
      end_time: schedule.end,
      night_work: schedule.night,
      weekend_work: schedule.weekend
    };
  }

  /**
   * Generate work description
   */
  generateWorkDescription(work_type, work_style, address, roadData) {
    const typeDescriptions = {
      emergency: `Emergency ${work_style} works`,
      maintenance: `Planned maintenance ${work_style} works`,
      construction: `Construction ${work_style} works`
    };
    
    const baseDesc = typeDescriptions[work_type?.toLowerCase()] || 'Road works';
    const location = address.split(',')[0];
    const roadClass = roadData?.road_classification || 'road';
    
    return `${baseDesc} on ${location} (${roadClass}). Traffic management in accordance with AS 1742.3 and AGTTM.`;
  }

  /**
   * Generate emergency contacts from profile and location
   */
  async generateEmergencyContacts(userProfile, address) {
    // Use profile contacts
    const primaryContact = {
      primary_contact_name: userProfile?.emergency_contact_name || userProfile?.name || '',
      primary_contact_phone: userProfile?.emergency_contact_phone || userProfile?.phone || '',
      secondary_contact_name: userProfile?.secondary_contact_name || '',
      secondary_contact_phone: userProfile?.secondary_contact_phone || ''
    };
    
    // Get REAL location-based emergency services using Google Places API
    const emergencyServices = await this.fetchRealEmergencyServices(address);
    
    return {
      ...primaryContact,
      emergency_services_notified: false,
      police_station: emergencyServices.police,
      ambulance_service: emergencyServices.ambulance,
      incident_response_plan: this.generateIncidentResponsePlan()
    };
  }

  /**
   * Fetch REAL emergency services near location using Google Places API (via backend proxy)
   */
  async fetchRealEmergencyServices(address) {
    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
      
      // First geocode the address via backend proxy
      const geocodeResponse = await fetch(
        `${BACKEND_URL}/api/proxy/geocode?address=${encodeURIComponent(address)}`
      );
      const geocodeData = await geocodeResponse.json();
      
      if (!geocodeData.results || geocodeData.results.length === 0) {
        throw new Error('Could not geocode address');
      }
      
      const location = geocodeData.results[0].geometry.location;
      
      // Search for police station via backend proxy
      const policeResponse = await fetch(
        `${BACKEND_URL}/api/proxy/places/nearby?lat=${location.lat}&lng=${location.lng}&radius=10000&place_type=police`
      );
      const policeData = await policeResponse.json();
      
      // Search for hospital/ambulance via backend proxy
      const ambulanceResponse = await fetch(
        `${BACKEND_URL}/api/proxy/places/nearby?lat=${location.lat}&lng=${location.lng}&radius=10000&place_type=hospital`
      );
      const ambulanceData = await ambulanceResponse.json();
      
      // Get place details for phone numbers
      let policeInfo = 'Local Police: 131 444 (non-emergency)';
      let ambulanceInfo = 'Ambulance: 000 (emergency)';
      
      if (policeData.results && policeData.results.length > 0) {
        const nearestPolice = policeData.results[0];
        const detailsResponse = await fetch(
          `${BACKEND_URL}/api/proxy/places/details?place_id=${nearestPolice.place_id}&fields=name,formatted_phone_number,vicinity`
        );
        const details = await detailsResponse.json();
        
        if (details.result) {
          policeInfo = `${details.result.name}: ${details.result.formatted_phone_number || '131 444'} - ${details.result.vicinity}`;
        }
      }
      
      if (ambulanceData.results && ambulanceData.results.length > 0) {
        const nearestHospital = ambulanceData.results[0];
        const detailsResponse = await fetch(
          `${BACKEND_URL}/api/proxy/places/details?place_id=${nearestHospital.place_id}&fields=name,formatted_phone_number,vicinity`
        );
        const details = await detailsResponse.json();
        
        if (details.result) {
          ambulanceInfo = `${details.result.name}: ${details.result.formatted_phone_number || '000'} - ${details.result.vicinity}`;
        }
      }
      
      return {
        police: policeInfo,
        ambulance: ambulanceInfo
      };
      
    } catch (error) {
      console.error('Error fetching emergency services:', error);
      // Fallback to generic
      const state = this.extractState(address);
      return this.getEmergencyServices(state);
    }
  }

  /**
   * Extract state from address
   */
  extractState(address) {
    const states = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT'];
    for (const state of states) {
      if (address.toUpperCase().includes(state)) {
        return state;
      }
    }
    return 'NSW'; // default
  }

  /**
   * Get emergency services by state
   */
  getEmergencyServices(state) {
    return {
      police: `${state} Police: 131 444 (non-emergency)`,
      ambulance: 'Ambulance: 000 (emergency) or local station'
    };
  }

  /**
   * Generate standard incident response plan
   */
  generateIncidentResponsePlan() {
    return `1. Secure the scene and ensure safety of all personnel
2. Call emergency services (000) if injuries or serious incident
3. Notify site supervisor and primary emergency contact immediately
4. Document incident with photos, witness statements, and incident report
5. Preserve evidence and do not move equipment unless safety risk
6. Complete incident report within 24 hours
7. Notify road authority and insurance provider as required`;
  }

  /**
   * Get personnel details from profile
   */
  getPersonnelDetails(userProfile) {
    return {
      site_supervisor_name: userProfile?.supervisor_name || '',
      site_supervisor_phone: userProfile?.supervisor_phone || '',
      site_supervisor_qualifications: userProfile?.supervisor_cert || 'RIIWHS205D',
      traffic_controller_1_name: userProfile?.controller_1_name || '',
      traffic_controller_1_cert: userProfile?.controller_1_cert || '',
      traffic_controller_2_name: userProfile?.controller_2_name || '',
      traffic_controller_2_cert: userProfile?.controller_2_cert || '',
      number_of_workers: '',
      all_personnel_inducted: false
    };
  }

  /**
   * Get insurance details from profile
   */
  getInsuranceDetails(userProfile) {
    return {
      road_occupation_permit_number: '',
      permit_issuing_authority: '',
      permit_issue_date: '',
      permit_expiry_date: '',
      public_liability_insurance: userProfile?.insurance_policy || '',
      insurance_amount: userProfile?.insurance_amount || '$20,000,000',
      insurance_expiry: userProfile?.insurance_expiry || '',
      workers_compensation_policy: userProfile?.workers_comp_policy || ''
    };
  }

  /**
   * Generate environmental conditions using REAL weather API (via backend proxy)
   */
  async generateEnvironmentalConditions(address, date) {
    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
      
      // Get coordinates for the address via backend proxy
      const geocodeResponse = await fetch(
        `${BACKEND_URL}/api/proxy/geocode?address=${encodeURIComponent(address)}`
      );
      const geocodeData = await geocodeResponse.json();
      
      if (!geocodeData.results || geocodeData.results.length === 0) {
        throw new Error('Could not geocode address');
      }
      
      const location = geocodeData.results[0].geometry.location;
      
      // Fetch REAL weather forecast from OpenWeatherMap via backend proxy
      const weatherResponse = await fetch(
        `${BACKEND_URL}/api/proxy/weather/forecast?lat=${location.lat}&lon=${location.lng}`
      );
      const weatherData = await weatherResponse.json();
      
      // Analyze weather data for the work date
      const workDate = new Date(date);
      const relevantForecasts = weatherData.list?.filter(forecast => {
        const forecastDate = new Date(forecast.dt * 1000);
        return forecastDate.toDateString() === workDate.toDateString();
      }) || [];
      
      // Calculate average conditions
      let avgTemp = 0;
      let maxWindSpeed = 0;
      let totalRain = 0;
      let conditions = [];
      
      relevantForecasts.forEach(forecast => {
        avgTemp += forecast.main.temp;
        maxWindSpeed = Math.max(maxWindSpeed, forecast.wind.speed * 3.6); // Convert m/s to km/h
        totalRain += forecast.rain?.['3h'] || 0;
        if (forecast.weather && forecast.weather[0]) {
          conditions.push(forecast.weather[0].main);
        }
      });
      
      if (relevantForecasts.length > 0) {
        avgTemp = Math.round(avgTemp / relevantForecasts.length);
      }
      
      // Generate weather considerations based on REAL data
      const weatherConsiderations = this.generateWeatherConsiderations(avgTemp, maxWindSpeed, totalRain, conditions);
      
      return {
        weather_considerations: weatherConsiderations,
        visibility_requirements: conditions.includes('Fog') || conditions.includes('Mist') ? 
          'Minimum 100m visibility required. Additional lighting and warning signage mandatory due to forecast fog.' :
          'Minimum 100m visibility required. Additional lighting provided for night works.',
        rain_contingency: totalRain > 5 ? 
          `Heavy rain forecast (${totalRain.toFixed(1)}mm expected). Works to be suspended if rainfall exceeds 10mm/hr. Site drainage ensured. All devices secured.` :
          'Works suspended if heavy rain occurs (>10mm/hr). All devices secured. Site made safe. Resume when conditions improve.',
        wind_speed_limit: maxWindSpeed > 40 ? 
          `50 km/h maximum. ALERT: Forecast winds up to ${Math.round(maxWindSpeed)}km/h - monitor closely and suspend if unsafe.` :
          '50 km/h maximum',
        temperature_considerations: this.generateTempConsiderations(avgTemp)
      };
      
    } catch (error) {
      console.error('Error fetching weather data:', error);
      // Fallback to generic conditions
      return {
        weather_considerations: 'Works to be suspended in heavy rain (>10mm/hr), high winds (>50km/h), or poor visibility (<100m)',
        visibility_requirements: 'Minimum 100m visibility required. Additional lighting provided for night works.',
        rain_contingency: 'Works suspended if heavy rain. All devices secured. Site made safe. Resume when conditions improve.',
        wind_speed_limit: '50 km/h maximum',
        temperature_considerations: 'Heat management: Regular breaks, hydration. Cold: Warm clothing, visibility maintained.'
      };
    }
  }

  /**
   * Generate weather considerations from real data
   */
  generateWeatherConsiderations(temp, windSpeed, rain, conditions) {
    let considerations = [];
    
    // Temperature considerations
    if (temp > 35) {
      considerations.push(`High temperature forecast (${temp}°C) - implement heat stress management`);
    } else if (temp < 5) {
      considerations.push(`Cold conditions forecast (${temp}°C) - ensure worker warming facilities`);
    } else {
      considerations.push(`Moderate temperature expected (${temp}°C)`);
    }
    
    // Wind considerations
    if (windSpeed > 40) {
      considerations.push(`Strong winds forecast (up to ${Math.round(windSpeed)}km/h) - secure all devices, monitor continuously`);
    } else if (windSpeed > 25) {
      considerations.push(`Moderate winds expected (${Math.round(windSpeed)}km/h) - ensure signs properly secured`);
    }
    
    // Rain considerations
    if (rain > 5) {
      considerations.push(`Rain forecast (${rain.toFixed(1)}mm expected) - prepare drainage, have wet weather gear ready`);
    }
    
    // Visibility considerations
    if (conditions.includes('Fog') || conditions.includes('Mist')) {
      considerations.push('Fog/mist forecast - additional warning devices and lighting required');
    }
    
    if (conditions.includes('Thunderstorm')) {
      considerations.push('Thunderstorms possible - have evacuation plan ready, suspend works during lightning');
    }
    
    return considerations.length > 0 ? 
      considerations.join('. ') + '. Works to be suspended if conditions unsafe.' :
      'Favorable weather conditions forecast. Standard safety protocols apply.';
  }

  /**
   * Generate temperature considerations
   */
  generateTempConsiderations(temp) {
    if (temp > 35) {
      return `Heat stress protocol: 15min breaks every hour, cool water available, shaded rest area mandatory. Monitor workers for heat exhaustion. Consider rescheduling to cooler hours.`;
    } else if (temp > 30) {
      return `Heat management: Regular breaks, hydration stations, sun protection. Adjust work pace as needed.`;
    } else if (temp < 5) {
      return `Cold weather protocol: Warm clothing layers, hot beverages available, warm-up breaks. Watch for hypothermia signs. High-vis over warm clothing.`;
    } else if (temp < 10) {
      return `Cool conditions: Appropriate warm clothing, regular movement breaks. Ensure high-vis remains visible over layers.`;
    } else {
      return `Moderate temperatures: Standard clothing and break schedule. Hydration and sun protection as needed.`;
    }
  }

  /**
   * Generate safety communications with REAL traffic data
   */
  generateSafetyCommunications(work_type, work_style, roadData) {
    const isHighSpeed = roadData?.speed_limit >= 80;
    const isHighVolume = roadData?.traffic_volume >= 20000;
    const isNationalHighway = roadData?.road_classification === 'National Highway';
    const roadName = roadData?.road_name || 'road';
    
    // Calculate advance warning based on REAL road data
    const advanceWarningDays = this.calculateAdvanceWarningDays(work_type, roadData);
    
    // Determine notification based on ACTUAL road importance
    const notificationMethod = this.getDetailedNotificationMethod(roadData, advanceWarningDays);
    
    return {
      worker_protection_measures: this.getWorkerProtection(work_type, isHighSpeed, roadData),
      ppe_requirements: this.getPPERequirements(work_type, roadData),
      public_notification_method: notificationMethod,
      advance_warning_days: advanceWarningDays,
      media_release_required: isHighVolume || isHighSpeed || isNationalHighway,
      resident_consultation: this.getConsultationRequirements(work_type, roadData),
      emergency_vehicle_access: this.getEmergencyAccessPlan(roadData)
    };
  }

  /**
   * Get detailed worker protection based on ACTUAL road conditions
   */
  getWorkerProtection(work_type, isHighSpeed, roadData) {
    let measures = [
      'Traffic control devices per AS 1742.3',
      'Advance warning signage',
      'Delineation with cones/barriers',
      'High-visibility clothing (Day/Night class)'
    ];
    
    if (isHighSpeed) {
      measures.push('Additional safety buffer zones (minimum 20m)');
      measures.push('Truck-mounted attenuators (TMA) for approach protection');
      measures.push('Speed reduction signage cascade');
    }
    
    if (roadData?.traffic_volume >= 30000) {
      measures.push('Additional traffic controllers for high volume');
      measures.push('Real-time traffic monitoring');
    }
    
    if (roadData?.lanes >= 3) {
      measures.push('Progressive lane closure with adequate merge length');
    }
    
    return measures.join(', ');
  }

  /**
   * Get PPE requirements based on actual work conditions
   */
  getPPERequirements(work_type, roadData) {
    const base = [
      'High-visibility clothing (AS/NZS 4602.1 Class D/N)',
      'Hard hat (AS/NZS 1801)',
      'Safety boots (AS/NZS 2210.3)',
      'Safety glasses (AS/NZS 1337.1)'
    ];
    
    if (roadData?.speed_limit >= 80) {
      base.push('Supplementary high-vis garments recommended');
    }
    
    if (work_type === 'construction') {
      base.push('Hearing protection (AS/NZS 1270)');
      base.push('Gloves (AS/NZS 2161.2)');
    }
    
    return base.join(', ');
  }

  /**
   * Calculate advance warning days from REAL road data
   */
  calculateAdvanceWarningDays(work_type, roadData) {
    if (work_type === 'emergency') return '0';
    
    // National highways require more notice
    if (roadData?.road_classification === 'National Highway') return '14';
    
    // High volume roads
    if (roadData?.traffic_volume >= 30000) return '10';
    if (roadData?.traffic_volume >= 20000) return '7';
    
    // Arterial roads
    if (roadData?.road_classification?.includes('Arterial')) return '7';
    
    // Standard roads
    if (roadData?.traffic_volume >= 10000) return '5';
    
    return '3';
  }

  /**
   * Get detailed notification method based on REAL road importance
   */
  getDetailedNotificationMethod(roadData, advanceWarningDays) {
    const methods = [];
    
    // Always include
    methods.push('On-site signage per AS 1742.3');
    
    // Based on road classification
    if (roadData?.road_classification === 'National Highway') {
      methods.push('VMS signs at major intersections');
      methods.push('Transport authority website');
      methods.push('Media release to major news outlets');
      methods.push('Social media announcements');
      methods.push('Traffic apps (Google Maps, Waze notifications)');
    } else if (roadData?.traffic_volume >= 20000) {
      methods.push('VMS signs');
      methods.push('Local authority website');
      methods.push('Social media');
    } else if (roadData?.traffic_volume >= 10000) {
      methods.push('Local authority website');
      methods.push('Social media');
    }
    
    // For extended notice periods
    if (parseInt(advanceWarningDays) >= 7) {
      methods.push(`Letterbox drop to affected residents (${advanceWarningDays} days prior)`);
    }
    
    return methods.join(', ');
  }

  /**
   * Get consultation requirements based on work type and road data
   */
  getConsultationRequirements(work_type, roadData) {
    if (work_type === 'emergency') {
      return 'Emergency works - consultation not required. Public notification via signage and media.';
    }
    
    if (work_type === 'construction') {
      if (roadData?.traffic_volume >= 20000) {
        return 'Stakeholder consultation required: Residents within 500m, businesses with access affected, public transport operators. Community information session recommended.';
      }
      return 'Letterbox drop to affected residents 7 days prior. Contact details for queries provided.';
    }
    
    if (roadData?.road_classification?.includes('Collector') || roadData?.road_classification?.includes('Local')) {
      return 'Direct notification to immediately affected properties. Contact details provided on signage.';
    }
    
    return 'Public notification via standard channels. Consultation if requested by stakeholders.';
  }

  /**
   * Get emergency access plan based on road type
   */
  getEmergencyAccessPlan(roadData) {
    const isRoadClosure = roadData?.complete_road_closure;
    
    if (isRoadClosure) {
      return 'Emergency vehicle priority access maintained via traffic controllers. Detour route suitable for emergency vehicles verified. Traffic controllers trained in emergency vehicle protocols. Radio communication with emergency services dispatch.';
    }
    
    if (roadData?.speed_limit >= 80) {
      return 'Emergency vehicles given absolute priority. Works temporarily suspended on approach of emergency vehicles. Clear run-through lane maintained at all times. Traffic controllers have direct sight lines.';
    }
    
    return 'Emergency vehicles given priority access. Traffic controllers briefed on emergency protocols. Clear passage maintained with maximum 2-minute delay.';
  }

  /**
   * Generate contingency plans
   */
  generateContingencyPlans(work_type, road_occupancy) {
    const isRoadClosure = road_occupancy?.complete_road_closure;
    
    return {
      breakdown_procedure: 'Backup equipment on standby. If critical equipment fails, works suspended, site made safe, detour maintained if applicable. Equipment repaired/replaced within 4 hours or works rescheduled.',
      accident_procedure: '1. Stop work immediately. 2. Call 000 if injuries. 3. Secure scene. 4. First aid administered. 5. Notify supervisor and safety officer. 6. Document incident. 7. Investigate and report.',
      weather_delay_plan: 'Works suspended in adverse weather. Site secured, devices stabilized. Resume when safe. Notify road authority of delays. Extend permits if required.',
      traffic_buildup_response: isRoadClosure ? 
        'Monitor queue lengths. Additional traffic controllers deployed. Temporary signal optimization. Communication with road authority. Consider staged works.' :
        'Monitor traffic flow. Adjust lane closure timing. Add traffic controllers if needed. Provide real-time updates.',
      alternative_routes: isRoadClosure ? 
        'Alternative routes calculated and signed. Detour capacity verified. Emergency access maintained at all times.' :
        'Normal traffic flow with lane restrictions. No detour required.'
    };
  }

  /**
   * Infer control measures from road occupancy
   */
  inferControlMeasures(road_occupancy, work_type) {
    return {
      twenty_min_rule: work_type === 'maintenance' && !road_occupancy?.complete_road_closure,
      signage: true, // Always required
      speed_reduction: road_occupancy?.left_lane || road_occupancy?.right_lane || road_occupancy?.center_lane,
      detour: road_occupancy?.complete_road_closure
    };
  }

  /**
   * Generate approvals section
   */
  generateApprovals(userProfile) {
    const today = new Date().toISOString().split('T')[0];
    
    return {
      prepared_by_name: userProfile?.name || '',
      prepared_by_position: userProfile?.position || 'Traffic Manager',
      prepared_by_date: today,
      approved_by_name: '',
      approved_by_position: '',
      approved_by_signature: '',
      approved_by_date: '',
      declaration_accepted: false
    };
  }

  /**
   * Initialize templates library
   */
  initializeTemplates() {
    return {
      work_types: ['emergency', 'maintenance', 'construction'],
      work_styles: ['static', 'mobile'],
      standard_ppe: 'High-visibility clothing (Day/Night), hard hat, safety boots, hearing protection, safety glasses',
      // Add more templates as needed
    };
  }
}

export default TMPAutoPopulator;
