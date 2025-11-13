"""
Permit Management System
DIT TMC Permit application and tracking
Based on Crittendan Road example and DIT requirements
"""

from datetime import datetime, timedelta
from typing import Dict, List


def generate_permit_application(
    location: str,
    work_type: str,
    start_date: str,
    end_date: str,
    work_hours: str,
    applicant_details: Dict
) -> Dict:
    """
    Generate DIT Traffic Management Centre permit application
    
    Args:
        location: Work location
        work_type: Type of work
        start_date: Commencement date
        end_date: Completion date
        work_hours: Working hours
        applicant_details: Company and contact information
        
    Returns:
        Complete permit application structure
    """
    
    return {
        'permit_application': {
            'application_id': f"TMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'submission_date': datetime.now().strftime('%d/%m/%Y'),
            'status': 'Draft - Pending Submission'
        },
        
        'authority_information': {
            'issuing_authority': 'Department for Infrastructure and Transport (DIT)',
            'traffic_management_centre': {
                'name': 'DIT Traffic Management Centre (TMC)',
                'phone': '1300 TRAFFIC (1300 872 334)',
                'availability': '24/7 operations',
                'email': 'tmc@sa.gov.au',
                'address': 'Walkley Heights, Adelaide SA'
            },
            'permit_requirement': 'MANDATORY for works on DIT-managed roads',
            'processing_time': '5-10 business days (allow more for complex works)'
        },
        
        'applicant_details': {
            'company_name': applicant_details.get('company_name', ''),
            'abn': applicant_details.get('abn', ''),
            'contact_person': applicant_details.get('contact_person', ''),
            'phone': applicant_details.get('phone', ''),
            'email': applicant_details.get('email', ''),
            'address': applicant_details.get('address', '')
        },
        
        'work_details': {
            'location': location,
            'work_type': work_type,
            'description': '',
            'start_date': start_date,
            'end_date': end_date,
            'work_hours': work_hours,
            'out_of_hours': 'Yes/No - to be specified',
            'weekend_work': 'Yes/No - to be specified'
        },
        
        'traffic_management_details': {
            'traffic_control_required': True,
            'lane_closures': 'Yes/No/Partial',
            'traffic_controllers_required': 'Yes/No',
            'number_of_controllers': '',
            'detour_required': 'Yes/No',
            'continuous_traffic_flow': 'Must be maintained at all times',
            'speed_limit_changes': 'Yes/No - specify if required'
        },
        
        'critical_dit_requirements': {
            'tmp_responsibility': {
                'statement': 'DIT does NOT review or approve TMPs or TGS',
                'applicant_responsibility': 'Applicant is solely responsible for TMP and TGS compliance',
                'standards': 'Must comply with SA Standards for Workzone Traffic Management Section 5.3'
            },
            'traffic_flow': {
                'requirement': 'Continuous traffic flow MUST be maintained',
                'no_closures': 'No lane closures without specific approval',
                'one_lane_operations': 'Stop/slow control only with approval'
            },
            'worker_accreditation': {
                'requirement': 'All traffic controllers must be accredited',
                'standard': 'SA Works Zone Traffic Management',
                'verification': 'Accreditation records must be available on site'
            },
            'roadworks_app': {
                'requirement': 'MANDATORY logging in Roadworks Awareness App',
                'purpose': 'Real-time notification to road users',
                'timing': 'Must be logged before work commences'
            }
        },
        
        'permit_conditions': [
            {
                'condition': 'Compliance with Standards',
                'requirement': 'All work must comply with AS 1742.3 and SA DIT Field Guide',
                'mandatory': True
            },
            {
                'condition': 'Traffic Management Plan',
                'requirement': 'Approved TMP must be on-site and followed',
                'mandatory': True
            },
            {
                'condition': 'Risk Assessment',
                'requirement': 'Complete risk assessment before work commences',
                'mandatory': True
            },
            {
                'condition': 'Insurance',
                'requirement': 'Public liability insurance minimum $20 million',
                'mandatory': True
            },
            {
                'condition': '24/7 Contact',
                'requirement': 'Provide 24/7 emergency contact number',
                'mandatory': True
            },
            {
                'condition': 'Site Restoration',
                'requirement': 'Site must be restored to pre-work condition',
                'mandatory': True
            },
            {
                'condition': 'Notification',
                'requirement': 'Notify TMC of any incidents or changes',
                'mandatory': True
            },
            {
                'condition': 'Permit Display',
                'requirement': 'Permit number must be displayed on-site',
                'mandatory': True
            }
        ],
        
        'required_documentation': [
            {
                'document': 'Traffic Management Plan (TMP)',
                'status': 'Required',
                'notes': 'Site-specific TMP prepared by applicant'
            },
            {
                'document': 'Traffic Guidance Scheme (TGS)',
                'status': 'Required',
                'notes': 'Detailed layout drawings'
            },
            {
                'document': 'Risk Assessment',
                'status': 'Required',
                'notes': 'Comprehensive hazard identification and controls'
            },
            {
                'document': 'Traffic Controller Accreditation',
                'status': 'Required',
                'notes': 'Copies of current accreditations'
            },
            {
                'document': 'Insurance Certificate',
                'status': 'Required',
                'notes': 'Public liability minimum $20M'
            },
            {
                'document': 'Company Safety Policy',
                'status': 'Recommended',
                'notes': 'Company WHS policy'
            },
            {
                'document': 'Emergency Response Plan',
                'status': 'Recommended',
                'notes': 'Incident management procedures'
            }
        ],
        
        'approval_process': {
            'step_1': {
                'action': 'Submit application to DIT TMC',
                'method': 'Email or online portal',
                'documents': 'Include all required documentation'
            },
            'step_2': {
                'action': 'TMC reviews application',
                'timeframe': '5-10 business days',
                'outcome': 'Approved, Approved with conditions, or Rejected'
            },
            'step_3': {
                'action': 'Receive permit number',
                'format': 'DIT-TMP-YYYYMMDD-XXX',
                'validity': 'Valid for dates specified in application'
            },
            'step_4': {
                'action': 'Log works in Roadworks App',
                'timing': 'Before commencing work',
                'update': 'Update daily if required'
            },
            'step_5': {
                'action': 'Commence work',
                'requirements': 'Permit on-site, TMP followed, contacts available'
            }
        },
        
        'fees': {
            'application_fee': 'As per DIT fee schedule',
            'bond': 'May be required for significant works',
            'payment_method': 'Invoice or direct payment',
            'gst': 'GST applicable'
        },
        
        'permit_variations': {
            'when_required': [
                'Change to work dates',
                'Change to work hours',
                'Change to traffic management approach',
                'Extension of permit period',
                'Significant scope changes'
            ],
            'process': 'Submit variation request to TMC with justification',
            'approval': 'TMC approval required before implementing changes'
        },
        
        'compliance_monitoring': {
            'dit_inspections': 'DIT officers may inspect work sites without notice',
            'non_compliance': 'Permit may be suspended or revoked',
            'penalties': 'Fines and legal action for serious breaches',
            'reporting': 'All incidents must be reported to TMC within 24 hours'
        },
        
        'permit_closure': {
            'completion_notification': 'Notify TMC when works complete',
            'final_inspection': 'May be required',
            'site_restoration': 'Confirm site restored',
            'roadworks_app': 'Remove from Roadworks App',
            'bond_release': 'If applicable, after final inspection'
        },
        
        'emergency_contacts': {
            'dit_tmc_24_7': '1300 TRAFFIC (1300 872 334)',
            'police': '131 444 (non-emergency)',
            'emergency_services': '000',
            'sa_power_networks': '13 12 61',
            'sa_water': '1300 SA WATER'
        },
        
        'declaration': {
            'statement': 'I declare that the information provided is true and correct. I understand that I am solely responsible for the Traffic Management Plan and Traffic Guidance Scheme, and that DIT does not review or approve these documents. I acknowledge that I must comply with all relevant standards and regulations.',
            'name': '',
            'position': '',
            'signature': '',
            'date': ''
        },
        
        'metadata': {
            'form_version': '2025.1',
            'generated': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
        }
    }


