from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
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
    footpath: bool = False
    left_shoulder: bool = False
    left_lane: bool = False
    center_lane: bool = False
    right_lane: bool = False
    right_shoulder: bool = False
    median_strip: bool = False
    complete_road_closure: bool = False

class ControlMeasures(BaseModel):
    twenty_min_rule: bool = False
    signage: bool = False
    speed_reduction: bool = False
    detour: bool = False

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

@api_router.get("/road-data")
async def get_road_data(start_address: str, end_address: str):
    """Derive road data from start and end addresses"""
    # This is a simplified implementation
    # In a real app, you'd integrate with actual road data APIs
    start_coords = await geocode_address(start_address)
    end_coords = await geocode_address(end_address)
    
    # Calculate workzone size (rough distance calculation)
    import math
    lat1, lng1 = math.radians(start_coords["lat"]), math.radians(start_coords["lng"])
    lat2, lng2 = math.radians(end_coords["lat"]), math.radians(end_coords["lng"])
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    distance = 2 * math.asin(math.sqrt(a)) * 6371000  # Earth radius in meters
    
    return {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "workzone_size": round(distance, 2),
        "traffic_volume": 15000,  # Mock data
        "road_classification": "Major Urban Road",
        "road_type": "Arterial",
        "governing_body": "Local Council"
    }

# PDF generation
@api_router.get("/plans/{plan_id}/pdf")
async def generate_plan_pdf(plan_id: str, current_user: Dict = Depends(get_current_user)):
    plan = await db.plans.find_one({"id": plan_id, "user_id": current_user["user_id"]})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph("Traffic Management Plan", title_style))
    story.append(Spacer(1, 20))
    
    # Plan details
    story.append(Paragraph(f"<b>Plan Name:</b> {plan['plan_name']}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Company details
    story.append(Paragraph("<b>Primary Company Details:</b>", styles['Heading2']))
    company = plan['company_details']
    story.append(Paragraph(f"Company: {company['name']}", styles['Normal']))
    story.append(Paragraph(f"Address: {company['address']}", styles['Normal']))
    story.append(Paragraph(f"ABN: {company['abn']}", styles['Normal']))
    story.append(Paragraph(f"Phone: {company['phone']}", styles['Normal']))
    story.append(Paragraph(f"Liaison: {company['liaison_name']} ({company['liaison_email']})", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Work details
    story.append(Paragraph("<b>Work Details:</b>", styles['Heading2']))
    work = plan['work_details']
    story.append(Paragraph(f"Type: {work['work_type'].title()}", styles['Normal']))
    story.append(Paragraph(f"Style: {work['work_style'].title()}", styles['Normal']))
    story.append(Paragraph(f"Description: {work['description']}", styles['Normal']))
    story.append(Paragraph(f"Duration: {work['start_date']} to {work['end_date']}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Road occupancy
    story.append(Paragraph("<b>Road Occupancy:</b>", styles['Heading2']))
    occupancy = plan['road_occupancy']
    occupied_areas = [key.replace('_', ' ').title() for key, value in occupancy.items() if value]
    story.append(Paragraph(f"Occupied Areas: {', '.join(occupied_areas)}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Control measures
    story.append(Paragraph("<b>Control Measures:</b>", styles['Heading2']))
    measures = plan['control_measures']
    active_measures = [key.replace('_', ' ').title() for key, value in measures.items() if value]
    story.append(Paragraph(f"Active Measures: {', '.join(active_measures)}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Traffic devices
    if plan.get('devices'):
        story.append(Paragraph("<b>Traffic Control Devices:</b>", styles['Heading2']))
        device_data = []
        device_data.append(['Device Type', 'Device Name', 'Latitude', 'Longitude'])
        for device in plan['devices']:
            device_data.append([
                device['device_type'],
                device['device_name'],
                f"{device['position_lat']:.6f}",
                f"{device['position_lng']:.6f}"
            ])
        
        device_table = Table(device_data)
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(device_table)
    
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(buffer.getvalue()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=traffic_plan_{plan_id}.pdf"}
    )

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