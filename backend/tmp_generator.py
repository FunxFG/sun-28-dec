"""
Professional Traffic Management Plan Generator
Based on official DTMR/Austroads templates and standards
"""

from datetime import datetime, timezone
from typing import Dict, List, Any
import uuid

class TrafficManagementPlanGenerator:
    def __init__(self):
        self.template_sections = {
            'works': self._get_works_template_structure(),
            'event': self._get_event_template_structure()
        }
    
    def generate_professional_tmp(self, plan_data: Dict[str, Any], plan_type: str = 'works') -> Dict[str, Any]:
        """Generate a complete professional Traffic Management Plan"""
        
        # Handle None plan_data
        if plan_data is None:
            plan_data = {}
        
        # Get the appropriate template structure
        template = self.template_sections.get(plan_type, self.template_sections['works'])
        
        # Generate TMP number
        tmp_number = self._generate_tmp_number()
        
        # Build the complete TMP
        tmp = {
            'tmp_header': self._generate_header(plan_data, tmp_number, plan_type),
            'declaration': self._generate_declaration(plan_data),
            'table_of_contents': self._generate_toc(),
            'sections': {
                '1_introduction': self._generate_introduction(plan_data),
                '2_project_overview': self._generate_project_overview(plan_data),
                '3_risk_management': self._generate_risk_management(plan_data),
                '4_traffic_planning': self._generate_traffic_planning(plan_data),
                '5_site_assessment': self._generate_site_assessment(plan_data),
                '6_safety_plan': self._generate_safety_plan(plan_data),
                '7_implementation': self._generate_implementation(plan_data),
                '8_emergency_arrangements': self._generate_emergency_arrangements(plan_data),
                '9_monitoring': self._generate_monitoring(plan_data),
                '10_management_review': self._generate_management_review(plan_data)
            },
            'appendices': self._generate_appendices(plan_data),
            'traffic_guidance_schemes': self._generate_tgs_drawings(plan_data),
            'metadata': {
                'tmp_number': tmp_number,
                'generated_date': datetime.now(timezone.utc).isoformat(),
                'template_version': 'March 2025 edition',
                'compliance_standards': ['Main Roads Code of Practice', 'AGTTM', 'AS 1742.3']
            }
        }
        
        return tmp
    
    def _generate_tmp_number(self) -> str:
        """Generate unique TMP number"""
        year = datetime.now().year
        random_id = str(uuid.uuid4())[:8].upper()
        return f"TMP-{year}-{random_id}"
    
    def _generate_header(self, plan_data: Dict, tmp_number: str, plan_type: str) -> Dict:
        """Generate TMP header section"""
        # Handle None plan_data
        if plan_data is None:
            plan_data = {}
            
        work_type = plan_data.get('work_details', {}).get('work_type', 'Construction').upper()
        
        return {
            'title': 'WORKS ON ROADS TRAFFIC MANAGEMENT PLAN' if plan_type == 'works' else 'EVENT TRAFFIC MANAGEMENT PLAN',
            'work_type': work_type,
            'road_details': {
                'road_number': self._extract_road_number(plan_data.get('work_details', {}).get('start_address', '')),
                'road_name': self._extract_road_name(plan_data.get('work_details', {}).get('start_address', '')),
                'suburb': self._extract_suburb(plan_data.get('work_details', {}).get('start_address', ''))
            },
            'traffic_management_company': {
                # Handle cases where traffic_company may be None
                'name': (plan_data.get('traffic_company') or {}).get('name', 'TBC'),
                'contract': 'TBC',
                'date': 'March 2025 edition'
            },
            'tmp_identification': {
                'tmp_number': tmp_number,
                'revision_number': 'A',
                'date': datetime.now().strftime('%d/%m/%Y')
            }
        }
    
    def _generate_declaration(self, plan_data: Dict) -> Dict:
        """Generate declaration section"""
        # Handle None plan_data
        if plan_data is None:
            plan_data = {}
            
        return {
            'designer_declaration': {
                'certifier_name': (plan_data.get('traffic_company') or {}).get('liaison_name', 'TBC'),
                'awtm_cert_number': 'AWTM-TBC',
                'site_inspection_date': datetime.now().strftime('%d/%m/%Y'),
                'compliance_statement': 'This Traffic Management Plan has been prepared in accordance with the Main Roads Code of Practice, AGTTM and AS 1742.3',
                'signature_date': datetime.now().strftime('%d/%m/%Y')
            },
            'design_review_details': {
                'tmp_designed_by': (plan_data.get('traffic_company') or {}).get('liaison_name', 'TBC'),
                'tmp_reviewed_by': 'TBC',
                'rtm_reviewed_by': 'TBC',
                'compliance_audit_by': 'TBC'
            },
            'road_authority_authorisation': {
                'authorisation_statement': 'Road authority authorisation of the implementation of traffic signs and devices is given for this Traffic Management Plan',
                'authorised_officer': 'TBC',
                'position': 'TBC',
                'date': 'TBC'
            }
        }
    
    def _generate_introduction(self, plan_data: Dict) -> Dict:
        """Generate Section 1: Introduction"""
        # Handle None plan_data
        if plan_data is None:
            plan_data = {}
            
        return {
            '1.1_purpose_and_scope': {
                'purpose': f"This Traffic Management Plan (TMP) has been prepared for {plan_data.get('work_details', {}).get('description', 'roadworks')} on {plan_data.get('work_details', {}).get('start_address', 'TBC')}.",
                'scope': f"The scope includes {plan_data.get('work_details', {}).get('work_type', 'construction')} activities from {plan_data.get('work_details', {}).get('start_date', 'TBC')} to {plan_data.get('work_details', {}).get('end_date', 'TBC')}."
            },
            '1.2_objectives_and_strategies': {
                'objectives': [
                    'Safety of road workers',
                    'Safe guidance of all road users',
                    'Minimal network impact',
                    'Minimized disruption and inconvenience',
                    'Minimized impact on adjacent properties'
                ],
                'strategies': self._generate_strategies(plan_data)
            }
        }
    
    def _generate_project_overview(self, plan_data: Dict) -> Dict:
        """Generate Section 2: Project Overview"""
        return {
            '2.1_location': {
                'detailed_location': f"Works located between {plan_data.get('work_details', {}).get('start_address', 'TBC')} and {plan_data.get('work_details', {}).get('end_address', 'TBC')}",
                'map_reference': 'Figure 1 - Site Location Map',
                'site_photo': 'Figure 2 - Site Visit Photo'
            },
            '2.2_project_details': {
                'project_location': plan_data.get('work_details', {}).get('start_address', 'TBC'),
                'road_classification': plan_data.get('road_data', {}).get('road_classification', 'TBC'),
                'existing_speed_limit': f"{plan_data.get('road_data', {}).get('speed_limit', 60)} km/h",
                'road_authority': plan_data.get('road_data', {}).get('governing_body', 'Local Council'),
                'principal_contractor': plan_data.get('company_details', {}).get('name', 'TBC'),
                'scope_of_works': plan_data.get('work_details', {}).get('description', 'TBC'),
                'work_staging': plan_data.get('work_details', {}).get('work_style', 'Static'),
                'project_dates': f"{plan_data.get('work_details', {}).get('start_date', 'TBC')} to {plan_data.get('work_details', {}).get('end_date', 'TBC')}",
                'work_hours': 'Standard hours: 7:00 AM to 6:00 PM, Monday to Friday',
                'duration': 'TBC days',
                'constraints': self._identify_constraints(plan_data)
            },
            '2.3_existing_traffic': {
                'traffic_volume': f"{plan_data.get('road_data', {}).get('traffic_volume', 15000)} vehicles per day",
                'road_configuration': self._describe_road_configuration(plan_data),
                'pedestrian_cyclist_facilities': 'Existing footpaths and cycle lanes to be maintained where possible'
            },
            '2.4_proposed_ttm': {
                'ttm_description': self._generate_ttm_description(plan_data),
                'complexity': 'Non-complex traffic arrangements as per section 4.2.3 of CoP',
                'lane_closures': self._describe_lane_closures(plan_data),
                'speed_zones': self._describe_speed_zones(plan_data),
                'proposed_lane_widths': '3.0m minimum',
                'road_safety_barriers': 'Temporary barriers as required for worker protection'
            },
            '2.5_project_representatives': self._generate_project_representatives(plan_data)
        }
    
    def _generate_risk_management(self, plan_data: Dict) -> Dict:
        """Generate Section 3: Risk Management"""
        return {
            '3.1_risk_classification': {
                'consequence_levels': {
                    'catastrophic': 'Multiple fatalities, major environmental damage',
                    'major': 'Single fatality, serious injury, significant environmental impact',
                    'moderate': 'Medical treatment injury, moderate environmental impact',
                    'minor': 'First aid injury, minor environmental impact',
                    'negligible': 'No injury, no environmental impact'
                },
                'likelihood_levels': {
                    'almost_certain': 'Expected to occur in most circumstances',
                    'likely': 'Will probably occur in most circumstances',
                    'possible': 'Might occur at some time',
                    'unlikely': 'Could occur at some time',
                    'rare': 'May occur only in exceptional circumstances'
                }
            },
            '3.2_risk_register': {
                'generic_risks': self._generate_generic_risks(),
                'site_specific_risks': self._generate_site_specific_risks(plan_data)
            }
        }
    
    def _generate_traffic_planning(self, plan_data: Dict) -> Dict:
        """Generate Section 4: Traffic Management Planning and Assessment"""
        return {
            '4.1_traffic_assessment': {
                'traffic_data': {
                    'location': plan_data.get('work_details', {}).get('start_address', 'TBC'),
                    'volume': plan_data.get('road_data', {}).get('traffic_volume', 15000),
                    'heavy_vehicles': '8%',
                    'speed': f"{plan_data.get('road_data', {}).get('speed_limit', 60)} km/h",
                    'date': datetime.now().strftime('%d/%m/%Y'),
                    'source': 'Main Roads Traffic Data'
                },
                'traffic_flow_analysis': self._analyze_traffic_flow(plan_data),
                'temporary_speed_zones': self._detail_speed_zones(plan_data),
                'traffic_signals': 'No permanent traffic signals affected',
                'network_impact': 'Minimal impact on adjoining network',
                'queue_treatment': 'Queue management not required for this work type',
                'speed_management': self._detail_speed_management(plan_data)
            },
            '4.2_road_users': self._analyze_road_users(plan_data),
            '4.3_night_work': 'No night work proposed',
            '4.4_road_safety_barriers': self._detail_barriers(plan_data),
            '4.5_shadow_vehicles': 'Shadow vehicles not required',
            '4.6_consultation': self._detail_consultation(plan_data)
        }
    
    def _generate_safety_plan(self, plan_data: Dict) -> Dict:
        """Generate Section 6: Safety Plan"""
        return {
            '6.1_work_health_safety': 'All personnel have a duty of care to ensure work health and safety requirements are met',
            '6.2_roles_responsibilities': {
                'project_manager': 'Overall project responsibility and TMP compliance',
                'site_supervisor': 'Day-to-day management and safety oversight',
                'traffic_management_supervisor': 'Implementation and maintenance of traffic control',
                'traffic_controllers': 'Direct traffic control operations',
                'workers': 'Follow all safety procedures and TMP requirements'
            },
            '6.3_ppe': [
                'High visibility clothing (Class D/N as per AS/NZS 4602)',
                'Safety helmets',
                'Safety boots',
                'Additional PPE as required by risk assessment'
            ],
            '6.4_plant_equipment': 'All plant and equipment to be operated by competent personnel with valid tickets/licenses',
            '6.5_trip_hazards': 'All potential trip hazards to be identified and mitigated'
        }
    
    def _generate_implementation(self, plan_data: Dict) -> Dict:
        """Generate Section 7: Implementation"""
        return {
            '7.1_traffic_guidance_schemes': {
                'stage_1': {
                    'tgs_number': 'TGS-001',
                    'description': 'Initial setup and lane closure',
                    'reference': 'Appendix F - Drawing 1'
                }
            },
            '7.2_sequence_staging': self._detail_implementation_sequence(plan_data),
            '7.3_traffic_control_devices': {
                'sign_requirements': 'All signs to comply with AS 1742.3, AGTTM, and CoP',
                'positioning_tolerances': 'Signs positioned within ±0.5m of design location',
                'delineation': 'Traffic cones spaced as per AGTTM guidelines',
                'edge_clearance': 'Minimum 0.5m clearance from travel lane'
            },
            '7.4_site_access': 'Safe entry and exit procedures for all work vehicles',
            '7.5_communication': 'Daily pre-start meetings and safety briefings'
        }
    
    def _generate_emergency_arrangements(self, plan_data: Dict) -> Dict:
        """Generate Section 8: Emergency Arrangements and Contingencies"""
        return {
            '8.1_traffic_incidents': {
                'serious_injury': 'Stop all work, secure scene, call emergency services',
                'minor_incidents': 'Assess situation, provide first aid, report incident',
                'vehicle_breakdown': 'Move to safe location, use warning devices'
            },
            '8.2_emergency_services': 'Immediate notification of Police, Ambulance, Fire services',
            '8.3_dangerous_goods': 'Follow HAZMAT procedures, evacuate if necessary',
            '8.4_service_damage': 'Stop work immediately, notify service provider',
            '8.5_emergency_contacts': {
                'police': '000',
                'ambulance': '000',
                'fire': '000',
                'road_authority': 'TBC',
                'project_manager': plan_data.get('company_details', {}).get('phone', 'TBC')
            }
        }
    
    def _generate_monitoring(self, plan_data: Dict) -> Dict:
        """Generate Section 9: Monitoring and Measurement"""
        return {
            '9.1_daily_inspections': {
                'before_work': 'Check all devices in place and functioning',
                'during_work': 'Continuous monitoring of traffic conditions',
                'after_work': 'Ensure all devices secure for after-hours',
                'frequency': 'Minimum 3 times per day'
            },
            '9.2_audits': 'Independent TMP audit within 24 hours of implementation',
            '9.3_records': ['Daily diary', 'Incident reports', 'Device inspection records'],
            '9.4_public_feedback': 'Complaints hotline and response procedures established'
        }
    
    def _generate_management_review(self, plan_data: Dict) -> Dict:
        """Generate Section 10: Management Review and Approvals"""
        return {
            '10.1_tmp_review': 'Weekly review of TMP effectiveness and improvements',
            '10.2_variations': {
                'minor_adjustments': 'Site supervisor approval required',
                'major_variations': 'Road authority approval required',
                'emergency_modifications': 'Immediate implementation with post-event approval'
            },
            '10.3_approvals': [
                'Road authority permit',
                'Local government notification',
                'Utility service coordination',
                'Emergency services notification'
            ]
        }
    
    def _generate_appendices(self, plan_data: Dict) -> Dict:
        """Generate appendices"""
        return {
            'appendix_a': 'Notification of Roadworks',
            'appendix_b': 'Variation to Standards (if applicable)',
            'appendix_c': 'Record Forms (Daily Diary, Incident Report)',
            'appendix_d': 'Traffic Analysis and Volume Counts',
            'appendix_e': 'Roadway Access Authorisation Permit',
            'appendix_f': 'Traffic Guidance Schemes (TGS Drawings)'
        }
    
    def _generate_tgs_drawings(self, plan_data: Dict) -> List[Dict]:
        """Generate Traffic Guidance Scheme drawings"""
        tgs_drawings = []
        
        # Generate based on placed devices
        devices = plan_data.get('devices', [])
        if devices:
            tgs_drawings.append({
                'tgs_number': 'TGS-001',
                'title': 'Main Work Zone Setup',
                'devices': devices,
                'notes': [
                    'All signs to be retroreflective',
                    'Devices to be removed outside work hours unless approved for 24/7 operation',
                    'Regular inspection required'
                ],
                'compliance_reference': 'AS 1742.3 Section 4.2'
            })
        
        return tgs_drawings
    
    # Helper methods for generating specific content
    def _extract_road_number(self, address: str) -> str:
        """Extract road number from address"""
        # Simplified - would use more sophisticated parsing in production
        return 'TBC'
    
    def _extract_road_name(self, address: str) -> str:
        """Extract road name from address"""
        if not address:
            return 'TBC'
        parts = address.split(',')
        return parts[0].strip() if parts else 'TBC'
    
    def _extract_suburb(self, address: str) -> str:
        """Extract suburb from address"""
        if not address:
            return 'TBC'
        parts = address.split(',')
        return parts[1].strip() if len(parts) > 1 else 'TBC'
    
    def _generate_strategies(self, plan_data: Dict) -> List[str]:
        """Generate strategies based on plan data"""
        strategies = []
        
        # Handle None plan_data
        if plan_data is None:
            print(f"DEBUG: plan_data is None in _generate_strategies")
            plan_data = {}
        
        print(f"DEBUG: plan_data type: {type(plan_data)}, value: {plan_data}")
        
        control_measures = plan_data.get('control_measures') or {}
        if control_measures.get('speed_reduction'):
            strategies.append('Implement temporary speed reduction')
        
        if control_measures.get('signage'):
            strategies.append('Deploy appropriate warning and regulatory signage')
        
        if control_measures.get('detour'):
            strategies.append('Provide alternative route guidance')
        
        strategies.extend([
            'Maintain safe access for all road users',
            'Minimize work zone length and duration',
            'Provide clear advance warning of work activities'
        ])
        
        return strategies
    
    def _identify_constraints(self, plan_data: Dict) -> List[str]:
        """Identify project constraints"""
        constraints = []
        
        road_occupancy = plan_data.get('road_occupancy', {})
        if road_occupancy.get('complete_road_closure'):
            constraints.append('Complete road closure required')
        
        if road_occupancy.get('footpath'):
            constraints.append('Pedestrian access affected')
        
        constraints.extend([
            'Weather dependent activities',
            'Peak hour traffic considerations',
            'Coordination with adjacent properties'
        ])
        
        return constraints
    
    def _describe_road_configuration(self, plan_data: Dict) -> str:
        """Describe existing road configuration"""
        road_data = plan_data.get('road_data', {})
        return f"{road_data.get('road_type', 'Arterial')} road with {road_data.get('speed_limit', 60)} km/h speed limit"
    
    def _generate_ttm_description(self, plan_data: Dict) -> str:
        """Generate TTM description"""
        work_type = plan_data.get('work_details', {}).get('work_type', 'construction')
        return f"Temporary traffic management for {work_type} activities including lane management and worker protection"
    
    def _describe_lane_closures(self, plan_data: Dict) -> str:
        """Describe lane closures"""
        occupancy = plan_data.get('road_occupancy', {})
        closures = []
        
        if occupancy.get('left_lane'):
            closures.append('left lane')
        if occupancy.get('right_lane'):
            closures.append('right lane')
        if occupancy.get('complete_road_closure'):
            return 'Complete road closure'
        
        return f"Closure of {', '.join(closures)}" if closures else "No lane closures"
    
    def _describe_speed_zones(self, plan_data: Dict) -> str:
        """Describe speed zones"""
        if plan_data.get('control_measures', {}).get('speed_reduction'):
            return 'Temporary 40 km/h speed zone through work area'
        return 'No temporary speed zones'
    
    def _generate_project_representatives(self, plan_data: Dict) -> Dict:
        """Generate project representatives table"""
        return {
            'road_authority': {'name': 'TBC', 'contact': 'TBC'},
            'project_manager': {
                'name': plan_data.get('company_details', {}).get('liaison_name', 'TBC'),
                'contact': plan_data.get('company_details', {}).get('liaison_phone', 'TBC')
            },
            'site_supervisor': {'name': 'TBC', 'contact': 'TBC'},
            'tmp_designer': {
                'name': (plan_data.get('traffic_company') or {}).get('liaison_name', 'TBC'),
                'contact': (plan_data.get('traffic_company') or {}).get('liaison_phone', 'TBC')
            }
        }
    
    def _get_works_template_structure(self) -> Dict:
        """Get works template structure"""
        return {
            'type': 'works',
            'sections': [
                'Introduction', 'Project Overview', 'Risk Management',
                'Traffic Management Planning', 'Site Assessment', 'Safety Plan',
                'Implementation', 'Emergency Arrangements', 'Monitoring',
                'Management Review'
            ]
        }
    
    def _get_event_template_structure(self) -> Dict:
        """Get event template structure"""
        return {
            'type': 'event',
            'sections': [
                'Introduction', 'Event Overview', 'Risk Management',
                'Traffic Management Planning', 'Site Assessment', 'Statutory Requirements',
                'Implementation', 'Emergency Arrangements', 'Monitoring',
                'Management Review'
            ]
        }
    
    def _generate_generic_risks(self) -> List[Dict]:
        """Generate generic risk register"""
        return [
            {
                'risk_event': 'Vehicle collision with worker',
                'consequence': 'Major injury or fatality',
                'pre_treatment_risk': {'likelihood': 'Possible', 'consequence': 'Major', 'rating': 'High'},
                'treatment': 'Physical barriers, high-vis clothing, traffic control',
                'residual_risk': {'likelihood': 'Unlikely', 'consequence': 'Major', 'rating': 'Medium'}
            },
            {
                'risk_event': 'Vehicle collision in work zone',
                'consequence': 'Property damage, injury',
                'pre_treatment_risk': {'likelihood': 'Likely', 'consequence': 'Moderate', 'rating': 'High'},
                'treatment': 'Clear signage, adequate warning distance, traffic control',
                'residual_risk': {'likelihood': 'Unlikely', 'consequence': 'Moderate', 'rating': 'Low'}
            }
        ]
    
    def _generate_site_specific_risks(self, plan_data: Dict) -> List[Dict]:
        """Generate site-specific risks based on plan data"""
        risks = []
        
        if plan_data.get('road_occupancy', {}).get('complete_road_closure'):
            risks.append({
                'risk_event': 'Emergency vehicle access blocked',
                'consequence': 'Delayed emergency response',
                'pre_treatment_risk': {'likelihood': 'Possible', 'consequence': 'Major', 'rating': 'High'},
                'treatment': 'Emergency services notification, escort procedures',
                'residual_risk': {'likelihood': 'Rare', 'consequence': 'Major', 'rating': 'Medium'}
            })
        
        return risks
    
    def _analyze_traffic_flow(self, plan_data: Dict) -> Dict:
        """Analyze traffic flow"""
        return {
            'volume_analysis': f"Current volume: {plan_data.get('road_data', {}).get('traffic_volume', 15000)} vpd",
            'impact_assessment': 'Minimal impact during off-peak hours',
            'mitigation_measures': 'Sequential work staging to maintain traffic flow'
        }
    
    def _detail_speed_zones(self, plan_data: Dict) -> Dict:
        """Detail temporary speed zones"""
        if plan_data.get('control_measures', {}).get('speed_reduction'):
            return {
                'location': 'Through work zone',
                'speed': '40 km/h',
                'justification': 'Worker safety and reduced stopping distance',
                'dates': f"{plan_data.get('work_details', {}).get('start_date', 'TBC')} to {plan_data.get('work_details', {}).get('end_date', 'TBC')}"
            }
        return {'status': 'No temporary speed zones required'}
    
    def _detail_speed_management(self, plan_data: Dict) -> List[str]:
        """Detail speed management strategies"""
        strategies = []
        
        if plan_data.get('control_measures', {}).get('speed_reduction'):
            strategies.extend([
                'Temporary speed limit signs',
                'Speed enforcement coordination',
                'Speed feedback signs where appropriate'
            ])
        
        return strategies or ['Standard speed management through signage']
    
    def _analyze_road_users(self, plan_data: Dict) -> Dict:
        """Analyze different road user types"""
        return {
            'pedestrians': 'Maintain safe pedestrian access via temporary walkways',
            'cyclists': 'Provide safe passage through or around work zone',
            'public_transport': 'Coordinate with PT operators for service adjustments',
            'heavy_vehicles': 'Ensure adequate clearances for heavy vehicle access',
            'emergency_vehicles': 'Maintain emergency access at all times',
            'property_access': 'Coordinate with property owners for access requirements'
        }
    
    def _detail_barriers(self, plan_data: Dict) -> str:
        """Detail road safety barriers"""
        if plan_data.get('work_details', {}).get('work_type') == 'construction':
            return 'Temporary concrete barriers for high-risk construction activities'
        return 'Standard delineation devices adequate for this work type'
    
    def _detail_consultation(self, plan_data: Dict) -> Dict:
        """Detail consultation and communication"""
        return {
            'other_agencies': 'Coordination with emergency services, utilities, public transport',
            'public_notification': [
                'Letter drop to affected residents',
                'VMS boards for advance warning',
                'Media release if significant impact',
                'Project website updates'
            ]
        }
    
    def _detail_implementation_sequence(self, plan_data: Dict) -> List[Dict]:
        """Detail implementation sequence"""
        return [
            {
                'stage': 'Setup',
                'description': 'Install advance warning signs and initial traffic control',
                'safety_measures': 'Use of safety vehicles and trained personnel'
            },
            {
                'stage': 'Work Phase',
                'description': 'Maintain traffic control throughout work activities',
                'safety_measures': 'Continuous monitoring and adjustment as required'
            },
            {
                'stage': 'Removal',
                'description': 'Safe removal of all temporary devices',
                'safety_measures': 'Systematic removal in reverse order of installation'
            }
        ]
    
    def _generate_toc(self) -> List[Dict]:
        """Generate table of contents"""
        return [
            {'section': '1', 'title': 'Introduction', 'page': 6},
            {'section': '2', 'title': 'Project Overview', 'page': 7},
            {'section': '3', 'title': 'Risk Management', 'page': 10},
            {'section': '4', 'title': 'Traffic Management Planning and Assessment', 'page': 16},
            {'section': '5', 'title': 'Site Assessment', 'page': 19},
            {'section': '6', 'title': 'Safety Plan', 'page': 21},
            {'section': '7', 'title': 'Implementation', 'page': 26},
            {'section': '8', 'title': 'Emergency Arrangements and Contingencies', 'page': 30},
            {'section': '9', 'title': 'Monitoring and Measurement', 'page': 33},
            {'section': '10', 'title': 'Management Review and Approvals', 'page': 35}
        ]
    
    def _generate_site_assessment(self, plan_data: Dict) -> Dict:
        """Generate Section 5: Site Assessment"""
        return {
            '5.1_environmental_conditions': {
                'adverse_weather': 'Work suspension procedures for high winds, heavy rain, or severe weather',
                'sun_glare': 'Consider sun angle during setup and removal times',
                'fog_dust_smoke': 'Reduced visibility procedures and additional warning devices',
                'road_geometry': 'Site-specific considerations for curves, hills, and intersections'
            },
            '5.2_existing_signs': 'Assessment of existing signage for conflicts with temporary signs'
        }

# Create global instance
tmp_generator = TrafficManagementPlanGenerator()