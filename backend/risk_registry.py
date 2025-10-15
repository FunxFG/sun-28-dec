"""
Comprehensive Risk Registry for Roadwork Traffic Management
Based on AS 1742.3, AGTTM, and industry best practices
"""

RISK_CATEGORIES = {
    "people": "People",
    "information": "Information",
    "property": "Property & Equipment",
    "reputation": "Reputation",
    "financial": "Financial",
    "capability": "Capability"
}

LIKELIHOOD_LEVELS = {
    "rare": {"level": 1, "name": "Rare", "description": "May occur only in exceptional circumstances"},
    "unlikely": {"level": 2, "name": "Unlikely", "description": "Could occur at some time"},
    "possible": {"level": 3, "name": "Possible", "description": "Might occur at some time"},
    "likely": {"level": 4, "name": "Likely", "description": "Will probably occur in most circumstances"},
    "almost_certain": {"level": 5, "name": "Almost Certain", "description": "Expected to occur in most circumstances"}
}

CONSEQUENCE_LEVELS = {
    "insignificant": {"level": 1, "name": "Insignificant", "color": "#4CAF50"},
    "negligible": {"level": 2, "name": "Negligible", "color": "#8BC34A"},
    "moderate": {"level": 3, "name": "Moderate", "color": "#FFC107"},
    "extensive": {"level": 4, "name": "Extensive", "color": "#FF9800"},
    "significant": {"level": 5, "name": "Significant", "color": "#F44336"}
}

