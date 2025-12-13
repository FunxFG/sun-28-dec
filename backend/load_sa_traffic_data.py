"""
Load SA Traffic Volume Data into MongoDB
One-time data import script for 2024 traffic volumes
"""
import json
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def load_traffic_data():
    """Load GeoJSON traffic data into MongoDB"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.trafsafe
    
    # Create or get collection
    collection = db.sa_traffic_volumes
    
    print("Loading GeoJSON file...")
    with open('/tmp/TrafficVolumeEstimates_WGS1984.geojson', 'r') as f:
        data = json.load(f)
    
    features = data.get('features', [])
    print(f"Found {len(features)} road segments")
    
    # Drop existing collection to start fresh
    await collection.drop()
    print("Cleared existing data")
    
    # Prepare documents for MongoDB
    documents = []
    for feature in features:
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        # Convert to MongoDB document with GeoJSON geometry
        doc = {
            'road_no': props.get('ROAD_NO'),
            'tesecn_id': props.get('TESECN_ID'),
            'aadt': int(props.get('TESECN_VOLUME', 0)),
            'base_year': props.get('TESECN_BASE_YEAR'),
            'projected_year': props.get('TESECN_PROJECTED_YEAR'),
            'heavy_vehicle_percent': props.get('CV_PERCENT'),
            'number_heavy_vehicles': props.get('NUMBER_CVS'),
            'traffic_score': props.get('TRAFFIC_SCORE'),
            'start_distance': props.get('TESECN_START_RRD'),
            'end_distance': props.get('TESECN_END_RRD'),
            'geometry': geom,  # Store GeoJSON geometry for spatial queries
            'loaded_at': datetime.utcnow(),
            'data_source': 'SA DIT Traffic Volume Estimates 2024'
        }
        documents.append(doc)
    
    # Insert all documents
    print(f"Inserting {len(documents)} documents...")
    if documents:
        result = await collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} documents")
    
    # Create geospatial index for fast proximity queries
    print("Creating geospatial index...")
    await collection.create_index([("geometry", "2dsphere")])
    
    # Create other useful indexes
    await collection.create_index("aadt")
    await collection.create_index("road_no")
    
    print("✅ Data loading complete!")
    print(f"   - {len(documents)} road segments loaded")
    print(f"   - Geospatial index created")
    print(f"   - Ready for spatial queries")
    
    # Test query
    print("\nTesting spatial query...")
    test_location = {
        "type": "Point",
        "coordinates": [138.5721, -34.8899]  # Torrens Road
    }
    
    nearest = await collection.find_one({
        "geometry": {
            "$near": {
                "$geometry": test_location,
                "$maxDistance": 1000  # 1km radius
            }
        }
    })
    
    if nearest:
        print(f"✅ Test passed! Found road with AADT: {nearest['aadt']}")
    else:
        print("⚠️ No data found within 1km of test location")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(load_traffic_data())
