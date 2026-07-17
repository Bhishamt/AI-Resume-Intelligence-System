import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)

class PDFExporter:
    @staticmethod
    def export(resume_data: dict, output_path: str) -> bool:
        """Generates an ATS-compliant PDF resume."""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54
            )
            
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                alignment=TA_CENTER,
                spaceAfter=6
            )
            
            contact_style = ParagraphStyle(
                'ContactInfo',
                parent=styles['Normal'],
                fontSize=9,
                leading=12,
                alignment=TA_CENTER,
                spaceAfter=15
            )
            
            section_heading = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=12,
                leading=16,
                spaceBefore=10,
                spaceAfter=4,
                keepWithNext=True
            )
            
            body_style = ParagraphStyle(
                'BodyTextCustom',
                parent=styles['Normal'],
                fontSize=9.5,
                leading=13.5,
                spaceAfter=6
            )

            story = []
            
            # Personal info
            info = resume_data.get("personal_info", {})
            story.append(Paragraph(info.get("full_name", "Resume Candidate"), title_style))
            
            contact_line = f"{info.get('location', '')} | {info.get('phone', '')} | {info.get('email', '')} | {info.get('website', '')}"
            story.append(Paragraph(contact_line, contact_style))
            
            # Summary
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
            story.append(Paragraph(resume_data.get("summary", ""), body_style))
            story.append(Spacer(1, 4))
            
            # Experience
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
            for job in resume_data.get("experience", []):
                job_title = f"<b>{job.get('job_title', '')}</b> – {job.get('company', '')} ({job.get('start_date', '')} - {job.get('end_date', '')})"
                story.append(Paragraph(job_title, body_style))
                for highlight in job.get("highlights", []):
                    story.append(Paragraph(f"• {highlight}", body_style))
                story.append(Spacer(1, 3))
                
            # Skills
            story.append(Paragraph("SKILLS", section_heading))
            skills = resume_data.get("skills", {})
            skills_str = ", ".join([f"<b>{k.capitalize()}:</b> {', '.join(v)}" for k, v in skills.items() if v])
            story.append(Paragraph(skills_str, body_style))
            story.append(Spacer(1, 4))
            
            # Education
            story.append(Paragraph("EDUCATION", section_heading))
            for edu in resume_data.get("education", []):
                edu_str = f"<b>{edu.get('degree', '')}</b>, {edu.get('institution', '')} ({edu.get('graduation_year', '')})"
                story.append(Paragraph(edu_str, body_style))

            doc.build(story)
            return True
        except Exception as e:
            logger.error("Failed to generate PDF: %s", e)
            return False
        
    @staticmethod
    def export_cover_letter(letter_text: str, personal_info: dict, company_name: str, output_path: str) -> bool:
        """Generates cover letter PDF."""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, alignment=TA_LEFT, spaceAfter=4)
            body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
            
            story = []
            story.append(Paragraph(personal_info.get("full_name", ""), title_style))
            story.append(Paragraph(f"{personal_info.get('location', '')} | {personal_info.get('email', '')}", body_style))
            story.append(Spacer(1, 10))
            
            for paragraph in letter_text.split('\n\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph.replace('\n', '<br/>'), body_style))
                    story.append(Spacer(1, 6))
                    
            doc.build(story)
            return True
        except Exception as e:
            logger.error("Failed to generate cover letter PDF: %s", e)
            return False
