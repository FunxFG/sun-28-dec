"""
Visual TGS Drawing Generator
Creates actual traffic guidance scheme diagrams as images/PDFs
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrow, Wedge
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.lib import colors as pdf_colors
import io

class VisualTGSGenerator:
    """Generate professional visual TGS drawings"""
    
    def __init__(self):
        # A3 landscape dimensions
        self.page_width = 420  # mm
        self.page_height = 297  # mm
        
        # Colors (Austroads standard)
        self.color_yellow = '#FFD700'
        self.color_red = '#FF0000'
        self.color_blue = '#0066CC'
        self.color_green = '#00AA00'
        self.color_black = '#000000'
        self.color_white = '#FFFFFF'
        self.color_orange = '#FF8C00'
        
    def create_lane_closure_tgs(self, scenario_data, output_path):
        """Create TGS for lane closure with taper"""
        
        fig, ax = plt.subplots(figsize=(16.5, 11.7))  # A3 landscape in inches
        ax.set_xlim(0, 420)
        ax.set_ylim(0, 297)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title Block
        self._draw_title_block(ax, scenario_data)
        
        # Main schematic area
        schematic_y_start = 40
        schematic_height = 200
        
        # Draw road with lanes
        road_start_x = 50
        road_length = 320
        lane_width = 15
        
        # Left lane (closed)
        left_lane = Rectangle((road_start_x, schematic_y_start + 30), 
                              road_length, lane_width,
                              facecolor='#CCCCCC', edgecolor='black', linewidth=2,
                              hatch='///', label='Closed Lane')
        ax.add_patch(left_lane)
        
        # Right lane (open)
        right_lane = Rectangle((road_start_x, schematic_y_start + 30 + lane_width), 
                               road_length, lane_width,
                               facecolor='white', edgecolor='black', linewidth=2,
                               label='Open Lane')
        ax.add_patch(right_lane)
        
        # Draw center line
        for i in range(0, int(road_length), 10):
            ax.plot([road_start_x + i, road_start_x + i + 5], 
                   [schematic_y_start + 45, schematic_y_start + 45], 
                   'k--', linewidth=2)
        
        # Draw edge lines
        ax.plot([road_start_x, road_start_x + road_length], 
               [schematic_y_start + 30, schematic_y_start + 30], 
               'k-', linewidth=3)
        ax.plot([road_start_x, road_start_x + road_length], 
               [schematic_y_start + 60, schematic_y_start + 60], 
               'k-', linewidth=3)
        
        # BILATERAL SIGNAGE - Both sides
        sign_positions = [
            {'dist': -90, 'x': road_start_x - 40, 'code': 'W1-1', 'name': 'Road Work\nAhead'},
            {'dist': -45, 'x': road_start_x + 40, 'code': 'W1-2', 'name': 'Lane Closure\nAhead 45m'},
        ]
        
        for sign_data in sign_positions:
            x_pos = road_start_x + (sign_data['dist'] + 90) * 2.5
            
            # Left side sign (yellow warning)
            self._draw_warning_sign(ax, x_pos, schematic_y_start + 10, 
                                   sign_data['code'], sign_data['name'], 'left')
            
            # Right side sign (yellow warning)
            self._draw_warning_sign(ax, x_pos, schematic_y_start + 70, 
                                   sign_data['code'], sign_data['name'], 'right')
            
            # Distance marker
            ax.text(x_pos, schematic_y_start + 25, f"{sign_data['dist']}m", 
                   ha='center', fontsize=8, weight='bold')
        
        # Draw taper with cones
        taper_start_x = road_start_x + 140
        taper_length = 40
        cone_spacing = 10
        
        for i in range(0, int(taper_length), cone_spacing):
            cone_x = taper_start_x + i
            cone_y_offset = (i / taper_length) * lane_width
            self._draw_cone(ax, cone_x, schematic_y_start + 30 + cone_y_offset)
        
        # Draw work zone
        work_zone_start = taper_start_x + taper_length
        work_zone_length = 80
        
        work_zone_rect = Rectangle((work_zone_start, schematic_y_start + 30), 
                                   work_zone_length, lane_width,
                                   facecolor='yellow', alpha=0.3, edgecolor='red', 
                                   linewidth=2, linestyle='--')
        ax.add_patch(work_zone_rect)
        
        ax.text(work_zone_start + work_zone_length/2, schematic_y_start + 37.5, 
               'WORK ZONE', ha='center', fontsize=12, weight='bold')
        
        # Draw cones along work zone
        for i in range(0, int(work_zone_length), 20):
            self._draw_cone(ax, work_zone_start + i, schematic_y_start + 30)
        
        # Side streets
        side_streets = scenario_data.get('side_streets', [])
        for i, street in enumerate(side_streets[:2]):
            street_x = road_start_x + 100 + (i * 100)
            
            # Draw side street
            ax.plot([street_x, street_x], 
                   [schematic_y_start + 60, schematic_y_start + 90], 
                   'k-', linewidth=3)
            ax.text(street_x, schematic_y_start + 95, street['name'], 
                   ha='center', fontsize=9, weight='bold')
            
            # Side street warning sign
            self._draw_warning_sign(ax, street_x, schematic_y_start + 75, 
                                   'W1-1', 'Road Work\nAhead', 'top')
        
        # Traffic flow arrows
        self._draw_arrow(ax, road_start_x + 20, schematic_y_start + 52.5, 40, 0, 'green')
        ax.text(road_start_x + 45, schematic_y_start + 55, 'TRAFFIC FLOW →', 
               fontsize=10, color='green', weight='bold')
        
        # Legend
        self._draw_legend(ax, 50, 10)
        
        # Scale
        ax.text(370, 15, 'Scale: 1:500', fontsize=10, weight='bold')
        ax.text(370, 10, f'Date: Oct 2025', fontsize=8)
        
        # North arrow
        self._draw_north_arrow(ax, 395, 25)
        
        # Save
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def create_road_closure_detour_tgs(self, scenario_data, output_path):
        """Create TGS for complete road closure with detour"""
        
        fig, ax = plt.subplots(figsize=(16.5, 11.7))
        ax.set_xlim(0, 420)
        ax.set_ylim(0, 297)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title Block
        self._draw_title_block(ax, scenario_data)
        
        # Main road (closed)
        road_y = 150
        road_width = 30
        closure_start_x = 150
        closure_length = 100
        
        # Road before closure
        ax.add_patch(Rectangle((50, road_y), closure_start_x - 50, road_width,
                               facecolor='white', edgecolor='black', linewidth=2))
        
        # Closed section
        ax.add_patch(Rectangle((closure_start_x, road_y), closure_length, road_width,
                               facecolor='red', alpha=0.3, edgecolor='red', 
                               linewidth=3, linestyle='--'))
        ax.text(closure_start_x + closure_length/2, road_y + road_width/2, 
               'ROAD CLOSED\n70m', ha='center', va='center', 
               fontsize=14, weight='bold', color='red')
        
        # Road after closure
        ax.add_patch(Rectangle((closure_start_x + closure_length, road_y), 
                               120, road_width,
                               facecolor='white', edgecolor='black', linewidth=2))
        
        # Barriers at closure points
        for x in [closure_start_x - 2, closure_start_x + closure_length + 2]:
            for i in range(5):
                self._draw_barrier(ax, x, road_y + 5 + i*5)
        
        # Detour route (blue arrows)
        detour_path_x = [closure_start_x - 40, closure_start_x - 40, 
                        closure_start_x + 40, closure_start_x + 40, 
                        closure_start_x + closure_length + 40]
        detour_path_y = [road_y + road_width, road_y + 80, 
                        road_y + 80, road_y - 30, road_y - 30]
        
        ax.plot(detour_path_x, detour_path_y, 'b-', linewidth=4, alpha=0.7)
        ax.text(closure_start_x, road_y + 100, 'DETOUR ROUTE ➜', 
               fontsize=12, color='blue', weight='bold', ha='center')
        
        # Detour arrows
        for i in range(len(detour_path_x) - 1):
            self._draw_arrow(ax, detour_path_x[i], detour_path_y[i], 
                           detour_path_x[i+1] - detour_path_x[i], 
                           detour_path_y[i+1] - detour_path_y[i], 'blue')
        
        # Bilateral signage at approaches
        # North approach
        self._draw_warning_sign(ax, closure_start_x - 50, road_y - 15, 
                               'W1-3', 'Road Closed\nAhead', 'left')
        self._draw_warning_sign(ax, closure_start_x - 50, road_y + road_width + 15, 
                               'W1-3', 'Road Closed\nAhead', 'right')
        
        # Detour arrows (bilateral)
        self._draw_direction_sign(ax, closure_start_x - 25, road_y - 15, 'DETOUR →')
        self._draw_direction_sign(ax, closure_start_x - 25, road_y + road_width + 15, 'DETOUR →')
        
        # Side streets on detour route
        side_streets = ['Wright St', 'Hawker St', 'Park Tce']
        street_positions = [
            (closure_start_x - 40, road_y + 60),
            (closure_start_x + 40, road_y + 60),
            (closure_start_x + 40, road_y - 10)
        ]
        
        for street, pos in zip(side_streets, street_positions):
            ax.text(pos[0], pos[1], street, ha='center', fontsize=10, 
                   weight='bold', bbox=dict(boxstyle='round', facecolor='lightblue'))
        
        # Legend and details
        self._draw_legend(ax, 50, 10)
        ax.text(370, 15, 'Scale: 1:1000', fontsize=10, weight='bold')
        self._draw_north_arrow(ax, 395, 25)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def create_pedestrian_control_tgs(self, scenario_data, output_path):
        """Create TGS for pedestrian management"""
        
        fig, ax = plt.subplots(figsize=(16.5, 11.7))
        ax.set_xlim(0, 420)
        ax.set_ylim(0, 297)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title Block
        self._draw_title_block(ax, scenario_data)
        
        # Road with 3 lanes
        road_y = 140
        lane_width = 12
        road_length = 300
        
        for i in range(3):
            lane_color = '#CCCCCC' if i == 0 else 'white'
            lane = Rectangle((60, road_y + i * lane_width), road_length, lane_width,
                            facecolor=lane_color, edgecolor='black', linewidth=1)
            ax.add_patch(lane)
        
        # Original footpath (closed)
        ax.add_patch(Rectangle((60, road_y - 10), road_length, 8,
                               facecolor='#CCCCCC', edgecolor='red', 
                               linewidth=2, linestyle='--', hatch='xxx'))
        ax.text(210, road_y - 6, 'FOOTPATH CLOSED', ha='center', 
               fontsize=9, color='red', weight='bold')
        
        # Temporary footpath on road
        ax.add_patch(Rectangle((60, road_y + 2), road_length, 6,
                               facecolor='#90EE90', edgecolor='blue', 
                               linewidth=2, alpha=0.5))
        ax.text(210, road_y + 5, 'TEMPORARY FOOTPATH 1.5m', ha='center', 
               fontsize=9, color='blue', weight='bold')
        
        # Pedestrian barriers
        for x in range(60, int(60 + road_length), 20):
            ax.plot([x, x], [road_y + 2, road_y + 8], 'b-', linewidth=2)
        
        # Overhead protection
        for x in range(80, int(60 + road_length), 40):
            ax.add_patch(Rectangle((x, road_y - 2), 30, 12,
                                   facecolor='none', edgecolor='orange', 
                                   linewidth=2, linestyle=':'))
            ax.text(x + 15, road_y + 12, '↓', fontsize=16, ha='center', color='orange')
        
        ax.text(210, road_y + 48, 'OVERHEAD SCAFFOLDING PROTECTION', 
               ha='center', fontsize=10, weight='bold', color='orange')
        
        # Pedestrian crossing points (DDA compliant)
        crossing_points = [120, 200, 280]
        for x in crossing_points:
            # Ramp symbol
            ax.add_patch(Wedge((x, road_y + 5), 5, 180, 360, 
                              facecolor='yellow', edgecolor='black'))
            ax.text(x, road_y - 15, '♿ DDA\nRamp', ha='center', 
                   fontsize=8, weight='bold')
        
        # Traffic flow arrows (2 lanes open)
        for i in [1, 2]:
            y = road_y + i * lane_width + lane_width/2
            self._draw_arrow(ax, 80, y, 40, 0, 'green')
        
        # Side streets with pedestrian signage
        side_streets = scenario_data.get('side_streets', [])[:3]
        for i, street in enumerate(side_streets):
            street_x = 120 + i * 80
            
            # Intersection
            ax.plot([street_x, street_x], [road_y + 36, road_y + 60], 
                   'k-', linewidth=2)
            ax.text(street_x, road_y + 65, street['name'], 
                   ha='center', fontsize=9, weight='bold')
            
            # Pedestrian signs at intersection
            ax.text(street_x - 8, road_y + 50, '🚶', fontsize=16)
            ax.text(street_x + 8, road_y + 50, '→', fontsize=14, color='blue')
        
        # Legend
        self._draw_legend(ax, 50, 10)
        ax.text(370, 15, 'Scale: 1:200', fontsize=10, weight='bold')
        self._draw_north_arrow(ax, 395, 25)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def _draw_title_block(self, ax, scenario_data):
        """Draw title block at top of page"""
        # Main title box
        title_box = FancyBboxPatch((50, 260), 320, 30, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor='#E8F4F8', edgecolor='black', linewidth=2)
        ax.add_patch(title_box)
        
        # Title text
        ax.text(210, 280, 'TRAFFIC GUIDANCE SCHEME (TGS)', 
               ha='center', fontsize=16, weight='bold')
        ax.text(210, 273, scenario_data['name'], 
               ha='center', fontsize=12, weight='bold')
        ax.text(210, 266, f"AS 1742.3 Compliant | {scenario_data['road_name']}", 
               ha='center', fontsize=10)
        
        # Right info box
        info_box = FancyBboxPatch((375, 260), 40, 30, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor='white', edgecolor='black', linewidth=1)
        ax.add_patch(info_box)
        ax.text(395, 280, 'TMP-2025', ha='center', fontsize=9, weight='bold')
        ax.text(395, 273, 'Rev: 01', ha='center', fontsize=8)
        ax.text(395, 266, 'Oct 2025', ha='center', fontsize=8)
    
    def _draw_warning_sign(self, ax, x, y, code, text, position='left'):
        """Draw Austroads warning sign (yellow diamond)"""
        # Diamond shape
        diamond_size = 8
        diamond = patches.FancyBboxPatch((x - diamond_size/2, y - diamond_size/2), 
                                        diamond_size, diamond_size,
                                        boxstyle="round,pad=0.3",
                                        transform=ax.transData,
                                        facecolor=self.color_yellow, 
                                        edgecolor='black', linewidth=2)
        ax.add_patch(diamond)
        
        # Code
        ax.text(x, y, code, ha='center', va='center', 
               fontsize=7, weight='bold')
        
        # Text label
        text_x = x - 12 if position == 'left' else x + 12
        ax.text(text_x, y, text, ha='center', va='center', 
               fontsize=6, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _draw_direction_sign(self, ax, x, y, text):
        """Draw direction sign"""
        ax.add_patch(Rectangle((x-10, y-4), 20, 8,
                               facecolor='blue', edgecolor='black', linewidth=1))
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=7, color='white', weight='bold')
    
    def _draw_cone(self, ax, x, y):
        """Draw traffic cone"""
        cone = patches.Polygon([[x, y], [x-1, y+3], [x+1, y+3]], 
                               facecolor=self.color_orange, edgecolor='black')
        ax.add_patch(cone)
    
    def _draw_barrier(self, ax, x, y):
        """Draw concrete barrier"""
        ax.add_patch(Rectangle((x-1, y), 2, 3,
                               facecolor='#AAAAAA', edgecolor='black', linewidth=1))
    
    def _draw_arrow(self, ax, x, y, dx, dy, color='black'):
        """Draw directional arrow"""
        if dx == 0 and dy == 0:
            return
        arrow = FancyArrow(x, y, dx, dy, width=2, head_width=6, head_length=4,
                          fc=color, ec=color, alpha=0.7)
        ax.add_patch(arrow)
    
    def _draw_north_arrow(self, ax, x, y):
        """Draw north arrow"""
        ax.arrow(x, y, 0, 10, head_width=3, head_length=3, fc='black', ec='black')
        ax.text(x, y + 12, 'N', ha='center', fontsize=12, weight='bold')
    
    def _draw_legend(self, ax, x, y):
        """Draw legend"""
        legend_items = [
            ('yellow', 'square', 'Warning Sign'),
            ('blue', 'square', 'Guidance Sign'),
            ('orange', 'circle', 'Traffic Cone'),
            ('gray', 'square', 'Barrier'),
            ('green', 'arrow', 'Traffic Flow')
        ]
        
        for i, (color, shape, label) in enumerate(legend_items):
            item_y = y + i * 5
            
            if shape == 'square':
                ax.add_patch(Rectangle((x, item_y), 3, 3, facecolor=color, edgecolor='black'))
            elif shape == 'circle':
                ax.add_patch(Circle((x+1.5, item_y+1.5), 1.5, facecolor=color, edgecolor='black'))
            elif shape == 'arrow':
                self._draw_arrow(ax, x, item_y+1.5, 3, 0, color)
            
            ax.text(x + 5, item_y + 1.5, label, fontsize=7, va='center')

def generate_all_visual_tgs():
    """Generate visual TGS drawings for all 3 scenarios"""
    
    generator = VisualTGSGenerator()
    
    scenarios = [
        {
            'name': 'Chief Street Brompton - Lane Closure with Taper',
            'short_name': 'chief_street',
            'road_name': 'Chief Street, Brompton SA',
            'type': 'lane_closure',
            'side_streets': [
                {'name': 'Wright St'},
                {'name': 'Hawker St'}
            ]
        },
        {
            'name': 'Torrens Road Ridleyton - Complete Closure with Detour',
            'short_name': 'torrens_road',
            'road_name': 'Torrens Road, Ridleyton SA',
            'type': 'road_closure',
            'side_streets': [
                {'name': 'Wright St'},
                {'name': 'Park Tce'}
            ]
        },
        {
            'name': 'King William Street Adelaide - CBD Pedestrian Control',
            'short_name': 'king_william',
            'road_name': 'King William Street, Adelaide SA',
            'type': 'pedestrian',
            'side_streets': [
                {'name': 'Currie St'},
                {'name': 'Grenfell St'},
                {'name': 'Pirie St'}
            ]
        }
    ]
    
    generated_files = []
    
    for scenario in scenarios:
        output_path = f"/app/tmp_outputs/{scenario['short_name']}_TGS_Visual_Drawing.png"
        
        if scenario['type'] == 'lane_closure':
            generator.create_lane_closure_tgs(scenario, output_path)
        elif scenario['type'] == 'road_closure':
            generator.create_road_closure_detour_tgs(scenario, output_path)
        elif scenario['type'] == 'pedestrian':
            generator.create_pedestrian_control_tgs(scenario, output_path)
        
        print(f"✅ Generated: {output_path}")
        generated_files.append(output_path)
    
    return generated_files

if __name__ == "__main__":
    print("Generating visual TGS drawings...")
    files = generate_all_visual_tgs()
    print(f"\n✅ Generated {len(files)} visual TGS drawings")
