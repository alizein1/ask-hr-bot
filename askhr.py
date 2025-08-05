import streamlit as st
import pandas as pd
from transformers import pipeline

# Load data
@st.cache_data
def load_salary_data():
    return pd.read_excel("salaries.xlsx")

@st.cache_data
def load_vacation_data():
    return pd.read_excel("vacation.xlsx")

@st.cache_data
def load_policy():
    with open("Capital_Partners_Code_of_Conduct.txt", "r", encoding="utf-8") as f:
        return f.read()

@st.cache_resource
def get_bot():
    return pipeline("text-generation", model="tiiuae/falcon-7b-instruct", max_new_tokens=256)

# Main app
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.write("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

employee_name = st.selectbox("Select your name", salary_df["Name"].unique())

user_question = st.text_input("What do you want to ask?")

if user_question:
    # Extract employee-specific data
    selected_salary = salary_df[salary_df["Name"] == employee_name]
    selected_vacation = vacation_df[vacation_df["Name"] == employee_name]

    salary_info = selected_salary.to_string(index=False)
    vacation_info = selected_vacation.to_string(index=False)

    context = f"""Company HR Policy:
{policy_text}

Salary Info for {employee_name}:
{salary_info}

Vacation Info for {employee_name}:
{vacation_info}
"""

    bot = get_bot()
    with st.spinner("Thinking..."):
        response = bot(context + "\nUser: " + user_question)[0]['generated_text']
        response = response.split("User:")[-1].strip()
        st.success(response)