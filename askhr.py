
import streamlit as st
import pandas as pd
from transformers import pipeline

st.set_page_config(page_title="ASK HR", layout="centered")
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.markdown("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

# Load the policy text
@st.cache_data
def load_policy():
    with open("policy.txt", "r", encoding="utf-8") as f:
        return f.read()

# Load salary data
@st.cache_data
def load_salary_data():
    return pd.read_excel("salaries.xlsx")

# Load vacation data
@st.cache_data
def load_vacation_data():
    return pd.read_excel("vacation.xlsx")

# Initialize AI model
@st.cache_resource
def get_bot():
    return pipeline("text-generation", model="tiiuae/falcon-7b-instruct", max_new_tokens=256)

bot = get_bot()

salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

employee_name = st.selectbox("Select your name", salary_df["Name"].unique())

query = st.text_input("What do you want to ask?")

if st.button("Submit") and query:
    context = f"Company HR Policy:
{policy_text}

"
    selected_salary = salary_df[salary_df["Name"] == employee_name]
    if not selected_salary.empty:
        context += f"Salary Info for {employee_name}:
{selected_salary.to_string(index=False)}

"
    selected_vacation = vacation_df[vacation_df["Name"] == employee_name]
    if not selected_vacation.empty:
        context += f"Vacation Info for {employee_name}:
{selected_vacation.to_string(index=False)}

"
    with st.spinner("Thinking..."):
        response = bot(context + query)[0]['generated_text']
        st.markdown("### Response:")
        st.markdown(response)
