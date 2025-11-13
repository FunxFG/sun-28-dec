"""
Traffic Volume Calculator
Estimates AADT, construction traffic, and impact assessment
Based on Tailem Bend Solar TMP structure
"""

from typing import Dict, List
import math


def calculate_traffic_volumes(
    road_type: str,
    location_type: str,
    existing_aadt: int = None,
    commercial_percentage: float = None
) -> Dict:
    """
    Calculate and estimate traffic volumes for TMP
    
    Args:
        road_type: 'arterial', 'collector', 'local', 'highway'
        location_type: 'urban', 'rural', 'regional'
        existing_aadt: Known AADT value (optional)
        commercial_percentage: Known commercial % (optional)
        
    Returns:
        Comprehensive traffic volume analysis
    """
    
    # Default AADT estimates by road type and location
    aadt_defaults = {
        'highway': {'urban': 15000, 'rural': 5000, 'regional': 8000},
        'arterial': {'urban': 10000, 'rural': 3000, 'regional': 5000},
        'collector': {'urban': 5000, 'rural': 1500, 'regional': 2500},
        'local': {'urban': 2000, 'rural': 500, 'regional': 1000}
    }
    
    # Default commercial vehicle percentages
    commercial_defaults = {
        'highway': {'urban': 15, 'rural': 20, 'regional': 18},
        'arterial': {'urban': 10, 'rural': 15, 'regional': 12},
        'collector': {'urban': 8, 'rural': 12, 'regional': 10},
        'local': {'urban': 5, 'rural': 8, 'regional': 6}
    }
    
    # Use provided values or defaults
    if existing_aadt is None:
        existing_aadt = aadt_defaults.get(road_type, {}).get(location_type, 2000)
    
    if commercial_percentage is None:
        commercial_percentage = commercial_defaults.get(road_type, {}).get(location_type, 10)
    
    # Calculate daily volumes
    peak_hour_factor = 0.10  # Typically 10% of AADT in peak hour
    peak_hour_volume = int(existing_aadt * peak_hour_factor)
    
    commercial_vehicles_daily = int(existing_aadt * (commercial_percentage / 100))
    light_vehicles_daily = existing_aadt - commercial_vehicles_daily
    
    # Peak hour breakdown
    peak_hour_commercial = int(peak_hour_volume * (commercial_percentage / 100))
    peak_hour_light = peak_hour_volume - peak_hour_commercial
    
    return {
        'existing_traffic': {
            'aadt': existing_aadt,
            'description': f'Average Annual Daily Traffic: {existing_aadt:,} vehicles per day',
            'peak_hour_volume': peak_hour_volume,
            'peak_hour_description': f'Peak hour: {peak_hour_volume:,} vehicles (typically 7-9am or 4-6pm)',
            'commercial_percentage': commercial_percentage,
            'commercial_vehicles_daily': commercial_vehicles_daily,
            'light_vehicles_daily': light_vehicles_daily,
            'peak_hour_commercial': peak_hour_commercial,
            'peak_hour_light': peak_hour_light
        },
        
        'road_classification': {
            'type': road_type,
            'location': location_type,
            'traffic_category': categorize_traffic_volume(existing_aadt)
        },
        
        'data_source': 'Estimated based on road classification' if existing_aadt is None else 'Provided AADT data'
    }


def estimate_construction_traffic(
    project_duration_months: int,
    construction_type: str,
    project_size: str = 'medium'
) -> Dict:
    """
    Estimate construction traffic generation
    
    Args:
        project_duration_months: Duration in months
        construction_type: 'solar', 'wind', 'residential', 'commercial', 'infrastructure'
        project_size: 'small', 'medium', 'large'
        
    Returns:
        Construction traffic estimates
    """
    
    # Construction traffic multipliers
    multipliers = {
        'solar': {'small': 50, 'medium': 100, 'large': 200},
        'wind': {'small': 30, 'medium': 60, 'large': 120},
        'residential': {'small': 40, 'medium': 80, 'large': 150},
        'commercial': {'small': 60, 'medium': 120, 'large': 250},
        'infrastructure': {'small': 80, 'medium': 150, 'large': 300}
    }
    
    daily_vehicles = multipliers.get(construction_type, {}).get(project_size, 100)
    
    # Peak construction period (typically middle 50% of project)
    peak_months = int(project_duration_months * 0.5)
    peak_daily_vehicles = int(daily_vehicles * 1.5)
    
    # Vehicle breakdown
    heavy_vehicles_percentage = 60  # Typically 60% heavy in construction
    heavy_vehicles_daily = int(daily_vehicles * 0.6)
    light_vehicles_daily = daily_vehicles - heavy_vehicles_daily
    
    return {
        'construction_phase': {
            'duration_months': project_duration_months,
            'construction_type': construction_type,
            'project_size': project_size
        },
        
        'average_construction_traffic': {
            'daily_total': daily_vehicles,
            'heavy_vehicles': heavy_vehicles_daily,
            'light_vehicles': light_vehicles_daily,
            'heavy_percentage': heavy_vehicles_percentage
        },
        
        'peak_construction_traffic': {
            'peak_period': f'{peak_months} months (middle of project)',
            'daily_total': peak_daily_vehicles,
            'heavy_vehicles': int(peak_daily_vehicles * 0.6),
            'light_vehicles': int(peak_daily_vehicles * 0.4)
        },
        
        'monthly_movements': {
            'truck_movements': heavy_vehicles_daily * 22,  # 22 working days/month
            'light_vehicle_movements': light_vehicles_daily * 22,
            'total_monthly': daily_vehicles * 22
        },
        
        'vehicle_types': {
            'heavy_construction': [
                'Concrete trucks',
                'Low loaders (equipment)',
                'Articulated trucks (materials)',
                'Semi-trailers',
                'Crane trucks'
            ],
            'light_vehicles': [
                'Staff vehicles',
                'Supervisors',
                'Utilities/tools',
                'Service vehicles'
            ]
        }
    }


