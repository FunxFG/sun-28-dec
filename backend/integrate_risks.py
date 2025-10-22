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
                "risk_id": row['risk_id'],
                "hazard": row['hazard'],
                "consequence": row['consequence'],
                "likelihood": row['likelihood'].lower().replace(' ', '_'),
                "risk_level": row['risk_level'],
                "control_measures": row['control_measures'].split(',') if ',' in row['control_measures'] else [row['control_measures']],
                "category": determine_category(row['risk_id']),
                "agttm_reference": determine_agttm_reference(row['risk_id'])
            }
            risks.append(risk)
    
    return risks

def determine_category(risk_id):
    """Determine risk category from risk ID prefix"""
    prefix = risk_id[:2]
    categories = {
        'TF': 'Traffic Flow',
        'PC': 'Pedestrian/Cyclist',
        'WS': 'Worker Safety',
        'PE': 'Plant & Equipment',
        'EN': 'Environmental',
        'SD': 'Signage & Devices',
        'PB': 'Public Behavior',
        'EM': 'Emergency Management',
        'IF': 'Infrastructure',
        'CA': 'Compliance & Admin'
    }
    return categories.get(prefix, 'General')

def determine_agttm_reference(risk_id):
    """Map to AGTTM reference"""
    prefix = risk_id[:2]
    references = {
        'TF': 'AGTTM Part 3 - Traffic Flow',
        'PC': 'AGTTM Part 7 - Pedestrian/Cyclist',
        'WS': 'AS 1742.3 Section 3.2 - Worker Safety',
        'PE': 'AGTTM Part 5 - Equipment',
        'EN': 'AGTTM Part 2 - Environmental',
        'SD': 'AS 1742.3 - Sign Placement',
        'PB': 'AGTTM Part 4 - Public Interface',
        'EM': 'AGTTM Part 8 - Emergency',
        'IF': 'AGTTM Part 6 - Infrastructure',
        'CA': 'AGTTM Part 1 - Compliance'
    }
    return references.get(prefix, 'AS 1742.3')

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
