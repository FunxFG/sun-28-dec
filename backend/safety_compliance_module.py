"""
Safety Compliance Module
Implements SA DIT Field Guide and current industry standards (2025)
Based on MTM SA meeting minutes and professional TMP requirements
"""

from datetime import datetime
from typing import Dict, List


def generate_safety_compliance_section() -> Dict:
    """
    Generate comprehensive safety and compliance section for TMP
    Based on:
    - SA DIT Field Guide Version 9.1 2021
    - MTM SA Toolbox Minutes September 2025
    - Current industry practices
    """
    
    return {
        'section_title': 'Safety and Compliance Requirements',
        'mandatory_notice': '⚠️ ALL REQUIREMENTS ARE MANDATORY - NON-COMPLIANCE MAY RESULT IN SITE SHUTDOWN',
        
        'daily_requirements': {
            'title': 'Daily Site Requirements (MANDATORY)',
            'items': [
                {
                    'requirement': 'Job Safety Analysis (JSA)',
                    'frequency': 'DAILY - Every shift',
                    'timing': 'Before work commences',
                    'completion': 'All crew members must sign',
                    'consequences': 'Site shutdown if not completed'
                },
                {
                    'requirement': 'Safe Work Method Statement (SWMS)',
                    'frequency': 'DAILY - For each job location',
                    'timing': 'Sign on ONLY when on site (not before/after)',
                    'completion': 'Site-specific SWMS required',
                    'consequences': 'Non-compliance = permit violation'
                },
                {
                    'requirement': 'Fitness for Work Form',
                    'frequency': 'DAILY - Every shift',
                    'timing': 'At commencement of shift',
                    'completion': 'Individual self-assessment',
                    'consequences': 'Unfit workers removed from site'
                },
                {
                    'requirement': 'Photo Documentation',
                    'frequency': 'MANDATORY - All reports',
                    'timing': 'Throughout shift at key points',
                    'completion': 'Time-stamped photos required',
                    'photo_points': [
                        'Site setup (before work)',
                        'Signage placement',
                        'Traffic control devices',
                        'Work area configuration',
                        'Site completion (after pack-up)'
                    ]
                },
                {
                    'requirement': 'Client Sign-Off',
                    'frequency': 'REQUIRED - Before leaving site',
                    'timing': 'At completion of work',
                    'completion': 'Job docket signed by client',
                    'consequences': 'Payment may be withheld'
                },
                {
                    'requirement': 'Aftercare Reporting',
                    'frequency': 'MANDATORY',
                    'timing': 'Commencement and final pick-up',
                    'completion': 'Date stamped, separate report',
                    'notes': 'Required even if noted on JSEA'
                }
            ]
        },
        
        'ppe_requirements': {
            'title': 'Personal Protective Equipment (PPE) - MANDATORY',
            'arrival_rule': 'Must arrive on site wearing ALL required PPE for entirety of shift',
            'items': [
                {
                    'item': 'High-Vis Shirts',
                    'specification': 'Cotton drill or anti-static (orange/blue) with reflective tape',
                    'standard': 'AS/NZS 4602.1',
                    'mandatory': True
                },
                {
                    'item': 'High-Vis Pants',
                    'specification': 'Blue with reflective tape',
                    'standard': 'AS/NZS 4602.1',
                    'mandatory': True
                },
                {
                    'item': 'Hard Hat',
                    'specification': 'Compliant safety helmet',
                    'standard': 'AS/NZS 1801',
                    'mandatory': True
                },
                {
                    'item': 'Gloves',
                    'specification': 'For ALL manual handling activities',
                    'standard': 'AS/NZS 2161',
                    'mandatory': True
                },
                {
                    'item': 'Safety Boots',
                    'specification': 'Steel-capped safety footwear',
                    'standard': 'AS/NZS 2210',
                    'mandatory': True
                },
                {
                    'item': 'Safety Glasses',
                    'specification': 'Impact-resistant eye protection',
                    'standard': 'AS/NZS 1337',
                    'mandatory': True
                },
                {
                    'item': 'UHF Radio',
                    'specification': 'Charged and ready for use',
                    'purpose': 'Traffic controller communication',
                    'mandatory': True
                }
            ]
        },
        
        'fatigue_management': {
            'title': 'Fatigue Management (MANDATORY)',
            'zero_tolerance': 'Non-compliance will result in immediate removal from site',
            'requirements': [
                {
                    'rule': 'Rest Break Between Shifts',
                    'requirement': 'MINIMUM 10 hours between shifts',
                    'mandatory': True,
                    'consequences': 'Shift cancellation if not met'
                },
                {
                    'rule': 'Maximum Weekly Hours',
                    'requirement': 'NOT to exceed 50 hours per week',
                    'mandatory': True,
                    'consequences': 'Permit violation'
                },
                {
                    'rule': 'Shift Length Notification',
                    'requirement': 'Project Manager MUST be notified if shift exceeds 12 hours',
                    'timing': 'As soon as potential for long shift is known',
                    'mandatory': True,
                    'special_note': 'Critical for Fulton Hogan DC Maintenance Sites'
                },
                {
                    'rule': 'Fitness for Work',
                    'requirement': 'Workers must be fit and well enough to perform duties',
                    'includes': 'Not under influence of alcohol, drugs, or misused prescription medicines',
                    'mandatory': True
                }
            ]
        },
        
        'substance_abuse_policy': {
            'title': 'Drugs, Alcohol & Substance Abuse',
            'policy': 'ZERO TOLERANCE',
            'consequences': 'Immediate dismissal and ban from all sites',
            'requirements': [
                {
                    'policy': 'Fitness for Duty',
                    'description': 'All workers responsible for being fit for work',
                    'prohibition': 'No alcohol or drug use that impairs work capability'
                },
                {
                    'policy': 'Prescription Medicines',
                    'requirement': 'Consult doctor about work-related effects',
                    'action': 'Inform manager if taking medicines that may impair work'
                },
                {
                    'policy': 'Impaired Workers',
                    'action': 'Report to Team Leader or Project Manager immediately',
                    'safety': 'Impaired workers put themselves and others at risk'
                },
                {
                    'policy': 'Random Testing',
                    'frequency': 'Ongoing throughout year',
                    'consequence': 'Positive test = immediate action under P008 Drug & Alcohol Policy'
                }
            ]
        },
        
        'clearance_requirements': {
            'title': 'SA DIT Field Guide - Clearance Requirements',
            'critical_rule': 'Minimum 3m clearance from live traffic to work area',
            'requirements': [
                {
                    'condition': 'Clearance ≥ 3m',
                    'requirement': 'Standard traffic control devices (cones/bollards)',
                    'additional': 'High-vis PPE mandatory'
                },
                {
                    'condition': 'Clearance < 3m',
                    'requirement': 'CONTAINMENT FENCING MANDATORY',
                    'type': 'Chain mesh or similar physical barrier',
                    'purpose': 'Prevent encroachment into work area',
                    'additional': 'Enhanced PPE + physical barriers'
                }
            ]
        },
        
        'risk_assessment': {
            'title': 'Risk Assessment (MANDATORY)',
            'timing': 'BEFORE work commences',
            'requirements': [
                'Identify all hazards at work site',
                'Assess risk level for each hazard',
                'Implement control measures',
                'Document all findings in JSA/SWMS',
                'Review throughout shift as conditions change',
                'Update if new hazards identified'
            ],
            'permit_requirement': 'Risk assessment required for TMC permit approval'
        },
        
        'traffic_controller_requirements': {
            'title': 'Traffic Controller Requirements (SA DIT Field Guide)',
            'when_required': 'One-lane operations, complex layouts, high-risk situations',
            'minimum_controllers': {
                'one_lane_operation': 2, # Both ends
                'complex_sites': 'As per risk assessment'
            },
            'requirements': [
                {
                    'requirement': 'Accreditation',
                    'details': 'Current traffic controller accreditation required',
                    'standard': 'SA Works Zone Traffic Management standards'
                },
                {
                    'requirement': 'Stop/Slow Batons',
                    'details': 'MANDATORY for traffic control',
                    'standard': 'AS 1742.3 compliant batons'
                },
                {
                    'requirement': 'Communication',
                    'methods': ['UHF radio (preferred)', 'Visual sight line'],
                    'minimum_sight': '150m minimum sight distance'
                },
                {
                    'requirement': 'Positioning',
                    'clearance': '1.5m minimum from live traffic lane',
                    'escape_route': 'REQUIRED at all positions',
                    'visibility': 'High-vis clothing mandatory'
                },
                {
                    'requirement': 'Breaks',
                    'details': 'Regular breaks required (every 2 hours recommended)',
                    'reason': 'Maintain alertness and safety'
                }
            ]
        },
        
        'permit_requirements': {
            'title': 'DIT Traffic Management Centre (TMC) Permit',
            'when_required': 'Work on DIT-managed roads',
            'contact': {
                'centre': 'DIT Traffic Management Centre',
                'availability': '24/7',
                'phone': '1300 TRAFFIC',
                'requirement': 'Permit MUST be obtained before work commences'
            },
            'permit_conditions': [
                'Risk assessment completed and documented',
                'Traffic control plan approved',
                'All workers accredited/trained',
                'Equipment complies with standards',
                'Insurance and liability coverage current',
                'Emergency contact procedures in place'
            ]
        },
        
        'speed_limits': {
            'title': 'Work Zone Speed Limits (SA DIT Field Guide)',
            'default_limit': {
                'speed': 40, # km/h
                'description': 'Default work zone speed limit',
                'signage': 'Temporary speed limit signs required'
            },
            'high_hazard_limit': {
                'speed': 25, # km/h
                'when': 'High hazard situations (workers in lane, heavy plant, limited visibility)',
                'description': 'Enhanced safety speed limit',
                'signage': 'Multiple speed limit signs + warning signs'
            }
        },
        
        'environmental_compliance': {
            'title': 'Environmental Compliance (Policy P003)',
            'requirements': [
                'Dust suppression measures where required',
                'No littering or pollution',
                'Proper waste disposal',
                'Spill prevention and management',
                'Noise control during restricted hours',
                'Protection of vegetation and waterways'
            ]
        },
        
        'vehicle_management': {
            'title': 'Vehicle Management',
            'requirements': [
                {
                    'rule': 'Vehicle Idling',
                    'requirement': 'NOT permitted for long periods',
                    'action': 'Switch off vehicles to prevent damage',
                    'review': 'Excessive idling reviewed individually'
                },
                {
                    'rule': 'Vehicle Maintenance',
                    'requirement': 'Weekly checklist completion (Mondays)',
                    'reporting': 'All maintenance issues to site supervisor',
                    'prohibition': 'No unauthorized maintenance'
                },
                {
                    'rule': 'Restocking',
                    'requirement': 'Utes restocked at end of shift',
                    'accountability': 'No excuses for returning to yard to restock'
                }
            ]
        },
        
        'incident_management': {
            'title': 'Site Incident Management',
            'immediate_action': 'Project Manager MUST be notified ASAP regardless of time',
            'requirements': [
                'Record ALL incident information',
                'Obtain details from all involved parties',
                'Complete incident report on Actiond thoroughly',
                'Take time to provide all required information',
                'Contact office if unsure of procedures',
                'Refer to PR09 Incident Management procedure'
            ],
            'types_to_report': [
                'Traffic incidents',
                'Near misses',
                'Injuries',
                'Property damage',
                'Equipment failure',
                'Public complaints',
                'Non-compliance events'
            ]
        },
        
        'metadata': {
            'standards_compliance': [
                'SA DIT Field Guide Version 9.1 2021',
                'AS 1742.3-2019 (Traffic Control Devices)',
                'AS/NZS 4602.1 (High-Vis Clothing)',
                'MTM SA Current Practices (September 2025)',
                'Work Health and Safety Regulations 2012'
            ],
            'review_date': datetime.now().isoformat(),
            'mandatory_status': 'ALL REQUIREMENTS MANDATORY',
            'enforcement': 'Non-compliance may result in permit suspension, fines, or site shutdown'
        }
    }


