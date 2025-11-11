"""
Generate actual traffic sign images for TGS overlays
Creates realistic Australian traffic signs based on AS 1742.3 standards
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def create_sign_image(sign_code: str, sign_name: str, size: int = 120) -> Image.Image:
    """
    Create a realistic traffic sign image based on Australian standards
    
    Args:
        sign_code: Sign code (e.g., T1-1, G9-4, R5-3)
        sign_name: Sign name/description
        size: Sign size in pixels
        
    Returns:
        PIL Image of the traffic sign
    """
    
    # Determine sign type and styling from code
    if sign_code.startswith('T1'):
        return create_warning_sign(sign_code, sign_name, size)
    elif sign_code.startswith('G'):
        return create_guidance_sign(sign_code, sign_name, size)
    elif sign_code.startswith('R'):
        return create_regulatory_sign(sign_code, sign_name, size)
    elif 'BARRIER' in sign_code.upper():
        return create_barrier_symbol(size)
    elif 'CONE' in sign_code.upper():
        return create_cone_symbol(size)
    else:
        return create_generic_sign(sign_code, sign_name, size)


def create_warning_sign(sign_code: str, sign_name: str, size: int) -> Image.Image:
    """Create Australian warning sign (yellow diamond/rectangle)"""
    
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Australian warning signs are typically yellow rectangles with black border
    margin = 5
    
    # Draw white background rectangle
    draw.rectangle(
        [(margin, margin), (size - margin, size - margin)],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=3
    )
    
    # Draw yellow diamond inside
    points = [
        (size // 2, margin + 10),  # Top
        (size - margin - 10, size // 2),  # Right
        (size // 2, size - margin - 10),  # Bottom
        (margin + 10, size // 2)  # Left
    ]
    draw.polygon(points, fill=(255, 200, 0, 255), outline=(0, 0, 0, 255), width=3)
    
    # Add symbol based on sign type
    if 'Road Work' in sign_name or 'T1-1' in sign_code:
        # Worker symbol
        draw_worker_symbol(draw, size)
    elif 'Closed' in sign_name or 'T1-7' in sign_code:
        # X symbol for closure
        draw_x_symbol(draw, size, color=(0, 0, 0, 255))
    
    # Add text label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    # Draw sign code at bottom
    draw.text(
        (size // 2, size - 15),
        sign_code,
        fill=(0, 0, 0, 255),
        font=font,
        anchor="mm"
    )
    
    return img


def create_guidance_sign(sign_code: str, sign_name: str, size: int) -> Image.Image:
    """Create Australian guidance/direction sign (blue/white)"""
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = 5
    
    # Blue background for guidance signs
    draw.rectangle(
        [(margin, margin), (size - margin, size - margin)],
        fill=(0, 102, 204, 255),
        outline=(255, 255, 255, 255),
        width=3
    )
    
    # Add arrow based on sign type
    if 'Detour' in sign_name or 'G9' in sign_code:
        # Draw arrow
        if 'Left' in sign_name:
            draw_arrow(draw, size, direction='left', color=(255, 255, 255, 255))
        elif 'Right' in sign_name:
            draw_arrow(draw, size, direction='right', color=(255, 255, 255, 255))
        else:
            draw_arrow(draw, size, direction='straight', color=(255, 255, 255, 255))
        
        # Add "DETOUR" text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text(
            (size // 2, size - 25),
            "DETOUR",
            fill=(255, 255, 255, 255),
            font=font,
            anchor="mm"
        )
    
    # Add sign code
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    draw.text(
        (size // 2, size - 10),
        sign_code,
        fill=(255, 255, 255, 255),
        font=font,
        anchor="mm"
    )
    
    return img


def create_regulatory_sign(sign_code: str, sign_name: str, size: int) -> Image.Image:
    """Create Australian regulatory sign (red circle/white)"""
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = 10
    
    # White background with red circle
    draw.ellipse(
        [(margin, margin), (size - margin, size - margin)],
        fill=(255, 255, 255, 255),
        outline=(255, 0, 0, 255),
        width=6
    )
    
    # Add appropriate symbol
    if 'Stop' in sign_name or 'R1-1' in sign_code:
        # STOP sign is octagonal and red
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text(
            (size // 2, size // 2),
            "STOP",
            fill=(255, 0, 0, 255),
            font=font,
            anchor="mm"
        )
    elif 'Speed' in sign_name or 'R4' in sign_code:
        # Speed limit sign
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Extract speed if possible
        import re
        speed_match = re.search(r'\d+', sign_name)
        speed = speed_match.group() if speed_match else "40"
        
        draw.text(
            (size // 2, size // 2),
            speed,
            fill=(0, 0, 0, 255),
            font=font,
            anchor="mm"
        )
    
    return img


def create_barrier_symbol(size: int) -> Image.Image:
    """Create barrier/barricade symbol"""
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Orange and white striped barrier
    stripe_height = size // 6
    for i in range(6):
        color = (255, 140, 0, 255) if i % 2 == 0 else (255, 255, 255, 255)
        draw.rectangle(
            [(10, 10 + i * stripe_height), (size - 10, 10 + (i + 1) * stripe_height)],
            fill=color,
            outline=(0, 0, 0, 255)
        )
    
    # Add border
    draw.rectangle(
        [(5, 5), (size - 5, size - 5)],
        outline=(0, 0, 0, 255),
        width=3
    )
    
    return img


def create_cone_symbol(size: int) -> Image.Image:
    """Create traffic cone symbol"""
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Orange cone shape
    points = [
        (size // 2, 10),  # Top
        (size - 20, size - 20),  # Bottom right
        (20, size - 20)  # Bottom left
    ]
    draw.polygon(points, fill=(255, 140, 0, 255), outline=(0, 0, 0, 255), width=2)
    
    # White stripes
    for y in [30, 50, 70]:
        draw.line(
            [(30, y), (size - 30, y + 10)],
            fill=(255, 255, 255, 255),
            width=8
        )
    
    # Base
    draw.rectangle(
        [(15, size - 20), (size - 15, size - 5)],
        fill=(50, 50, 50, 255),
        outline=(0, 0, 0, 255)
    )
    
    return img


def create_generic_sign(sign_code: str, sign_name: str, size: int) -> Image.Image:
    """Create generic sign for unknown types"""
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Orange rectangle
    draw.rectangle(
        [(5, 5), (size - 5, size - 5)],
        fill=(255, 150, 50, 255),
        outline=(0, 0, 0, 255),
        width=3
    )
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    draw.text(
        (size // 2, size // 2),
        sign_code,
        fill=(0, 0, 0, 255),
        font=font,
        anchor="mm"
    )
    
    return img


def draw_worker_symbol(draw, size: int):
    """Draw worker/person symbol"""
    center_x, center_y = size // 2, size // 2
    
    # Head
    draw.ellipse(
        [(center_x - 8, center_y - 15), (center_x + 8, center_y + 1)],
        fill=(0, 0, 0, 255)
    )
    
    # Body
    draw.rectangle(
        [(center_x - 10, center_y), (center_x + 10, center_y + 20)],
        fill=(0, 0, 0, 255)
    )
    
    # Arms (holding shovel)
    draw.line(
        [(center_x - 10, center_y + 5), (center_x - 18, center_y + 12)],
        fill=(0, 0, 0, 255),
        width=3
    )
    draw.line(
        [(center_x + 10, center_y + 5), (center_x + 18, center_y + 12)],
        fill=(0, 0, 0, 255),
        width=3
    )


def draw_x_symbol(draw, size: int, color: tuple):
    """Draw X symbol for closure"""
    margin = size // 3
    draw.line(
        [(margin, margin), (size - margin, size - margin)],
        fill=color,
        width=8
    )
    draw.line(
        [(size - margin, margin), (margin, size - margin)],
        fill=color,
        width=8
    )


def draw_arrow(draw, size: int, direction: str, color: tuple):
    """Draw directional arrow"""
    center_x, center_y = size // 2, size // 2
    
    if direction == 'left':
        # Left arrow
        points = [
            (center_x - 20, center_y),  # Left point
            (center_x, center_y - 15),  # Top
            (center_x, center_y - 5),  # Top inner
            (center_x + 20, center_y - 5),  # Right top
            (center_x + 20, center_y + 5),  # Right bottom
            (center_x, center_y + 5),  # Bottom inner
            (center_x, center_y + 15)  # Bottom
        ]
    elif direction == 'right':
        # Right arrow
        points = [
            (center_x + 20, center_y),  # Right point
            (center_x, center_y - 15),  # Top
            (center_x, center_y - 5),  # Top inner
            (center_x - 20, center_y - 5),  # Left top
            (center_x - 20, center_y + 5),  # Left bottom
            (center_x, center_y + 5),  # Bottom inner
            (center_x, center_y + 15)  # Bottom
        ]
    else:  # straight
        # Up arrow
        points = [
            (center_x, center_y - 20),  # Top point
            (center_x - 15, center_y),  # Left
            (center_x - 5, center_y),  # Left inner
            (center_x - 5, center_y + 20),  # Left bottom
            (center_x + 5, center_y + 20),  # Right bottom
            (center_x + 5, center_y),  # Right inner
            (center_x + 15, center_y)  # Right
        ]
    
    draw.polygon(points, fill=color, outline=(0, 0, 0, 255), width=2)
