import streamlit as st
import pandas as pd
import os
from utils.openai_utils import ask_openai, ask_hr_excel_bot
from utils.dashboard_utils import load_dashboard_data, show_dashboard
from docx import Document

st.set_page_config(page_title="Ask HR - Capital Partners Group", layout="wide")

# Logo and Banner
if os.path.exists("assets/logo.png"):
    try:
        st.image("assets/logo.png", width=150)
    except Exception as e:
        st.warning(f"Logo error: {e}")

st.title("\U0001F468\u200D\U0001F4BC Ask HR - Capital Partners Group")

if os.path.exists("assets/middle_banner_image.png"):
    try:
        st.image("assets/middle_banner_image.png", width=600)
    except Exception as e:
        st.warning(f"Banner error: {e}")

# Prompt input
prompt = st.text_input("Ask me anything (salary, leaves, law, etc.):")

# Load Data
try:
    df = load_dashboard_data()
    st.success("Data loaded successfully.")
except Exception as e:
    st.error(f"Failed to load Excel data: {e}")
    st.stop()

# Load Policy
def load_policy():
    try:
        doc = Document("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        return f"Error loading policy: {e}"

policy_text = load_policy()

# Check if prompt relates to Excel

def is_excel_related(prompt, df):
    prompt = prompt.lower()
    keywords = ["dashboard", "distribution", "count", "how many", "list", "number", "show", "compare", "breakdown"]
    columns = [col.lower() for col in df.columns]
    return any(word in prompt for word in keywords + columns)

# Process Prompt
if prompt:
    if is_excel_related(prompt, df):
        st.markdown("\U0001F4CA **Answer from Excel file:**")
        try:
            st.write(ask_hr_excel_bot(df, prompt))
            show_dashboard(df, prompt)
        except Exception as e:
            st.error(f"Excel handling error: {e}")
    elif any(word in prompt.lower() for word in ["policy", "conduct", "ethics", "harassment", "conflict", "bribery", "discipline"]):
        st.markdown("\U0001F4CB **Answer from Policy:**")
        try:
            summary_prompt = f"Summarize the Capital Partners Group policy to answer this question:\n\n{prompt}\n\nPolicy:\n{policy_text}"
            st.info(ask_openai(summary_prompt))
        except Exception as e:
            st.error(f"Policy AI error: {e}")
    else:
        st.markdown("\U0001F916 **General answer from HR bot:**")
        try:
            st.info(ask_openai(prompt))
        except Exception as e:
            st.error(f"OpenAI error: {e}")