def generate_daily_checklist() -> Dict:
    """Generate daily site checklist"""
    
    return {
        'title': 'Daily Pre-Start Checklist',
        'completion': 'MANDATORY - Complete before commencing work',
        
        'checklist_items': [
            {
                'category': 'Documentation',
                'items': [
                    {'item': 'JSA completed and signed', 'mandatory': True},
                    {'item': 'SWMS completed (on-site only)', 'mandatory': True},
                    {'item': 'Fitness for Work form completed', 'mandatory': True},
                    {'item': 'Job docket created for site', 'mandatory': True},
                    {'item': 'Permit number confirmed', 'mandatory': True}
                ]
            },
            {
                'category': 'PPE Check',
                'items': [
                    {'item': 'High-vis shirt with reflective tape', 'mandatory': True},
                    {'item': 'High-vis pants with reflective tape', 'mandatory': True},
                    {'item': 'Hard hat', 'mandatory': True},
                    {'item': 'Gloves', 'mandatory': True},
                    {'item': 'Steel-capped boots', 'mandatory': True},
                    {'item': 'Safety glasses', 'mandatory': True},
                    {'item': 'UHF radio charged', 'mandatory': True}
                ]
            },
            {
                'category': 'Vehicle & Equipment',
                'items': [
                    {'item': 'Vehicle pre-start inspection', 'mandatory': True},
                    {'item': 'Traffic control devices loaded', 'mandatory': True},
                    {'item': 'Signs clean and visible', 'mandatory': True},
                    {'item': 'Cones/bollards sufficient quantity', 'mandatory': True},
                    {'item': 'Stop/Slow batons (if TC role)', 'mandatory': True}
                ]
            },
            {
                'category': 'Site Assessment',
                'items': [
                    {'item': 'Risk assessment completed', 'mandatory': True},
                    {'item': 'Escape route identified', 'mandatory': True},
                    {'item': 'Clearance measurements confirmed (≥3m)', 'mandatory': True},
                    {'item': 'Weather conditions assessed', 'mandatory': True},
                    {'item': 'Traffic volumes observed', 'mandatory': True}
                ]
            },
            {
                'category': 'Communication',
                'items': [
                    {'item': 'UHF radio tested', 'mandatory': True},
                    {'item': 'Team members briefed', 'mandatory': True},
                    {'item': 'TMC/Client contact confirmed', 'mandatory': True},
                    {'item': 'Emergency contacts known', 'mandatory': True}
                ]
            }
        ],
        
        'sign_off': {
            'site_supervisor': {'name': '', 'signature': '', 'time': ''},
            'workers': [],
            'date': datetime.now().strftime('%d/%m/%Y')
        }
    }
