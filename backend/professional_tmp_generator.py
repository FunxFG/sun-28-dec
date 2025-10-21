"""
Professional Traffic Management Plan (TMP) Generator
Matches MRWA/Austroads format with complete sections, forms, and TCDs
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image, KeepTogether)
from reportlab.pdfgen import canvas as pdf_canvas
from datetime import datetime, timedelta
import io

class ProfessionalTMPGenerator:
    """Generate complete professional TMP documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='TMPTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='TMPBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Table header
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
    def generate_complete_tmp(self, plan_data, output_path):
        """Generate complete TMP document"""
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # 1. TITLE PAGE
        story.extend(self._create_title_page(plan_data))
        story.append(PageBreak())
        
        # 2. DECLARATION
        story.extend(self._create_declaration(plan_data))
        story.append(PageBreak())
        
        # 3. TABLE OF CONTENTS
        story.extend(self._create_table_of_contents())
        story.append(PageBreak())
        
        # 4. SECTION 1: INTRODUCTION
        story.extend(self._create_introduction(plan_data))
        story.append(PageBreak())
        
        # 5. SECTION 2: PROJECT OVERVIEW
        story.extend(self._create_project_overview(plan_data))
        story.append(PageBreak())
        
        # 6. SECTION 3: PROJECT REPRESENTATIVES
        story.extend(self._create_project_representatives(plan_data))
        story.append(PageBreak())
        
        # 7. SECTION 4: TRAFFIC MANAGEMENT ADMINISTRATION
        story.extend(self._create_administration(plan_data))
        story.append(PageBreak())
        
        # 8. SECTION 5: SAFETY PLAN
        story.extend(self._create_safety_plan(plan_data))
        story.append(PageBreak())
        
        # 9. SECTION 6: HAZARD IDENTIFICATION & RISK ASSESSMENT
        story.extend(self._create_risk_assessment(plan_data))
        story.append(PageBreak())
        
        # 10. SECTION 7: EMERGENCY ARRANGEMENTS
        story.extend(self._create_emergency_arrangements(plan_data))
        story.append(PageBreak())
        
        # 11. SECTION 8: APPROVALS
        story.extend(self._create_approvals(plan_data))
        story.append(PageBreak())
        
        # 12. SECTION 9: NOTIFICATION
        story.extend(self._create_notification(plan_data))
        story.append(PageBreak())
        
        # 13. SECTION 10: TRAFFIC ASSESSMENT
        story.extend(self._create_traffic_assessment(plan_data))
        story.append(PageBreak())
        
        # 14. SECTION 11: TRAFFIC MANAGEMENT IMPLEMENTATION
        story.extend(self._create_implementation(plan_data))
        story.append(PageBreak())
        
        # 15. SECTION 12: COMMUNICATION
        story.extend(self._create_communication(plan_data))
        story.append(PageBreak())
        
        # 16. SECTION 13: TRAFFIC MANAGEMENT MONITORING
        story.extend(self._create_monitoring(plan_data))
        story.append(PageBreak())
        
        # 17. SECTION 14: IMPLEMENTATION STANDARDS
        story.extend(self._create_implementation_standards(plan_data))
        story.append(PageBreak())
        
        # 18. SECTION 15: MANAGEMENT REVIEW
        story.extend(self._create_management_review(plan_data))
        story.append(PageBreak())
        
        # 19. SECTION 16: REFERENCES
        story.extend(self._create_references())
        story.append(PageBreak())
        
        # 20. APPENDICES
        story.extend(self._create_appendices(plan_data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, 
                 onLaterPages=self._add_header_footer)
        
        return output_path
    
    def _create_title_page(self, plan_data):
        """Create title page"""
        elements = []
        
        # Logo/Header space
        elements.append(Spacer(1, 50))
        
        # Main title
        title = Paragraph("TRAFFIC MANAGEMENT PLAN", self.styles['TMPTitle'])
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Project name
        project_name = Paragraph(
            f"<b>{plan_data.get('plan_name', 'Project Name')}</b>",
            ParagraphStyle('ProjectName', parent=self.styles['TMPTitle'], fontSize=18)
        )
        elements.append(project_name)
        elements.append(Spacer(1, 50))
        
        # Project details table
        details_data = [
            ['<b>Project Name:</b>', plan_data.get('plan_name', 'N/A')],
            ['<b>Location:</b>', f"{plan_data.get('work_details', {}).get('start_address', 'N/A')}"],
            ['<b>Road Authority:</b>', plan_data.get('road_data', {}).get('governing_body', 'N/A')],
            ['<b>Contractor:</b>', plan_data.get('company_details', {}).get('name', 'N/A')],
            ['<b>Contract No:</b>', 'TMP-' + datetime.now().strftime('%Y%m%d')],
            ['<b>TMP Classification:</b>', self._determine_classification(plan_data)],
            ['<b>Date Prepared:</b>', datetime.now().strftime('%d/%m/%Y')],
        ]
        
        details_table = Table(details_data, colWidths=[150, 300])
        details_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 50))
        
        # Prepared by
        elements.append(Paragraph("<b>Prepared By:</b>", self.styles['SubsectionHeading']))
        elements.append(Paragraph(
            f"{plan_data.get('company_details', {}).get('name', 'N/A')}<br/>"
            f"ABN: {plan_data.get('company_details', {}).get('abn', 'N/A')}<br/>"
            f"Phone: {plan_data.get('company_details', {}).get('phone', 'N/A')}",
            self.styles['TMPBody']
        ))
        
        return elements
    
    def _create_declaration(self, plan_data):
        """Create AWTM declaration page"""
        elements = []
        
        elements.append(Paragraph("DECLARATION", self.styles['SectionHeading']))
        elements.append(Spacer(1, 20))
        
        declaration_text = """
        I, <b>[AWTM Name]</b>, being an Accredited Work Zone Traffic Management Person, 
        declare that this Traffic Management Plan has been prepared in accordance with the 
        requirements of:
        <br/><br/>
        • AS 1742.3 Manual of uniform traffic control devices – Part 3: Traffic control for works on roads<br/>
        • Main Roads Western Australia Traffic Management for Works on Roads Code of Practice<br/>
        • Austroads Guide to Temporary Traffic Management<br/>
        <br/>
        This plan complies with all relevant standards and regulations for traffic management 
        during roadworks.
        """
        
        elements.append(Paragraph(declaration_text, self.styles['TMPBody']))
        elements.append(Spacer(1, 40))
        
        # Signature block
        sig_data = [
            ['<b>AWTM Name:</b>', '_' * 40],
            ['<b>AWTM Number:</b>', '_' * 40],
            ['<b>Signature:</b>', '_' * 40],
            ['<b>Date:</b>', datetime.now().strftime('%d/%m/%Y')],
        ]
        
        sig_table = Table(sig_data, colWidths=[120, 300])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(sig_table)
        
        return elements
    
    def _create_table_of_contents(self):
        """Create table of contents"""
        elements = []
        
        elements.append(Paragraph("TABLE OF CONTENTS", self.styles['SectionHeading']))
        elements.append(Spacer(1, 20))
        
        toc_items = [
            ('1.', 'INTRODUCTION', '4'),
            ('1.1', 'Purpose', '4'),
            ('1.2', 'Scope', '4'),
            ('1.3', 'Objectives', '4'),
            ('1.4', 'Strategies', '5'),
            ('2.', 'PROJECT OVERVIEW', '6'),
            ('2.1', 'Project Location', '6'),
            ('2.2', 'Project Details', '6'),
            ('2.3', 'Site Constraints', '7'),
            ('3.', 'PROJECT REPRESENTATIVES', '8'),
            ('4.', 'TRAFFIC MANAGEMENT ADMINISTRATION', '9'),
            ('5.', 'SAFETY PLAN', '10'),
            ('5.1', 'Occupational Safety and Health', '10'),
            ('5.2', 'Competencies and Training', '11'),
            ('5.3', 'Responsibilities', '11'),
            ('6.', 'HAZARD IDENTIFICATION & RISK ASSESSMENT', '12'),
            ('6.1', 'Risk Classification', '12'),
            ('6.2', 'Risk Register', '13'),
            ('7.', 'EMERGENCY ARRANGEMENTS', '16'),
            ('7.1', 'Emergency Services', '16'),
            ('7.2', 'Emergency Contacts', '16'),
            ('7.3', 'Contingency Plans', '17'),
            ('8.', 'APPROVALS', '18'),
            ('9.', 'NOTIFICATION', '19'),
            ('10.', 'TRAFFIC ASSESSMENT', '20'),
            ('10.1', 'Existing Traffic Environment', '20'),
            ('10.2', 'Traffic Volumes', '21'),
            ('10.3', 'Traffic Impact', '21'),
            ('11.', 'TRAFFIC MANAGEMENT IMPLEMENTATION', '22'),
            ('11.1', 'Staging of Works', '22'),
            ('11.2', 'Traffic Control Diagrams', '23'),
            ('11.3', 'Signage and Delineation', '24'),
            ('12.', 'COMMUNICATION', '25'),
            ('13.', 'TRAFFIC MANAGEMENT MONITORING', '26'),
            ('13.1', 'Daily Inspections', '26'),
            ('13.2', 'Auditing', '26'),
            ('14.', 'IMPLEMENTATION STANDARDS', '27'),
            ('15.', 'MANAGEMENT REVIEW', '28'),
            ('16.', 'REFERENCES', '29'),
            ('', '<b>APPENDICES</b>', ''),
            ('A', 'Notification of Road Works', '30'),
            ('B', 'Variation to Standards', '31'),
            ('C', 'Record Forms', '32'),
            ('D', 'Traffic Control Diagrams (TCDs)', '35'),
            ('E', 'Traffic Analysis', '45'),
            ('F', 'Barrier Design', '46'),
            ('G', 'Temporary Speed Exemption Request', '47'),
        ]
        
        toc_table_data = []
        for num, title, page in toc_items:
            if title.startswith('<b>'):
                toc_table_data.append([
                    Paragraph(f"<b>{num}</b>", self.styles['Normal']),
                    Paragraph(title, self.styles['Normal']),
                    Paragraph(f"<b>{page}</b>", self.styles['Normal'])
                ])
            else:
                indent = '    ' * (len(num.split('.')) - 1) if '.' in num else ''
                toc_table_data.append([
                    Paragraph(num, self.styles['Normal']),
                    Paragraph(f"{indent}{title}", self.styles['Normal']),
                    Paragraph(page, self.styles['Normal'])
                ])
        
        toc_table = Table(toc_table_data, colWidths=[60, 380, 60])
        toc_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(toc_table)
        
        return elements
    
    def _create_introduction(self, plan_data):
        """Create introduction section"""
        elements = []
        
        elements.append(Paragraph("1. INTRODUCTION", self.styles['SectionHeading']))
        elements.append(Spacer(1, 10))
        
        # 1.1 Purpose
        elements.append(Paragraph("1.1 Purpose", self.styles['SubsectionHeading']))
        purpose_text = f"""
        This Traffic Management Plan (TMP) has been prepared for {plan_data.get('plan_name', 'the project')} 
        located at {plan_data.get('work_details', {}).get('start_address', 'project location')}.
        The purpose of this TMP is to:
        <br/><br/>
        • Ensure the safety of road users, workers, and the public<br/>
        • Minimize disruption to traffic flow<br/>
        • Comply with AS 1742.3 and relevant road authority requirements<br/>
        • Provide clear guidance for traffic management implementation<br/>
        • Define roles and responsibilities for all personnel<br/>
        """
        elements.append(Paragraph(purpose_text, self.styles['TMPBody']))
        elements.append(Spacer(1, 15))
        
        # 1.2 Scope
        elements.append(Paragraph("1.2 Scope", self.styles['SubsectionHeading']))
        scope_text = f"""
        This TMP covers all traffic management activities associated with 
        {plan_data.get('work_details', {}).get('description', 'the works')}.
        The works are scheduled to commence on {plan_data.get('work_details', {}).get('start_date', 'TBC')} 
        and are expected to be completed by {plan_data.get('work_details', {}).get('end_date', 'TBC')}.
        <br/><br/>
        The scope includes:<br/>
        • Installation and maintenance of traffic control devices<br/>
        • Management of traffic during {plan_data.get('work_details', {}).get('work_style', 'static')} works<br/>
        • Monitoring and adjustment of traffic management measures<br/>
        • Emergency response procedures<br/>
        • Communication with stakeholders<br/>
        """
        elements.append(Paragraph(scope_text, self.styles['TMPBody']))
        elements.append(Spacer(1, 15))
        
        # 1.3 Objectives
        elements.append(Paragraph("1.3 Objectives", self.styles['SubsectionHeading']))
        objectives_text = """
        The key objectives of this TMP are to:<br/><br/>
        1. <b>Safety:</b> Ensure the safety of all road users, workers, and pedestrians<br/>
        2. <b>Compliance:</b> Meet all regulatory requirements and Australian Standards<br/>
        3. <b>Traffic Flow:</b> Maintain traffic flow with minimal disruption<br/>
        4. <b>Communication:</b> Provide clear information to road users and stakeholders<br/>
        5. <b>Risk Management:</b> Identify and mitigate all traffic-related risks<br/>
        6. <b>Emergency Response:</b> Ensure rapid and effective response to incidents<br/>
        """
        elements.append(Paragraph(objectives_text, self.styles['TMPBody']))
        elements.append(Spacer(1, 15))
        
        # 1.4 Strategies
        elements.append(Paragraph("1.4 Strategies", self.styles['SubsectionHeading']))
        strategies_text = """
        The following strategies will be employed to achieve the objectives:<br/><br/>
        • Use of Australian Standard-compliant traffic control devices<br/>
        • Bilateral signage placement where required<br/>
        • Staged implementation to minimize impact<br/>
        • 24/7 emergency contact availability<br/>
        • Daily inspections and maintenance<br/>
        • Clear communication protocols<br/>
        • Trained and accredited traffic management personnel<br/>
        """
        elements.append(Paragraph(strategies_text, self.styles['TMPBody']))
        
        return elements
    
    def _determine_classification(self, plan_data):
        """Determine if TMP is complex or non-complex"""
        # Simple logic - can be enhanced
        if plan_data.get('road_occupancy', {}).get('complete_road_closure'):
            return 'COMPLEX'
        elif plan_data.get('road_data', {}).get('traffic_volume', 0) > 20000:
            return 'COMPLEX'
        else:
            return 'NON-COMPLEX'
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to pages"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(30*mm, 280*mm, "TRAFFIC MANAGEMENT PLAN")
        canvas.line(30*mm, 278*mm, 180*mm, 278*mm)
        
        # Footer
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        canvas.drawString(95*mm, 15*mm, f"Page {page_num}")
        
        canvas.restoreState()
    
    # Placeholder methods for other sections - will implement fully
    def _create_project_overview(self, plan_data):
        elements = []
        elements.append(Paragraph("2. PROJECT OVERVIEW", self.styles['SectionHeading']))
        elements.append(Paragraph("Section to be implemented with full details...", self.styles['TMPBody']))
        return elements
    
    def _create_project_representatives(self, plan_data):
        elements = []
        elements.append(Paragraph("3. PROJECT REPRESENTATIVES", self.styles['SectionHeading']))
        return elements
    
    def _create_administration(self, plan_data):
        elements = []
        elements.append(Paragraph("4. TRAFFIC MANAGEMENT ADMINISTRATION", self.styles['SectionHeading']))
        return elements
    
    def _create_safety_plan(self, plan_data):
        elements = []
        elements.append(Paragraph("5. SAFETY PLAN", self.styles['SectionHeading']))
        return elements
    
    def _create_risk_assessment(self, plan_data):
        elements = []
        elements.append(Paragraph("6. HAZARD IDENTIFICATION & RISK ASSESSMENT", self.styles['SectionHeading']))
        return elements
    
    def _create_emergency_arrangements(self, plan_data):
        elements = []
        elements.append(Paragraph("7. EMERGENCY ARRANGEMENTS", self.styles['SectionHeading']))
        return elements
    
    def _create_approvals(self, plan_data):
        elements = []
        elements.append(Paragraph("8. APPROVALS", self.styles['SectionHeading']))
        return elements
    
    def _create_notification(self, plan_data):
        elements = []
        elements.append(Paragraph("9. NOTIFICATION", self.styles['SectionHeading']))
        return elements
    
    def _create_traffic_assessment(self, plan_data):
        elements = []
        elements.append(Paragraph("10. TRAFFIC ASSESSMENT", self.styles['SectionHeading']))
        return elements
    
    def _create_implementation(self, plan_data):
        elements = []
        elements.append(Paragraph("11. TRAFFIC MANAGEMENT IMPLEMENTATION", self.styles['SectionHeading']))
        return elements
    
    def _create_communication(self, plan_data):
        elements = []
        elements.append(Paragraph("12. COMMUNICATION", self.styles['SectionHeading']))
        return elements
    
    def _create_monitoring(self, plan_data):
        elements = []
        elements.append(Paragraph("13. TRAFFIC MANAGEMENT MONITORING", self.styles['SectionHeading']))
        return elements
    
    def _create_implementation_standards(self, plan_data):
        elements = []
        elements.append(Paragraph("14. IMPLEMENTATION STANDARDS", self.styles['SectionHeading']))
        return elements
    
    def _create_management_review(self, plan_data):
        elements = []
        elements.append(Paragraph("15. MANAGEMENT REVIEW", self.styles['SectionHeading']))
        return elements
    
    def _create_references(self):
        elements = []
        elements.append(Paragraph("16. REFERENCES", self.styles['SectionHeading']))
        return elements
    
    def _create_appendices(self, plan_data):
        elements = []
        elements.append(Paragraph("APPENDICES", self.styles['SectionHeading']))
        return elements