def assess_traffic_impact(
    existing_aadt: int,
    construction_vehicles_daily: int,
    road_type: str
) -> Dict:
    """
    Assess impact of construction traffic on existing traffic
    
    Args:
        existing_aadt: Existing daily traffic
        construction_vehicles_daily: Additional construction vehicles
        road_type: Type of road
        
    Returns:
        Impact assessment
    """
    
    total_traffic = existing_aadt + construction_vehicles_daily
    percentage_increase = (construction_vehicles_daily / existing_aadt) * 100
    
    # Road capacity estimates (vehicles per day)
    capacity = {
        'highway': 20000,
        'arterial': 15000,
        'collector': 8000,
        'local': 3000
    }
    
    road_capacity = capacity.get(road_type, 10000)
    capacity_utilization = (total_traffic / road_capacity) * 100
    
    # Impact rating
    if percentage_increase < 5:
        impact_level = 'Negligible'
        mitigation = 'Standard traffic management'
    elif percentage_increase < 10:
        impact_level = 'Low'
        mitigation = 'Enhanced signage and monitoring'
    elif percentage_increase < 20:
        impact_level = 'Moderate'
        mitigation = 'Traffic control, possible peak hour restrictions'
    else:
        impact_level = 'High'
        mitigation = 'Comprehensive traffic management, off-peak restrictions, possible road upgrades'
    
    return {
        'impact_assessment': {
            'existing_aadt': existing_aadt,
            'construction_traffic': construction_vehicles_daily,
            'total_traffic': total_traffic,
            'percentage_increase': round(percentage_increase, 1),
            'impact_level': impact_level
        },
        
        'capacity_analysis': {
            'road_capacity': road_capacity,
            'current_utilization': round((existing_aadt / road_capacity) * 100, 1),
            'with_construction': round(capacity_utilization, 1),
            'capacity_adequate': capacity_utilization < 80
        },
        
        'mitigation_measures': {
            'required_level': impact_level,
            'primary_measures': mitigation,
            'recommendations': generate_mitigation_recommendations(impact_level, percentage_increase)
        }
    }


def generate_mitigation_recommendations(impact_level: str, percentage_increase: float) -> List[str]:
    """Generate traffic mitigation recommendations"""
    
    recommendations = []
    
    if impact_level in ['Moderate', 'High']:
        recommendations.extend([
            'Restrict construction vehicles to off-peak hours (9:30am-3:00pm, after 7:00pm)',
            'Implement traffic controllers at site access points',
            'Enhanced advance warning signage',
            'Regular road condition monitoring and maintenance'
        ])
    
    if impact_level == 'High':
        recommendations.extend([
            'Consider road widening or strengthening at access points',
            'Implement vehicle booking system to spread traffic',
            'Coordinate with local authorities for traffic management',
            'Possible requirement for road dilapidation bond',
            'Enhanced dust suppression measures',
            'Speed restrictions through construction zone'
        ])
    
    if percentage_increase > 15:
        recommendations.append('Public notification of increased construction traffic')
    
    return recommendations


def categorize_traffic_volume(aadt: int) -> str:
    """Categorize traffic volume level"""
    
    if aadt < 1000:
        return 'Very Low'
    elif aadt < 3000:
        return 'Low'
    elif aadt < 10000:
        return 'Medium'
    elif aadt < 20000:
        return 'High'
    else:
        return 'Very High'