# Comprehensive roadwork risk registry
RISK_REGISTRY = [
    {
        "id": "risk_001",
        "category": "people",
        "title": "Vehicle collision with workers",
        "description": "Vehicles entering the work zone and colliding with workers",
        "default_likelihood": "possible",
        "default_consequence": "significant",
        "controls": [
            "Physical barriers between traffic and workers",
            "High visibility PPE for all workers",
            "Advance warning signage",
            "Traffic control personnel at entry/exit points",
            "Speed reduction through work zone",
            "Clear sight lines maintained"
        ],
        "references": ["AS 1742.3 Section 3.2", "AGTTM Chapter 4"],
        "agttm_rule": "riicwd503d_worker_safety"
    },
    {
        "id": "risk_002",
        "category": "people",
        "title": "Pedestrian injury in work zone",
        "description": "Pedestrians entering work area or being struck by equipment",
        "default_likelihood": "likely",
        "default_consequence": "extensive",
        "controls": [
            "Dedicated pedestrian diversions",
            "Footpath closure signage",
            "Physical barriers around work zone",
            "Elevated walkways where required",
            "Clear pedestrian signage and wayfinding",
            "Lighting for night works"
        ],
        "references": ["AS 1742.3 Section 5.7", "AGTTM Section 6.3"],
        "agttm_rule": "riicwd503d_pedestrian_management"
    },
    {
        "id": "risk_003",
        "category": "people",
        "title": "Worker fatigue-related incidents",
        "description": "Accidents caused by worker fatigue during extended work periods",
        "default_likelihood": "possible",
        "default_consequence": "extensive",
        "controls": [
            "Maximum shift duration limits",
            "Mandatory rest breaks",
            "Rotation of traffic control personnel",
            "Adequate staffing levels",
            "Fatigue management training",
            "Environmental controls (shade, water, rest areas)"
        ],
        "references": ["AGTTM Section 3.4", "Work Health and Safety Act 2011"],
        "agttm_rule": "riicwd503d_worker_welfare"
    },
    {
        "id": "risk_004",
        "category": "people",
        "title": "Vehicle-to-vehicle collisions in work zone",
        "description": "Rear-end or side-impact collisions due to reduced speeds or lane changes",
        "default_likelihood": "likely",
        "default_consequence": "moderate",
        "controls": [
            "Advance warning signs at appropriate distances",
            "Progressive speed reduction",
            "Clear lane markings and delineation",
            "Adequate taper lengths for lane closures",
            "Variable Message Signs for real-time warnings",
            "Buffer zones between work and traffic"
        ],
        "references": ["AS 1742.3 Section 3.5", "AGTTM Table 4.3"],
        "agttm_rule": "riicwd503d_traffic_control"
    },
    {
        "id": "risk_005",
        "category": "people",
        "title": "Equipment rollover or instability",
        "description": "Heavy machinery rollover or loss of stability on uneven surfaces",
        "default_likelihood": "unlikely",
        "default_consequence": "significant",
        "controls": [
            "Ground stability assessment before equipment placement",
            "Exclusion zones around heavy equipment",
            "Certified equipment operators only",
            "Regular equipment inspections",
            "Clear operating procedures",
            "Spotter personnel when required"
        ],
        "references": ["AS 2550 Mobile Cranes", "AGTTM Section 7.2"],
        "agttm_rule": "riicwd503d_equipment_safety"
    },
    {
        "id": "risk_006",
        "category": "people",
        "title": "Heat stress and dehydration",
        "description": "Workers suffering heat-related illness during hot weather operations",
        "default_likelihood": "likely",
        "default_consequence": "moderate",
        "controls": [
            "Regular water and electrolyte breaks",
            "Shade structures at work sites",
            "Adjustment of work hours in extreme heat",
            "Heat stress monitoring and training",
            "Light-colored, breathable PPE",
            "Buddy system for monitoring workers"
        ],
        "references": ["Safe Work Australia Heat Stress Guide", "AGTTM Section 3.4"],
        "agttm_rule": "riicwd503d_environmental_controls"
    },
    {
        "id": "risk_007",
        "category": "people",
        "title": "Struck by objects or falling materials",
        "description": "Workers struck by falling or flying objects from equipment or vehicles",
        "default_likelihood": "possible",
        "default_consequence": "extensive",
        "controls": [
            "Hard hats mandatory in all work areas",
            "Secure storage of materials and equipment",
            "Overhead protection where required",
            "Load securing procedures for vehicles",
            "Exclusion zones during lifting operations",
            "Regular inspection of material storage"
        ],
        "references": ["AS 1742.3 Section 3.2.3", "AGTTM Section 7.4"],
        "agttm_rule": "riicwd503d_falling_objects"
    },
    {
        "id": "risk_008",
        "category": "property",
        "title": "Damage to underground services",
        "description": "Excavation work damaging underground utilities (power, water, gas, telecom)",
        "default_likelihood": "possible",
        "default_consequence": "significant",
        "controls": [
            "Dial Before You Dig service location",
            "Ground Penetrating Radar surveys",
            "Hand excavation near identified services",
            "Service authority notifications and approvals",
            "Emergency response procedures for service strikes",
            "Daily toolbox talks on service locations"
        ],
        "references": ["AS 5488 Underground Utility Services", "AGTTM Section 8.3"],
        "agttm_rule": "riicwd503d_service_protection"
    },
    {
        "id": "risk_009",
        "category": "property",
        "title": "Damage to traffic control devices",
        "description": "Signs, barriers, or equipment damaged by vehicles or weather",
        "default_likelihood": "likely",
        "default_consequence": "moderate",
        "controls": [
            "Adequate setback from active traffic lanes",
            "Secure anchoring of all devices",
            "Regular inspection and maintenance schedule",
            "Immediate replacement of damaged devices",
            "Weather monitoring and device reinforcement",
            "Inventory management and spare equipment"
        ],
        "references": ["AS 1742.3 Section 2.5", "AGTTM Section 5.6"],
        "agttm_rule": "riicwd503d_device_maintenance"
    },
    {
        "id": "risk_010",
        "category": "property",
        "title": "Damage to adjacent property",
        "description": "Work activities causing damage to neighboring properties or infrastructure",
        "default_likelihood": "unlikely",
        "default_consequence": "moderate",
        "controls": [
            "Pre-work condition surveys of adjacent properties",
            "Vibration monitoring for sensitive structures",
            "Protective barriers and hoarding",
            "Access maintenance for property owners",
            "Regular communication with affected parties",
            "Insurance and liability coverage verification"
        ],
        "references": ["AGTTM Section 9.2", "Local Government guidelines"],
        "agttm_rule": "riicwd503d_property_protection"
    },
    {
        "id": "risk_011",
        "category": "reputation",
        "title": "Inadequate public notification",
        "description": "Insufficient advance notice to affected residents and businesses",
        "default_likelihood": "possible",
        "default_consequence": "moderate",
        "controls": [
            "Letter drop to affected properties 7+ days in advance",
            "Public notices in local media",
            "Variable Message Signs for approaching traffic",
            "Project website with updates",
            "24/7 contact number for inquiries",
            "Stakeholder liaison officer assigned"
        ],
        "references": ["AGTTM Section 10.1", "Local Government requirements"],
        "agttm_rule": "riicwd503d_community_engagement"
    },
    {
        "id": "risk_012",
        "category": "reputation",
        "title": "Excessive traffic delays",
        "description": "Work causing significant disruption beyond acceptable levels",
        "default_likelihood": "likely",
        "default_consequence": "moderate",
        "controls": [
            "Off-peak work scheduling where possible",
            "Efficient work practices and staging",
            "Real-time traffic monitoring",
            "Alternative route planning and signage",
            "Coordination with other roadworks in area",
            "Regular progress updates to public"
        ],
        "references": ["AGTTM Section 4.5", "Traffic Management Plan requirements"],
        "agttm_rule": "riicwd503d_traffic_management"
    },
    {
        "id": "risk_013",
        "category": "reputation",
        "title": "Non-compliance with standards",
        "description": "TMP or TGS not meeting AS 1742.3 or AGTTM requirements",
        "default_likelihood": "unlikely",
        "default_consequence": "extensive",
        "controls": [
            "Design by qualified traffic management personnel",
            "Independent review and approval",
            "Regular compliance audits during works",
            "Up-to-date standards and guidelines",
            "Training for all traffic control personnel",
            "Documentation and record keeping"
        ],
        "references": ["AS 1742.3 All Sections", "AGTTM Compliance Requirements"],
        "agttm_rule": "riicwd503d_compliance_verification"
    },
    {
        "id": "risk_014",
        "category": "financial",
        "title": "Cost overruns due to extended duration",
        "description": "Project costs exceeding budget due to delays or inefficiencies",
        "default_likelihood": "possible",
        "default_consequence": "moderate",
        "controls": [
            "Detailed work programming and staging",
            "Weather contingency planning",
            "Adequate resource allocation",
            "Regular progress monitoring",
            "Change management procedures",
            "Contract terms with flexibility provisions"
        ],
        "references": ["AGTTM Section 11.3", "Project management standards"],
        "agttm_rule": "riicwd503d_project_planning"
    },
    {
        "id": "risk_015",
        "category": "financial",
        "title": "Liability claims from incidents",
        "description": "Financial liability from accidents, injuries, or property damage",
        "default_likelihood": "unlikely",
        "default_consequence": "significant",
        "controls": [
            "Comprehensive public liability insurance",
            "Professional indemnity insurance",
            "Strict adherence to all safety procedures",
            "Incident investigation and reporting",
            "Legal review of TMP and contracts",
            "Emergency response and claims management procedures"
        ],
        "references": ["Insurance requirements", "Legal obligations"],
        "agttm_rule": "riicwd503d_insurance_requirements"
    },
    {
        "id": "risk_016",
        "category": "financial",
        "title": "Penalties for non-compliance",
        "description": "Fines or penalties from regulatory authorities for breaches",
        "default_likelihood": "rare",
        "default_consequence": "moderate",
        "controls": [
            "Regular compliance audits",
            "Qualified supervision of all works",
            "Permit conditions strictly followed",
            "Corrective actions for any non-conformances",
            "Relationship management with authorities",
            "Proactive reporting of issues"
        ],
        "references": ["Local Government regulations", "Traffic Management Act"],
        "agttm_rule": "riicwd503d_regulatory_compliance"
    },
    {
        "id": "risk_017",
        "category": "capability",
        "title": "Insufficient qualified personnel",
        "description": "Lack of appropriately trained traffic control personnel",
        "default_likelihood": "possible",
        "default_consequence": "extensive",
        "controls": [
            "Verification of traffic controller qualifications",
            "Minimum staffing levels maintained",
            "Backup personnel on standby",
            "Regular training and refresher courses",
            "Competency assessments",
            "Succession planning for key roles"
        ],
        "references": ["AGTTM Section 2.3", "Training requirements"],
        "agttm_rule": "riicwd503d_personnel_competency"
    },
    {
        "id": "risk_018",
        "category": "capability",
        "title": "Equipment failure or inadequacy",
        "description": "Traffic control equipment failure or insufficient quantities",
        "default_likelihood": "unlikely",
        "default_consequence": "moderate",
        "controls": [
            "Regular equipment maintenance schedules",
            "Pre-work equipment checks",
            "Adequate spare equipment inventory",
            "Equipment replacement program",
            "Quality assurance for all devices",
            "Supplier relationships and backup options"
        ],
        "references": ["AS 1742.3 Section 2.4", "AGTTM Section 5.5"],
        "agttm_rule": "riicwd503d_equipment_management"
    },
    {
        "id": "risk_019",
        "category": "people",
        "title": "Emergency vehicle access restriction",
        "description": "Work zone impeding emergency services access to area",
        "default_likelihood": "unlikely",
        "default_consequence": "significant",
        "controls": [
            "Emergency services consultation prior to works",
            "Maintained emergency vehicle access at all times",
            "Emergency contact numbers displayed on site",
            "Rapid traffic control device removal procedures",
            "Communication plan with emergency services",
            "Alternative access route identification"
        ],
        "references": ["AGTTM Section 6.5", "Emergency Services guidelines"],
        "agttm_rule": "riicwd503d_emergency_access"
    },
    {
        "id": "risk_020",
        "category": "people",
        "title": "Poor visibility conditions",
        "description": "Reduced visibility due to weather, dust, or time of day affecting safety",
        "default_likelihood": "likely",
        "default_consequence": "extensive",
        "controls": [
            "Enhanced lighting for night and low-light work",
            "Weather monitoring and work cessation criteria",
            "Dust suppression measures",
            "High-intensity warning lights on vehicles",
            "Reflective markings on all devices and PPE",
            "Reduced work hours during poor visibility"
        ],
        "references": ["AS 1742.3 Section 3.7", "AGTTM Section 4.8"],
        "agttm_rule": "riicwd503d_visibility_management"
    },
    {
        "id": "risk_021",
        "category": "information",
        "title": "Loss of TMP documentation",
        "description": "Critical traffic management plan documents lost or inaccessible",
        "default_likelihood": "unlikely",
        "default_consequence": "moderate",
        "controls": [
            "Cloud-based document storage with backups",
            "Physical copies at site office",
            "Document version control",
            "Access permissions and security",
            "Regular backup procedures",
            "Recovery procedures documented"
        ],
        "references": ["AGTTM Section 12.2", "Records management"],
        "agttm_rule": "riicwd503d_document_control"
    },
    {
        "id": "risk_022",
        "category": "capability",
        "title": "Communication system failure",
        "description": "Radio or phone systems failing, impacting coordination",
        "default_likelihood": "unlikely",
        "default_consequence": "moderate",
        "controls": [
            "Multiple communication systems (radio + phone)",
            "Regular equipment testing",
            "Backup communication devices",
            "Emergency communication protocols",
            "Signal boosters where required",
            "Visual communication backup procedures"
        ],
        "references": ["AGTTM Section 7.6", "Communication protocols"],
        "agttm_rule": "riicwd503d_communication_systems"
    },
    {
        "id": "risk_023",
        "category": "people",
        "title": "Cyclist safety in work zone",
        "description": "Cyclists navigating through or around work area unsafely",
        "default_likelihood": "possible",
        "default_consequence": "extensive",
        "controls": [
            "Dedicated cyclist diversions where possible",
            "Clear signage for cyclists",
            "Adequate width for cyclist passage",
            "Smooth transitions and surfaces",
            "Separation from heavy vehicles",
            "Night lighting on cyclist paths"
        ],
        "references": ["AS 1742.3 Section 5.8", "AGTTM Cyclist Management"],
        "agttm_rule": "riicwd503d_cyclist_safety"
    },
    {
        "id": "risk_024",
        "category": "people",
        "title": "Manual handling injuries",
        "description": "Workers injured while lifting or moving traffic control equipment",
        "default_likelihood": "possible",
        "default_consequence": "moderate",
        "controls": [
            "Manual handling training for all workers",
            "Mechanical aids for heavy equipment",
            "Team lifting procedures",
            "Ergonomic equipment design",
            "Regular breaks and job rotation",
            "Pre-work stretching and warm-up"
        ],
        "references": ["Safe Work Australia Manual Handling Guide", "WHS Act"],
        "agttm_rule": "riicwd503d_manual_handling"
    },
    {
        "id": "risk_025",
        "category": "reputation",
        "title": "Accessibility issues for disabled persons",
        "description": "Work zone creating barriers for people with disabilities",
        "default_likelihood": "likely",
        "default_consequence": "moderate",
        "controls": [
            "DDA-compliant pedestrian diversions",
            "Tactile indicators maintained",
            "Accessible routes clearly marked",
            "Consultation with disability advocacy groups",
            "Audio warnings where appropriate",
            "Alternative access arrangements communicated"
        ],
        "references": ["DDA Standards", "AS 1428 Design for Access"],
        "agttm_rule": "riicwd503d_accessibility"
    }
]

