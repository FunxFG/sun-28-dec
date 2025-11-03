from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import jwt
import hashlib
import httpx
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import base64
from risk_registry import (
    get_risk_registry,
    calculate_risk_score,
    RISK_CATEGORIES,
    LIKELIHOOD_LEVELS,
    CONSEQUENCE_LEVELS
)
from device_library import (
    DEVICE_LIBRARY,
    DEVICE_CATEGORIES,
    get_device_by_code,
    get_devices_by_category,
    search_devices,
    get_required_devices_for_scenario
)
from enhanced_device_library import (
    get_device_library,
    get_sa_sign_by_code,
    search_sa_signs,
    get_sa_signs_by_category,
    get_recommended_signs_for_tmp,
    get_device_statistics,
    SA_SIGNS,
    CORE_DEVICE_LIBRARY
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Traffic Management Plan API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
JWT_SECRET = "traffic-management-secret-key-2025"

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    company_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CompanyDetails(BaseModel):
    name: str
    address: str
    abn: str
    phone: str
    liaison_name: str
    liaison_phone: str
    liaison_email: str

class TrafficManagementCompany(BaseModel):
    name: str
    address: str
    phone: str
    liaison_name: str
    liaison_phone: str
    liaison_email: str

class WorkDetails(BaseModel):
    work_type: str  # emergency, maintenance, construction
    work_style: str  # static, mobile
    description: str
    start_date: str
    end_date: str
    start_address: str
    end_address: str

class RoadOccupancy(BaseModel):
    """Comprehensive road occupancy options - can vary by time/stage"""
    
    # Footpath/Shoulder Occupancy
    footpath: bool = False
    left_shoulder: bool = False
    right_shoulder: bool = False
    
    # Lane Occupancy
    left_lane: bool = False
    center_lane: bool = False
    right_lane: bool = False
    turning_lane: bool = False
    
    # Other Occupancy
    median_strip: bool = False
    parking_lane: bool = False
    bike_lane: bool = False
    bus_lane: bool = False
    
    # Complete Closures
    complete_road_closure: bool = False
    full_carriageway_closure: bool = False
    
    # Time-based Occupancy
    occupancy_schedule: Optional[str] = None  # e.g., "Mon-Fri 9am-3pm", "Night works 7pm-6am"
    
    # Stage-based Occupancy
    stage_1_occupancy: Optional[str] = None
    stage_2_occupancy: Optional[str] = None
    stage_3_occupancy: Optional[str] = None
    
    # Work Zone Details
    workzone_length: Optional[float] = None  # meters
    taper_length: Optional[float] = None  # meters
    buffer_length: Optional[float] = None  # meters
    
    # Traffic Impact
    lanes_closed_count: int = 0
    lanes_remaining_count: Optional[int] = None
    estimated_delay_minutes: Optional[int] = None
    
    # Additional Notes
    occupancy_notes: Optional[str] = None

class ControlMeasures(BaseModel):
    """Comprehensive Austroads/AS 1742.3 approved traffic control measures"""
    
    # Temporal Controls
    twenty_min_rule: bool = False
    night_works_only: bool = False
    off_peak_hours: bool = False
    weekend_works: bool = False
    staged_works: bool = False
    
    # Speed Management
    speed_reduction: bool = False
    temporary_speed_limit_40: bool = False
    temporary_speed_limit_60: bool = False
    temporary_speed_limit_80: bool = False
    variable_speed_limits: bool = False
    
    # Traffic Control Devices
    static_signs: bool = False
    portable_vms: bool = False
    arrow_boards: bool = False
    temporary_traffic_signals: bool = False
    stop_slow_bats: bool = False
    
    # Lane Management
    lane_closure: bool = False
    lane_shift: bool = False
    contra_flow: bool = False
    shoulder_use: bool = False
    merge_taper: bool = False
    
    # Road Closure & Diversion
    complete_road_closure: bool = False
    detour: bool = False
    local_access_only: bool = False
    
    # Pedestrian & Cyclist Management
    pedestrian_detour: bool = False
    temporary_footpath: bool = False
    cyclist_detour: bool = False
    shared_path_closure: bool = False
    
    # Parking & Loading
    parking_restrictions: bool = False
    no_stopping_zone: bool = False
    loading_zone_suspension: bool = False
    
    # Public Transport
    bus_stop_relocation: bool = False
    public_transport_coordination: bool = False
    
    # Safety Systems
    safety_barriers: bool = False
    water_filled_barriers: bool = False
    concrete_barriers: bool = False
    delineation_devices: bool = False
    lighting_systems: bool = False
    
    # Monitoring & Management
    traffic_management_plan: bool = False
    traffic_controllers: bool = False
    cctv_monitoring: bool = False
    incident_response_plan: bool = False
    
    # Communication
    public_notification: bool = False
    stakeholder_consultation: bool = False
    emergency_services_notification: bool = False
    media_release: bool = False
    
    # Environmental
    dust_suppression: bool = False
    noise_management: bool = False
    vibration_monitoring: bool = False
    
    # Additional Notes
    control_measures_notes: Optional[str] = None


class RoadData(BaseModel):
    traffic_volume: Optional[int] = None
    road_classification: Optional[str] = None
    road_type: Optional[str] = None
    governing_body: Optional[str] = None
    workzone_size: Optional[float] = None

class TrafficDevice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_type: str
    device_name: str
    position_lat: float
    position_lng: float
    properties: Dict[str, Any] = {}

class TrafficManagementPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_name: str
    company_details: CompanyDetails
    traffic_company: TrafficManagementCompany
    work_details: WorkDetails
    road_occupancy: RoadOccupancy
    control_measures: ControlMeasures
    road_data: RoadData
    devices: List[TrafficDevice] = []
    map_center_lat: float
    map_center_lng: float
    map_zoom: int = 15
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrafficManagementPlanCreate(BaseModel):
    plan_name: str
    company_details: CompanyDetails
    traffic_company: TrafficManagementCompany
    work_details: WorkDetails
    road_occupancy: RoadOccupancy
    control_measures: ControlMeasures
    road_data: RoadData
    devices: List[TrafficDevice] = []
    map_center_lat: float
    map_center_lng: float
    map_zoom: int = 15

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc).timestamp() + 86400  # 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    return verify_jwt_token(credentials.credentials)

# Authentication routes
@api_router.post("/auth/register", response_model=Dict)
async def register_user(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["password"] = hash_password(user_data.password)
    user_obj = User(
        email=user_data.email,
        company_name=user_data.company_name
    )
    user_dict["id"] = user_obj.id
    user_dict["created_at"] = user_obj.created_at
    
    await db.users.insert_one(user_dict)
    
    token = create_jwt_token(user_obj.id, user_obj.email)
    return {"token": token, "user": {"id": user_obj.id, "email": user_obj.email, "company_name": user_obj.company_name}}

@api_router.post("/auth/login", response_model=Dict)
async def login_user(login_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": login_data.email})
    if not user or user["password"] != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["id"], user["email"])
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "company_name": user["company_name"]}}

# Traffic Management Plan routes
@api_router.post("/plans", response_model=TrafficManagementPlan)
async def create_plan(plan_data: TrafficManagementPlanCreate, current_user: Dict = Depends(get_current_user)):
    plan_dict = plan_data.dict()
    plan_obj = TrafficManagementPlan(
        user_id=current_user["user_id"],
        **plan_dict
    )
    
    # Prepare for MongoDB
    plan_dict_for_mongo = plan_obj.dict()
    plan_dict_for_mongo["created_at"] = plan_obj.created_at.isoformat()
    plan_dict_for_mongo["updated_at"] = plan_obj.updated_at.isoformat()
    
    await db.plans.insert_one(plan_dict_for_mongo)
    return plan_obj

