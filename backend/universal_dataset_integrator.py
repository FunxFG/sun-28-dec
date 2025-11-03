"""
Universal SA Government Dataset Integrator
Automatically discovers resource IDs and integrates all priority datasets
"""

import httpx
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

SA_DATA_API_BASE = "https://data.sa.gov.au/data/api/3/action"
PACKAGE_SEARCH = f"{SA_DATA_API_BASE}/package_search"
DATASTORE_SEARCH = f"{SA_DATA_API_BASE}/datastore_search"
PACKAGE_SHOW = f"{SA_DATA_API_BASE}/package_show"


class SADatasetIntegrator:
    """Universal integrator for SA Government datasets"""
    
    def __init__(self):
        self.cache = {}
        self.resource_map = {}
    
    async def discover_dataset_resources(self, dataset_name_keywords: List[str]) -> List[Dict]:
        """
        Discover dataset resources by searching for keywords
        """
        discovered = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Search for packages matching keywords
                search_query = ' '.join(dataset_name_keywords)
                params = {
                    'q': search_query,
                    'rows': 20
                }
                
                response = await client.get(PACKAGE_SEARCH, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success') and data.get('result', {}).get('results'):
                        packages = data['result']['results']
                        
                        for package in packages:
                            package_name = package.get('name', '')
                            package_title = package.get('title', '')
                            
                            logger.info(f"Found package: {package_title}")
                            
                            # Get all resources from this package
                            for resource in package.get('resources', []):
                                discovered.append({
                                    'package_name': package_name,
                                    'package_title': package_title,
                                    'resource_id': resource.get('id'),
                                    'resource_name': resource.get('name', ''),
                                    'resource_format': resource.get('format', ''),
                                    'resource_url': resource.get('url', ''),
                                    'description': resource.get('description', ''),
                                    'last_modified': resource.get('last_modified', '')
                                })
                        
                        logger.info(f"Discovered {len(discovered)} resources for '{search_query}'")
                
        except Exception as e:
            logger.error(f"Error discovering resources: {str(e)}")
        
        return discovered
    
    async def fetch_dataset(self, resource_id: str, filters: Dict = None, limit: int = 1000) -> Dict[str, Any]:
        """
        Fetch data from a specific resource
        """
        result = {
            'success': False,
            'resource_id': resource_id,
            'records': [],
            'total_records': 0,
            'fields': [],
            'error': None
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    'resource_id': resource_id,
                    'limit': limit
                }
                
                # Add filters if provided
                if filters:
                    params.update(filters)
                
                response = await client.get(DATASTORE_SEARCH, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success') and data.get('result'):
                        result_data = data['result']
                        result['success'] = True
                        result['records'] = result_data.get('records', [])
                        result['total_records'] = result_data.get('total', 0)
                        result['fields'] = result_data.get('fields', [])
                        
                        logger.info(f"Fetched {len(result['records'])} records from resource {resource_id}")
                    else:
                        result['error'] = 'No data in response'
                else:
                    result['error'] = f'HTTP {response.status_code}'
                    logger.error(f"HTTP {response.status_code} for resource {resource_id}")
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error fetching dataset {resource_id}: {str(e)}")
        
        return result
    
    async def integrate_dataset_by_name(self, dataset_name: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Integrate a dataset by discovering it first, then fetching data
        """
        integration_result = {
            'dataset_name': dataset_name,
            'status': 'PENDING',
            'resources_found': 0,
            'data': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Discover resources
            logger.info(f"Discovering dataset: {dataset_name}")
            resources = await self.discover_dataset_resources(keywords)
            integration_result['resources_found'] = len(resources)
            
            if not resources:
                integration_result['status'] = 'FAILED'
                integration_result['error'] = 'No resources found'
                return integration_result
            
            # Step 2: Fetch data from first available resource
            primary_resource = resources[0]
            logger.info(f"Fetching data from resource: {primary_resource['resource_id']}")
            
            data = await self.fetch_dataset(primary_resource['resource_id'])
            
            if data['success']:
                integration_result['status'] = 'SUCCESS'
                integration_result['data'] = data
                integration_result['resource_id'] = primary_resource['resource_id']
                integration_result['resource_name'] = primary_resource['resource_name']
            else:
                integration_result['status'] = 'FAILED'
                integration_result['error'] = data['error']
            
        except Exception as e:
            integration_result['status'] = 'FAILED'
            integration_result['error'] = str(e)
            logger.error(f"Integration error for {dataset_name}: {str(e)}")
        
        return integration_result


async def integrate_phase1_datasets():
    """
    Integrate all Phase 1 (Critical Priority) datasets
    """
    integrator = SADatasetIntegrator()
    
    phase1_datasets = [
        {
            'name': 'Roadworks, Incidents & Road Closures',
            'keywords': ['roadworks', 'incidents', 'closures', 'detours', 'real-time']
        },
        {
            'name': 'Traffic Volumes - Top 40 Roads',
            'keywords': ['traffic volumes', 'top 40', 'road sections']
        },
        {
            'name': 'Traffic Volumes - Top 40 Intersections',
            'keywords': ['traffic volumes', 'intersections', 'top 40']
        },
        {
            'name': 'Bluetooth Detection Sites',
            'keywords': ['bluetooth', 'detection', 'travel time']
        },
        {
            'name': 'Travel Speed in Metropolitan Adelaide',
            'keywords': ['travel speed', 'metropolitan', 'adelaide']
        }
    ]
    
    print("=" * 80)
    print("PHASE 1: CRITICAL PRIORITY DATASETS INTEGRATION")
    print("=" * 80)
    
    results = []
    
    for dataset_config in phase1_datasets:
        print(f"\n{'='*80}")
        print(f"📊 Integrating: {dataset_config['name']}")
        print(f"{'='*80}")
        
        result = await integrator.integrate_dataset_by_name(
            dataset_config['name'],
            dataset_config['keywords']
        )
        
        results.append(result)
        
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_emoji} Status: {result['status']}")
        print(f"   Resources Found: {result['resources_found']}")
        
        if result['status'] == 'SUCCESS':
            print(f"   Resource ID: {result.get('resource_id', 'N/A')}")
            print(f"   Records Fetched: {result['data']['total_records']}")
            print(f"   Sample Fields: {[f['id'] for f in result['data']['fields'][:5]]}")
        else:
            print(f"   Error: {result['error']}")
    
    # Save results
    with open('/app/phase1_integration_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("PHASE 1 INTEGRATION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"\n💾 Results saved to: /app/phase1_integration_results.json")
    
    return results


if __name__ == "__main__":
    results = asyncio.run(integrate_phase1_datasets())
