import streamlit as st
import pandas as pd
import openai
import base64
import matplotlib.pyplot as plt
from dashboard_module import show_hr_dashboard

# === CONFIG ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === LOAD DATA ===
employee_data = pd.read_excel("PROLOGISTICS.xlsx", sheet_name="FULL TIMERS")
employee_data["Name"] = employee_data["Name"].str.strip().str.lower()
employee_data["ECODE"] = employee_data["ECODE"].str.strip().str.upper()
pin_map = pd.read_csv("Employee_PIN_List.csv")

# === DASHBOARD DATA ===
dashboard_data = pd.read_excel("dashboard_data.xlsx")  # 🔄 renamed for safety

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

# === HEADER ===
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
            if ecode_or_name.upper() in employee_data.ECODE.values:
                user_row = employee_data[employee_data.ECODE == ecode_or_name.upper()]
            elif ecode_or_name in employee_data.Name.values:
                user_row = employee_data[employee_data.Name == ecode_or_name]

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

# === MAIN CHAT ===
if st.session_state.logged_in and st.session_state.user_row is not None:
    user_row = st.session_state.user_row
    name = user_row.iloc[0]['Name'].title()
    prompt = st.text_area("Ask me anything (salary, leaves, law, etc.)")

    if st.button("Ask"):
        response = ""

        # === SALARY ===
        if "salary" in prompt.lower():
            salary = user_row.iloc[0]['Total']
            breakdown = user_row.iloc[0][['BCSA', 'TRANSPORT', 'INCOMETAX', 'Total Ded']]
            response = f"**Salary Breakdown for {name}:**\n\n"
            response += f"Basic: ${breakdown['BCSA']}\nTransport: ${breakdown['TRANSPORT']}\n"
            response += f"Income Tax: ${breakdown['INCOMETAX']}\nDeductions: ${breakdown['Total Ded']}\n"
            response += f"**Net Salary: ${salary}**"

        # === LEAVES ===
        elif "leave" in prompt.lower() or "vacation" in prompt.lower():
            days = user_row.iloc[0]['ANNUAL LEAVES']
            response = f"{name}, you have **{days} days** of annual leave remaining."

        # === SSN ===
        elif "social" in prompt.lower():
            ssn = user_row.iloc[0].get("SOCIAL SECURITY NUMBER", "Not Available")
            if pd.isna(ssn) or str(ssn).strip() == "":
                response = "Your Social Security Number is not available. Please contact HR."
            else:
                response = f"Your Social Security Number is: **{ssn}**"

        # === JOIN DATE ===
        elif "join" in prompt.lower():
            date = user_row.iloc[0]['JOINING DATE']
            response = f"Your joining date is: **{pd.to_datetime(date).strftime('%d %B %Y')}**"

        # === EMOTIONAL SUPPORT ===
        elif any(word in prompt.lower() for word in ["sad", "angry", "depressed", "bad"]):
            response = "I'm here for you. 🌈 Take a break, drink water, talk to someone you trust. You matter. 💖"

        # === JOKE ===
        elif any(word in prompt.lower() for word in ["joke", "funny"]):
            response = "Why did the HR manager sit at their desk all day? Because they couldn't *stand* anymore meetings! 😄"

        # === DASHBOARD QUESTIONS ===
        elif any(word in prompt.lower() for word in ["dashboard", "age", "grade", "band", "gender", "company", "title", "nationality"]):
            show_hr_dashboard(dashboard_data, prompt.lower())
            response = ""  # Handled by the dashboard module

        # === POLICY HANDLING ===
        elif any(word in prompt.lower() for word in ["policy", "ethics", "code", "conduct", "behavior", "dress code", "conflict of interest", "harassment", "compliance"]):
            try:
                with open("Capital_Partners_Code_of_Conduct.txt", "r", encoding="utf-8") as file:
                    policy_text = file.read()

                openai_response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an HR assistant. Use only the Capital Partners Group policy provided. Do not use external laws or content."},
                        {"role": "user", "content": f"According to our company policy: {policy_text[:3000]}\n\nUser question: {prompt}"}
                    ]
                )
                response = openai_response.choices[0].message.content
            except Exception:
                response = "Policy file not found or can't be read."

        # === OPENAI GENERAL HANDLER ===
        else:
            try:
                openai_response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a professional Lebanese HR assistant. Reply in Arabic if asked in Arabic, otherwise English."},
                        {"role": "user", "content": prompt}
                    ]
                )
                response = openai_response.choices[0].message.content
            except Exception as e:
                response = "Unable to connect to OpenAI. Please try again later."

        st.markdown(response)
