"""
CSV Risk Parser - Parses risk_data.csv into structured risk registry
"""
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Risk rating colors
RISK_COLORS = {
    "Low": "#4CAF50",      # Green
    "Medium": "#FFC107",   # Yellow
    "High": "#FF9800",     # Orange
    "Extreme": "#F44336",  # Red
}

# Category icons/emojis for better UX
CATEGORY_INFO = {
    "Traffic Flow & Vehicle Interaction": {"icon": "🚗", "short": "TF"},
    "Pedestrian & Cyclist Safety": {"icon": "🚶", "short": "PC"},
    "Worker Safety": {"icon": "👷", "short": "WS"},
    "Plant & Equipment": {"icon": "🚜", "short": "PE"},
    "Environmental": {"icon": "🌤️", "short": "EN"},
    "Signage & Devices": {"icon": "🚧", "short": "SD"},
    "Public Behaviour": {"icon": "👥", "short": "PB"},
    "Emergency & Incident": {"icon": "🚨", "short": "EM"},
    "Interface with Infrastructure": {"icon": "🏗️", "short": "IF"},
    "Compliance & Admin": {"icon": "📋", "short": "CA"},
}

def parse_controls(controls_str: str) -> List[str]:
    """Parse controls string into list of individual controls"""
    if not controls_str:
        return []
    # Split by semicolon or comma, but be careful with quotes
    controls = []
    for control in controls_str.split(';'):
        control = control.strip()
        if control:
            # Also split by comma if no semicolon was found
            if ',' in control and ';' not in controls_str:
                controls.extend([c.strip() for c in control.split(',') if c.strip()])
            else:
                controls.append(control)
    return controls

def parse_hierarchy(hierarchy_str: str) -> List[str]:
    """Parse control hierarchy string"""
    if not hierarchy_str:
        return ["Administrative"]
    # Remove brackets and quotes
    cleaned = hierarchy_str.replace("[", "").replace("]", "").replace("'", "").replace('"', '')
    return [h.strip() for h in cleaned.split(',') if h.strip()]

def likelihood_to_level(likelihood: str) -> int:
    """Convert likelihood string to numeric level"""
    mapping = {
        "Rare": 1,
        "Unlikely": 2,
        "Possible": 3,
        "Likely": 4,
        "Almost Certain": 5,
        "Likely (in storms)": 4,  # Special case
    }
    return mapping.get(likelihood, 3)

def rating_to_level(rating: str) -> int:
    """Convert risk rating to numeric level"""
    mapping = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Extreme": 4,
    }
    return mapping.get(rating, 2)

def parse_csv_risk_registry() -> List[Dict[str, Any]]:
    """Parse risk_data.csv and return structured risk registry"""
    csv_path = Path(__file__).parent / "risk_data.csv"
    
    if not csv_path.exists():
        logger.warning(f"Risk CSV not found at {csv_path}, using empty registry")
        return []
    
    risks = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                risk_id = row.get('ID', '').strip()
                if not risk_id:
                    continue
                
                category = row.get('Category', 'Unknown').strip()
                category_info = CATEGORY_INFO.get(category, {"icon": "⚠️", "short": "XX"})
                
                likelihood = row.get('Likelihood', 'Possible').strip()
                risk_rating = row.get('Risk Rating', 'Medium').strip()
                residual_risk = row.get('Residual Risk', 'Low').strip()
                
                risk = {
                    "id": risk_id,
                    "category": category,
                    "category_icon": category_info["icon"],
                    "category_short": category_info["short"],
                    "subcategory": row.get('Subcategory', '').strip(),
                    "hazard": row.get('Hazard', '').strip(),
                    "title": row.get('Hazard', '').strip(),  # Alias for compatibility
                    "trigger": row.get('Trigger/Context', '').strip(),
                    "consequence": row.get('Potential Consequence', '').strip(),
                    "likelihood": likelihood,
                    "likelihood_level": likelihood_to_level(likelihood),
                    "risk_rating": risk_rating,
                    "risk_level": rating_to_level(risk_rating),
                    "risk_color": RISK_COLORS.get(risk_rating, "#FFC107"),
                    "controls": parse_controls(row.get('Controls / Mitigation', '')),
                    "controls_hierarchy": parse_hierarchy(row.get('Controls Hierarchy', '')),
                    "monitoring": row.get('Monitoring / Verification', '').strip(),
                    "responsible_role": row.get('Responsible Role', '').strip(),
                    "reference": row.get('Reference', '').strip(),
                    "residual_risk": residual_risk,
                    "residual_risk_level": rating_to_level(residual_risk),
                    "residual_risk_color": RISK_COLORS.get(residual_risk, "#4CAF50"),
                    # Default selection state
                    "selected": False,
                    "selected_controls": [],
                }
                
                risks.append(risk)
        
        logger.info(f"Loaded {len(risks)} risks from CSV")
        return risks
        
    except Exception as e:
        logger.error(f"Error parsing risk CSV: {e}")
        return []

def get_risks_by_category() -> Dict[str, List[Dict]]:
    """Get risks organized by category"""
    risks = parse_csv_risk_registry()
    categorized = {}
    
    for risk in risks:
        category = risk['category']
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(risk)
    
    return categorized

def get_risk_summary() -> Dict[str, Any]:
    """Get summary statistics of risk registry"""
    risks = parse_csv_risk_registry()
    
    categories = {}
    risk_levels = {"Low": 0, "Medium": 0, "High": 0, "Extreme": 0}
    
    for risk in risks:
        cat = risk['category']
        categories[cat] = categories.get(cat, 0) + 1
        
        rating = risk['risk_rating']
        if rating in risk_levels:
            risk_levels[rating] += 1
    
    return {
        "total_risks": len(risks),
        "categories": categories,
        "risk_levels": risk_levels,
    }

# For testing
if __name__ == "__main__":
    risks = parse_csv_risk_registry()
    print(f"Loaded {len(risks)} risks")
    
    by_cat = get_risks_by_category()
    for cat, cat_risks in by_cat.items():
        print(f"  {cat}: {len(cat_risks)} risks")
    
    print("\nFirst risk:")
    if risks:
        import json
        print(json.dumps(risks[0], indent=2))
