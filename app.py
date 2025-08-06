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

# === SESSION INIT ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# === LOGIN FORM ===
if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("Employee Login")
        ecode_or_name = st.text_input("Enter ECODE or Name").strip().lower()
        pin_input = st.text_input("Enter your 3-digit PIN", max_chars=3)
        submitted = st.form_submit_button("Login")

    user_row = None
    if submitted:
        try:
            if ecode_or_name.upper() in data.ECODE.values:
                user_row = data[data.ECODE == ecode_or_name.upper()]
            elif ecode_or_name in data.Name.values:
                user_row = data[data.Name == ecode_or_name]

            pin_match = pin_map[
                (pin_map["ECODE"] == user_row.iloc[0]["ECODE"]) &
                (pin_map["PIN"] == int(pin_input))
            ]

            if user_row is not None and not pin_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_row = user_row
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Please check your ECODE/Name and PIN.")
        except Exception as e:
            st.error("Login failed. Please double-check your details.")

# === MAIN INTERFACE ===
if st.session_state.logged_in:
    user_row = st.session_state.user_row
    name = user_row.iloc[0]['Name'].title()
    user_code = user_row.iloc[0]['ECODE']

    prompt = st.text_area("Ask me anything (salary, leaves, law, etc.)")
    if st.button("Ask"):
        response = ""

        if "salary" in prompt.lower():
            salary = user_row.iloc[0]['Total']
            breakdown = user_row.iloc[0][['BCSA', 'TRANSPORT', 'INCOMETAX', 'Total Ded']]
            response = f"\n**Salary Breakdown for {name}:**\n\nBasic: ${breakdown['BCSA']}\n\nTransport: ${breakdown['TRANSPORT']}\n\nIncome Tax: ${breakdown['INCOMETAX']}\n\nTotal Deductions: ${breakdown['Total Ded']}\n\n**Net Salary: ${salary}**"

        elif "leave" in prompt.lower() or "vacation" in prompt.lower():
            days = user_row.iloc[0]['ANNUAL LEAVES']
            response = f"{name}, you have **{days} days** of annual leave remaining."

        elif "social" in prompt.lower():
            ssn = user_row.iloc[0]['Social Security Number']
            response = f"Your Social Security Number is: **{ssn}**"

        elif "join" in prompt.lower():
            date = user_row.iloc[0]['JOINING DATE']
            response = f"Your joining date is: **{pd.to_datetime(date).strftime('%d %B %Y')}**"

        elif any(word in prompt.lower() for word in ["sad", "angry", "depressed", "bad"]):
            response = "I'm here for you. Sometimes, talking to someone or taking a short walk can help. If you're feeling overwhelmed, don't hesitate to reach out to our HR team confidentially. You matter. 💖"

        elif any(word in prompt.lower() for word in ["joke", "funny"]):
            response = "Why did the HR manager bring a ladder to work? Because they were going for a raise! 🌟"

               else:
            from openai import OpenAI
            client = OpenAI()

            chat_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're a bilingual HR assistant for a Lebanese company. Be helpful and reply in Arabic if asked in Arabic, otherwise use English."},
                    {"role": "user", "content": prompt}
                ]
            )
            response = chat_response.choices[0].message.content



        st.markdown(response)
