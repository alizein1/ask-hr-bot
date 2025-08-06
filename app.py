
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import base64

# === CONFIG ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === DATA ===
data = pd.read_excel("PROLOGISTICS.xlsx", sheet_name="FULL TIMERS")
pin_map = pd.read_csv("Employee_PIN_List.csv")
dashboard_data = pd.read_csv("cleaned_mass_file.csv")
dashboard_data["Age Group"] = pd.cut(dashboard_data["Age"], bins=[0, 25, 35, 45, 55, 65, 100], labels=["<25", "25-35", "36-45", "46-55", "56-65", "65+"])

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

# === HEADER IMAGE ===
try:
    st.image("ChatGPT Image Aug 6, 2025, 05_15_34 PM.png", width=200)
except:
    st.warning("Header image not found.")

st.markdown("# 👨‍💼 Ask HR")

# === SESSION STATE ===
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
        user_row = None
        if ecode_or_name.upper() in data.ECODE.values:
            user_row = data[data.ECODE == ecode_or_name.upper()]
        elif ecode_or_name in data.Name.str.lower().values:
            user_row = data[data.Name.str.lower() == ecode_or_name]

        if user_row is not None and not user_row.empty:
            ecode = user_row.iloc[0]["ECODE"]
            try:
                pin_match = pin_map[(pin_map["ECODE"] == ecode) & (pin_map["PIN"] == int(pin_input))]
                if not pin_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_row = user_row
                    st.success("Access granted. How can I help you today?")
                else:
                    st.error("Invalid PIN.")
            except:
                st.error("Invalid PIN format.")
        else:
            st.error("Invalid ECODE or Name.")

# === HR CHATBOT + DASHBOARD ===
if st.session_state.logged_in and st.session_state.user_row is not None:
    user_row = st.session_state.user_row
    name = user_row.iloc[0]['Name'].title()
    prompt = st.text_area("Ask me anything (salary, leaves, law, etc.)")

    if st.button("Ask"):
        response = ""

        if "salary" in prompt.lower():
            salary = user_row.iloc[0]['Total']
            breakdown = user_row.iloc[0][['BCSA', 'TRANSPORT', 'INCOMETAX', 'Total Ded']]
            response = f"**Salary Breakdown for {name}:**\n\nBasic: ${breakdown['BCSA']}\nTransport: ${breakdown['TRANSPORT']}\nIncome Tax: ${breakdown['INCOMETAX']}\nDeductions: ${breakdown['Total Ded']}\n\n**Net Salary: ${salary}**"

        elif "leave" in prompt.lower() or "vacation" in prompt.lower():
            days = user_row.iloc[0]['ANNUAL LEAVES']
            response = f"{name}, you have **{days} days** of annual leave remaining."

        elif "social" in prompt.lower():
            ssn = user_row.iloc[0].get("Social Security Number", "Not Available")
            response = f"Your Social Security Number is: **{ssn}**" if pd.notna(ssn) else "Your Social Security Number is not available. Please contact HR."

        elif "join" in prompt.lower():
            date = user_row.iloc[0]['JOINING DATE']
            response = f"Your joining date is: **{pd.to_datetime(date).strftime('%d %B %Y')}**"

        elif any(word in prompt.lower() for word in ["sad", "angry", "depressed", "bad"]):
            response = "I'm here for you. 🌈 Take a break, drink water, talk to someone you trust. You matter. 💖"

        elif any(word in prompt.lower() for word in ["joke", "funny"]):
            response = "Why did the HR manager sit at their desk all day? Because they couldn't *stand* anymore meetings! 😄"

        elif any(word in prompt.lower() for word in ["dashboard", "age", "grade", "band", "gender", "company", "title", "nationality"]):
            st.subheader("📊 HR Insights Dashboard")
            def chart(title, series):
                fig, ax = plt.subplots()
                series.value_counts().sort_index().plot(kind="bar", ax=ax)
                ax.set_title(title)
                st.pyplot(fig)

            chart("Age Groups", dashboard_data["Age Group"])
            chart("Nationalities", dashboard_data["Nationality"])
            chart("Gender", dashboard_data["Gender"])
            chart("Band", dashboard_data["Band"])
            chart("Grade", dashboard_data["Grade"])
            chart("Job Titles", dashboard_data["Job Title"])
            chart("Companies", dashboard_data["Entity"])
            response = "**Above are your requested HR insights.**"

        else:
            try:
                openai_response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You're a helpful Lebanese HR assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                response = openai_response.choices[0].message.content
            except:
                response = "Unable to connect to OpenAI. Please try again later."

        st.markdown(response)
