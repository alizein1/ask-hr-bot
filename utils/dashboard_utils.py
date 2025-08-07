import pandas as pd
import base64
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def load_dashboard_data():
    try:
        return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx", engine="openpyxl")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None

def generate_excel_download_link(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="employee_data.xlsx">📥 Download Excel file</a>'
    return href

def generate_pdf_download_link(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Add title
    elements.append(Paragraph("Employee Data Summary", styles['Heading1']))

    # Prepare table data (limit rows for readability)
    preview_df = df.head(20)
    table_data = [preview_df.columns.tolist()] + preview_df.values.tolist()

    # Create table
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))

    elements.append(table)
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()

    b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="employee_data.pdf">📄 Download PDF file</a>'
    return href
