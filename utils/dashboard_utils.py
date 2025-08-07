# utils/dashboard_utils.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


def load_dashboard_data():
    return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")


def show_employee_details(df, prompt):
    filtered = df[df['Full Name'].str.lower().str.contains(prompt.lower())]
    if not filtered.empty:
        st.dataframe(filtered)
    else:
        st.warning("No matching employee found.")


def show_dashboard(df, prompt):
    prompt = prompt.lower()
    matched_column = None
    for col in df.columns:
        if col.lower() in prompt:
            matched_column = col
            break

    if matched_column:
        try:
            data = df.groupby(['Entity', matched_column]).size().unstack(fill_value=0)
            st.bar_chart(data.T)
        except Exception as e:
            st.error(f"Couldn't generate dashboard for: {matched_column}")
            st.exception(e)

    elif "age" in prompt:
        bins = [18, 25, 35, 45, 55, 70]
        labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
        df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
        data = df.groupby(['Entity', 'Age Group']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    else:
        st.warning("No matching dashboard available for this prompt.")


def export_dashboard_data(df, prompt):
    prompt = prompt.lower()
    for col in df.columns:
        if col.lower() in prompt:
            return df[['Entity', col]]
    if "age" in prompt:
        return df[['Entity', 'Age']]
    return pd.DataFrame()


def export_pdf(filtered_df, filename="dashboard_output.pdf"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    style = getSampleStyleSheet()
    data = [filtered_df.columns.tolist()] + filtered_df.astype(str).values.tolist()

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(Paragraph("📊 Dashboard Output", style['Heading2']))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
