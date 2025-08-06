import streamlit as st
import pandas as pd
import openai
import base64
from datetime import datetime

# === CONFIG ===
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Add your key to Streamlit Secrets

# === LOAD DATA ===
data = pd.read_excel("PROLOGISTICS.xlsx", sheet_name="FULL TIMERS")
data["Name"] = data["Name"].str.strip().str.lower()
data["ECODE"] = data["ECODE"].str.strip().str.upper()
pin_map = pd.read_csv("Employee_PIN_List.csv")

# === PAGE CONFIG ===
st.set_page_config(page_title="Ask HR - Capital Partners", layout="wide")

# === BACKGROUND STYLING ===
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
    encoded = base64.b64encode(img_bytes).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url('data:image/jpeg;base64,{encoded}');
            background-size: cover;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("CP Letter Head.jpg")

# === HR TEAM HEADER ===
try:
    st.image("HRTEAM.jpg", width=300)
except Exception:
    st.warning("HR team image not found or unreadable.")
st.markdown("# 👨‍💼 Ask HR")

# === LOGIN ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("Employee Login")
        ecode_or_name = st.text_input("Enter ECODE or Name").strip().lower()
        pin_input = st.text_input("Enter your 3-digit PIN", max_chars=3)
        submitted = st.form_submit_button("Login")

    if submitted:
        user_row = None
        try:
            if ecode_or_name.upper() in data.ECODE.values:
                user_row = data[data.ECODE == ecode_or_name.upper()]
            elif ecode_or_name in data.Name.values:
                user_row = data[data.Name == ecode_or_name]

            if user_row is not None and not user_row.empty:
                user_ecode = user_row.iloc[0]["ECODE"]
                pin_match = pin_map[(pin_map["ECODE"] == user_ecode) & (pin_map["PIN"] == int(pin_input))]
                if not pin_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_row = user_row
                    st.experimental_rerun()
                else:
                    st.error("Invalid PIN.")
            else:
                st.error("ECODE or Name not found.")

        except Exception:
            st.error("Login failed. Please try again.")

# === MAIN INTERFACE ===
if st.session_state.logged_in:
    user_row = st.session_state.user_row
    name = user_row.iloc[0]['Name'].title()
    prompt = st.text_area("Ask me anything (salary, leaves, law, etc.)")

    if st.button("Ask"):
        response = ""

        if "salary" in prompt.lower():
            salary = user_row.iloc[0]['Total']
            breakdown = user_row.iloc[0][['BCSA', 'TRANSPORT', 'INCOMETAX', 'Total Ded']]
            response = f"\n**Salary Breakdown for {name}:**\n\nBasic: ${breakdown['BCSA']}\n\nTransport: ${breakdown['TRANSPORT']}\n\nIncome Tax: ${breakdow