def generate_permit_checklist() -> Dict:
    """Generate permit application checklist"""
    
    return {
        'title': 'DIT TMC Permit Application Checklist',
        'subtitle': 'Complete ALL items before submission',
        
        'checklist': [
            {
                'category': 'Application Form',
                'items': [
                    {'item': 'All sections completed', 'status': '☐'},
                    {'item': 'Applicant details accurate', 'status': '☐'},
                    {'item': 'Work dates confirmed', 'status': '☐'},
                    {'item': 'Declaration signed', 'status': '☐'}
                ]
            },
            {
                'category': 'Traffic Management Plan',
                'items': [
                    {'item': 'Site-specific TMP prepared', 'status': '☐'},
                    {'item': 'AS 1742.3 compliant', 'status': '☐'},
                    {'item': 'SA DIT Field Guide followed', 'status': '☐'},
                    {'item': 'All sections complete', 'status': '☐'},
                    {'item': 'Emergency contacts included', 'status': '☐'}
                ]
            },
            {
                'category': 'Traffic Guidance Scheme',
                'items': [
                    {'item': 'Detailed layout drawings', 'status': '☐'},
                    {'item': 'Device specifications', 'status': '☐'},
                    {'item': 'Distances documented', 'status': '☐'},
                    {'item': 'Sign schedule included', 'status': '☐'}
                ]
            },
            {
                'category': 'Risk Assessment',
                'items': [
                    {'item': 'All hazards identified', 'status': '☐'},
                    {'item': 'Risk ratings assigned', 'status': '☐'},
                    {'item': 'Control measures documented', 'status': '☐'},
                    {'item': 'Signed by supervisor', 'status': '☐'}
                ]
            },
            {
                'category': 'Worker Qualifications',
                'items': [
                    {'item': 'Traffic controller accreditations current', 'status': '☐'},
                    {'item': 'Copies of certificates attached', 'status': '☐'},
                    {'item': 'Workers inducted', 'status': '☐'}
                ]
            },
            {
                'category': 'Insurance & Liability',
                'items': [
                    {'item': 'Public liability certificate (min $20M)', 'status': '☐'},
                    {'item': 'Workers compensation current', 'status': '☐'},
                    {'item': 'Professional indemnity (if applicable)', 'status': '☐'}
                ]
            },
            {
                'category': 'Roadworks App',
                'items': [
                    {'item': 'Account created/verified', 'status': '☐'},
                    {'item': 'Work location mapped', 'status': '☐'},
                    {'item': 'Ready to log before commencement', 'status': '☐'}
                ]
            },
            {
                'category': '24/7 Contacts',
                'items': [
                    {'item': 'Emergency contact number provided', 'status': '☐'},
                    {'item': 'Site supervisor contact', 'status': '☐'},
                    {'item': 'After-hours contact', 'status': '☐'}
                ]
            }
        ],
        
        'final_check': {
            'all_documents_attached': '☐',
            'application_fee_paid': '☐',
            'ready_for_submission': '☐'
        }
    }
