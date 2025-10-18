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

    // Generate all sections
    const populated = {
      // Company details from user profile
      company_details: this.getCompanyDetails(userProfile),
      traffic_company: this.getTrafficCompanyDetails(userProfile),
      
      // Work details with smart defaults
      work_details: await this.generateWorkDetails(minimalInputs, roadData),
      
      // Emergency contacts from profile + location
      emergency_contacts: await this.generateEmergencyContacts(userProfile, start_address),
      
      // Personnel from user's team
      personnel: this.getPersonnelDetails(userProfile),
      
      // Insurance from profile
      permits_insurance: this.getInsuranceDetails(userProfile),
      
      // Environmental based on date + location
      environmental_conditions: await this.generateEnvironmentalConditions(start_address, start_date),
      
      // Safety based on work type
      safety_communications: this.generateSafetyCommunications(work_type, work_style, roadData),
      
      // Contingency templates
      contingency_plans: this.generateContingencyPlans(work_type, road_occupancy),
      
      // Auto-fill approval preparer
      approvals: this.generateApprovals(userProfile),
      
      // Road occupancy and control measures
      road_occupancy: road_occupancy,
      control_measures: this.inferControlMeasures(road_occupancy, work_type)
    };

    return populated;
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
   * Fetch REAL emergency services near location using Google Places API
   */
  async fetchRealEmergencyServices(address) {
    try {
      // First geocode the address
      const geocodeResponse = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs`
      );
      const geocodeData = await geocodeResponse.json();
      
      if (!geocodeData.results || geocodeData.results.length === 0) {
        throw new Error('Could not geocode address');
      }
      
      const location = geocodeData.results[0].geometry.location;
      
      // Search for police station
      const policeResponse = await fetch(
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${location.lat},${location.lng}&radius=10000&type=police&key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs`
      );
      const policeData = await policeResponse.json();
      
      // Search for hospital/ambulance
      const ambulanceResponse = await fetch(
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${location.lat},${location.lng}&radius=10000&type=hospital&key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs`
      );
      const ambulanceData = await ambulanceResponse.json();
      
      // Get place details for phone numbers
      let policeInfo = 'Local Police: 131 444 (non-emergency)';
      let ambulanceInfo = 'Ambulance: 000 (emergency)';
      
      if (policeData.results && policeData.results.length > 0) {
        const nearestPolice = policeData.results[0];
        const detailsResponse = await fetch(
          `https://maps.googleapis.com/maps/api/place/details/json?place_id=${nearestPolice.place_id}&fields=name,formatted_phone_number,vicinity&key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs`
        );
        const details = await detailsResponse.json();
        
        if (details.result) {
          policeInfo = `${details.result.name}: ${details.result.formatted_phone_number || '131 444'} - ${details.result.vicinity}`;
        }
      }
      
      if (ambulanceData.results && ambulanceData.results.length > 0) {
        const nearestHospital = ambulanceData.results[0];
        const detailsResponse = await fetch(
          `https://maps.googleapis.com/maps/api/place/details/json?place_id=${nearestHospital.place_id}&fields=name,formatted_phone_number,vicinity&key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs`
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
   * Generate environmental conditions using REAL weather API
   */
  async generateEnvironmentalConditions(address, date) {
    try {
      // Get coordinates for the address
      const geocodeResponse = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs`
      );
      const geocodeData = await geocodeResponse.json();
      
      if (!geocodeData.results || geocodeData.results.length === 0) {
        throw new Error('Could not geocode address');
      }
      
      const location = geocodeData.results[0].geometry.location;
      
      // Fetch REAL weather forecast from OpenWeatherMap
      const weatherResponse = await fetch(
        `https://api.openweathermap.org/data/2.5/forecast?lat=${location.lat}&lon=${location.lng}&appid=4d8fb5b93d4af21d66a2948710284366&units=metric`
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
   * Generate safety communications
   */
  generateSafetyCommunications(work_type, work_style, roadData) {
    const isHighSpeed = roadData?.speed_limit >= 80;
    const isHighVolume = roadData?.traffic_volume >= 20000;
    
    return {
      worker_protection_measures: this.getWorkerProtection(work_type, isHighSpeed),
      ppe_requirements: 'High-visibility clothing (Day/Night), hard hat, safety boots, hearing protection, safety glasses',
      public_notification_method: this.getNotificationMethod(roadData),
      advance_warning_days: this.getAdvanceWarningDays(work_type, roadData),
      media_release_required: isHighVolume || isHighSpeed,
      resident_consultation: work_type === 'construction' ? 'Letterbox drop to affected residents 7 days prior' : 'Not required for short-duration works',
      emergency_vehicle_access: 'Emergency vehicles given priority access at all times. Traffic controllers briefed on emergency protocols.'
    };
  }

  /**
   * Get worker protection measures
   */
  getWorkerProtection(work_type, isHighSpeed) {
    const base = 'Traffic control devices per AS 1742.3, advance warning signage, delineation with cones/barriers';
    if (isHighSpeed) {
      return `${base}, additional safety buffer zones, truck-mounted attenuators for high-speed roads`;
    }
    return base;
  }

  /**
   * Get public notification method
   */
  getNotificationMethod(roadData) {
    if (roadData?.road_classification === 'National Highway') {
      return 'VMS signs, website, media release, social media';
    }
    if (roadData?.traffic_volume >= 20000) {
      return 'VMS signs, website, social media';
    }
    return 'Local signage, website notification';
  }

  /**
   * Get advance warning days
   */
  getAdvanceWarningDays(work_type, roadData) {
    if (work_type === 'emergency') return '0';
    if (roadData?.road_classification === 'National Highway') return '14';
    if (roadData?.traffic_volume >= 20000) return '7';
    return '3';
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
