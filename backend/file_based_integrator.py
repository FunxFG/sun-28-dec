"""
File-Based SA Dataset Integration
Downloads and parses CSV/JSON files from data.sa.gov.au for datasets not accessible via API
"""

import httpx
import asyncio
import pandas as pd
import json
from typing import Dict, Any, List
from io import StringIO
import logging

logger = logging.getLogger(__name__)

# Dataset URLs for direct file download
DATASET_FILES = {
    'signalised_intersections': {
        'name': 'SA Signalised Intersections and Crossings',
        'url': 'https://data.sa.gov.au/data/dataset/a9cf6a81-9454-4d43-9dab-66b85439bf01/resource/latest/download',
        'format': 'csv',
        'fields': ['intersection_id', 'location', 'latitude', 'longitude', 'type']
    },
    'pedestrian_crossings': {
        'name': 'Pedestrian Crossings',
        'url': 'https://data.sa.gov.au/data/dataset/2d972378-33e0-4be3-a412-c65a02fccb25/resource/latest/download',
        'format': 'csv',
        'fields': ['crossing_id', 'location', 'latitude', 'longitude', 'type']
    },
    'parking_zones': {
        'name': 'On Street Parking Zones',
        'url': 'https://data.sa.gov.au/data/dataset/0cb3b204-41f6-4703-aabf-c8c5adfc08d0/resource/latest/download',
        'format': 'csv',
        'fields': ['zone_id', 'location', 'restrictions']
    },
    'bike_paths': {
        'name': 'Bike and Pedestrian Paths',
        'url': 'https://data.sa.gov.au/data/dataset/0f2403fd-a8f9-4d4c-9fb3-8a613c7b4022/resource/latest/download',
        'format': 'csv',
        'fields': ['path_id', 'name', 'type', 'geometry']
    }
}


async def download_and_parse_dataset(dataset_key: str, config: Dict) -> Dict[str, Any]:
    """
    Download and parse a dataset from CSV/JSON file
    """
    result = {
        'dataset': config['name'],
        'status': 'PENDING',
        'records': [],
        'total_records': 0,
        'error': None
    }
    
    try:
        logger.info(f"Downloading {config['name']} from {config['url']}")
        
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # Try to download the file
            response = await client.get(config['url'])
            
            if response.status_code == 200:
                content = response.text
                
                if config['format'] == 'csv':
                    # Parse CSV
                    df = pd.read_csv(StringIO(content))
                    
                    # Convert to records
                    result['records'] = df.to_dict('records')
                    result['total_records'] = len(df)
                    result['columns'] = df.columns.tolist()
                    result['status'] = 'SUCCESS'
                    
                    logger.info(f"Successfully parsed {result['total_records']} records from {config['name']}")
                    
                elif config['format'] == 'json':
                    # Parse JSON
                    data = json.loads(content)
                    result['records'] = data if isinstance(data, list) else [data]
                    result['total_records'] = len(result['records'])
                    result['status'] = 'SUCCESS'
                    
            else:
                result['status'] = 'FAILED'
                result['error'] = f'HTTP {response.status_code}'
                logger.error(f"Failed to download {config['name']}: HTTP {response.status_code}")
                
    except Exception as e:
        result['status'] = 'FAILED'
        result['error'] = str(e)
        logger.error(f"Error processing {config['name']}: {str(e)}")
    
    return result


async def integrate_all_file_based_datasets():
    """
    Attempt to download and parse all file-based datasets
    """
    print("=" * 80)
    print("FILE-BASED DATASET INTEGRATION")
    print("=" * 80)
    
    results = {}
    
    for key, config in DATASET_FILES.items():
        print(f"\n{'='*80}")
        print(f"📥 Downloading: {config['name']}")
        print(f"{'='*80}")
        
        result = await download_and_parse_dataset(key, config)
        results[key] = result
        
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_emoji} Status: {result['status']}")
        
        if result['status'] == 'SUCCESS':
            print(f"   Records: {result['total_records']}")
            print(f"   Columns: {result.get('columns', [])[:8]}")
            
            # Show sample record
            if result['records']:
                print(f"   Sample: {list(result['records'][0].keys())[:5]}")
        else:
            print(f"   Error: {result['error']}")
    
    # Save results
    with open('/app/file_based_integration_results.json', 'w') as f:
        # Remove actual records to keep file size manageable
        summary = {k: {**v, 'records': f"[{v['total_records']} records - not saved]"} 
                  for k, v in results.items()}
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 80)
    print("FILE-BASED INTEGRATION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"\n💾 Results saved to: /app/file_based_integration_results.json")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(integrate_all_file_based_datasets())
