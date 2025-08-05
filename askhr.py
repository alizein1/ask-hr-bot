import streamlit as st
import pandas as pd
from transformers import pipeline

@st.cache_data
def load_salary_data():
    return pd.read_excel("salaries.xlsx")

@st.cache_data
def load_vacation_data():
    return pd.read_excel("vacation.xlsx")

@st.cache_data
def load_policy():
    with open("policy.txt", "r", encoding="utf-8") as f:
        return f.read()

# Load data
salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

# Title
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.markdown("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

# Select employee
employee_name = st.selectbox("Select your name", salary_df["Name"].unique())

# Ask a question
user_question = st.text_input("What do you want to ask?")

# Load Hugging Face model
@st.cache_resource
def get_bot():
    return pipeline("text-generation", model="tiiuae/falcon-7b-instruct", max_new_tokens=256)

bot = get_bot()

if user_question and employee_name:
    # Filter data
    emp_salary = salary_df[salary_df["Name"] == employee_name].to_dict(orient="records")[0]
    emp_vac = vacation_df[vacation_df["Name"] == employee_name].to_dict(orient="records")[0]

    # Context preparation
    context = f"You are an HR assistant. Answer based on this policy:\n{policy_text}\n"
    context += f"\nSalary Info for {employee_name}: {emp_salary}\n"
    context += f"\nVacation Info for {employee_name}: {emp_vac}\n"

    # Generate response
    with st.spinner("Thinking..."):
        result = bot(f"{context}\nQuestion: {user_question}")
        st.write(result[0]['generated_text'].split('Question:')[-1].strip())