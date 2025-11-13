"""
Risk Assessment Module
Automated hazard identification and risk matrix generation
Based on SA DIT Field Guide and WHS Regulations
"""

from typing import Dict, List, Tuple


def generate_risk_assessment(
    work_type: str,
    road_classification: str,
    speed_limit: int,
    traffic_volume: int,
    clearance: float,
    weather_conditions: str = 'normal'
) -> Dict:
    """
    Generate comprehensive risk assessment for TMP
    
    Args:
        work_type: Type of work being conducted
        road_classification: Road type
        speed_limit: Posted speed limit
        traffic_volume: AADT
        clearance: Distance from traffic to work area
        weather_conditions: Current/expected weather
        
    Returns:
        Complete risk assessment with controls
    """
    
    # Identify hazards based on work parameters
    hazards = identify_hazards(
        work_type, road_classification, speed_limit, 
        traffic_volume, clearance, weather_conditions
    )
    
    # Assess each hazard
    risk_matrix = []
    for hazard in hazards:
        risk = assess_risk(hazard, speed_limit, traffic_volume, clearance)
        risk_matrix.append(risk)
    
    # Sort by risk level
    risk_matrix.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return {
        'risk_assessment_title': 'Traffic Management Risk Assessment',
        'assessment_date': 'To be completed before work commences',
        'reviewed_by': '',
        'approved_by': '',
        
        'site_parameters': {
            'work_type': work_type,
            'road_classification': road_classification,
            'speed_limit': speed_limit,
            'traffic_volume': traffic_volume,
            'clearance_distance': clearance,
            'weather_conditions': weather_conditions
        },
        
        'risk_matrix_legend': {
            'consequence': {
                '1': 'Insignificant - Minor injury, no lost time',
                '2': 'Minor - First aid treatment, possible lost time',
                '3': 'Moderate - Medical treatment required',
                '4': 'Major - Serious injury, extended hospitalization',
                '5': 'Catastrophic - Fatality or multiple serious injuries'
            },
            'likelihood': {
                '1': 'Rare - May occur in exceptional circumstances',
                '2': 'Unlikely - Could occur but not expected',
                '3': 'Possible - Might occur occasionally',
                '4': 'Likely - Will probably occur',
                '5': 'Almost Certain - Expected to occur frequently'
            },
            'risk_rating': {
                'Low': '1-4 (Green) - Manage with standard procedures',
                'Medium': '5-9 (Yellow) - Specific controls required',
                'High': '10-15 (Orange) - Senior approval required',
                'Extreme': '16-25 (Red) - Work cannot proceed without additional controls'
            }
        },
        
        'identified_hazards': risk_matrix,
        
        'overall_risk_level': calculate_overall_risk(risk_matrix),
        
        'mandatory_controls': generate_mandatory_controls(risk_matrix),
        
        'emergency_procedures': {
            'incident_response': [
                'Stop work immediately',
                'Ensure area is safe',
                'Provide first aid if required',
                'Call emergency services (000)',
                'Notify Project Manager',
                'Preserve incident scene',
                'Complete incident report'
            ],
            'emergency_contacts': {
                'emergency_services': '000',
                'dit_tmc': '1300 TRAFFIC',
                'project_manager': 'TBC',
                'site_supervisor': 'TBC'
            }
        },
        
        'sign_off': {
            'risk_assessor': {'name': '', 'signature': '', 'date': ''},
            'site_supervisor': {'name': '', 'signature': '', 'date': ''},
            'project_manager': {'name': '', 'signature': '', 'date': ''}
        }
    }


