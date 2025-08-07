import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import UnidentifiedImageError
from utils.dashboard_utils import (
    load_dashboard_data,
    generate_excel_download_link,
    generate_pdf_download_link
)

# --- Page config ---
st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

# --- Banner ---
banner_path = "assets/middle_banner_image.png"
if os.path.exists(banner_path):
    try:
        st.image(banner_path, use_container_width=True)
    except UnidentifiedImageError:
        st.warning("⚠️ Banner image is corrupted or unreadable. Please upload a valid PNG.")
else:
    st.info("ℹ️ No banner image found.")

st.title("👨‍💼 Ask HR - Capital Partners Group")
st.markdown("**Ask me anything (salary, leaves, law, employees, charts, etc.):**")

# --- Load Data ---
df = load_dashboard_data()

if df is None or df.empty:
    st.error("❌ Could not load employee data. Please check the Excel file path and content.")
    st.stop()

# --- User Input ---
user_input = st.text_input("🗨️ Type your question here:")

# --- Handle User Input ---
if user_input:
    lower_input = user_input.lower()

    # Nationalities
    if "nationalit" in lower_input:
        nationalities = df["Nationality"].dropna().unique()
        st.success("🌍 Nationalities in the company:")
        st.write(", ".join(sorted(nationalities)))
        st.markdown(generate_excel_download_link(df[["Name", "Nationality"]]), unsafe_allow_html=True)

    # Age groups
    elif "age group" in lower_input or "age distribution" in lower_input:
        st.subheader("📊 Age Group Distribution")
        fig = px.histogram(df, x="Age", nbins=10, title="Age Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Job Titles
    elif "job title" in lower_input:
        st.subheader("📊 Job Titles")
        job_counts = df["Job Title"].value_counts().reset_index()
        job_counts.columns = ["Job Title", "Count"]
        fig = px.bar(job_counts, x="Job Title", y="Count", title="Job Title Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Gender
    elif "gender" in lower_input or "male" in lower_input or "female" in lower_input:
        st.subheader("📊 Gender Breakdown")
        fig = px.pie(df, names="Gender", title="Gender Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Grade / Band / Entity
    elif "grade" in lower_input or "band" in lower_input or "entity" in lower_input or "company" in lower_input:
        columns_to_check = ["Grade", "Band", "Entity"]
        for col in columns_to_check:
            if col in df.columns:
                st.subheader(f"📊 {col} Distribution")
                fig = px.bar(df[col].value_counts().reset_index(), x="index", y=col,
                             labels={"index": col, col: "Count"}, title=f"{col} Breakdown")
                st.plotly_chart(fig, use_container_width=True)

    # Specific employee details
    elif any(name in lower_input for name in df["Name"].dropna().str.lower()):
        matched = df[df["Name"].str.lower().str.contains(lower_input)]
        if not matched.empty:
            st.success("👤 Employee Details:")
            st.dataframe(matched)
            st.markdown(generate_excel_download_link(matched), unsafe_allow_html=True)
            st.markdown(generate_pdf_download_link(matched), unsafe_allow_html=True)
        else:
            st.warning("Employee not found. Please check the name or try a different keyword.")

    # Fallback
    else:
        st.info("🤖 I understand basic HR questions like:\n- Nationalities\n- Age Groups\n- Job Titles\n- Grades, Bands, Entities\n- Employee lookup\nTry one of those!")

# --- Optional: Footer ---
st.markdown("---")
st.caption("Capital Partners Group © 2025 — HR Virtual Assistant")

