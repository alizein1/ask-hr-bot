import streamlit as st
import pandas as pd
import plotly.express as px
from utils.dashboard_utils import load_dashboard_data, generate_dashboard_chart, generate_excel_download_link, generate_pdf_download_link

# Set page config
st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

# UI
st.title("\U0001F468‍\U0001F4BC Ask HR - Capital Partners Group")
st.write("Ask me anything about salary, leaves, nationalities, job titles, age groups, etc.")

# Load data
df = load_dashboard_data()

if df is None or df.empty:
    st.error("❌ Failed to load employee data. Please check the Excel file path or format.")
    st.stop()
else:
    st.success(f"✅ Employee data loaded successfully. Total records: {len(df)}")

# Input from user
user_input = st.text_input("\U0001F4AC Your question:")

if user_input:
    user_input_lower = user_input.lower()

    # Nationalities
    if "nationalit" in user_input_lower:
        nationalities = df['Nationality'].dropna().unique().tolist()
        st.write(f"The nationalities in our company are: {', '.join(sorted(nationalities))}.")

    # Age groups
    elif "age" in user_input_lower:
        df['Age Group'] = pd.cut(df['Age'], bins=[0, 25, 35, 45, 55, 100], labels=["<25", "25-34", "35-44", "45-54", "55+"])
        fig = px.histogram(df, x='Age Group', color='Entity', barmode='group', title="Age Group Distribution by Entity")
        st.plotly_chart(fig, use_container_width=True)

    # Job titles
    elif "job title" in user_input_lower or "position" in user_input_lower:
        job_counts = df['Job Title'].value_counts().reset_index()
        job_counts.columns = ['Job Title', 'Count']
        fig = px.bar(job_counts, x='Job Title', y='Count', title="Job Title Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Entities, Bands, Grades
    elif any(term in user_input_lower for term in ["entity", "band", "grade"]):
        col = "Entity" if "entity" in user_input_lower else "Band" if "band" in user_input_lower else "Grade"
        count_df = df[col].value_counts().reset_index()
        count_df.columns = [col, 'Count']
        fig = px.pie(count_df, names=col, values='Count', title=f"{col} Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Employee-specific
    elif any(name in user_input_lower for name in df['Full Name'].str.lower()):
        match = df[df['Full Name'].str.lower().apply(lambda x: x in user_input_lower)]
        st.write("Employee details:")
        st.dataframe(match)

    # Unrecognized input
    else:
        st.info("I'm still learning. Try asking about nationalities, age groups, job titles, entities, grades, bands, or employee names.")

    # Optional downloads
    st.markdown("### \U0001F4BE Download Data")
    st.markdown(generate_excel_download_link(df), unsafe_allow_html=True)
    st.markdown(generate_pdf_download_link(df), unsafe_allow_html=True)