def identify_hazards(
    work_type: str,
    road_classification: str,
    speed_limit: int,
    traffic_volume: int,
    clearance: float,
    weather_conditions: str
) -> List[Dict]:
    """Identify relevant hazards based on work parameters"""
    
    hazards = []
    
    # Common hazards for all traffic management work
    hazards.extend([
        {
            'hazard': 'Vehicle incursion into work area',
            'description': 'Live traffic striking workers or equipment',
            'category': 'Traffic',
            'base_likelihood': 3,
            'base_consequence': 5
        },
        {
            'hazard': 'Worker struck by moving vehicle',
            'description': 'Pedestrian worker in proximity to live traffic',
            'category': 'Traffic',
            'base_likelihood': 2,
            'base_consequence': 5
        },
        {
            'hazard': 'Inadequate sight distance',
            'description': 'Insufficient warning for approaching traffic',
            'category': 'Traffic Control',
            'base_likelihood': 2,
            'base_consequence': 4
        }
    ])
    
    # Speed-related hazards
    if speed_limit >= 80:
        hazards.append({
            'hazard': 'High-speed traffic impact',
            'description': 'Increased severity of incidents at high speeds',
            'category': 'Speed',
            'base_likelihood': 2,
            'base_consequence': 5
        })
    
    # Clearance-related hazards
    if clearance < 3.0:
        hazards.append({
            'hazard': 'Insufficient clearance from traffic',
            'description': 'Workers within 3m of live traffic without containment',
            'category': 'Clearance',
            'base_likelihood': 4,
            'base_consequence': 5
        })
    
    # Traffic volume hazards
    if traffic_volume > 10000:
        hazards.append({
            'hazard': 'High traffic volume',
            'description': 'Increased exposure due to high traffic density',
            'category': 'Traffic Volume',
            'base_likelihood': 3,
            'base_consequence': 4
        })
    
    # Weather hazards
    if weather_conditions in ['rain', 'fog', 'night']:
        hazards.append({
            'hazard': 'Reduced visibility',
            'description': f'Poor visibility conditions ({weather_conditions})',
            'category': 'Environment',
            'base_likelihood': 3,
            'base_consequence': 4
        })
    
    # Work-specific hazards
    if 'excavation' in work_type.lower():
        hazards.extend([
            {
                'hazard': 'Underground services strike',
                'description': 'Contact with buried utilities',
                'category': 'Services',
                'base_likelihood': 2,
                'base_consequence': 5
            },
            {
                'hazard': 'Trench collapse',
                'description': 'Unstable excavation',
                'category': 'Ground',
                'base_likelihood': 2,
                'base_consequence': 4
            }
        ])
    
    if 'overhead' in work_type.lower() or 'elevated' in work_type.lower():
        hazards.append({
            'hazard': 'Overhead power lines',
            'description': 'Contact with energized conductors',
            'category': 'Services',
            'base_likelihood': 2,
            'base_consequence': 5
        })
    
    return hazards


def assess_risk(hazard: Dict, speed_limit: int, traffic_volume: int, clearance: float) -> Dict:
    """Assess risk level for identified hazard"""
    
    likelihood = hazard['base_likelihood']
    consequence = hazard['base_consequence']
    
    # Adjust likelihood based on conditions
    if speed_limit >= 80:
        likelihood = min(5, likelihood + 1)
    if traffic_volume > 15000:
        likelihood = min(5, likelihood + 1)
    if clearance < 2.0:
        likelihood = min(5, likelihood + 1)
    
    # Calculate risk score
    risk_score = likelihood * consequence
    
    # Determine risk rating
    if risk_score <= 4:
        risk_rating = 'Low'
        color = 'Green'
    elif risk_score <= 9:
        risk_rating = 'Medium'
        color = 'Yellow'
    elif risk_score <= 15:
        risk_rating = 'High'
        color = 'Orange'
    else:
        risk_rating = 'Extreme'
        color = 'Red'
    
    # Generate controls
    controls = generate_risk_controls(hazard, risk_rating)
    
    return {
        'hazard': hazard['hazard'],
        'description': hazard['description'],
        'category': hazard['category'],
        'likelihood': likelihood,
        'consequence': consequence,
        'risk_score': risk_score,
        'risk_rating': risk_rating,
        'risk_color': color,
        'existing_controls': controls['existing'],
        'additional_controls': controls['additional'],
        'residual_risk': calculate_residual_risk(risk_score, len(controls['existing']) + len(controls['additional']))
    }


