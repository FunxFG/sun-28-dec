"""
Visual TGS Generator with Sign Overlays on Satellite Imagery and Street View Integration
Generates professional Traffic Guidance Schemes with actual sign images overlaid on Google Maps
"""

import os
import io
import base64
import httpx
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging
import math
from datetime import datetime

logger = logging.getLogger(__name__)

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', '')
GOOGLE_STATIC_MAPS_BASE = "https://maps.googleapis.com/maps/api/staticmap"
GOOGLE_STREETVIEW_BASE = "https://maps.googleapis.com/maps/api/streetview"


class VisualTGSGenerator:
    """Generate visual TGS with sign overlays on satellite imagery"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GOOGLE_MAPS_API_KEY
        self.sign_library_path = Path(__file__).parent / 'sa_sign_library.json'
        
    async def generate_satellite_with_signs(
        self,
        center_lat: float,
        center_lng: float,
        placed_devices: List[Dict],
        zoom: int = 18,
        width: int = 1280,
        height: int = 720
    ) -> Dict[str, Any]:
        """
        Generate satellite imagery with sign overlays
        
        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            placed_devices: List of placed devices with positions
            zoom: Map zoom level (18 = street level)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Dict with image data, sign positions, and metadata
        """
        try:
            # Step 1: Fetch satellite imagery from Google Maps
            satellite_image = await self._fetch_satellite_image(
                center_lat, center_lng, zoom, width, height
            )
            
            if not satellite_image:
                logger.error("Failed to fetch satellite image")
                return {"error": "Failed to fetch satellite imagery"}
            
            # Step 2: Calculate pixel positions for each sign
            sign_positions = self._calculate_sign_positions(
                placed_devices, center_lat, center_lng, zoom, width, height
            )
            
            # Step 3: Overlay sign images on satellite map
            composite_image = await self._overlay_signs_on_map(
                satellite_image, sign_positions, placed_devices
            )
            
            # Step 4: Add measurements, labels, and legend
            final_image = self._add_annotations(
                composite_image, placed_devices, sign_positions
            )
            
            # Step 5: Convert to base64 for frontend
            image_base64 = self._image_to_base64(final_image)
            
            return {
                "success": True,
                "image_base64": image_base64,
                "image_format": "png",
                "dimensions": {"width": width, "height": height},
                "center": {"lat": center_lat, "lng": center_lng},
                "zoom": zoom,
                "sign_positions": sign_positions,
                "total_signs": len(placed_devices)
            }
            
        except Exception as e:
            logger.error(f"Error generating satellite TGS: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_satellite_image(
        self, lat: float, lng: float, zoom: int, width: int, height: int
    ) -> Optional[Image.Image]:
        """Fetch satellite imagery from Google Maps Static API"""
        try:
            params = {
                'center': f"{lat},{lng}",
                'zoom': zoom,
                'size': f"{width}x{height}",
                'maptype': 'satellite',
                'key': self.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(GOOGLE_STATIC_MAPS_BASE, params=params)
                response.raise_for_status()
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(response.content))
                return image
                
        except Exception as e:
            logger.error(f"Error fetching satellite image: {str(e)}")
            return None
    
    def _calculate_sign_positions(
        self,
        devices: List[Dict],
        center_lat: float,
        center_lng: float,
        zoom: int,
        width: int,
        height: int
    ) -> List[Dict]:
        """
        Calculate pixel positions for each sign on the map
        Converts GPS coordinates to pixel coordinates
        """
        positions = []
        
        for device in devices:
            # Get device GPS coordinates (from placement rules)
            device_lat = device.get('latitude', center_lat)
            device_lng = device.get('longitude', center_lng)
            
            # Convert GPS to pixel coordinates using Mercator projection
            pixel_x, pixel_y = self._gps_to_pixel(
                device_lat, device_lng, center_lat, center_lng, zoom, width, height
            )
            
            positions.append({
                'device_code': device.get('code', 'UNKNOWN'),
                'device_name': device.get('name', 'Sign'),
                'latitude': device_lat,
                'longitude': device_lng,
                'pixel_x': pixel_x,
                'pixel_y': pixel_y,
                'distance_from_start': device.get('distance', 0),
                'side': device.get('side', 'left')
            })
        
        return positions
    
    def _gps_to_pixel(
        self,
        point_lat: float,
        point_lng: float,
        center_lat: float,
        center_lng: float,
        zoom: int,
        width: int,
        height: int
    ) -> Tuple[int, int]:
        """
        Convert GPS coordinates to pixel coordinates using Web Mercator projection
        """
        # Calculate the scale at this zoom level
        scale = 2 ** zoom
        
        # Convert center to world coordinates
        center_x = (center_lng + 180.0) / 360.0 * 256 * scale
        center_y = ((1.0 - math.log(math.tan(math.radians(center_lat)) + 
                    (1.0 / math.cos(math.radians(center_lat)))) / math.pi) / 2.0) * 256 * scale
        
        # Convert point to world coordinates
        point_x = (point_lng + 180.0) / 360.0 * 256 * scale
        point_y = ((1.0 - math.log(math.tan(math.radians(point_lat)) + 
                   (1.0 / math.cos(math.radians(point_lat)))) / math.pi) / 2.0) * 256 * scale
        
        # Calculate pixel offset from center
        pixel_x = int((point_x - center_x) + width / 2)
        pixel_y = int((point_y - center_y) + height / 2)
        
        return pixel_x, pixel_y
    
    async def _overlay_signs_on_map(
        self,
        base_image: Image.Image,
        sign_positions: List[Dict],
        devices: List[Dict]
    ) -> Image.Image:
        """
        Overlay sign images on the satellite map
        """
        # Create a copy to work with
        composite = base_image.copy()
        draw = ImageDraw.Draw(composite, 'RGBA')
        
        for i, position in enumerate(sign_positions):
            device = devices[i] if i < len(devices) else {}
            
            # Get sign image (for now, use colored markers)
            sign_marker = self._create_sign_marker(device, 60, 60)
            
            # Calculate position (offset to center the marker)
            x = position['pixel_x'] - 30  # Half of marker width
            y = position['pixel_y'] - 60  # Full height to position at point
            
            # Ensure marker is within bounds
            if 0 <= x < composite.width - 60 and 0 <= y < composite.height - 60:
                # Paste sign marker
                composite.paste(sign_marker, (x, y), sign_marker)
                
                # Draw connection line to road
                draw.line(
                    [(position['pixel_x'], position['pixel_y']),
                     (position['pixel_x'], position['pixel_y'] + 20)],
                    fill=(255, 255, 0, 200),
                    width=2
                )
        
        return composite
    
    def _create_sign_marker(self, device: Dict, width: int, height: int) -> Image.Image:
        """
        Create a visual marker for a traffic sign
        For now creates a colored icon, later can be replaced with actual sign images
        """
        # Create transparent image
        marker = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(marker)
        
        # Determine color based on sign type
        sign_code = device.get('code', '')
        if 'T1' in sign_code or 'warning' in device.get('name', '').lower():
            color = (255, 200, 0, 220)  # Yellow for warning
        elif 'R' in sign_code or 'regulatory' in device.get('name', '').lower():
            color = (255, 50, 50, 220)  # Red for regulatory
        elif 'G' in sign_code or 'guide' in device.get('name', '').lower():
            color = (50, 150, 255, 220)  # Blue for guidance
        else:
            color = (255, 150, 50, 220)  # Orange for other
        
        # Draw sign shape (diamond for warning, circle for regulatory, rectangle for guide)
        if 'T1' in sign_code or 'warning' in device.get('name', '').lower():
            # Draw diamond shape
            points = [(width//2, 5), (width-5, height//2), (width//2, height-5), (5, height//2)]
            draw.polygon(points, fill=color, outline=(0, 0, 0, 255))
        elif 'R' in sign_code or 'stop' in device.get('name', '').lower():
            # Draw circle
            draw.ellipse([5, 5, width-5, height-5], fill=color, outline=(0, 0, 0, 255))
        else:
            # Draw rectangle
            draw.rectangle([5, 5, width-5, height-5], fill=color, outline=(0, 0, 0, 255))
        
        # Add code label
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
        except:
            font = ImageFont.load_default()
        
        code_text = device.get('code', '?')[:4]
        bbox = draw.textbbox((0, 0), code_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw.text((text_x, text_y), code_text, fill=(255, 255, 255, 255), font=font)
        
        return marker
    
    def _add_annotations(
        self,
        image: Image.Image,
        devices: List[Dict],
        positions: List[Dict]
    ) -> Image.Image:
        """
        Add measurements, labels, and legend to the TGS
        """
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated, 'RGBA')
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
        
        # Add title bar
        draw.rectangle([0, 0, image.width, 60], fill=(0, 0, 0, 200))
        draw.text((20, 15), "Traffic Guidance Scheme - Satellite View", 
                  fill=(255, 255, 255, 255), font=title_font)
        
        # Add sign count
        draw.text((20, 40), f"Total Signs: {len(devices)}", 
                  fill=(200, 200, 200, 255), font=label_font)
        
        # Add legend in bottom right
        legend_height = 150
        legend_width = 250
        legend_x = image.width - legend_width - 20
        legend_y = image.height - legend_height - 20
        
        # Legend background
        draw.rectangle(
            [legend_x, legend_y, legend_x + legend_width, legend_y + legend_height],
            fill=(255, 255, 255, 230),
            outline=(0, 0, 0, 255)
        )
        
        # Legend title
        draw.text((legend_x + 10, legend_y + 10), "Sign Legend:", 
                  fill=(0, 0, 0, 255), font=title_font)
        
        # Legend items
        legend_items = [
            ("◆ Warning Signs", (255, 200, 0, 255)),
            ("● Regulatory Signs", (255, 50, 50, 255)),
            ("▬ Guide Signs", (50, 150, 255, 255))
        ]
        
        y_offset = legend_y + 45
        for text, color in legend_items:
            draw.text((legend_x + 10, y_offset), text, fill=color, font=label_font)
            y_offset += 25
        
        # Add scale indicator
        scale_text = "Scale: Approx 1:500 @ Zoom 18"
        draw.text((legend_x + 10, y_offset + 10), scale_text, 
                  fill=(100, 100, 100, 255), font=label_font)
        
        return annotated
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    async def generate_streetview_with_signs(
        self,
        sign_positions: List[Dict],
        heading: int = 0,
        pitch: int = 0,
        fov: int = 90,
        width: int = 800,
        height: int = 600
    ) -> Dict[str, Any]:
        """
        Generate Street View images showing sign positions from driver's perspective
        
        Args:
            sign_positions: List of sign positions with GPS coordinates
            heading: Camera heading (0-360, 0=North)
            pitch: Camera pitch (-90 to 90, 0=horizontal)
            fov: Field of view (1-120 degrees)
            width: Image width
            height: Image height
            
        Returns:
            Dict with Street View image data and sign visibility info
        """
        streetview_images = []
        
        try:
            for position in sign_positions[:5]:  # Limit to 5 positions for performance
                lat = position['latitude']
                lng = position['longitude']
                
                # Calculate heading to face the sign
                # For now, use provided heading or default
                sign_heading = position.get('heading', heading)
                
                # Fetch Street View image
                params = {
                    'location': f"{lat},{lng}",
                    'size': f"{width}x{height}",
                    'heading': sign_heading,
                    'pitch': pitch,
                    'fov': fov,
                    'key': self.api_key
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(GOOGLE_STREETVIEW_BASE, params=params)
                    
                    if response.status_code == 200:
                        # Convert to base64
                        image_base64 = base64.b64encode(response.content).decode('utf-8')
                        
                        streetview_images.append({
                            'sign_code': position['device_code'],
                            'sign_name': position['device_name'],
                            'location': {'lat': lat, 'lng': lng},
                            'heading': sign_heading,
                            'image_base64': image_base64,
                            'distance': position.get('distance_from_start', 0)
                        })
            
            return {
                "success": True,
                "streetview_images": streetview_images,
                "total_views": len(streetview_images)
            }
            
        except Exception as e:
            logger.error(f"Error generating Street View: {str(e)}")
            return {"error": str(e)}


# Initialize generator
tgs_generator = VisualTGSGenerator()


async def generate_complete_visual_tgs(
    center_lat: float,
    center_lng: float,
    placed_devices: List[Dict],
    include_streetview: bool = True,
    plan_name: str = "tgs"
) -> Dict[str, Any]:
    """
    Generate complete visual TGS with both satellite overlay and Street View
    
    Args:
        center_lat: Work zone center latitude
        center_lng: Work zone center longitude
        placed_devices: List of placed traffic control devices
        include_streetview: Whether to include Street View images
        plan_name: Name of the plan (for file naming)
        
    Returns:
        Complete TGS package with satellite map and Street View images
    """
    from datetime import datetime
    
    result = {
        "satellite_tgs": {},
        "streetview_images": [],
        "metadata": {},
        "saved_files": []
    }
    
    try:
        # Generate satellite view with sign overlays
        satellite_result = await tgs_generator.generate_satellite_with_signs(
            center_lat, center_lng, placed_devices
        )
        result["satellite_tgs"] = satellite_result
        
        # Save satellite TGS image to disk
        output_dir = Path("/app/tmp_outputs")
        output_dir.mkdir(exist_ok=True)
        
        clean_plan_name = plan_name.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if satellite_result.get('image_base64'):
            # Save PNG
            png_filename = f"{clean_plan_name}_{timestamp}_TGS_Drawing.png"
            png_path = output_dir / png_filename
            
            # Decode base64 and save
            image_data = base64.b64decode(satellite_result['image_base64'])
            with open(png_path, 'wb') as f:
                f.write(image_data)
            
            result["saved_files"].append({
                "type": "satellite_png",
                "filename": png_filename,
                "path": str(png_path),
                "size": len(image_data)
            })
            logger.info(f"Visual TGS PNG saved to: {png_path}")
            
            # Also save as PDF
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            pdf_filename = f"{clean_plan_name}_{timestamp}_TGS_Drawing.pdf"
            pdf_path = output_dir / pdf_filename
            
            # Create PDF with image
            c = canvas.Canvas(str(pdf_path), pagesize=landscape(A4))
            img = ImageReader(io.BytesIO(image_data))
            
            # Scale image to fit A4 landscape
            page_width, page_height = landscape(A4)
            c.drawImage(img, 50, 50, width=page_width-100, height=page_height-100, preserveAspectRatio=True)
            
            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, page_height - 30, f"Traffic Guidance Scheme - {plan_name}")
            c.setFont("Helvetica", 10)
            c.drawString(50, page_height - 45, f"Generated: {datetime.now().strftime('%d %B %Y at %I:%M %p')}")
            
            c.save()
            
            result["saved_files"].append({
                "type": "satellite_pdf",
                "filename": pdf_filename,
                "path": str(pdf_path),
                "size": pdf_path.stat().st_size
            })
            logger.info(f"Visual TGS PDF saved to: {pdf_path}")
        
        # Generate Street View images if requested
        if include_streetview and satellite_result.get('sign_positions'):
            streetview_result = await tgs_generator.generate_streetview_with_signs(
                satellite_result['sign_positions']
            )
            result["streetview_images"] = streetview_result.get('streetview_images', [])
            
            # Save individual Street View images
            for idx, sv_img in enumerate(result["streetview_images"]):
                sv_filename = f"{clean_plan_name}_{timestamp}_StreetView_{idx+1}_{sv_img['sign_code']}.png"
                sv_path = output_dir / sv_filename
                
                # Decode and save
                sv_data = base64.b64decode(sv_img['image_base64'])
                with open(sv_path, 'wb') as f:
                    f.write(sv_data)
                
                result["saved_files"].append({
                    "type": "streetview",
                    "filename": sv_filename,
                    "path": str(sv_path),
                    "sign_code": sv_img['sign_code'],
                    "size": len(sv_data)
                })
                logger.info(f"Street View image saved to: {sv_path}")
        
        # Add metadata
        result["metadata"] = {
            "total_signs": len(placed_devices),
            "center": {"lat": center_lat, "lng": center_lng},
            "has_streetview": include_streetview and len(result["streetview_images"]) > 0,
            "generation_timestamp": datetime.now().isoformat(),
            "files_saved": len(result["saved_files"]),
            "output_directory": str(output_dir)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating complete visual TGS: {str(e)}")
        return {"error": str(e)}
