"""
Script to parse CSV risk data and update risk_registry.py
"""
import csv
import json

def parse_csv_to_risk_registry(csv_path):
    risks = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            risk = {
                "id": row['id'],
                "category": map_category(row['category']),
                "title": row['site_type'],
                "hazard": row['hazard'],
                "cause": row['cause'],
                "description": row['consequence'],
                "default_likelihood": row['likelihood'].lower().replace(' ', '_'),
                "default_consequence": row['consequence_level'].lower(),
                "risk_score": int(row['risk_score']),
                "risk_level": row['risk_level'],
                "controls": {
                    "elimination": row['control_elimination'],
                    "substitution": row['control_substitution'],
                    "engineering": row['control_engineering'],
                    "administrative": row['control_administrative'],
                    "ppe": row['control_ppe']
                },
                "residual_risk": {
                    "likelihood": row['residual_likelihood'].lower().replace(' ', '_'),
                    "consequence": row['residual_consequence_level'].lower(),
                    "score": int(row['residual_risk_score']),
                    "level": row['residual_risk_level']
                },
                "references": parse_refs(row['standards_refs']),
                "standards": {
                    "SA_WZTM": row.get('std_SA_WZTM', ''),
                    "AGTTM": row.get('std_AGTTM', ''),
                    "AS1742_3": row.get('std_AS1742_3', ''),
                    "DIT_Field_Guide": row.get('std_DIT_Field_Guide', '')
                }
            }
            risks.append(risk)
    
    return risks

def map_category(csv_category):
    mapping = {
        "Traffic Control – Static": "traffic_control",
        "Traffic Control – Mobile": "traffic_control",
        "Traffic Control – Intersections": "traffic_control",
        "Environment & Lighting": "environment",
        "Vulnerable Road Users": "vulnerable_users",
        "Plant & Equipment": "equipment",
        "Underground Services": "services",
        "Worker Safety": "people",
        "Public Safety": "people"
    }
    return mapping.get(csv_category, "general")

def parse_refs(refs_str):
    try:
        refs = eval(refs_str)
        return refs if isinstance(refs, list) else []
    except:
        return []

if __name__ == "__main__":
    risks = parse_csv_to_risk_registry('risk_data.csv')
    print(f"Parsed {len(risks)} risks")
    print(json.dumps(risks[0], indent=2))
