"""
Improved Visual TGS Generator
Creates clear, professional TGS diagrams using Google Maps satellite imagery
with easy-to-understand traffic device overlays
"""

import os
import io
import base64
import httpx
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any
import math
import logging
from sign_image_generator import create_sign_image

logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')
GOOGLE_STATIC_MAPS_BASE = "https://maps.googleapis.com/maps/api/staticmap"


async def generate_improved_visual_tgs(
    center_lat: float,
    center_lng: float,
    devices: List[Dict],
    plan_name: str = "TGS"
) -> Dict[str, Any]:
    """
    Generate improved visual TGS with clear satellite imagery and device overlays
    
    Args:
        center_lat: Center latitude of work zone
        center_lng: Center longitude of work zone
        devices: List of traffic control devices
        plan_name: Name of the plan
        
    Returns:
        Dictionary with image data and file paths
    """
    
    try:
        logger.info(f"Generating improved visual TGS for {plan_name}")
        logger.info(f"Center: {center_lat}, {center_lng}")
        logger.info(f"Devices: {len(devices)}")
        
        # Step 1: Fetch high-quality satellite imagery
        logger.info("Step 1: Fetching satellite imagery...")
        satellite_image = await fetch_satellite_image(
            center_lat, center_lng,
            zoom=19,  # Higher zoom for better detail
            width=1600,  # Higher resolution
            height=1200
        )
        
        if not satellite_image:
            logger.error("Failed to fetch satellite image")
            return {"error": "Failed to fetch satellite imagery"}
        
        logger.info(f"Satellite image fetched: {satellite_image.size}")
        
        # Step 2: Create overlay with devices
        logger.info("Step 2: Creating device overlays...")
        tgs_image = create_device_overlays(
            satellite_image,
            devices,
            center_lat,
            center_lng,
            zoom=19,
            width=1600,
            height=1200
        )
        
        # Step 3: Add professional annotations
        logger.info("Step 3: Adding annotations...")
        final_image = add_professional_annotations(
            tgs_image,
            plan_name,
            devices,
            center_lat,
            center_lng
        )
        
        # Step 4: Save to files
        logger.info("Step 4: Saving files...")
        from pathlib import Path
        from datetime import datetime
        
        output_dir = Path("/app/tmp_outputs")
        output_dir.mkdir(exist_ok=True)
        
        clean_name = plan_name.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save PNG
        png_path = output_dir / f"{clean_name}_{timestamp}_TGS_Satellite.png"
        final_image.save(png_path, 'PNG', quality=95)
        logger.info(f"Saved PNG: {png_path}")
        
        # Save PDF
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        
        pdf_path = output_dir / f"{clean_name}_{timestamp}_TGS_Satellite.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=landscape(A4))
        
        # Add image to PDF
        img_reader = ImageReader(final_image)
        page_width, page_height = landscape(A4)
        
        # Scale image to fit page
        img_width, img_height = final_image.size
        scale = min((page_width - 100) / img_width, (page_height - 100) / img_height)
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        
        x = (page_width - scaled_width) / 2
        y = (page_height - scaled_height) / 2
        
        c.drawImage(img_reader, x, y, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, page_height - 30, f"Traffic Guidance Scheme - {plan_name}")
        c.setFont("Helvetica", 10)
        c.drawString(50, page_height - 45, f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}")
        
        c.save()
        logger.info(f"Saved PDF: {pdf_path}")
        
        # Convert to base64
        buffered = io.BytesIO()
        final_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return {
            "success": True,
            "image_base64": img_base64,
            "png_path": str(png_path),
            "pdf_path": str(pdf_path),
            "png_filename": png_path.name,
            "pdf_filename": pdf_path.name,
            "dimensions": {"width": 1600, "height": 1200},
            "device_count": len(devices)
        }
        
    except Exception as e:
        logger.error(f"Error generating improved visual TGS: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


async def fetch_satellite_image(
    lat: float,
    lng: float,
    zoom: int = 19,
    width: int = 1600,
    height: int = 1200
) -> Image.Image:
    """Fetch high-quality satellite imagery from Google Maps"""
    
    try:
        params = {
            'center': f"{lat},{lng}",
            'zoom': zoom,
            'size': f"{width}x{height}",
            'maptype': 'satellite',
            'key': GOOGLE_MAPS_API_KEY,
            'scale': 2  # High DPI
        }
        
        logger.info(f"Fetching satellite image: {GOOGLE_STATIC_MAPS_BASE}")
        logger.info(f"Params: {params}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(GOOGLE_STATIC_MAPS_BASE, params=params)
            
            if response.status_code != 200:
                logger.error(f"Google Maps API error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content))
            logger.info(f"Image fetched successfully: {image.size}")
            return image
            
    except Exception as e:
        logger.error(f"Error fetching satellite image: {str(e)}")
        return None


def create_device_overlays(
    base_image: Image.Image,
    devices: List[Dict],
    center_lat: float,
    center_lng: float,
    zoom: int,
    width: int,
    height: int
) -> Image.Image:
    """Create clear device overlays on satellite image"""
    
    # Create a copy
    composite = base_image.copy()
    
    # Create overlay layer
    overlay = Image.new('RGBA', composite.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    for i, device in enumerate(devices):
        # Get device position
        device_lat = device.get('position_lat', center_lat)
        device_lng = device.get('position_lng', center_lng)
        
        # Convert GPS to pixel
        pixel_x, pixel_y = gps_to_pixel(
            device_lat, device_lng,
            center_lat, center_lng,
            zoom, width, height
        )
        
        # Skip if out of bounds
        if not (0 <= pixel_x < width and 0 <= pixel_y < height):
            continue
        
        # Get device info
        device_code = device.get('device_code', '')
        device_name = device.get('device_name', 'Sign')
        
        # Generate actual sign image (80x80 pixels)
        sign_image = create_sign_image(device_code, device_name, size=80)
        
        # Calculate position to center the sign image
        sign_x = pixel_x - 40  # Half of sign width
        sign_y = pixel_y - 80  # Full height above the point
        
        # Ensure sign is within bounds
        if sign_x < 0 or sign_y < 0 or sign_x + 80 > width or sign_y + 80 > height:
            # If out of bounds, draw at edge
            sign_x = max(0, min(sign_x, width - 80))
            sign_y = max(0, min(sign_y, height - 80))
        
        # Draw shadow for visibility
        shadow = Image.new('RGBA', (84, 84), (0, 0, 0, 100))
        overlay.paste(shadow, (sign_x + 2, sign_y + 2), shadow)
        
        # Paste actual sign image
        overlay.paste(sign_image, (sign_x, sign_y), sign_image)
        
        # Draw white circle with number below the sign
        marker_size = 30
        number_y = pixel_y + 15
        
        draw.ellipse(
            [(pixel_x - marker_size//2, number_y - marker_size//2),
             (pixel_x + marker_size//2, number_y + marker_size//2)],
            fill=(255, 255, 255, 255),
            outline=(0, 0, 0, 255),
            width=3
        )
        
        # Draw number
        number_text = str(i + 1)
        draw.text(
            (pixel_x, number_y),
            number_text,
            fill=(0, 0, 0, 255),
            font=font,
            anchor="mm"
        )
        
        # Draw connecting line from sign to number
        draw.line(
            [(pixel_x, pixel_y), (pixel_x, number_y - marker_size//2)],
            fill=(255, 255, 255, 200),
            width=2
        )
        
        # Draw label box below marker
        label_text = f"{device_code}: {device_name}"
        
        # Get text bbox
        bbox = draw.textbbox((0, 0), label_text, font=small_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw label background
        label_y = pixel_y + marker_size//2 + 5
        draw.rectangle(
            [(pixel_x - text_width//2 - 5, label_y - 2),
             (pixel_x + text_width//2 + 5, label_y + text_height + 2)],
            fill=(255, 255, 255, 220),
            outline=(0, 0, 0, 255),
            width=2
        )
        
        # Draw label text
        draw.text(
            (pixel_x, label_y + text_height//2),
            label_text,
            fill=(0, 0, 0, 255),
            font=small_font,
            anchor="mm"
        )
    
    # Composite overlay onto base image
    composite.paste(overlay, (0, 0), overlay)
    
    return composite


def add_professional_annotations(
    image: Image.Image,
    plan_name: str,
    devices: List[Dict],
    center_lat: float,
    center_lng: float
) -> Image.Image:
    """Add professional title, legend, and annotations"""
    
    # Create new image with space for title and legend
    final_width = image.width
    final_height = image.height + 150  # Extra space for title and legend
    
    final_image = Image.new('RGB', (final_width, final_height), (255, 255, 255))
    
    # Paste main image
    final_image.paste(image, (0, 80))
    
    draw = ImageDraw.Draw(final_image)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        legend_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        legend_font = ImageFont.load_default()
    
    # Draw title bar
    draw.rectangle([(0, 0), (final_width, 80)], fill=(30, 70, 120))
    
    # Draw title
    draw.text(
        (20, 20),
        f"Traffic Guidance Scheme - {plan_name}",
        fill=(255, 255, 255),
        font=title_font
    )
    
    # Draw subtitle
    from datetime import datetime
    subtitle = f"Location: {center_lat:.6f}, {center_lng:.6f} | Devices: {len(devices)} | Generated: {datetime.now().strftime('%d %B %Y')}"
    draw.text(
        (20, 55),
        subtitle,
        fill=(200, 220, 255),
        font=subtitle_font
    )
    
    # Draw legend at bottom
    legend_y = image.height + 85
    draw.rectangle([(0, legend_y), (final_width, final_height)], fill=(240, 245, 250))
    
    legend_items = [
        ("⚠️", "Warning Signs (T1-1)", (255, 200, 0)),
        ("🚫", "Closure Signs (T1-7)", (255, 50, 50)),
        ("➡️", "Detour Signs (G9)", (50, 150, 255)),
        ("🚧", "Barriers", (255, 100, 0))
    ]
    
    x_offset = 20
    for emoji, text, color in legend_items:
        # Draw color circle
        draw.ellipse(
            [(x_offset, legend_y + 15), (x_offset + 30, legend_y + 45)],
            fill=color,
            outline=(100, 100, 100),
            width=2
        )
        
        # Draw legend text
        draw.text(
            (x_offset + 40, legend_y + 30),
            text,
            fill=(50, 50, 50),
            font=legend_font,
            anchor="lm"
        )
        
        x_offset += 300
    
    # Draw scale/note
    draw.text(
        (20, legend_y + 55),
        "Note: Numbers on map correspond to device sequence. Satellite imagery © Google Maps",
        fill=(100, 100, 100),
        font=legend_font
    )
    
    return final_image


def gps_to_pixel(
    point_lat: float,
    point_lng: float,
    center_lat: float,
    center_lng: float,
    zoom: int,
    width: int,
    height: int
) -> tuple:
    """Convert GPS coordinates to pixel coordinates"""
    
    scale = 2 ** zoom
    
    # Convert to world coordinates
    center_x = (center_lng + 180.0) / 360.0 * 256 * scale
    center_y = ((1.0 - math.log(math.tan(math.radians(center_lat)) + 
                (1.0 / math.cos(math.radians(center_lat)))) / math.pi) / 2.0) * 256 * scale
    
    point_x = (point_lng + 180.0) / 360.0 * 256 * scale
    point_y = ((1.0 - math.log(math.tan(math.radians(point_lat)) + 
               (1.0 / math.cos(math.radians(point_lat)))) / math.pi) / 2.0) * 256 * scale
    
    # Calculate pixel offset
    pixel_x = int((point_x - center_x) + width / 2)
    pixel_y = int((point_y - center_y) + height / 2)
    
    return pixel_x, pixel_y
