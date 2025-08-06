import streamlit as st
import pandas as pd
from utils.openai_utils import ask_openai
from utils.dashboard_utils import load_dashboard_data, show_dashboard
from docx import Document

# Load logo
st.image("assets/logo.png", width=150)

st.title("👨‍💼 Ask HR - Capital Partners Group")

prompt = st.text_input("Ask me anything (salary, leaves, law, etc.):")

# Load Excel Data
df = load_dashboard_data()

# Load Policy
def load_policy():
    doc = Document("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

policy_text = load_policy()

# Handle Question
if prompt:
    if any(word in prompt.lower() for word in ["age", "nationality", "gender", "job title", "grade", "band", "company"]):
        show_dashboard(df, prompt.lower())
    elif any(word in prompt.lower() for word in ["policy", "conduct", "ethics", "harassment", "conflict"]):
        summary_prompt = f"Summarize relevant policy to answer this HR question:\n\n{prompt}\n\nPolicy:\n{policy_text}"
        st.info(ask_openai(summary_prompt))
    else:
        st.info(ask_openai(prompt))
