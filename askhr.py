
import streamlit as st
import pandas as pd
import google.generativeai as genai

# Page setup
st.set_page_config(page_title="ASK HR - Tawfeer", layout="centered")
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.markdown("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

# Gemini API Key
api_key = st.text_input("Enter your Gemini API Key:", type="password")
if not api_key:
    st.stop()

genai.configure(api_key=api_key)

# Load files
@st.cache_data
def load_salary_data():
    return pd.read_excel("salaries.xlsx")

@st.cache_data
def load_vacation_data():
    return pd.read_excel("vacation.xlsx")

@st.cache_data
def load_policy_text():
    with open("Capital_Partners_Code_of_Conduct.txt", "r", encoding="utf-8") as file:
        return file.read()

# Load data
salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy_text()

# Employee name selection
employee_names = salary_df['Employee Name'].dropna().unique().tolist()
selected_employee = st.selectbox("Select your name", employee_names)

# Question input
user_question = st.text_input("What do you want to ask?")

if user_question and selected_employee:
    model = genai.GenerativeModel("gemini-pro")

    # Build context from policy + employee salary/vacation data
    context = "You are an HR assistant. Answer based on this:
"
    context += f"

HR Policy:
{policy_text}"

    emp_salary_info = salary_df[salary_df['Employee Name'] == selected_employee]
    emp_vacation_info = vacation_df[vacation_df['Employee Name'] == selected_employee]

    if not emp_salary_info.empty:
        context += f"

Salary Info for {selected_employee}:
{emp_salary_info.to_string(index=False)}"
    if not emp_vacation_info.empty:
        context += f"

Vacation Balance for {selected_employee}:
{emp_vacation_info.to_string(index=False)}"

    try:
        response = model.generate_content([context, user_question])
        st.markdown("### Answer:")
        st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
