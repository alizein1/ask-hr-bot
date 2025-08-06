import streamlit as st
import pandas as pd
import openai
import base64
from datetime import datetime

# === CONFIG ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === LOAD DATA ===
data = pd.read_excel("PROLOGISTICS.xlsx", sheet_name="FULL TIMERS")
data["Name"] = data["Name"].str.strip().str.lower()
data["ECODE"] = data["ECODE"].str.strip().str.upper()
pin_map = pd.read_csv("Employee_PIN_List.csv")

# === PAGE CONFIG ===
st.set_page_config(page_title="Ask HR - Capital Partners", layout="wide")

# === BACKGROUND IMAGE ===
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/jpeg;base64,{encoded}');
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

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
if "user_row" not in st.session_state:
    st.session_state.user_row = None

# === LOGIN ===
if not st.session_state.logged_in:
    with st.form("login_form"):
        st.subheader("Employee Login")
        ecode_or_name = st.text_input("Enter ECODE or Name").strip().lower()
        pin_input = st.text_input("Enter your 3-digit PIN", max_chars=3)
        submitted = st.form_submit_button("Login")

    if submitted:
        try:
            user_row = None
            if ecode_or_name.upper() in data.ECODE.values:
                user_row = data[data.ECODE == ecode_or_name.upper()]
            elif ecode_or_name in data.Name.values:
                user_row = data[data.Name == ecode_or_name]

            if user_row is not None and not user_row.empty:
                ecode = user_row.iloc[0]["ECODE"]
                pin_match = pin_map[(pin_map["ECODE"] == ecode) & (pin_map["PIN"] == int(pin_input))]
                if not pin_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_row = user_row
                    st.success("Access granted. How can I help you today?")
                else:
                    st.error("Invalid PIN.")
            else:
                st.error("Invalid ECODE or Name.")
        except Exception:
            st.error("Login failed. Please try again.")

# === MAIN BOT ===
if st.session_state.logged_in and st.session_state.user_row is not None:
    user_row = st.session_state.user_row
    name = user_row.iloc[0]['Name'].title()
    prompt = st.text_area("Ask me anything (salary, leaves, law, etc.)")

    if st.button("Ask"):
        response = ""

        if "salary" in prompt.lower():
            breakdown = user_row.iloc[0][['BCSA', 'TRANSPORT', 'INCOMETAX', 'Total Ded']]
            salary = user_row.iloc[0]['Total']
            salary_df = pd.DataFrame({
                "Component": ['Basic', 'Transport', 'Income Tax', 'Total Deductions', 'Net Salary'],
                "Amount": [
                    breakdown['BCSA'],
                    breakdown['TRANSPORT'],
                    breakdown['INCOMETAX'],
                    breakdown['Total Ded'],
                    salary
                ]
            })
            st.markdown(f"**Salary Breakdown for {name}:**")
            st.table(salary_df)

        elif "leave" in prompt.lower() or "vacation" in prompt.lower():
            days = user_row.iloc[0]['ANNUAL LEAVES']
            response = f"{name}, you have **{days} days** of annual leave remaining."
            st.markdown(response)

        elif "social" in prompt.lower():
            ssn = user_row.iloc[0].get("SOCIAL SECURITY NUMBER", "Not Available")
            response = f"Your Social Security Number is: **{ssn}**" if pd.notna(ssn) else "Your Social Security Number is not available. Please contact HR."
            st.markdown(response)

        elif "join" in prompt.lower():
            date = user_row.iloc[0]['JOINING DATE']
            response = f"Your joining date is: **{pd.to_datetime(date).strftime('%d %B %Y')}**"
            st.markdown(response)

        elif any(word in prompt.lower() for word in ["sad", "angry", "depressed", "bad"]):
            st.markdown("I'm here for you. 🌈 Take a break, drink water, talk to someone you trust. You matter. 💖")

        elif any(word in prompt.lower() for word in ["joke", "funny"]):
            st.markdown("Why did the HR manager sit at their desk all day? Because they couldn't *stand* anymore meetings! 😄")

        elif any(word in prompt.lower() for word in ["quote", "motivation", "hr quote"]):
            st.image("1753186824732.jpg", use_column_width=True)
            st.image("1753858092673.jpg", use_column_width=True)

        else:
            try:
                openai_response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a professional Lebanese HR assistant. Respond in Arabic if question is Arabic, otherwise English."},
                        {"role": "user", "content": prompt}
                    ]
                )
                response = openai_response.choices[0].message.content
                st.markdown(response)
            except:
                st.error("Unable to connect to OpenAI. Please try again later.")
