
import streamlit as st
import pandas as pd
from transformers import pipeline
import torch

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

@st.cache_resource
def get_bot():
    return pipeline("text-generation", model="distilgpt2", max_new_tokens=100)

st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.write("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

employee_name = st.selectbox("Select your name", salary_df["Name"].unique())
user_question = st.text_input("What do you want to ask?")

bot = get_bot()

if user_question:
    context = "You are an HR assistant. Answer based on this:\n"

    selected_salary = salary_df[salary_df["Name"] == employee_name]
    if not selected_salary.empty:
        context += f"Salary Info for {employee_name}: {selected_salary.to_dict(orient='records')[0]}\n"

    selected_vacation = vacation_df[vacation_df["Name"] == employee_name]
    if not selected_vacation.empty:
        context += f"Vacation Info for {employee_name}: {selected_vacation.to_dict(orient='records')[0]}\n"

    context += f"Policy Info: {policy_text}\n"

    response = bot(f"{context}\n{user_question}")
    st.write("**Answer:**", response[0]['generated_text'])
