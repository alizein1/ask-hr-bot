import streamlit as st
import pandas as pd
import os
from utils.openai_utils import ask_openai, ask_hr_excel_bot
from utils.dashboard_utils import (
    load_dashboard_data,
    show_dashboard,
    show_employee_details,
    export_dashboard_data,
    export_pdf
)
from docx import Document
from io import BytesIO

# Set page config and logo
st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

st.title("👨‍💼 Ask HR - Capital Partners Group")

# Optional: add middle banner
if os.path.exists("assets/middle_banner_image.png"):
    st.image("assets/middle_banner_image.png", use_column_width=True)

prompt = st.text_input("Ask me anything (salary, leaves, law, etc.):")

# Load Excel data
df = load_dashboard_data()

# Load Policy text
def load_policy():
    doc = Document("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

policy_text = load_policy()

# Determine prompt intent
def is_excel_related(prompt, df):
    prompt = prompt.lower()
    keywords = ["dashboard", "distribution", "count", "how many", "list", "number", "show", "compare", "breakdown"]
    columns = [col.lower() for col in df.columns]
    return any(word in prompt for word in keywords + columns)

# Main logic
if prompt:
    # 1. Excel questions (dashboard/data)
    if is_excel_related(prompt, df):
        st.markdown("📊 **Answer from Excel file:**")
        st.write(ask_hr_excel_bot(df, prompt))

        # Draw dashboard
        show_dashboard(df, prompt)

        # Download data
        filtered_data = export_dashboard_data(df, prompt)
        if not filtered_data.empty:
            # Excel download
            towrite = BytesIO()
            filtered_data.to_excel(towrite, index=False, sheet_name="Dashboard")
            towrite.seek(0)
            st.download_button(
                label="📥 Download Dashboard Data (Excel)",
                data=towrite,
                file_name="dashboard_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # PDF download
            pdf_file = export_pdf(filtered_data)
            st.download_button(
                label="📄 Download Dashboard (PDF)",
                data=pdf_file,
                file_name="dashboard_output.pdf",
                mime="application/pdf"
            )

    # 2. Employee-specific query
    elif any(name.lower() in prompt.lower() for name in df['Full Name'].dropna().unique()):
        st.markdown("👤 **Employee Information:**")
        show_employee_details(df, prompt)

    # 3. Policy questions
    elif any(word in prompt.lower() for word in ["policy", "conduct", "ethics", "harassment", "conflict", "bribery", "discipline"]):
        summary_prompt = f"Summarize the Capital Partners Group policy to answer this question:\n\n{prompt}\n\nPolicy:\n{policy_text}"
        st.markdown("📋 **Answer from Policy:**")
        st.info(ask_openai(summary_prompt))

    # 4. General fallback to OpenAI
    else:
        st.markdown("🤖 **General answer from HR bot:**")
        st.info(ask_openai(prompt))