@api_router.get("/plans", response_model=List[TrafficManagementPlan])
async def get_user_plans(current_user: Dict = Depends(get_current_user)):
    plans = await db.plans.find({"user_id": current_user["user_id"]}).to_list(1000)
    result = []
    for plan in plans:
        # Parse dates back from MongoDB
        if isinstance(plan.get("created_at"), str):
            plan["created_at"] = datetime.fromisoformat(plan["created_at"])
        if isinstance(plan.get("updated_at"), str):
            plan["updated_at"] = datetime.fromisoformat(plan["updated_at"])
        result.append(TrafficManagementPlan(**plan))
    return result

@api_router.get("/plans/{plan_id}", response_model=TrafficManagementPlan)
async def get_plan(plan_id: str, current_user: Dict = Depends(get_current_user)):
    plan = await db.plans.find_one({"id": plan_id, "user_id": current_user["user_id"]})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Parse dates back from MongoDB
    if isinstance(plan.get("created_at"), str):
        plan["created_at"] = datetime.fromisoformat(plan["created_at"])
    if isinstance(plan.get("updated_at"), str):
        plan["updated_at"] = datetime.fromisoformat(plan["updated_at"])
    
    return TrafficManagementPlan(**plan)

@api_router.put("/plans/{plan_id}", response_model=TrafficManagementPlan)
async def update_plan(plan_id: str, plan_data: TrafficManagementPlanCreate, current_user: Dict = Depends(get_current_user)):
    existing_plan = await db.plans.find_one({"id": plan_id, "user_id": current_user["user_id"]})
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    update_dict = plan_data.dict()
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.plans.update_one(
        {"id": plan_id, "user_id": current_user["user_id"]},
        {"$set": update_dict}
    )
    
    updated_plan = await db.plans.find_one({"id": plan_id})
    if isinstance(updated_plan.get("created_at"), str):
        updated_plan["created_at"] = datetime.fromisoformat(updated_plan["created_at"])
    if isinstance(updated_plan.get("updated_at"), str):
        updated_plan["updated_at"] = datetime.fromisoformat(updated_plan["updated_at"])
    
    return TrafficManagementPlan(**updated_plan)

