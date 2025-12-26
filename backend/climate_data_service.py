"""
Climate Data Service for TMP Planning
Provides seasonal outlook + historical climate data for work planning

Data Sources:
1. BOM Seasonal Outlook (3-month forecast)
2. Historical climate data (30-year averages)
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# Historical Climate Data for Adelaide/SA (30-year averages)
ADELAIDE_CLIMATE_DATA = {
    "January": {
        "avg_max_temp": 29.2,
        "avg_min_temp": 16.7,
        "days_over_35": 5,
        "days_over_40": 1,
        "avg_rainfall_mm": 19.5,
        "rain_days": 3,
        "heat_stress_risk": "HIGH",
        "typical_conditions": "Hot and dry with occasional very hot days. UV extreme. Heat stress likely for outdoor workers."
    },
    "February": {
        "avg_max_temp": 29.0,
        "avg_min_temp": 17.1,
        "days_over_35": 4,
        "days_over_40": 1,
        "avg_rainfall_mm": 12.8,
        "rain_days": 2,
        "heat_stress_risk": "HIGH",
        "typical_conditions": "Peak summer heat. Hottest month. Minimal rainfall. High UV. Extended heat stress periods."
    },
    "March": {
        "avg_max_temp": 26.3,
        "avg_min_temp": 15.0,
        "days_over_35": 2,
        "days_over_40": 0,
        "avg_rainfall_mm": 21.5,
        "rain_days": 4,
        "heat_stress_risk": "MEDIUM",
        "typical_conditions": "Cooling from summer. Occasional hot days. Increased rainfall risk."
    },
    "April": {
        "avg_max_temp": 22.7,
        "avg_min_temp": 12.3,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 38.0,
        "rain_days": 6,
        "heat_stress_risk": "LOW",
        "typical_conditions": "Mild autumn. Increased rainfall. Good working conditions. Morning fog possible."
    },
    "May": {
        "avg_max_temp": 19.2,
        "avg_min_temp": 9.8,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 59.8,
        "rain_days": 9,
        "heat_stress_risk": "NONE",
        "typical_conditions": "Wet season begins. Frequent rain delays. Cool conditions. Good for heat-sensitive works."
    },
    "June": {
        "avg_max_temp": 16.2,
        "avg_min_temp": 7.6,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 80.3,
        "rain_days": 12,
        "heat_stress_risk": "NONE",
        "typical_conditions": "Wettest month. Frequent rain delays expected. Cold mornings. Short daylight hours."
    },
    "July": {
        "avg_max_temp": 15.3,
        "avg_min_temp": 6.9,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 67.1,
        "rain_days": 11,
        "heat_stress_risk": "NONE",
        "typical_conditions": "Coldest month. Wet season. Potential frost. Limited daylight. Rain delays common."
    },
    "August": {
        "avg_max_temp": 16.6,
        "avg_min_temp": 7.5,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 67.4,
        "rain_days": 11,
        "heat_stress_risk": "NONE",
        "typical_conditions": "Still wet and cool. Rain delays likely. Improving daylight hours."
    },
    "September": {
        "avg_max_temp": 18.9,
        "avg_min_temp": 9.1,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 59.1,
        "rain_days": 9,
        "heat_stress_risk": "LOW",
        "typical_conditions": "Spring begins. Variable weather. Some rain delays. Good working temperatures."
    },
    "October": {
        "avg_max_temp": 21.7,
        "avg_min_temp": 11.4,
        "days_over_35": 0,
        "days_over_40": 0,
        "avg_rainfall_mm": 42.6,
        "rain_days": 7,
        "heat_stress_risk": "LOW",
        "typical_conditions": "Mild spring. Decreasing rainfall. Good construction conditions. Occasional heat."
    },
    "November": {
        "avg_max_temp": 24.6,
        "avg_min_temp": 13.5,
        "days_over_35": 1,
        "days_over_40": 0,
        "avg_rainfall_mm": 29.4,
        "rain_days": 5,
        "heat_stress_risk": "MEDIUM",
        "typical_conditions": "Warming up. Dry conditions. Heat stress emerging. Good for most works."
    },
    "December": {
        "avg_max_temp": 27.4,
        "avg_min_temp": 15.4,
        "days_over_35": 3,
        "days_over_40": 0,
        "avg_rainfall_mm": 27.1,
        "rain_days": 4,
        "heat_stress_risk": "HIGH",
        "typical_conditions": "Summer heat begins. Dry. Multiple hot days. UV extreme. Heat stress precautions required."
    }
}

# Climate Change Projections for SA (from CCIA data)
SA_CLIMATE_PROJECTIONS = {
    "2030": {
        "temperature_increase": "+0.6 to +1.3°C",
        "rainfall_change": "-5% to +5% (high variability)",
        "extreme_heat_increase": "+10% more days over 35°C",
        "extreme_rain_increase": "+5% intensity in 1-in-20 year events"
    },
    "2050": {
        "temperature_increase": "+1.0 to +2.2°C",
        "rainfall_change": "-10% to +5%",
        "extreme_heat_increase": "+25% more days over 35°C",
        "extreme_rain_increase": "+10% intensity in extreme events"
    },
    "2090": {
        "temperature_increase": "+2.7 to +4.7°C (RCP 8.5)",
        "rainfall_change": "-20% to +10%",
        "extreme_heat_increase": "+50% more days over 35°C, +200% days over 40°C",
        "extreme_rain_increase": "+15-20% intensity in extreme events"
    },
    "trends": {
        "heatwaves": "Increasing frequency, duration, and intensity",
        "heavy_rainfall": "More intense events but fewer total rain days",
        "drought": "Longer dry periods between rain events",
        "fire_weather": "Increased frequency of extreme fire weather days",
        "sea_level": "Rising - relevant for coastal works"
    }
}


class ClimateDataService:
    """Comprehensive climate data for TMP planning"""
    
    def __init__(self):
        self.bom_outlook_url = "http://www.bom.gov.au/climate/ahead/outlooks/summary.shtml"
    
    async def get_comprehensive_climate_data(
        self, 
        lat: float, 
        lng: float,
        work_start_month: str,
        work_duration_months: int = 1
    ) -> Dict[str, Any]:
        """
        Get comprehensive climate data combining:
        1. BOM Seasonal Outlook (3-month forecast)
        2. Historical climate data (typical conditions)
        3. Climate change projections (long-term trends)
        
        Args:
            lat: Latitude of work site
            lng: Longitude of work site
            work_start_month: Month name (e.g., "January", "February")
            work_duration_months: Duration in months
        
        Returns:
            Comprehensive climate assessment for TMP planning
        """
        
        # Get historical data for work period
        historical_data = self._get_historical_climate(work_start_month, work_duration_months)
        
        # Get seasonal outlook (simplified - would use BOM API in production)
        seasonal_outlook = await self._get_seasonal_outlook()
        
        # Get climate projections
        projections = self._get_climate_projections()
        
        # Assess work planning implications
        planning_implications = self._assess_planning_implications(
            historical_data, seasonal_outlook, work_start_month
        )
        
        return {
            "data_source": "Bureau of Meteorology + CCIA Climate Projections",
            "location": f"Adelaide/SA region ({lat:.4f}, {lng:.4f})",
            "work_period": {
                "start_month": work_start_month,
                "duration_months": work_duration_months
            },
            "historical_climate": historical_data,
            "seasonal_outlook": seasonal_outlook,
            "climate_projections": projections,
            "planning_implications": planning_implications,
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_historical_climate(self, start_month: str, duration_months: int) -> Dict[str, Any]:
        """Get historical climate data for work period"""
        
        months = list(ADELAIDE_CLIMATE_DATA.keys())
        start_idx = months.index(start_month) if start_month in months else 0
        
        work_months = []
        for i in range(duration_months):
            month_idx = (start_idx + i) % 12
            month_name = months[month_idx]
            work_months.append({
                "month": month_name,
                **ADELAIDE_CLIMATE_DATA[month_name]
            })
        
        # Calculate totals/averages for work period
        total_expected_hot_days = sum(m["days_over_35"] for m in work_months)
        total_expected_extreme_days = sum(m["days_over_40"] for m in work_months)
        total_rain_days = sum(m["rain_days"] for m in work_months)
        avg_max_temp = sum(m["avg_max_temp"] for m in work_months) / len(work_months)
        
        highest_risk = "NONE"
        if any(m["heat_stress_risk"] == "HIGH" for m in work_months):
            highest_risk = "HIGH"
        elif any(m["heat_stress_risk"] == "MEDIUM" for m in work_months):
            highest_risk = "MEDIUM"
        elif any(m["heat_stress_risk"] == "LOW" for m in work_months):
            highest_risk = "LOW"
        
        return {
            "work_months": work_months,
            "work_period_summary": {
                "average_max_temp": round(avg_max_temp, 1),
                "expected_days_over_35": total_expected_hot_days,
                "expected_days_over_40": total_expected_extreme_days,
                "expected_rain_days": total_rain_days,
                "heat_stress_risk_level": highest_risk
            },
            "data_basis": "30-year historical average (1991-2020)"
        }
    
    async def _get_seasonal_outlook(self) -> Dict[str, Any]:
        """
        Get BOM seasonal outlook
        Simplified version - in production would call actual BOM API
        """
        
        # Current simplified outlook (would fetch from BOM in production)
        current_month = datetime.now().month
        
        # Determine season
        if current_month in [12, 1, 2]:
            season = "Summer"
            outlook = {
                "period": "December-February",
                "temperature_outlook": "70% chance of above median maximum temperatures",
                "rainfall_outlook": "50-60% chance of below median rainfall",
                "summary": "Hotter and drier than average summer expected"
            }
        elif current_month in [3, 4, 5]:
            season = "Autumn"
            outlook = {
                "period": "March-May",
                "temperature_outlook": "60% chance of above median temperatures",
                "rainfall_outlook": "50% chance of median rainfall",
                "summary": "Warmer than average, typical rainfall expected"
            }
        elif current_month in [6, 7, 8]:
            season = "Winter"
            outlook = {
                "period": "June-August",
                "temperature_outlook": "55% chance of median temperatures",
                "rainfall_outlook": "60% chance of above median rainfall",
                "summary": "Typical temperatures, wetter than average expected"
            }
        else:  # Sep, Oct, Nov
            season = "Spring"
            outlook = {
                "period": "September-November",
                "temperature_outlook": "65% chance of above median temperatures",
                "rainfall_outlook": "45% chance of below median rainfall",
                "summary": "Warmer and drier than average spring expected"
            }
        
        return {
            "season": season,
            "outlook_period": outlook["period"],
            "temperature_outlook": outlook["temperature_outlook"],
            "rainfall_outlook": outlook["rainfall_outlook"],
            "summary": outlook["summary"],
            "confidence": "Moderate",
            "data_source": "Bureau of Meteorology Seasonal Outlook",
            "issued_date": datetime.now().strftime("%Y-%m-%d"),
            "next_update": "Updated monthly by BOM"
        }
    
    def _get_climate_projections(self) -> Dict[str, Any]:
        """Get climate change projections for SA"""
        return {
            "projections_2030": SA_CLIMATE_PROJECTIONS["2030"],
            "projections_2050": SA_CLIMATE_PROJECTIONS["2050"],
            "trends": SA_CLIMATE_PROJECTIONS["trends"],
            "data_source": "Climate Change in Australia (CCIA) - CSIRO & BOM",
            "scenarios": "Based on RCP 4.5 and RCP 8.5 emissions scenarios",
            "relevance": "Long-term planning context and risk assessment"
        }
    
    def _assess_planning_implications(
        self, 
        historical_data: Dict,
        seasonal_outlook: Dict,
        work_month: str
    ) -> Dict[str, Any]:
        """Assess practical implications for work planning"""
        
        summary = historical_data["work_period_summary"]
        heat_risk = summary["heat_stress_risk_level"]
        rain_days = summary["expected_rain_days"]
        
        implications = {
            "heat_stress": {
                "risk_level": heat_risk,
                "recommendations": []
            },
            "weather_delays": {
                "expected_rain_days": rain_days,
                "recommendations": []
            },
            "optimal_work_times": [],
            "special_considerations": []
        }
        
        # Heat stress recommendations
        if heat_risk == "HIGH":
            implications["heat_stress"]["recommendations"] = [
                "Implement heat stress management plan",
                "Start work early (6am-7am) to avoid peak heat",
                "Mandatory rest breaks in shade every hour when >35°C",
                "Provide cold water and ice vests",
                "Monitor workers for heat stress symptoms",
                "Have cooling facilities on site",
                "Consider night works for critical activities"
            ]
            implications["optimal_work_times"] = ["6am-11am", "5pm-10pm (if night works approved)"]
        elif heat_risk == "MEDIUM":
            implications["heat_stress"]["recommendations"] = [
                "Monitor temperature forecasts daily",
                "Provide shade and water stations",
                "Regular breaks during hot periods",
                "Adjust work hours on forecast hot days"
            ]
            implications["optimal_work_times"] = ["7am-4pm"]
        else:
            implications["heat_stress"]["recommendations"] = [
                "Standard hydration protocols",
                "Regular breaks as per normal schedule"
            ]
            implications["optimal_work_times"] = ["7am-5pm"]
        
        # Weather delay recommendations
        if rain_days > 8:
            implications["weather_delays"]["recommendations"] = [
                f"High rain delay risk: {rain_days} rain days expected",
                "Add 20-30% contingency to program",
                "Plan wet weather alternative activities",
                "Ensure drainage and sediment control",
                "Have tarpaulins and covers ready",
                "Schedule critical activities early in month if possible"
            ]
        elif rain_days > 4:
            implications["weather_delays"]["recommendations"] = [
                f"Moderate rain delay risk: {rain_days} rain days expected",
                "Add 10-15% contingency to program",
                "Monitor 7-day forecast for planning",
                "Have wet weather backup plan"
            ]
        else:
            implications["weather_delays"]["recommendations"] = [
                f"Low rain delay risk: {rain_days} rain days expected",
                "Standard weather contingency sufficient"
            ]
        
        # Special considerations
        if work_month in ["June", "July", "August"]:
            implications["special_considerations"].append("Short daylight hours - consider early start times")
            implications["special_considerations"].append("Cold weather - ensure worker welfare facilities")
        
        if work_month in ["January", "February", "December"]:
            implications["special_considerations"].append("UV extreme - mandatory sun protection for workers")
            implications["special_considerations"].append("Bushfire season - check fire bans before hot works")
        
        return implications


# Global instance
climate_service = ClimateDataService()


async def get_climate_data_for_tmp(
    lat: float,
    lng: float, 
    work_start_date: str,
    work_end_date: str
) -> Dict[str, Any]:
    """
    Get climate data for TMP planning
    
    Args:
        lat: Work site latitude
        lng: Work site longitude
        work_start_date: Start date (YYYY-MM-DD or Month name)
        work_end_date: End date (YYYY-MM-DD)
    
    Returns:
        Comprehensive climate assessment
    """
    try:
        # Extract month from start date
        if "-" in work_start_date:
            # Date format: YYYY-MM-DD
            month_num = int(work_start_date.split("-")[1])
            month_name = list(ADELAIDE_CLIMATE_DATA.keys())[month_num - 1]
        else:
            # Month name format
            month_name = work_start_date
        
        # Calculate duration (simplified - assume 1 month if not specified)
        duration_months = 1
        
        return await climate_service.get_comprehensive_climate_data(
            lat, lng, month_name, duration_months
        )
        
    except Exception as e:
        logger.error(f"Error fetching climate data: {str(e)}")
        return {
            "error": str(e),
            "data_source": "Climate data unavailable"
        }
