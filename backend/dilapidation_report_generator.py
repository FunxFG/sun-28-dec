"""
Dilapidation Report Generator
Pre-work and post-work road condition assessment
Based on professional TMP requirements (Tailem Bend Solar example)
"""

from datetime import datetime
from typing import Dict, List


def generate_dilapidation_report(
    location: str,
    report_type: str = 'pre-construction',
    inspector_name: str = '',
    photos: List[Dict] = None
) -> Dict:
    """
    Generate comprehensive dilapidation report
    
    Args:
        location: Road/site location
        report_type: 'pre-construction' or 'post-construction'
        inspector_name: Name of inspector
        photos: List of photo references with GPS coordinates
        
    Returns:
        Structured dilapidation report
    """
    
    if photos is None:
        photos = []
    
    return {
        'report_title': f'{report_type.upper().replace("-", " ")} DILAPIDATION REPORT',
        'location': location,
        'report_type': report_type,
        'inspection_date': datetime.now().strftime('%d/%m/%Y'),
        'inspection_time': datetime.now().strftime('%H:%M'),
        'inspector': inspector_name,
        
        'purpose': {
            'pre-construction': 'Document existing road conditions before construction activities commence to establish baseline for post-work comparison and rehabilitation requirements.',
            'post-construction': 'Document road conditions after construction completion to assess impact and determine rehabilitation requirements as per pre-construction baseline.'
        }.get(report_type, 'Road condition assessment'),
        
        'inspection_methodology': {
            'visual_inspection': 'Complete visual assessment of road surface, edges, drainage',
            'photo_documentation': 'Time-stamped, GPS-tagged photographs at regular intervals',
            'defect_identification': 'Classification of all existing defects by type and severity',
            'measurement': 'Dimensions recorded for significant defects',
            'reference_markers': 'Chainage or landmark-based positioning system'
        },
        
        'defect_categories': [
            {
                'category': 'Pavement Defects',
                'types': [
                    {
                        'defect': 'Rutting',
                        'severity_levels': {
                            'Low': '< 10mm depth',
                            'Medium': '10-20mm depth',
                            'High': '> 20mm depth'
                        },
                        'intervention': 'Repair if High severity or Medium with active deterioration'
                    },
                    {
                        'defect': 'Potholes',
                        'severity_levels': {
                            'Low': '< 50mm diameter, < 20mm deep',
                            'Medium': '50-200mm diameter, 20-50mm deep',
                            'High': '> 200mm diameter or > 50mm deep'
                        },
                        'intervention': 'Immediate repair for Medium and High'
                    },
                    {
                        'defect': 'Cracking',
                        'types': ['Longitudinal', 'Transverse', 'Alligator', 'Edge'],
                        'severity_levels': {
                            'Low': 'Hairline cracks, < 3mm width',
                            'Medium': '3-10mm width, some ravelling',
                            'High': '> 10mm width, significant ravelling'
                        },
                        'intervention': 'Seal Low, repair Medium and High'
                    },
                    {
                        'defect': 'Surface Deterioration',
                        'types': ['Ravelling', 'Bleeding', 'Stripping', 'Polishing'],
                        'intervention': 'Based on extent and traffic volume'
                    }
                ]
            },
            {
                'category': 'Edge Defects',
                'types': [
                    {
                        'defect': 'Edge Break',
                        'measurement': 'Width and length of break',
                        'intervention': 'Repair if > 150mm width or safety concern'
                    },
                    {
                        'defect': 'Shoulder Drop-off',
                        'measurement': 'Height of drop',
                        'severity_levels': {
                            'Low': '< 50mm',
                            'Medium': '50-100mm',
                            'High': '> 100mm (safety hazard)'
                        },
                        'intervention': 'Immediate action for High'
                    }
                ]
            },
            {
                'category': 'Drainage Defects',
                'types': [
                    {
                        'defect': 'Table Drain Blockage',
                        'assessment': 'Percentage blocked',
                        'intervention': 'Clear if > 50% blocked'
                    },
                    {
                        'defect': 'Scour',
                        'assessment': 'Extent and depth',
                        'intervention': 'Stabilization required'
                    },
                    {
                        'defect': 'Ponding',
                        'assessment': 'Area and depth',
                        'intervention': 'Drainage improvement required'
                    }
                ]
            },
            {
                'category': 'Other Infrastructure',
                'types': [
                    'Guideposts (damaged/missing)',
                    'Signs (damaged/faded)',
                    'Line marking (faded/damaged)',
                    'Culverts (blocked/damaged)',
                    'Bridges (structural issues)',
                    'Guard rails (damaged)'
                ]
            }
        ],
        
        'inspection_results': {
            'overall_condition': '',  # Excellent/Good/Fair/Poor
            'defects_identified': [],  # List of specific defects
            'photos': photos,
            'summary': '',
            'recommendations': []
        },
        
        'intervention_levels': {
            'immediate': {
                'timeframe': '24 hours',
                'triggers': [
                    'Safety hazard to road users',
                    'Potholes > 200mm diameter',
                    'Shoulder drop-off > 100mm',
                    'Surface failures affecting traffic'
                ]
            },
            'short_term': {
                'timeframe': '1-4 weeks',
                'triggers': [
                    'Medium severity defects',
                    'Progressive deterioration',
                    'Multiple minor defects'
                ]
            },
            'long_term': {
                'timeframe': '1-12 months',
                'triggers': [
                    'Low severity defects',
                    'Preventative maintenance',
                    'Scheduled rehabilitation'
                ]
            }
        },
        
        'inspection_checklist': [
            {'item': 'Sealed pavement condition', 'status': '', 'notes': ''},
            {'item': 'Unsealed surface condition (if applicable)', 'status': '', 'notes': ''},
            {'item': 'Edge condition both sides', 'status': '', 'notes': ''},
            {'item': 'Shoulder condition', 'status': '', 'notes': ''},
            {'item': 'Drainage infrastructure', 'status': '', 'notes': ''},
            {'item': 'Line marking quality', 'status': '', 'notes': ''},
            {'item': 'Signage condition', 'status': '', 'notes': ''},
            {'item': 'Guideposts', 'status': '', 'notes': ''},
            {'item': 'Vegetation encroachment', 'status': '', 'notes': ''},
            {'item': 'Structural elements (bridges, culverts)', 'status': '', 'notes': ''}
        ],
        
        'photo_requirements': {
            'frequency': 'Every 100-200m along route',
            'minimum_photos': [
                'Overall road condition (wide shot)',
                'Each identified defect (close-up)',
                'Edge conditions both sides',
                'Drainage structures',
                'Signage and infrastructure',
                'Reference markers/chainages'
            ],
            'photo_metadata': {
                'timestamp': 'MANDATORY',
                'gps_coordinates': 'MANDATORY',
                'chainage_reference': 'Recommended',
                'description': 'Required for each photo'
            }
        },
        
        'rehabilitation_commitment': {
            'pre-construction': 'Baseline established for post-construction comparison',
            'post-construction': 'Rehabilitation to pre-construction condition or better',
            'responsibility': 'Contractor responsible for construction-related deterioration',
            'dispute_resolution': 'Pre-construction photos are reference for claims',
            'timeframe': 'Defect rectification within agreed timeframe (typically 30 days)'
        },
        
        'sign_off': {
            'inspector': {'name': inspector_name, 'signature': '', 'date': ''},
            'contractor': {'name': '', 'signature': '', 'date': ''},
            'client': {'name': '', 'signature': '', 'date': ''},
            'authority': {'name': '', 'signature': '', 'date': ''}
        },
        
        'attachments': {
            'photos': f'{len(photos)} photos attached',
            'maps': 'Route map with photo locations',
            'defect_register': 'Detailed defect listing with locations'
        },
        
        'metadata': {
            'report_version': '1.0',
            'generated': datetime.now().isoformat(),
            'standard': 'Based on ARRB Road Condition Assessment standards',
            'next_inspection': 'Post-construction (at completion of works)'
        }
    }


def calculate_defect_severity_score(defects: List[Dict]) -> Dict:
    """Calculate overall severity score based on defects"""
    
    severity_weights = {'Low': 1, 'Medium': 3, 'High': 5}
    total_score = 0
    defect_count = {'Low': 0, 'Medium': 0, 'High': 0}
    
    for defect in defects:
        severity = defect.get('severity', 'Low')
        defect_count[severity] = defect_count.get(severity, 0) + 1
        total_score += severity_weights.get(severity, 1)
    
    # Overall condition rating
    if total_score == 0:
        condition = 'Excellent'
    elif total_score <= 5:
        condition = 'Good'
    elif total_score <= 15:
        condition = 'Fair'
    else:
        condition = 'Poor'
    
    return {
        'overall_condition': condition,
        'severity_score': total_score,
        'defect_breakdown': defect_count,
        'intervention_required': total_score > 10
    }
