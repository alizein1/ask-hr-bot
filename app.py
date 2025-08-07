import streamlit as st
import pandas as pd
from utils.openai_utils import ask_openai, ask_hr_excel_bot
from utils.dashboard_utils import (
    load_dashboard_data,
    show_dashboard,
    show_employee_details,
    export_dashboard_data
)
from docx import Document
import os
from io import BytesIO

st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

if os.path.exists("assets/middle_banner_image.png"):
    st.image("assets/middle_banner_image.png", use_column_width=True)

st.title("👨‍💼 Ask HR - Capital Partners Group")
prompt = st.text_input("Ask me anything (salary, leaves, law, etc.):")

df = load_dashboard_data()

def load_policy():
    doc = Document("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

policy_text = load_policy()

def is_excel_related(prompt, df):
    prompt = prompt.lower()
    keywords = ["dashboard", "distribution", "count", "how many", "list", "number", "show", "compare", "breakdown"]
    columns = [col.lower() for col in df.columns]
    return any(word in prompt for word in keywords + columns)

if prompt:
    if is_excel_related(prompt, df):
        st.markdown("📊 **Answer from Excel file:**")
        st.write(ask_hr_excel_bot(df, prompt))
        show_employee_details(df, prompt)
        show_dashboard(df, prompt)

        # Excel download
        filtered_data = export_dashboard_data(df, prompt)
        if not filtered_data.empty:
            towrite = BytesIO()
            filtered_data.to_excel(towrite, index=False, sheet_name="Dashboard")
            towrite.seek(0)
            st.download_button(
                label="📥 Download Dashboard Data (Excel)",
                data=towrite,
                file_name="dashboard_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif any(word in prompt.lower() for word in ["policy", "conduct", "ethics", "harassment", "conflict", "bribery", "discipline"]):
        summary_prompt = f"Summarize the Capital Partners Group policy to answer this question:\n\n{prompt}\n\nPolicy:\n{policy_text}"
        st.markdown("📋 **Answer from Policy:**")
        st.info(ask_openai(summary_prompt))
    else:
        st.markdown("🤖 **General answer from HR bot:**")
        st.info(ask_openai(prompt))
