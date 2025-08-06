import streamlit as st
import pandas as pd
import openai

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

def authenticate_user(ecode, pin, df):
    user = df[df["Ecode"] == ecode]
    if not user.empty and str(user["PIN"].values[0]).zfill(4) == pin:
        return user.iloc[0]["Name"]
    return None

salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.markdown("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
if not openai_api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

ecode = st.text_input("Enter your Ecode:")
pin = st.text_input("Enter your 4-digit PIN:", type="password", max_chars=4)

if not ecode or not pin:
    st.stop()

employee_name = authenticate_user(ecode, pin, salary_df)
if not employee_name:
    st.error("Invalid Ecode or PIN.")
    st.stop()

st.success(f"Welcome {employee_name}!")

user_question = st.text_input("What do you want to ask?")

if user_question:
    openai.api_key = openai_api_key

    context = [
        {"role": "system", "content": f"You are an HR assistant. Answer based on this HR policy:
{policy_text}"},
        {"role": "user", "content": f"Employee {employee_name} asked: {user_question}"}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context
        )
        answer = response.choices[0].message.content
        st.write(answer)
    except Exception as e:
        st.error(f"Error: {str(e)}")

    if "salary" in user_question.lower():
        selected_salary = salary_df[salary_df["Ecode"] == ecode]
        if not selected_salary.empty:
            st.subheader("Your Salary Breakdown:")
            st.dataframe(selected_salary)

    if "vacation" in user_question.lower():
        selected_vacation = vacation_df[vacation_df["Ecode"] == ecode]
        if not selected_vacation.empty:
            st.subheader("Your Vacation Details:")
            st.dataframe(selected_vacation)
