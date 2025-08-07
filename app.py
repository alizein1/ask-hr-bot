import streamlit as st
import pandas as pd
import os
from PIL import UnidentifiedImageError

from utils.dashboard_utils import (
    load_dashboard_data,
    dynamic_data_response,
    generate_excel_download_link,
    generate_pdf_download_link
)
from utils.policy_utils import load_policy_sections, answer_policy_question

# Page config
st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

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

policy_sections = load_policy_sections("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")

user_input = st.text_input("🗨️ Type your question here:")

if user_input:
    # Try to answer dynamically from Excel data
    excel_response = dynamic_data_response(df, user_input)

    if excel_response["found"]:
        # Show results: chart or table + GPT explanation
        if excel_response["chart"]:
            st.plotly_chart(excel_response["chart"], use_container_width=True)
        if excel_response["table"] is not None:
            st.dataframe(excel_response["table"])
            st.markdown(generate_excel_download_link(excel_response["table"]), unsafe_allow_html=True)
            st.markdown(generate_pdf_download_link(excel_response["table"]), unsafe_allow_html=True)
        if excel_response["explanation"]:
            st.markdown("🧠 **Insights:**")
            st.info(excel_response["explanation"])
    else:
        # Fallback: answer from policy
        response = answer_policy_question(user_input, policy_sections)
        if response and "no relevant content found" not in response.lower():
            st.success("📘 Policy Answer:")
            st.write(response)
        else:
            st.info("🤖 Sorry, I couldn't find info in Excel data or policy. Please ask differently.")

st.markdown("---")
st.caption("Capital Partners Group © 2025 — HR Virtual Assistant")
