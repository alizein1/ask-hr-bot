import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import UnidentifiedImageError

from utils.dashboard_utils import (
    load_dashboard_data,
    generate_excel_download_link,
    generate_pdf_download_link,
    show_dashboard,
    show_employee_details,
    export_dashboard_data,
    explain_dashboard
)

from utils.policy_utils import load_policy_text, answer_policy_question

# Page config
st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

# Banner
banner_path = "assets/middle_banner_image.png"
if os.path.exists(banner_path):
    try:
        st.image(banner_path, use_container_width=True)
    except UnidentifiedImageError:
        st.warning("⚠️ Banner image is unreadable. Please upload a valid PNG image.")
else:
    st.info("ℹ️ No banner image found in the assets folder.")

st.title("👨‍💼 Ask HR - Capital Partners Group")
st.markdown("**Ask me anything (salary, leaves, law, employees, dashboards, or policy):**")

# Load data
df = load_dashboard_data()
if df is None or df.empty:
    st.error("❌ Could not load employee data. Please check the Excel file path and content.")
    st.stop()

# Cache policy file
@st.cache_data
def get_policy_text():
    return load_policy_text("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")

policy_text = get_policy_text()

# Input
user_input = st.text_input("🗨️ Type your question here:")

# Logic
if user_input:
    lower_input = user_input.lower()

    # Try to answer from policy
    response = answer_policy_question(user_input, policy_text)

    if response and "no relevant content found" not in response.lower():
        st.success("📘 Policy Answer:")
        st.write(response)

    # If no good policy match, check dashboard logic
    elif any(term in lower_input for term in ["nationalit", "gender", "band", "grade", "job title", "age"]):
        show_dashboard(df, lower_input)
        export_df = export_dashboard_data(df, lower_input)
        if not export_df.empty:
            st.markdown(generate_excel_download_link(export_df), unsafe_allow_html=True)
            st.markdown(generate_pdf_download_link(export_df), unsafe_allow_html=True)
            explain_dashboard(export_df, lower_input)

    # Employee details
    elif any(name in lower_input for name in df["Full Name"].dropna().str.lower()):
        show_employee_details(df, lower_input)
        filtered = df[df["Full Name"].str.lower().str.contains(lower_input)]
        st.markdown(generate_excel_download_link(filtered), unsafe_allow_html=True)
        st.markdown(generate_pdf_download_link(filtered), unsafe_allow_html=True)

    # Final fallback
    else:
        st.info("🤖 I can show dashboards (age, gender, job title, grades, bands, nationalities), employee details, or explain policies. Try asking about those!")

# Footer
st.markdown("---")
st.caption("Capital Partners Group © 2025 — HR Virtual Assistant")
