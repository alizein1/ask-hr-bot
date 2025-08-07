import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# GPT fallback if not available
try:
    from openai_utils import ask_openai
except ImportError:
    def ask_openai(prompt):
        return "[OpenAI not available] GPT-based explanation would appear here."

def load_dashboard_data():
    try:
        return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx", engine="openpyxl")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

def show_employee_details(df, prompt):
    filtered = df[df['Full Name'].str.lower().str.contains(prompt.lower())]
    if not filtered.empty:
        st.dataframe(filtered)
    else:
        st.warning("No matching employee found.")

def show_dashboard(df, prompt):
    prompt = prompt.lower()

    if "nationalit" in prompt:
        data = df.groupby(['Entity', 'Nationality']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "gender" in prompt:
        data = df.groupby(['Entity', 'Gender']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "band" in prompt:
        data = df.groupby(['Entity', 'Band']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "grade" in prompt:
        data = df.groupby(['Entity', 'Grade']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "job title" in prompt:
        data = df.groupby(['Entity', 'Job Title']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "age" in prompt:
        bins = [18, 25, 35, 45, 55, 70]
        labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
        df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
        data = df.groupby(['Entity', 'Age Group']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

def export_dashboard_data(df, prompt):
    prompt = prompt.lower()

    if "nationalit" in prompt:
        return df[['Entity', 'Nationality']]
    elif "gender" in prompt:
        return df[['Entity', 'Gender']]
    elif "band" in prompt:
        return df[['Entity', 'Band']]
    elif "grade" in prompt:
        return df[['Entity', 'Grade']]
    elif "job title" in prompt:
        return df[['Entity', 'Job Title']]
    elif "age" in prompt:
        return df[['Entity', 'Age']]

    return pd.DataFrame()

def export_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Dashboard Export", styles["Title"])]

    for col in df.columns:
        values = ', '.join(map(str, df[col].unique()))
        elements.append(Paragraph(f"<b>{col}</b>: {values}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_excel_download_link(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="export.xlsx">📥 Download Excel file</a>'

def generate_pdf_download_link(df):
    pdf_buffer = export_pdf(df)
    b64 = base64.b64encode(pdf_buffer.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="export.pdf">📄 Download PDF file</a>'

def explain_dashboard(df, prompt):
    sample = df.head(10).to_markdown()
    explanation_prompt = f"""You are an HR analyst. Here is sample data:

{sample}

The user asked for: \"{prompt}\"

Please explain the insights from this data in a concise way."""
    explanation = ask_openai(explanation_prompt)
    st.markdown("🧠 **Chart Insights:**")
    st.info(explanation)
