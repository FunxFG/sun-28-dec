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
    
    // Get location-based emergency services
    const state = this.extractState(address);
    const emergencyServices = this.getEmergencyServices(state);
    
    return {
      ...primaryContact,
      emergency_services_notified: false,
      police_station: emergencyServices.police,
      ambulance_service: emergencyServices.ambulance,
      incident_response_plan: this.generateIncidentResponsePlan()
    };
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
   * Generate environmental conditions
   */
  async generateEnvironmentalConditions(address, date) {
    // TODO: Integrate with weather API
    return {
      weather_considerations: 'Works to be suspended in heavy rain (>10mm/hr), high winds (>50km/h), or poor visibility (<100m)',
      visibility_requirements: 'Minimum 100m visibility required. Additional lighting provided for night works.',
      rain_contingency: 'Works suspended if heavy rain. All devices secured. Site made safe. Resume when conditions improve.',
      wind_speed_limit: '50 km/h maximum',
      temperature_considerations: 'Heat management: Regular breaks, hydration. Cold: Warm clothing, visibility maintained.'
    };
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
