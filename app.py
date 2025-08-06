
import streamlit as st
import pandas as pd
from utils.openai_utils import ask_openai, ask_hr_excel_bot
from utils.dashboard_utils import load_dashboard_data, show_dashboard, show_employee_details
from docx import Document
import os

st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=150)

st.title("\U0001F468\u200D\U0001F4BC Ask HR - Capital Partners Group")
st.image("assets/middle_banner_image.png", width=600)

prompt = st.text_input("Ask me anything (salary, leaves, law, etc.):")

df = load_dashboard_data()

def load_policy():
    doc = Document("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

policy_text = load_policy()

def is_excel_related(prompt, df):
    prompt = prompt.lower()
    keywords = ["dashboard", "distribution", "count", "how many", "list", "number", "show", "compare", "breakdown", "employees", "titles", "grades", "genders", "nationalities", "bands"]
    columns = [col.lower() for col in df.columns]
    return any(word in prompt for word in keywords + columns)

def is_employee_lookup(prompt, df):
    return any(name.lower() in prompt.lower() for name in df['Full Name'].dropna())

if prompt:
    if is_employee_lookup(prompt, df):
        st.markdown("👤 **Employee Record:**")
        show_employee_details(df, prompt)
    elif is_excel_related(prompt, df):
        st.markdown("\U0001F4CA **Answer from Excel file:**")
        st.write(ask_hr_excel_bot(df, prompt))
        show_dashboard(df, prompt)
    elif any(word in prompt.lower() for word in ["policy", "conduct", "ethics", "harassment", "conflict", "bribery", "discipline"]):
        summary_prompt = f"Summarize the Capital Partners Group policy to answer this question:\n\n{prompt}\n\nPolicy:\n{policy_text}"
        st.markdown("\U0001F4CB **Answer from Policy:**")
        st.info(ask_openai(summary_prompt))
    else:
        st.markdown("\U0001F916 **General answer from HR bot:**")
        st.info(ask_openai(prompt))
