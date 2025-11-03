"""
Systematic SA Government Dataset Integration
Step-by-step integration of all 98 priority datasets for TMP system

Integration Progress Tracker
"""

INTEGRATION_PHASES = {
    'Phase 1 - Real-Time Traffic Intelligence (CRITICAL)': {
        'priority': 'CRITICAL',
        'datasets': [
            {
                'id': 1,
                'name': 'Roadworks, Incidents & Road Closures Real-time',
                'resource_id': '8d75dfcc-cc95-4be3-8747-ff273e8c53db',
                'update_frequency': 'Real-time',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Prevent TMP conflicts with existing roadworks'
            },
            {
                'id': 2,
                'name': 'Traffic Volumes - Top 40 Road Sections',
                'resource_id': '6d9f9ab2-85eb-49ee-8124-d4bd9c1764e9',
                'update_frequency': 'Daily',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Actual AADT data for major roads'
            },
            {
                'id': 3,
                'name': 'Traffic Volumes - Top 40 Intersections',
                'resource_id': '30923a23-a396-445c-a082-43dc19c2f789',
                'update_frequency': 'Daily',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Intersection turning movement volumes'
            },
            {
                'id': 4,
                'name': 'Bluetooth Detection Sites',
                'resource_id': '54b072b7-ce24-48f5-9b57-e5e9bf380c00',
                'update_frequency': 'As required',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Real travel times and origin-destination'
            },
            {
                'id': 5,
                'name': 'Travel Speed in Metropolitan Adelaide',
                'resource_id': '6165be8c-de3c-43df-b8ef-adecda469880',
                'update_frequency': 'Annual',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Average travel speeds by road segment'
            }
        ]
    },
    'Phase 2 - Infrastructure & Signals (HIGH VALUE)': {
        'priority': 'HIGH',
        'datasets': [
            {
                'id': 6,
                'name': 'SA Signalised Intersections and Crossings',
                'resource_id': 'a9cf6a81-9454-4d43-9dab-66b85439bf01',
                'update_frequency': 'Quarterly',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': '500+ traffic signals with coordination info'
            },
            {
                'id': 7,
                'name': 'Pedestrian Crossings',
                'resource_id': '2d972378-33e0-4be3-a412-c65a02fccb25',
                'update_frequency': 'As required',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'All pedestrian crossing locations'
            },
            {
                'id': 8,
                'name': 'Traffic Lane Vehicle Counts at Signals',
                'resource_id': 'e6c1f446-de74-4270-811d-5dc5ec79643b',
                'update_frequency': 'Once off',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Lane-by-lane traffic volumes'
            },
            {
                'id': 9,
                'name': 'State Maintained Structures (Bridges)',
                'resource_id': '5e3310bb-b963-4079-aaef-5a8e345266e7',
                'update_frequency': 'Weekly',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Bridge locations and constraints'
            },
            {
                'id': 10,
                'name': 'Bike and Pedestrian Paths',
                'resource_id': '0f2403fd-a8f9-4d4c-9fb3-8a613c7b4022',
                'update_frequency': 'Daily',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Cycling and walking infrastructure'
            }
        ]
    },
    'Phase 3 - Public Transport (HIGH VALUE)': {
        'priority': 'HIGH',
        'datasets': [
            {
                'id': 11,
                'name': 'Adelaide Metro Real-Time Passenger Info',
                'resource_id': 'e794a379-fbf5-457f-b195-7a0be974cc69',
                'update_frequency': 'Real-time/Daily',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Live bus/tram/train positions'
            },
            {
                'id': 12,
                'name': 'Adelaide Public Transport Stop Data',
                'resource_id': '0d2f65f9-4386-4352-b46e-1259ebc06afe',
                'update_frequency': 'Weekly',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': '3000+ bus/tram/train stops'
            },
            {
                'id': 13,
                'name': 'Adelaide Metro General Transit Feed (GTFS)',
                'resource_id': '4e191c1e-b971-441f-83f7-45e266c41b99',
                'update_frequency': 'Daily',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Complete transit schedule data'
            }
        ]
    },
    'Phase 4 - Parking & Access (MEDIUM VALUE)': {
        'priority': 'MEDIUM',
        'datasets': [
            {
                'id': 14,
                'name': 'On Street Parking Zones',
                'resource_id': '0cb3b204-41f6-4703-aabf-c8c5adfc08d0',
                'update_frequency': 'Weekly',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Parking zone boundaries and restrictions'
            },
            {
                'id': 15,
                'name': 'Disability Parking Permits by Postcode',
                'resource_id': 'a993b8a0-e6d1-4149-8f37-02c9089668b5',
                'update_frequency': 'Other',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Accessible parking requirements'
            },
            {
                'id': 16,
                'name': 'Bluebays Accessible Car Parks',
                'resource_id': '5a561b5b-3989-4fae-8088-247be8110222',
                'update_frequency': 'Infrequently',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Disabled parking bay locations'
            }
        ]
    },
    'Phase 5 - Infrastructure Assets (MEDIUM VALUE)': {
        'priority': 'MEDIUM',
        'datasets': [
            {
                'id': 17,
                'name': 'State Maintained Roads',
                'resource_id': '23633a1b-27c6-41fc-84cc-e43afc24996f',
                'update_frequency': 'Weekly',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Official state road network'
            },
            {
                'id': 18,
                'name': 'Regulatory Signs on State Roads',
                'resource_id': 'dfb0e89b-1dc8-47e4-a9a6-eaf6fb199cb5',
                'update_frequency': 'As required',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Existing sign inventory'
            },
            {
                'id': 19,
                'name': 'Road Maintenance Markers',
                'resource_id': '781a1a63-604f-4e40-aefc-a56699e849ec',
                'update_frequency': 'Weekly',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Road chainage and markers'
            },
            {
                'id': 20,
                'name': 'Emergency Location Markers',
                'resource_id': 'TBD',
                'update_frequency': 'As required',
                'api_endpoint': 'https://data.sa.gov.au/data/api/3/action/datastore_search',
                'status': 'PENDING',
                'value': 'Emergency access points'
            }
        ]
    }
}

# Total: 20 highest priority datasets to start
# Additional 78 datasets available for subsequent phases