def generate_risk_controls(hazard: Dict, risk_rating: str) -> Dict:
    """Generate control measures for hazard"""
    
    controls = {
        'existing': [],
        'additional': []
    }
    
    # Standard controls for all traffic hazards
    if hazard['category'] == 'Traffic':
        controls['existing'] = [
            'High-visibility PPE (AS/NZS 4602.1)',
            'Traffic control plan implemented',
            'Advance warning signage (AS 1742.3)',
            'Traffic management training completed',
            'Site induction completed'
        ]
        
        if risk_rating in ['High', 'Extreme']:
            controls['additional'] = [
                'Physical barriers/containment fencing',
                'Traffic controllers deployed',
                'Reduced speed limit through work zone',
                'Enhanced lighting for night work',
                'Regular toolbox talks on traffic hazards'
            ]
    
    # Clearance controls
    if 'clearance' in hazard['hazard'].lower():
        controls['existing'].append('Minimum 3m clearance maintained')
        controls['additional'] = [
            'Containment fencing (chain mesh)',
            'Concrete barriers if clearance < 2m',
            'Additional high-vis personnel',
            'Spotter/banksman assigned'
        ]
    
    # High-speed controls
    if hazard['category'] == 'Speed':
        controls['additional'] = [
            'Temporary speed limit reduction',
            'Multiple advance warning signs',
            'Enhanced delineation (additional cones)',
            'Active warning devices (flashing lights)',
            'Traffic controller presence'
        ]
    
    # Underground services
    if 'services' in hazard['category'].lower() and 'underground' in hazard['description'].lower():
        controls['existing'] = [
            'Dial Before You Dig (1100) completed',
            'Service plans obtained',
            'Services marked on ground',
            'Hand excavation near services'
        ]
        controls['additional'] = [
            'Service location verification (potholing)',
            'Exclusion zones around services',
            'Qualified personnel for service work',
            'Emergency procedures for service strike'
        ]
    
    return controls


def calculate_residual_risk(initial_risk: int, controls_count: int) -> Dict:
    """Calculate residual risk after controls"""
    
    # Risk reduction based on number of controls
    reduction_factor = min(0.7, controls_count * 0.1)
    residual_score = int(initial_risk * (1 - reduction_factor))
    
    if residual_score <= 4:
        rating = 'Low'
    elif residual_score <= 9:
        rating = 'Medium'
    elif residual_score <= 15:
        rating = 'High'
    else:
        rating = 'Extreme'
    
    return {
        'score': residual_score,
        'rating': rating,
        'acceptable': residual_score <= 9
    }


def calculate_overall_risk(risk_matrix: List[Dict]) -> str:
    """Calculate overall risk level for work"""
    
    extreme_count = sum(1 for r in risk_matrix if r['risk_rating'] == 'Extreme')
    high_count = sum(1 for r in risk_matrix if r['risk_rating'] == 'High')
    
    if extreme_count > 0:
        return 'Extreme - Work cannot proceed without additional controls and senior approval'
    elif high_count >= 3:
        return 'High - Significant controls required, PM approval needed'
    elif high_count > 0:
        return 'High-Medium - Enhanced controls required'
    else:
        return 'Medium-Low - Standard traffic management controls adequate'


def generate_mandatory_controls(risk_matrix: List[Dict]) -> List[str]:
    """Generate list of mandatory controls based on identified risks"""
    
    mandatory = set()
    
    for risk in risk_matrix:
        if risk['risk_rating'] in ['High', 'Extreme']:
            mandatory.update(risk['additional_controls'])
        mandatory.update(risk['existing_controls'])
    
    return sorted(list(mandatory))