def calculate_risk_score(likelihood: str, consequence: str) -> dict:
    """Calculate risk score and rating based on likelihood and consequence"""
    l_level = LIKELIHOOD_LEVELS.get(likelihood, {}).get("level", 3)
    c_level = CONSEQUENCE_LEVELS.get(consequence, {}).get("level", 3)
    
    score = l_level * c_level
    
    # Risk rating matrix
    if score <= 4:
        rating = "Low"
        color = "#4CAF50"
        action = "Monitor and maintain existing controls"
    elif score <= 9:
        rating = "Medium"
        color = "#FFC107"
        action = "Review controls and consider enhancements"
    elif score <= 16:
        rating = "High"
        color = "#FF9800"
        action = "Immediate action required to reduce risk"
    else:
        rating = "Critical"
        color = "#F44336"
        action = "Work should not proceed without additional controls"
    
    return {
        "score": score,
        "rating": rating,
        "color": color,
        "action": action
    }

def get_risk_registry():
    """Get complete risk registry with calculated scores"""
    enriched_registry = []
    
    for risk in RISK_REGISTRY:
        risk_data = risk.copy()
        risk_score = calculate_risk_score(
            risk["default_likelihood"],
            risk["default_consequence"]
        )
        risk_data["risk_score"] = risk_score
        enriched_registry.append(risk_data)
    
    return enriched_registry