@api_router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, current_user: Dict = Depends(get_current_user)):
    result = await db.plans.delete_one({"id": plan_id, "user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}

# Google Maps integration routes
@api_router.get("/geocode")
async def geocode_address(address: str):
    """Get coordinates from address using Google Maps Geocoding API"""
    api_key = "AIzaSyBbADUvXPuDrd51iZogWd6sR-DMolBjHfs"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            result = data["results"][0]
            location = result["geometry"]["location"]
            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "formatted_address": result["formatted_address"]
            }
        else:
            raise HTTPException(status_code=400, detail="Address not found")

# ===================================================
# SA GOVERNMENT TRAFFIC VOLUMES INTEGRATION
# ===================================================

SA_TRAFFIC_DATA = None  # Will be loaded on first use

async def fetch_sa_traffic_volume(lat: float, lng: float):
    """
    Fetch official traffic volumes from SA Government dataset
    Uses 2024 Traffic Volume Estimates GeoJSON data
    """
    global SA_TRAFFIC_DATA
    
    try:
        # Load data on first use (caching)
        if SA_TRAFFIC_DATA is None:
            import json
            import os
            
            geojson_path = '/tmp/sa_traffic_volumes_2024.geojson'
            if os.path.exists(geojson_path):
                with open(geojson_path, 'r') as f:
                    SA_TRAFFIC_DATA = json.load(f)
                logger.info(f"Loaded {len(SA_TRAFFIC_DATA['features'])} SA traffic volume segments")
            else:
                logger.warning("SA traffic data not found - will use fallback")
                return None
        
        if not SA_TRAFFIC_DATA:
            return None
        
        # Find nearest road segment within 100m
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance in meters between two points"""
            R = 6371000  # Earth radius in meters
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        nearest_segment = None
        min_distance = float('inf')
        
        for feature in SA_TRAFFIC_DATA['features']:
            if feature['geometry']['type'] == 'LineString':
                coords = feature['geometry']['coordinates']
                # Check distance to start and end points
                for coord in [coords[0], coords[-1]]:
                    dist = haversine_distance(lat, lng, coord[1], coord[0])
                    if dist < min_distance:
                        min_distance = dist
                        nearest_segment = feature
        
        # Only use if within 100m
        if nearest_segment and min_distance < 100:
            props = nearest_segment['properties']
            
            return {
                'aadt': int(props.get('TESECN_VOLUME', 0)) if props.get('TESECN_VOLUME') else None,
                'road_no': props.get('ROAD_NO'),
                'section_id': props.get('TESECN_ID'),
                'base_year': props.get('TESECN_BASE_YEAR'),
                'projected_year': props.get('TESECN_PROJECTED_YEAR'),
                'heavy_vehicle_pct': int(props.get('CV_PERCENT', 0)) if props.get('CV_PERCENT') else None,
                'distance_to_segment': round(min_distance, 1)
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching SA traffic volume: {str(e)}")
        return None

# ===================================================
# EXISTING TRAFFIC ASSESSMENT ENDPOINT (ENHANCED)
# ===================================================

@api_router.get("/traffic-assessment")
async def get_traffic_assessment(lat: float, lng: float, address: str):
    """
    Fetch comprehensive traffic assessment data from multiple sources
    - AADT from SA Government Traffic Volumes (official data)
    - Digital Atlas / OpenStreetMap (fallback)
    - Peak hour volumes (calculated)
    - Speed data from OSM
    - Crash history from state databases
    - Heavy vehicle data
    """
    try:
        # Try SA Government official traffic volumes FIRST
        sa_traffic_data = await fetch_sa_traffic_volume(lat, lng)
        
        # Get road data
        osm_data = await fetch_osm_road_data(lat, lng)
        
        # Use official SA data if available, otherwise calculate estimate
        if sa_traffic_data and sa_traffic_data.get('aadt'):
            aadt = sa_traffic_data['aadt']
            data_source = "SA Government Traffic Volumes 2024 (Official)"
            assessment_method = "Automated using SA DIT official traffic volume estimates"
        else:
            # Fallback to calculation
            aadt = calculate_aadt_from_classification(osm_data)
            data_source = osm_data.get('data_source', 'Estimated') if osm_data else 'Estimated'
            assessment_method = "Estimated from road classification (OSM/Digital Atlas)"
        
        # Calculate peak hour volume (typically 10% of AADT)
        peak_hour_volume = int(aadt * 0.10)
        
        # Get 85th percentile speed (typically speed limit + 5-10 km/h)
        speed_limit = osm_data.get('speed_limit', 60) if osm_data else 60
        percentile_85_speed = speed_limit + 8
        
        # Heavy vehicle percentage - use SA data if available
        if sa_traffic_data and sa_traffic_data.get('heavy_vehicle_pct'):
            heavy_vehicle_pct = sa_traffic_data['heavy_vehicle_pct']
        else:
            heavy_vehicle_pct = estimate_heavy_vehicle_percentage(osm_data)
        
        # Fetch crash data from state databases (if available)
        crash_history = await fetch_crash_history(lat, lng, address)
        
        result = {
            "aadt": aadt,
            "peak_hour_volume": peak_hour_volume,
            "85th_percentile_speed": f"{percentile_85_speed} km/h",
            "crash_history": crash_history,
            "heavy_vehicle_percentage": f"{heavy_vehicle_pct}%",
            "assessment_method": assessment_method,
            "data_source": data_source
        }
        
        # Include SA data details if available
        if sa_traffic_data:
            result['sa_traffic_details'] = {
                'road_no': sa_traffic_data.get('road_no'),
                'section_id': sa_traffic_data.get('section_id'),
                'base_year': sa_traffic_data.get('base_year'),
                'projected_year': sa_traffic_data.get('projected_year')
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching traffic assessment: {str(e)}")
        return {
            "aadt": 15000,
            "peak_hour_volume": 1500,
            "85th_percentile_speed": "65 km/h",
            "crash_history": "Data unavailable - manual assessment required",
            "heavy_vehicle_percentage": "12%",
            "assessment_method": "Estimated values",
            "data_source": "Fallback estimates"
        }

def calculate_aadt_from_classification(osm_data):
    """Calculate AADT based on road classification"""
    if not osm_data:
        return 15000
    
    classification = osm_data.get('road_classification', '')
    highway_type = osm_data.get('highway_type', '')
    
    # AADT estimates based on Austroads road classification
    aadt_estimates = {
        'National Highway': 45000,
        'Major Urban Arterial': 35000,
        'Major Urban Road': 25000,
        'Urban Collector': 12000,
        'Local Street': 3000
    }
    
    # OSM highway type mapping
    osm_estimates = {
        'motorway': 50000,
        'trunk': 40000,
        'primary': 30000,
        'secondary': 20000,
        'tertiary': 10000,
        'residential': 3000
    }
    
    # Try classification first
    if classification in aadt_estimates:
        return aadt_estimates[classification]
    
    # Fall back to highway type
    if highway_type in osm_estimates:
        return osm_estimates[highway_type]
    
    return 15000

def estimate_heavy_vehicle_percentage(osm_data):
    """Estimate heavy vehicle percentage based on road type"""
    if not osm_data:
        return 12
    
    classification = osm_data.get('road_classification', '')
    highway_type = osm_data.get('highway_type', '')
    
    # Heavy vehicle percentages by road type
    if 'Highway' in classification or highway_type in ['motorway', 'trunk']:
        return 18  # Higher on highways
    elif 'Arterial' in classification or highway_type == 'primary':
        return 15
    elif 'Collector' in classification or highway_type == 'secondary':
        return 10
    else:
        return 5  # Low on local streets

async def fetch_crash_history(lat: float, lng: float, address: str):
    """
    Fetch crash history from state databases
    This would integrate with state-specific crash databases
    """
    try:
        # Extract state from address
        state = extract_state_from_address(address)
        
        # State-specific crash database queries would go here
        # For now, return template with recommendation
        return f"Manual assessment required. Contact {state} road authority for crash data within 1km radius of location."
        
    except Exception as e:
        logger.error(f"Error fetching crash history: {str(e)}")
        return "No crash data available - contact local road authority"

def extract_state_from_address(address: str) -> str:
    """Extract Australian state from address"""
    states = {
        'NSW': 'NSW Transport Roads & Maritime',
        'VIC': 'VicRoads',
        'QLD': 'Queensland Department of Transport and Main Roads',
        'SA': 'Department for Infrastructure and Transport SA',
        'WA': 'Main Roads Western Australia',
        'TAS': 'Department of State Growth Tasmania',
        'NT': 'Department of Infrastructure NT',
        'ACT': 'Transport Canberra'
    }
    
    address_upper = address.upper()
    for code, authority in states.items():
        if code in address_upper:
            return authority
    
    return 'State Road Authority'

@api_router.get("/site-assessment")
async def get_site_assessment(lat: float, lng: float, address: str):
    """
    Fetch comprehensive site assessment data
    - Road geometry from OSM
    - Sight distances (calculated)
    - Parking restrictions from OSM
    - Public transport from transit APIs
    - Pedestrian/cyclist facilities from OSM
    - Utilities from government databases
    """
    try:
        # Get detailed OSM data
        osm_data = await fetch_detailed_osm_data(lat, lng)
        
        # Get public transport data
        public_transport = await fetch_public_transport(lat, lng)
        
        # Get parking restrictions
        parking = osm_data.get('parking', 'No restrictions - verify on site')
        
        # Calculate sight distances based on speed
        speed_limit = osm_data.get('speed_limit', 60)
        sight_distance = calculate_sight_distance(speed_limit)
        
        # Get pedestrian facilities
        pedestrian_facilities = extract_pedestrian_facilities(osm_data)
        
        # Get cyclist facilities
        cyclist_facilities = extract_cyclist_facilities(osm_data)
        
        # Get road geometry
        road_geometry = extract_road_geometry(osm_data)
        
        # Utilities information
        utilities = "Underground services - Dial Before You Dig (1100) required"
        
        # Environmental factors
        environmental = extract_environmental_factors(osm_data, address)
        
        return {
            "road_geometry": road_geometry,
            "sight_distances": sight_distance,
            "parking_restrictions": parking,
            "pedestrian_facilities": pedestrian_facilities,
            "cyclist_facilities": cyclist_facilities,
            "public_transport": public_transport,
            "utility_services": utilities,
            "environmental_factors": environmental
        }
        
    except Exception as e:
        logger.error(f"Error fetching site assessment: {str(e)}")
        return {
            "road_geometry": "2 lanes, 3.5m width each - verify on site",
            "sight_distances": "Minimum 100m - verify on site",
            "parking_restrictions": "Verify local parking controls",
            "pedestrian_facilities": "Footpaths present - assess accessibility",
            "cyclist_facilities": "No dedicated facilities observed",
            "public_transport": "Verify bus routes with local authority",
            "utility_services": "Dial Before You Dig (1100) required",
            "environmental_factors": "Standard urban environment"
        }

async def fetch_detailed_osm_data(lat: float, lng: float):
    """Fetch detailed OSM data including facilities"""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Comprehensive query for road and surrounding facilities
        query = f"""
        [out:json][timeout:15];
        (
          way(around:100,{lat},{lng})["highway"];
          way(around:100,{lat},{lng})["cycleway"];
          way(around:100,{lat},{lng})["footway"];
          way(around:100,{lat},{lng})["sidewalk"];
          node(around:200,{lat},{lng})["amenity"="parking"];
          node(around:500,{lat},{lng})["public_transport"];
        );
        out tags;
        """
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            
            if response.status_code == 200:
                data = response.json()
                return parse_osm_facilities(data)
            
            return {}
            
    except Exception as e:
        logger.error(f"Error fetching detailed OSM data: {str(e)}")
        return {}

def parse_osm_facilities(osm_response):
    """Parse OSM response for facility information"""
    facilities = {
        'lanes': None,
        'width': None,
        'cycleway': None,
        'sidewalk': None,
        'parking': [],
        'public_transport': []
    }
    
    for element in osm_response.get('elements', []):
        tags = element.get('tags', {})
        
        if 'lanes' in tags:
            facilities['lanes'] = tags['lanes']
        if 'width' in tags:
            facilities['width'] = tags['width']
        if 'cycleway' in tags:
            facilities['cycleway'] = tags['cycleway']
        if 'sidewalk' in tags:
            facilities['sidewalk'] = tags['sidewalk']
        if tags.get('amenity') == 'parking':
            facilities['parking'].append(tags.get('name', 'Parking area'))
        if 'public_transport' in tags:
            facilities['public_transport'].append(tags.get('name', 'Transit stop'))
    
    return facilities

async def fetch_public_transport(lat: float, lng: float):
    """Fetch public transport information near location"""
    try:
        # Query OSM for public transport
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
        [out:json][timeout:10];
        (
          node(around:500,{lat},{lng})["public_transport"="stop_position"];
          node(around:500,{lat},{lng})["highway"="bus_stop"];
          way(around:500,{lat},{lng})["railway"];
        );
        out body;
        """
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                
                if elements:
                    stops = [e.get('tags', {}).get('name', 'Transit stop') for e in elements if e.get('tags')]
                    if stops:
                        return f"Bus stops nearby: {', '.join(stops[:3])}"
                
            return "No public transport identified within 500m - verify with local authority"
            
    except Exception as e:
        logger.error(f"Error fetching public transport: {str(e)}")
        return "Public transport data unavailable - verify with local authority"

def calculate_sight_distance(speed_limit: int) -> str:
    """Calculate minimum sight distance based on speed"""
    # AS 1742.3 sight distance requirements
    sight_distances = {
        40: 40,
        50: 65,
        60: 85,
        70: 110,
        80: 130,
        90: 160,
        100: 185,
        110: 215
    }
    
    distance = sight_distances.get(speed_limit, 100)
    return f"Minimum {distance}m required (AS 1742.3) - verify on site"

def extract_pedestrian_facilities(osm_data: dict) -> str:
    """Extract pedestrian facility information"""
    facilities = []
    
    if osm_data.get('sidewalk'):
        facilities.append(f"Sidewalk: {osm_data['sidewalk']}")
    else:
        facilities.append("Footpath assessment required")
    
    facilities.append("Verify DDA compliance (1.2m min width)")
    facilities.append("Assess crossing points and ramps")
    
    return "; ".join(facilities)

def extract_cyclist_facilities(osm_data: dict) -> str:
    """Extract cyclist facility information"""
    cycleway = osm_data.get('cycleway')
    
    if cycleway:
        return f"Cycleway type: {cycleway} - maintain safe passage (1.5m min)"
    else:
        return "No dedicated cycle facilities - assess shared road usage"

def extract_road_geometry(osm_data: dict) -> str:
    """Extract road geometry information"""
    lanes = osm_data.get('lanes', '2')
    width = osm_data.get('width', '7.0m total')
    
    geometry = [
        f"{lanes} lanes",
        f"Width: {width}",
        "Verify curves, gradients, and intersections on site",
        "Check for median strips, shoulders, verges"
    ]
    
    return "; ".join(geometry)

def extract_environmental_factors(osm_data: dict, address: str) -> str:
    """Extract environmental factors"""
    factors = []
    
    # Urban/rural determination
    if 'CBD' in address.upper() or 'CITY' in address.upper():
        factors.append("Urban environment - noise and dust management required")
    elif any(word in address.upper() for word in ['HIGHWAY', 'FREEWAY', 'MOTORWAY']):
        factors.append("High-speed environment - enhanced safety measures")
    else:
        factors.append("Suburban environment - consider residential amenity")
    
    factors.append("Heritage considerations - check with local council")
    factors.append("Vegetation protection may be required")
    
    return "; ".join(factors)

@api_router.get("/road-data")
async def get_road_data(start_address: str, end_address: str):
    """Derive comprehensive road data from start and end addresses using OpenStreetMap"""
    # Get coordinates for both addresses
    start_coords = await geocode_address(start_address)
    end_coords = await geocode_address(end_address)
    
    # Calculate workzone size (distance between points)
    import math
    lat1, lng1 = math.radians(start_coords["lat"]), math.radians(start_coords["lng"])
    lat2, lng2 = math.radians(end_coords["lat"]), math.radians(end_coords["lng"])
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    distance = 2 * math.asin(math.sqrt(a)) * 6371000  # Earth radius in meters
    
    # Fetch actual road data from OpenStreetMap
    osm_road_data = await fetch_osm_road_data(start_coords["lat"], start_coords["lng"])
    
    # Use OSM data if available, otherwise fall back to estimation
    if osm_road_data:
        road_classification = osm_road_data.get('road_classification', 'Major Urban Road')
        speed_limit = osm_road_data.get('speed_limit', 60)
        road_type = osm_road_data.get('road_type', 'Arterial')
        road_name = osm_road_data.get('road_name', 'Unknown Road')
        surface = osm_road_data.get('surface', 'asphalt')
        lanes = osm_road_data.get('lanes', 2)
        
        logger.info(f"OSM data found: {road_name}, {road_classification}, {speed_limit}km/h")
    else:
        # Fallback to estimation
        logger.warning("OSM data not found, using estimation")
        road_classification = determine_road_classification(start_address, end_address)
        speed_limit = determine_speed_limit(road_classification, start_address)
        road_type = determine_road_type(road_classification)
        road_name = extract_road_name(start_address)
        surface = 'asphalt'
        lanes = 2
    
    traffic_volume = estimate_traffic_volume(road_classification, start_address)
    governing_body = determine_governing_body_from_classification(road_classification, start_address)
    
    # Add data accuracy note
    data_note = ""
    if osm_road_data:
        data_note = "Data from OpenStreetMap - lane counts and speeds may vary by section. Verify on-site."
    else:
        data_note = "Estimated data - verify all details on-site before plan submission."
    
    return {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "workzone_size": round(distance, 2),
        "traffic_volume": traffic_volume,
        "road_classification": road_classification,
        "road_type": road_type,
        "road_name": road_name,
        "governing_body": governing_body,
        "speed_limit": speed_limit,
        "surface": surface,
        "lanes": lanes,
        "environment": determine_environment(start_address),
        "austroads_category": determine_austroads_category(road_classification, traffic_volume),
        "data_source": "OpenStreetMap" if osm_road_data else "Estimated",
        "data_note": data_note
    }

async def fetch_osm_road_data(lat: float, lng: float):
    """Fetch road data from Digital Atlas of Australia (primary) and OpenStreetMap (fallback)"""
    try:
        # First try Digital Atlas of Australia for official Australian road data
        daa_data = await fetch_digital_atlas_road_data(lat, lng)
        if daa_data:
            logger.info(f"Using Digital Atlas data: {daa_data.get('road_name')}")
            return daa_data
        
        # Fallback to OpenStreetMap if Digital Atlas fails
        logger.info("Digital Atlas unavailable, using OpenStreetMap")
        
        # Overpass API query to get road/highway data near the coordinates
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Query for highway/road within 100m radius - get ALL roads to pick the most important
        query = f"""
        [out:json][timeout:10];
        (
          way(around:100,{lat},{lng})["highway"];
        );
        out tags;
        """
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(overpass_url, data={"data": query})
            
            if response.status_code != 200:
                logger.error(f"OSM Overpass API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('elements'):
                logger.warning("No road data found in OSM")
                return None
            
            # Sort roads by importance (prioritize major roads over residential)
            road_priority = {
                'motorway': 1,
                'trunk': 2,
                'primary': 3,
                'secondary': 4,
                'tertiary': 5,
                'unclassified': 6,
                'residential': 7,
                'service': 8,
                'track': 9
            }
            
            # Get the most important road (lowest priority number)
            roads = data['elements']
            roads.sort(key=lambda r: road_priority.get(r.get('tags', {}).get('highway', 'unclassified'), 10))
            
            road = roads[0]
            tags = road.get('tags', {})
            
            # Extract road information from OSM tags
            highway_type = tags.get('highway', 'unclassified')
            osm_name = tags.get('name', 'Unknown Road')
            osm_maxspeed = tags.get('maxspeed', None)
            osm_lanes = tags.get('lanes', None)
            osm_surface = tags.get('surface', 'asphalt')
            osm_ref = tags.get('ref', '')  # Road reference number (e.g., M1, A1)
            
            # Convert OSM highway type to Austroads classification
            road_classification = convert_osm_to_austroads_classification(highway_type, osm_ref)
            
            # Parse speed limit
            speed_limit = parse_osm_speed_limit(osm_maxspeed, highway_type)
            
            # Parse lanes
            lanes = int(osm_lanes) if osm_lanes and osm_lanes.isdigit() else estimate_lanes(highway_type)
            
            # Determine road type for AGTTM
            road_type = get_road_type_from_highway(highway_type)
            
            logger.info(f"OSM road found: {osm_name} ({highway_type}), {speed_limit}km/h, {lanes} lanes")
            
            return {
                'road_classification': road_classification,
                'road_type': road_type,
                'road_name': osm_name,
                'speed_limit': speed_limit,
                'lanes': lanes,
                'surface': osm_surface,
                'highway_type': highway_type,
                'reference': osm_ref,
                'data_source': 'OpenStreetMap'
            }
            
    except Exception as e:
        logger.error(f"Error fetching road data: {str(e)}")
        return None

async def fetch_digital_atlas_road_data(lat: float, lng: float):
    """Fetch road data from Digital Atlas of Australia National Roads dataset"""
    try:
        # Digital Atlas ArcGIS Feature Service endpoint for National Roads
        base_url = "https://services.ga.gov.au/gis/rest/services/NationalMap/National_Roads/MapServer/0/query"
        
        # Query parameters for spatial search
        params = {
            'f': 'json',
            'geometry': f'{lng},{lat}',
            'geometryType': 'esriGeometryPoint',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'distance': '100',  # Search within 100m
            'units': 'esriSRUnit_Meter',
            'outFields': '*',
            'returnGeometry': 'false'
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(base_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Digital Atlas API error: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('features') or len(data['features']) == 0:
                logger.warning("No road data found in Digital Atlas")
                return None
            
            # Get the first road feature (closest match)
            road_attrs = data['features'][0]['attributes']
            
            # Extract Australian road data
            road_name = road_attrs.get('ROADNAME') or road_attrs.get('NAME') or 'Unknown Road'
            road_class = road_attrs.get('CLASS') or road_attrs.get('ROAD_CLASS') or 'Local'
            road_type_code = road_attrs.get('TYPE') or road_attrs.get('ROAD_TYPE')
            surface = road_attrs.get('SURFACE', 'sealed')
            lanes = road_attrs.get('LANES', 2)
            state = road_attrs.get('STATE') or road_attrs.get('STATE_CODE')
            route_number = road_attrs.get('ROUTE_NUMBER') or road_attrs.get('ROUTE')
            
            # Convert Digital Atlas classification to Austroads standard
            road_classification = convert_digital_atlas_to_austroads(road_class, route_number)
            
            # Determine speed limit based on road classification and location
            speed_limit = determine_speed_limit_from_classification(road_classification, road_class)
            
            # Determine road type for AGTTM
            road_type = get_road_type_from_classification(road_classification)
            
            # Determine governing body
            governing_body = determine_governing_body_from_digital_atlas(road_class, state, route_number)
            
            logger.info(f"Digital Atlas road found: {road_name} ({road_classification}), {speed_limit}km/h")
            
            return {
                'road_classification': road_classification,
                'road_type': road_type,
                'road_name': road_name,
                'speed_limit': speed_limit,
                'lanes': int(lanes) if lanes else 2,
                'surface': surface,
                'route_number': route_number,
                'state': state,
                'governing_body': governing_body,
                'data_source': 'Digital Atlas of Australia',
                'official_data': True
            }
            
    except Exception as e:
        logger.error(f"Error fetching Digital Atlas data: {str(e)}")
        return None

def convert_digital_atlas_to_austroads(road_class: str, route_number: str) -> str:
    """Convert Digital Atlas road classification to Austroads standard"""
    if not road_class:
        return "Local Street"
    
    road_class_lower = road_class.lower()
    
    # National Highways (with route numbers like M1, A1, National Highway 1)
    if route_number and (route_number.startswith('M') or route_number.startswith('A') or 'National' in route_number):
        return "National Highway"
    
    # Map Digital Atlas classifications
    class_mapping = {
        'national': 'National Highway',
        'highway': 'National Highway',
        'freeway': 'National Highway',
        'motorway': 'National Highway',
        'arterial': 'Major Urban Arterial',
        'sub-arterial': 'Major Urban Arterial',
        'collector': 'Urban Collector',
        'distributor': 'Urban Collector',
        'local': 'Local Street',
        'access': 'Local Street'
    }
    
    for key, value in class_mapping.items():
        if key in road_class_lower:
            return value
    
    return "Major Urban Road"

def determine_speed_limit_from_classification(austroads_class: str, digital_atlas_class: str) -> int:
    """Determine speed limit from road classification"""
    speed_mapping = {
        'National Highway': 100,
        'Major Urban Arterial': 70,
        'Major Urban Road': 60,
        'Urban Collector': 60,
        'Local Street': 50
    }
    
    # Check for specific types
    if digital_atlas_class and 'freeway' in digital_atlas_class.lower():
        return 110
    if digital_atlas_class and 'motorway' in digital_atlas_class.lower():
        return 100
    
    return speed_mapping.get(austroads_class, 60)

def get_road_type_from_classification(austroads_class: str) -> str:
    """Get road type for AGTTM from Austroads classification"""
    type_mapping = {
        'National Highway': 'Divided Highway',
        'Major Urban Arterial': 'Arterial',
        'Major Urban Road': 'Arterial',
        'Urban Collector': 'Collector',
        'Local Street': 'Local'
    }
    return type_mapping.get(austroads_class, 'Arterial')

def determine_governing_body_from_digital_atlas(road_class: str, state: str, route_number: str) -> str:
    """Determine governing body from Digital Atlas road data"""
    if route_number and (route_number.startswith('M') or route_number.startswith('A') or 'National' in str(route_number)):
        return f"National Transport Commission / {state or 'State'} Government"
    
    if road_class and ('national' in road_class.lower() or 'highway' in road_class.lower()):
        return f"{state or 'State'} Government (Department of Transport)"
    
    if road_class and 'arterial' in road_class.lower():
        return f"{state or 'State'} Government (Main Roads)"
    
    return "Local Council"

def convert_osm_to_austroads_classification(highway_type: str, ref: str) -> str:
    """Convert OpenStreetMap highway type to Austroads road classification"""
    
    # National Highways (M prefix or specific names)
    if ref and (ref.startswith('M') or ref.startswith('A')):
        return "National Highway"
    
    # Map OSM highway types to Austroads classifications
    osm_to_austroads = {
        'motorway': 'National Highway',
        'trunk': 'National Highway',
        'primary': 'Major Urban Arterial',
        'secondary': 'Major Urban Arterial',
        'tertiary': 'Urban Collector',
        'residential': 'Local Street',
        'unclassified': 'Local Street',
        'service': 'Local Street',
        'living_street': 'Local Street'
    }
    
    return osm_to_austroads.get(highway_type, 'Major Urban Road')

def parse_osm_speed_limit(maxspeed: str, highway_type: str) -> int:
    """Parse OpenStreetMap speed limit tag"""
    if not maxspeed:
        # Default speeds based on highway type
        defaults = {
            'motorway': 100,
            'trunk': 100,
            'primary': 80,
            'secondary': 70,
            'tertiary': 60,
            'residential': 50,
            'living_street': 40,
            'service': 40
        }
        return defaults.get(highway_type, 60)
    
    # Parse speed limit (handle "60", "60 km/h", "60 mph" formats)
    maxspeed = maxspeed.lower().replace('km/h', '').replace('mph', '').strip()
    
    try:
        speed = int(maxspeed)
        # If it was in mph, convert to km/h
        if 'mph' in maxspeed.lower():
            speed = int(speed * 1.60934)
        return speed
    except ValueError:
        return 60  # Default to 60 km/h

def estimate_lanes(highway_type: str) -> int:
    """Estimate number of lanes based on highway type"""
    lane_estimates = {
        'motorway': 3,
        'trunk': 2,
        'primary': 2,
        'secondary': 2,
        'tertiary': 2,
        'residential': 1,
        'living_street': 1,
        'service': 1
    }
    return lane_estimates.get(highway_type, 2)

def get_road_type_from_highway(highway_type: str) -> str:
    """Get road type for AGTTM categorization from OSM highway type"""
    type_mapping = {
        'motorway': 'Divided Highway',
        'trunk': 'Divided Highway',
        'primary': 'Arterial',
        'secondary': 'Arterial',
        'tertiary': 'Collector',
        'residential': 'Local',
        'unclassified': 'Local',
        'service': 'Local',
        'living_street': 'Local'
    }
    return type_mapping.get(highway_type, 'Arterial')

def extract_road_name(address: str) -> str:
    """Extract road name from address string"""
    # Simple extraction - take first part before comma
    parts = address.split(',')
    return parts[0].strip() if parts else 'Unknown Road'

def determine_governing_body_from_classification(classification: str, address: str) -> str:
    """Determine governing body based on road classification"""
    if classification == "National Highway":
        return "National Transport Commission / State Government"
    elif classification in ["Major Urban Arterial", "Major Urban Road"]:
        # Check if it's a state-managed arterial
        if any(state in address.lower() for state in ['highway', 'arterial']):
            return "State Government (Department of Transport)"
        return "Local Council"
    else:
        return "Local Council"

def determine_road_classification(start_address: str, end_address: str) -> str:
    """Determine road classification based on address analysis"""
    address_lower = f"{start_address} {end_address}".lower()
    
    if any(highway in address_lower for highway in ['highway', 'freeway', 'motorway', 'pacific highway', 'bruce highway']):
        return "National Highway"
    elif any(arterial in address_lower for arterial in ['arterial', 'main road', 'ring road']):
        return "Major Urban Arterial"
    elif any(collector in address_lower for collector in ['collector', 'connecting road']):
        return "Urban Collector"
    elif any(local in address_lower for local in ['street', 'avenue', 'close', 'court', 'place']):
        return "Local Street"
    else:
        return "Major Urban Road"  # Default

def determine_speed_limit(road_classification: str, address: str) -> int:
    """Determine likely speed limit based on road classification and location"""
    if road_classification == "National Highway":
        return 100 if 'rural' in address.lower() else 80
    elif road_classification == "Major Urban Arterial":
        return 70
    elif road_classification == "Urban Collector":
        return 60
    elif road_classification == "Local Street":
        return 50
    else:
        return 60  # Default urban speed

def estimate_traffic_volume(road_classification: str, address: str) -> int:
    """Estimate Average Daily Traffic (ADT) based on road classification"""
    base_volumes = {
        "National Highway": 40000,
        "Major Urban Arterial": 25000,
        "Urban Collector": 15000,
        "Local Street": 3000,
        "Major Urban Road": 18000
    }
    
    base = base_volumes.get(road_classification, 15000)
    
    # Adjust for location (CBD vs suburban)
    if any(cbd in address.lower() for cbd in ['cbd', 'city', 'central', 'downtown']):
        return int(base * 1.5)
    elif any(suburban in address.lower() for suburban in ['suburban', 'residential']):
        return int(base * 0.7)
    
    return base

def determine_governing_body(address: str) -> str:
    """Determine which authority governs the road"""
    address_lower = address.lower()
    
    if any(state in address_lower for state in ['highway', 'state route', 'arterial']):
        return "State Government (DTMR)"
    elif any(council in address_lower for council in ['street', 'avenue', 'close', 'court']):
        return "Local Council"
    else:
        return "Local Council"  # Default for most urban roads

def determine_road_type(road_classification: str) -> str:
    """Determine road type for Austroads categorization"""
    type_mapping = {
        "National Highway": "Divided Highway",
        "Major Urban Arterial": "Arterial",
        "Urban Collector": "Collector",
        "Local Street": "Local",
        "Major Urban Road": "Arterial"
    }
    return type_mapping.get(road_classification, "Arterial")

def determine_environment(address: str) -> str:
    """Determine environmental context"""
    address_lower = address.lower()
    
    if any(urban in address_lower for urban in ['cbd', 'city', 'urban', 'street', 'avenue']):
        return "Urban"
    elif any(rural in address_lower for rural in ['rural', 'country', 'highway']):
        return "Rural"
    else:
        return "Urban"  # Default

def determine_austroads_category(road_classification: str, traffic_volume: int) -> str:
    """Determine Austroads traffic management category"""
    if traffic_volume > 30000:
        return "Category 1 - High Volume"
    elif traffic_volume > 15000:
        return "Category 2 - Medium Volume"
    elif traffic_volume > 5000:
        return "Category 3 - Low Volume"
    else:
        return "Category 4 - Very Low Volume"

# PDF generation
@api_router.get("/plans/{plan_id}/pdf")
async def generate_plan_pdf(plan_id: str, current_user: Dict = Depends(get_current_user)):
    plan = await db.plans.find_one({"id": plan_id, "user_id": current_user["user_id"]})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Import the TMP generator
    from tmp_generator import tmp_generator
    
    # Generate professional TMP structure
    professional_tmp = tmp_generator.generate_professional_tmp(plan, 'works')
    
    # Create PDF with professional TMP content
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          topMargin=1*inch, bottomMargin=1*inch,
                          leftMargin=1*inch, rightMargin=1*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for professional TMP
    title_style = ParagraphStyle(
        'TMPTitle',
        parent=styles['Title'],
        fontSize=16,
        fontName='Helvetica-Bold',
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'TMPHeading',
        parent=styles['Heading1'],
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=12,
        spaceBefore=20
    )
    
    subheading_style = ParagraphStyle(
        'TMPSubHeading',
        parent=styles['Heading2'],
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=6,
        spaceBefore=12
    )
    
    # TMP Header
    story.append(Paragraph("WORKS ON ROADS TRAFFIC MANAGEMENT PLAN", title_style))
    story.append(Paragraph(f"Work Type: {professional_tmp['tmp_header']['work_type']}", styles['Normal']))
    story.append(Paragraph(f"TMP Number: {professional_tmp['metadata']['tmp_number']}", styles['Normal']))
    story.append(Paragraph(f"Date: {professional_tmp['tmp_header']['tmp_identification']['date']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Declaration Section
    story.append(Paragraph("DECLARATION", heading_style))
    declaration = professional_tmp['declaration']['designer_declaration']
    story.append(Paragraph(f"I, {declaration['certifier_name']} (AWTM Cert No. {declaration['awtm_cert_number']}) "
                          f"declare that I have designed this Traffic Management Plan following a site inspection on "
                          f"{declaration['site_inspection_date']}.", styles['Normal']))
    story.append(Paragraph(declaration['compliance_statement'], styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Signature: ........................... Date: {declaration['signature_date']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Table of Contents
    story.append(Paragraph("TABLE OF CONTENTS", heading_style))
    toc_data = [['Section', 'Title', 'Page']]
    for item in professional_tmp['table_of_contents']:
        toc_data.append([item['section'], item['title'], str(item['page'])])
    
    toc_table = Table(toc_data, colWidths=[1*inch, 4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 30))
    
    # Section 1: Introduction
    intro = professional_tmp['sections']['1_introduction']
    story.append(Paragraph("1. INTRODUCTION", heading_style))
    
    story.append(Paragraph("1.1 Purpose and Scope", subheading_style))
    story.append(Paragraph(intro['1.1_purpose_and_scope']['purpose'], styles['Normal']))
    story.append(Paragraph(intro['1.1_purpose_and_scope']['scope'], styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.2 Objectives and Strategies", subheading_style))
    story.append(Paragraph("<b>Objectives:</b>", styles['Normal']))
    for obj in intro['1.2_objectives_and_strategies']['objectives']:
        story.append(Paragraph(f"• {obj}", styles['Normal']))
    
    story.append(Paragraph("<b>Strategies:</b>", styles['Normal']))
    for strategy in intro['1.2_objectives_and_strategies']['strategies']:
        story.append(Paragraph(f"• {strategy}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Section 2: Project Overview
    overview = professional_tmp['sections']['2_project_overview']
    story.append(Paragraph("2. PROJECT OVERVIEW", heading_style))
    
    story.append(Paragraph("2.1 Location", subheading_style))
    story.append(Paragraph(overview['2.1_location']['detailed_location'], styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.2 Project Details", subheading_style))
    details_data = [
        ['Item', 'Details'],
        ['Project Location', overview['2.2_project_details']['project_location']],
        ['Road Classification', overview['2.2_project_details']['road_classification']],
        ['Existing Speed Limit', overview['2.2_project_details']['existing_speed_limit']],
        ['Road Authority', overview['2.2_project_details']['road_authority']],
        ['Principal Contractor', overview['2.2_project_details']['principal_contractor']],
        ['Scope of Works', overview['2.2_project_details']['scope_of_works']],
        ['Project Dates', overview['2.2_project_details']['project_dates']],
        ['Work Hours', overview['2.2_project_details']['work_hours']]
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    # Section 3: Risk Management
    risk = professional_tmp['sections']['3_risk_management']
    story.append(Paragraph("3. RISK MANAGEMENT", heading_style))
    
    story.append(Paragraph("3.1 Risk Classification", subheading_style))
    story.append(Paragraph("Risk assessment follows the qualitative risk matrix approach with consequence and likelihood ratings.", styles['Normal']))
    
    # Risk Register
    story.append(Paragraph("3.2 Risk Register", subheading_style))
    risk_data = [['Risk Event', 'Consequence', 'Pre-Treatment Risk', 'Treatment', 'Residual Risk']]
    
    for risk_item in risk['3.2_risk_register']['generic_risks']:
        risk_data.append([
            risk_item['risk_event'],
            risk_item['consequence'],
            risk_item['pre_treatment_risk']['rating'],
            risk_item['treatment'],
            risk_item['residual_risk']['rating']
        ])
    
    risk_table = Table(risk_data, colWidths=[1.5*inch, 1.2*inch, 0.8*inch, 1.8*inch, 0.7*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 20))
    
    # Traffic Guidance Schemes
    if plan.get('devices'):
        story.append(Paragraph("TRAFFIC GUIDANCE SCHEMES", heading_style))
        story.append(Paragraph("The following traffic control devices have been positioned according to Austroads standards:", styles['Normal']))
        
        device_data = [['Device Type', 'Device Name', 'Position', 'Compliance']]
        for device in plan['devices']:
            compliance = "Auto-placed (AGTTM compliant)" if device.get('properties', {}).get('auto_placed') else "Manual placement"
            device_data.append([
                device['device_type'].title(),
                device['device_name'],
                f"Lat: {device['position_lat']:.6f}, Lng: {device['position_lng']:.6f}",
                compliance
            ])
        
        device_table = Table(device_data, colWidths=[1.2*inch, 2*inch, 1.8*inch, 1*inch])
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(device_table)
        story.append(Spacer(1, 20))
    
    # Implementation section
    impl = professional_tmp['sections']['7_implementation']
    story.append(Paragraph("7. IMPLEMENTATION", heading_style))
    
    story.append(Paragraph("7.1 Traffic Guidance Schemes", subheading_style))
    for stage_key, stage_info in impl['7.1_traffic_guidance_schemes'].items():
        story.append(Paragraph(f"<b>{stage_key.replace('_', ' ').title()}:</b> {stage_info['description']}", styles['Normal']))
    
    story.append(Paragraph("7.2 Sequence and Staging", subheading_style))
    for i, stage in enumerate(impl['7.2_sequence_staging'], 1):
        story.append(Paragraph(f"<b>Stage {i} - {stage['stage']}:</b>", styles['Normal']))
        story.append(Paragraph(stage['description'], styles['Normal']))
        story.append(Paragraph(f"Safety Measures: {stage['safety_measures']}", styles['Normal']))
        story.append(Spacer(1, 6))
    
    # Emergency contacts
    emergency = professional_tmp['sections']['8_emergency_arrangements']
    story.append(Paragraph("8. EMERGENCY ARRANGEMENTS", heading_style))
    
    story.append(Paragraph("8.5 Emergency Contacts", subheading_style))
    emergency_data = [['Service', 'Contact']]
    for service, contact in emergency['8.5_emergency_contacts'].items():
        emergency_data.append([service.replace('_', ' ').title(), contact])
    
    emergency_table = Table(emergency_data, colWidths=[2*inch, 2*inch])
    emergency_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(emergency_table)
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("This Traffic Management Plan has been prepared in accordance with:", styles['Normal']))
    for standard in professional_tmp['metadata']['compliance_standards']:
        story.append(Paragraph(f"• {standard}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}", styles['Normal']))
    story.append(Paragraph(f"Template Version: {professional_tmp['metadata']['template_version']}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(buffer.getvalue()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=TMP_{professional_tmp['metadata']['tmp_number']}.pdf"}
    )

# ==========================================
# Risk Management Endpoints
# ==========================================

@api_router.get("/risks")
async def get_risks():
    """
    Get comprehensive risk registry for roadwork traffic management
    Returns all 106 identified risks from expanded Austroads register
    """
    try:
        import csv
        import os
        
        risks = []
        csv_path = os.path.join(os.path.dirname(__file__), 'risk_data.csv')
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    risks.append({
                        'risk_id': row['ID'],
                        'category': row['Category'],
                        'subcategory': row['Subcategory'] if row['Subcategory'] else None,
                        'hazard': row['Hazard'],
                        'trigger': row['Trigger/Context'] if row['Trigger/Context'] else None,
                        'consequence': row['Potential Consequence'],
                        'likelihood': row['Likelihood'],
                        'risk_level': row['Risk Rating'],
                        'control_measures': row['Controls / Mitigation'],
                        'controls_hierarchy': row['Controls Hierarchy'],
                        'monitoring': row['Monitoring / Verification'],
                        'responsible': row['Responsible Role'],
                        'reference': row['Reference'],
                        'residual_risk': row['Residual Risk']
                    })
        else:
            logger.warning(f"Risk data CSV not found at {csv_path}")
        
        return risks
    except Exception as e:
        logger.error(f"Error loading risks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Duplicate endpoint - removed

@api_router.post("/risks/calculate")
async def calculate_risk(request: dict):
    """
    Calculate risk score based on likelihood and consequence
    Request body: {"likelihood": "possible", "consequence": "moderate"}
    """
    try:
        likelihood = request.get("likelihood")
        consequence = request.get("consequence")
        
        if not likelihood or not consequence:
            raise HTTPException(status_code=400, detail="likelihood and consequence are required")
        
        risk_score = calculate_risk_score(likelihood, consequence)
        return risk_score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/plans/{plan_id}/risk-assessment")
async def save_risk_assessment(plan_id: str, assessment: dict, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Save risk assessment for a specific traffic management plan
    """
    try:
        user_data = verify_token(credentials.credentials)
        
        # Update plan with risk assessment
        result = await db.plans.update_one(
            {"id": plan_id, "user_id": user_data["user_id"]},
            {"$set": {
                "risk_assessment": assessment,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {"message": "Risk assessment saved successfully"}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/plans/{plan_id}/risk-assessment")
async def get_plan_risk_assessment(plan_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get risk assessment for a specific traffic management plan
    """
    try:
        user_data = verify_token(credentials.credentials)
        
        plan = await db.plans.find_one({"id": plan_id, "user_id": user_data["user_id"]})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {
            "risk_assessment": plan.get("risk_assessment", {}),
            "plan_id": plan_id
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Risk Registry Endpoints
# ==========================================

@api_router.get("/risks")
async def get_risks(category: str = None):
    """
    Get comprehensive risk registry for roadwork traffic management
    Optional category filter: people, information, property, reputation, financial, capability
    """
    try:
        risks = get_risk_registry()
        
        if category:
            filtered_risks = [r for r in risks if r.get('category') == category]
            return {
                "category": category,
                "risks": filtered_risks,
                "count": len(filtered_risks)
            }
        
        return {
            "categories": RISK_CATEGORIES,
            "risks": risks,
            "total_risks": len(risks),
            "likelihood_levels": LIKELIHOOD_LEVELS,
            "consequence_levels": CONSEQUENCE_LEVELS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/risks/{risk_id}")
async def get_risk_details(risk_id: str):
    """
    Get detailed information for a specific risk by ID
    """
    try:
        risks = get_risk_registry()
        risk = next((r for r in risks if r.get('id') == risk_id), None)
        
        if not risk:
            raise HTTPException(status_code=404, detail=f"Risk {risk_id} not found")
        
        return risk
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/risks/calculate")
async def calculate_risk(risk_data: dict):
    """
    Calculate risk score based on likelihood and consequence
    Request body example:
    {
        "likelihood": "possible",
        "consequence": "significant"
    }
    """
    try:
        score = calculate_risk_score(
            risk_data.get('likelihood'),
            risk_data.get('consequence')
        )
        return {
            "likelihood": risk_data.get('likelihood'),
            "consequence": risk_data.get('consequence'),
            "risk_score": score
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Device Library Endpoints
# ==========================================

@api_router.get("/devices")
async def get_devices(category: str = None):
    """
    Get traffic control device library
    Optional category filter: warning, regulatory, guidance, delineation, barriers, signals, vehicles
    """
    try:
        if category:
            devices = get_devices_by_category(category)
            return {
                "category": category,
                "devices": devices
            }
        
        return {
            "categories": DEVICE_CATEGORIES,
            "library": DEVICE_LIBRARY,
            "total_devices": sum(len(devices) for devices in DEVICE_LIBRARY.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/devices/{code}")
async def get_device_details(code: str):
    """
    Get detailed specifications for a specific device by AS 1742.3 code
    """
    try:
        device = get_device_by_code(code)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {code} not found")
        
        return device
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/devices/search/{term}")
async def search_device_library(term: str):
    """
    Search device library by name, description, or code
    """
    try:
        results = search_devices(term)
        return {
            "query": term,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/devices/recommend")
async def recommend_devices(scenario: dict):
    """
    Get recommended devices based on work scenario
    Request body example:
    {
        "work_type": "static",
        "speed_limit": 80,
        "lanes": 2,
        "duration": "medium",
        "time_of_day": "day"
    }
    """
    try:
        devices = get_required_devices_for_scenario(**scenario)
        return {
            "scenario": scenario,
            "recommended_devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SA SIGN LIBRARY ENDPOINTS (NEW)
# ============================================

@api_router.get("/sa-signs/stats")
async def get_sa_sign_statistics():
    """
    Get statistics about the SA Sign Library
    Returns total signs, categories, etc.
    """
    try:
        stats = get_device_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sa-signs")
async def get_all_sa_signs(
    category: Optional[str] = None,
    limit: Optional[int] = 100,
    skip: Optional[int] = 0
):
    """
    Get all SA signs or filter by category
    Query params:
    - category: Filter by category (Warning, Regulatory, Guide, etc.)
    - limit: Max number of results (default 100)
    - skip: Number of records to skip (default 0)
    """
    try:
        if category:
            signs = get_sa_signs_by_category(category)
        else:
            signs = SA_SIGNS
        
        # Apply pagination
        paginated_signs = signs[skip:skip + limit]
        
        return {
            "total": len(signs),
            "skip": skip,
            "limit": limit,
            "signs": paginated_signs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sa-signs/search")
async def search_sa_sign_library(
    q: str,
    category: Optional[str] = None,
    limit: Optional[int] = 20
):
    """
    Search SA sign library by code or description
    Query params:
    - q: Search query (searches code and description)
    - category: Filter by category
    - limit: Max results (default 20)
    """
    try:
        results = search_sa_signs(q, category=category, limit=limit)
        return {
            "query": q,
            "category": category,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sa-signs/{code}")
async def get_sa_sign_by_sign_code(code: str):
    """
    Get a specific SA sign by its code
    Example: /api/sa-signs/T1-1 or /api/sa-signs/13699
    """
    try:
        sign = get_sa_sign_by_code(code)
        if not sign:
            raise HTTPException(status_code=404, detail=f"SA Sign {code} not found")
        
        return sign
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/sa-signs/recommend")
async def recommend_sa_signs_for_tmp(request: dict):
    """
    Get recommended SA signs for a TMP based on work type and road classification
    Request body example:
    {
        "work_type": "lane closure",
        "road_classification": "State Arterial Road"
    }
    """
    try:
        work_type = request.get('work_type', 'general')
        road_classification = request.get('road_classification', 'local')
        
        recommended = get_recommended_signs_for_tmp(work_type, road_classification)
        
        return {
            "work_type": work_type,
            "road_classification": road_classification,
            "recommended_signs": recommended,
            "count": len(recommended)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/devices/recommend")
async def recommend_devices_old(scenario: dict):
    """
    Get recommended devices based on work scenario
    Request body example:
    {
        "work_type": "static",
        "speed_limit": 80,
        "lanes": 2,
        "duration": "medium",
        "time_of_day": "day"
    }
    """
    try:
        required_codes = get_required_devices_for_scenario(scenario)
        devices = [get_device_by_code(code) for code in required_codes]
        
        return {
            "scenario": scenario,
            "recommended_devices": [dev for dev in devices if dev],
            "device_codes": required_codes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================
# COMPREHENSIVE AUTO-POPULATION ENDPOINT
# ===================================================

@api_router.get("/comprehensive-auto-populate")
async def get_comprehensive_auto_populate(
    lat: float, 
    lng: float, 
    start_address: str, 
    end_address: str,
    work_type: str = None
):
    """
    MASTER AUTO-POPULATION ENDPOINT
    Returns ALL possible auto-populated data to minimize user input
    Combines: road, traffic, site, side streets, risks, devices, contacts, etc.
    """
    try:
        from comprehensive_auto_population import get_comprehensive_auto_population
        
        result = await get_comprehensive_auto_population(
            lat, lng, start_address, end_address, work_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in comprehensive auto-population: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================
# GOOGLE PLACES API PROXY ENDPOINTS (CORS FIX)
# ===================================================

@api_router.get("/proxy/geocode")
async def proxy_geocode(address: str):
    """
    Proxy endpoint for Google Geocoding API to fix CORS issues
    """
    try:
        google_api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        if not google_api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
    except Exception as e:
        logger.error(f"Error in geocode proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/proxy/places/nearby")
async def proxy_places_nearby(lat: float, lng: float, radius: int = 10000, place_type: str = "police"):
    """
    Proxy endpoint for Google Places Nearby Search API to fix CORS issues
    """
    try:
        google_api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        if not google_api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type={place_type}&key={google_api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
    except Exception as e:
        logger.error(f"Error in places nearby proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/proxy/places/details")
async def proxy_places_details(place_id: str, fields: str = "name,formatted_phone_number,vicinity"):
    """
    Proxy endpoint for Google Places Details API to fix CORS issues
    """
    try:
        google_api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        if not google_api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={google_api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
    except Exception as e:
        logger.error(f"Error in places details proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================
# OPENWEATHERMAP API PROXY ENDPOINT (CORS FIX)
# ===================================================

@api_router.get("/proxy/weather/forecast")
async def proxy_weather_forecast(lat: float, lon: float):
    """
    Proxy endpoint for OpenWeatherMap Forecast API to fix CORS issues
    Note: Using the free API key from the frontend code
    """
    try:
        # Using the OpenWeatherMap API key found in frontend code
        weather_api_key = "4d8fb5b93d4af21d66a2948710284366"
        
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
    except Exception as e:
        logger.error(f"Error in weather forecast proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================
# FILE DOWNLOAD ENDPOINTS FOR TMP OUTPUTS
# ===================================================

@api_router.get("/downloads/list")
async def list_available_downloads():
    """List all available TMP output files for download"""
    try:
        output_dir = Path("/app/tmp_outputs")
        if not output_dir.exists():
            return {"files": [], "message": "No files available"}
        
        files = []
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": "pdf" if file_path.suffix == ".pdf" else "text",
                    "download_url": f"/api/downloads/file/{file_path.name}"
                })
        
        return {
            "files": files,
            "total": len(files),
            "message": "TMP output files ready for download"
        }
    except Exception as e:
        logger.error(f"Error listing downloads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/downloads/file/{filename}")
async def download_file(filename: str):
    """Download a specific TMP output file"""
    try:
        file_path = Path(f"/app/tmp_outputs/{filename}")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type
        if filename.endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.endswith('.txt'):
            media_type = "text/plain"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()