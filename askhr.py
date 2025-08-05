import streamlit as st
import pandas as pd
import google.generativeai as genai

# Load the policy
def load_policy():
    with open("policy.txt", "r", encoding="utf-8") as f:
        return f.read()

# Load salary data
@st.cache_data
def load_salary_data():
    return pd.read_excel("salaries.xlsx")

# Load vacation balance
@st.cache_data
def load_vacation_data():
    return pd.read_excel("vacation.xlsx")

# UI
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.write("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

# Gemini API
api_key = st.text_input("Enter your Gemini API Key:", type="password")
if not api_key:
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

# Load data
salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

# Employee selector
selected_employee = st.selectbox("Select your name", salary_df["Employee Name"].unique())
user_question = st.text_input("What do you want to ask?")

if st.button("Ask"):
    if not user_question:
        st.warning("Please enter your question.")
    else:
        context = f"You are an HR assistant. Answer based on this policy:\n{policy_text}\n\n"
        emp_salary = salary_df[salary_df["Employee Name"] == selected_employee]
        emp_vacation = vacation_df[vacation_df["Employee Name"] == selected_employee]

        if not emp_salary.empty:
            context += f"\nSalary Info for {selected_employee}:\n{emp_salary.to_string(index=False)}"

        if not emp_vacation.empty:
            context += f"\nVacation Info for {selected_employee}:\n{emp_vacation.to_string(index=False)}"

        try:
            response = model.generate_content([context, user_question])
            st.markdown("### Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
