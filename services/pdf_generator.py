from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from typing import List, Dict
import os
from datetime import datetime

class PDFGenerator:
    def __init__(self, output_dir: str = 'generated_pdfs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_schedule_pdf(self, schedule: List[Dict], metrics: Dict) -> str:
        """
        Generate a PDF document containing the repayment schedule.
        
        Args:
            schedule: List of monthly repayment records
            metrics: Dictionary containing schedule metrics
            
        Returns:
            Path to the generated PDF file
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'repayment_schedule_{timestamp}.pdf'
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = Paragraph("Repayment Schedule", styles['Title'])
        elements.append(title)
        
        # Add metrics summary
        metrics_text = f"""
        Total Amount: ${metrics['total_payments']:,.2f}
        Average Monthly Payment: ${metrics['average_payment']:,.2f}
        Minimum Payment: ${metrics['min_payment']:,.2f}
        Maximum Payment: ${metrics['max_payment']:,.2f}
        Completion Date: {metrics['completion_date']}
        Total Months: {metrics['total_months']}
        """
        summary = Paragraph(metrics_text, styles['Normal'])
        elements.append(summary)
        
        # Create schedule table
        table_data = [['Date', 'Payment', 'Remaining Balance', 'Season']]
        for record in schedule:
            table_data.append([
                record['date'],
                f"${record['payment']:,.2f}",
                f"${record['remaining_balance']:,.2f}",
                record['season'].capitalize()
            ])
        
        # Style the table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return filepath 