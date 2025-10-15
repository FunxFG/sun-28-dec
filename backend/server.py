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
from risk_registry import (
    get_risk_registry,
    calculate_risk_score,
    RISK_CATEGORIES,
    LIKELIHOOD_LEVELS,
    CONSEQUENCE_LEVELS
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
    """Derive comprehensive road data from start and end addresses for Austroads compliance"""
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
    
    # Enhanced road classification based on location analysis
    # This is a simplified implementation - in production, you'd use actual road data APIs
    road_classification = determine_road_classification(start_address, end_address)
    speed_limit = determine_speed_limit(road_classification, start_address)
    traffic_volume = estimate_traffic_volume(road_classification, start_address)
    governing_body = determine_governing_body(start_address)
    
    return {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "workzone_size": round(distance, 2),
        "traffic_volume": traffic_volume,
        "road_classification": road_classification,
        "road_type": determine_road_type(road_classification),
        "governing_body": governing_body,
        "speed_limit": speed_limit,
        "environment": determine_environment(start_address),
        "austroads_category": determine_austroads_category(road_classification, traffic_volume)
    }

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