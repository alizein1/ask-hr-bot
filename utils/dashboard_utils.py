import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
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
    result_df = pd.DataFrame()

    if "nationalit" in prompt:
        result_df = df[['Entity', 'Nationality']]

    elif "gender" in prompt:
        result_df = df[['Entity', 'Gender']]

    elif "band" in prompt:
        result_df = df[['Entity', 'Band']]

    elif "grade" in prompt:
        result_df = df[['Entity', 'Grade']]

    elif "job title" in prompt:
        result_df = df[['Entity', 'Job Title']]

    elif "age" in prompt:
        result_df = df[['Entity', 'Age']]

    return result_df

def export_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Dashboard Export", styles["Title"])]

    for col in df.columns:
        text = f"<b>{col}</b>: {', '.join(map(str, df[col].unique()))}"
        elements.append(Paragraph(text, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def explain_dashboard(df, prompt):
    sample = df.head(10).to_markdown()
    explanation_prompt = f"""You are an HR analyst. Here is sample data:

{sample}

The user asked for: "{prompt}"

Please explain the insights from this data in a concise way."""
    explanation = ask_openai(explanation_prompt)
    st.markdown("🧠 **Chart Insights:**")
    st.info(explanation)
