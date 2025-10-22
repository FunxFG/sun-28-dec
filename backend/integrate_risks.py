"""
Risk Register Integration Script
Updates existing /api/risks endpoint with expanded 100+ risk register
DOES NOT change database or frontend - just enhances backend data
"""

import csv

def load_expanded_risk_register():
    """Load the 100+ comprehensive risk register from CSV"""
    
    risks = []
    
    with open('/tmp/austroads_risk_register_v2_expanded.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            risk = {
                "risk_id": row['ID'],
                "category": row['Category'],
                "subcategory": row['Subcategory'] if row['Subcategory'] else None,
                "hazard": row['Hazard'],
                "trigger": row['Trigger/Context'] if row['Trigger/Context'] else None,
                "consequence": row['Potential Consequence'],
                "likelihood": row['Likelihood'].lower().replace(' ', '_'),
                "risk_level": row['Risk Rating'],
                "control_measures": row['Controls / Mitigation'].split(';') if ';' in row['Controls / Mitigation'] else [row['Controls / Mitigation']],
                "controls_hierarchy": row['Controls Hierarchy'],
                "monitoring": row['Monitoring / Verification'],
                "responsible": row['Responsible Role'],
                "reference": row['Reference'],
                "residual_risk": row['Residual Risk']
            }
            risks.append(risk)
    
    return risks

def determine_category(risk_id):
    """Keep actual category from CSV"""
    return None  # Not needed, using CSV category

def determine_agttm_reference(risk_id):
    """Keep actual reference from CSV"""
    return None  # Not needed, using CSV reference

if __name__ == "__main__":
    risks = load_expanded_risk_register()
    print(f"✅ Loaded {len(risks)} risks")
    print(f"\nCategories:")
    categories = {}
    for risk in risks:
        cat = risk['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} risks")
    
    print(f"\nRisk Levels:")
    levels = {}
    for risk in risks:
        level = risk['risk_level']
        levels[level] = levels.get(level, 0) + 1
    
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count} risks")
