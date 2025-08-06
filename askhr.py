
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

# Load data
salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

# UI
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.markdown("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

api_key = st.text_input("Enter your OpenAI API Key:", type="password")
if not api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

ecode_list = salary_df["Ecode"].astype(str).unique()
selected_ecode = st.selectbox("Select your Ecode", ecode_list)
employee_row = salary_df[salary_df["Ecode"].astype(str) == selected_ecode].iloc[0]

pin_input = st.text_input("Enter your 4-digit PIN", type="password")
correct_pin = str(employee_row["PIN"]).zfill(4)

if pin_input != correct_pin:
    st.error("Incorrect PIN")
    st.stop()

employee_name = employee_row["Name"]
user_question = st.text_input("What do you want to ask?")

if user_question:
    messages = [
        {"role": "system", "content": f"You are an HR assistant. Answer based on this HR policy:
{policy_text}"},
        {"role": "user", "content": f"Employee Name: {employee_name}
Ecode: {selected_ecode}
Question: {user_question}"}
    ]

    openai.api_key = api_key
    try:
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            answer = response['choices'][0]['message']['content']
            st.success(answer)
    except Exception as e:
        st.error(str(e))

    if "salary" in user_question.lower():
        st.subheader("Salary Breakdown")
        st.dataframe(salary_df[salary_df["Ecode"].astype(str) == selected_ecode])

    if "vacation" in user_question.lower():
        st.subheader("Vacation Balance")
        st.dataframe(vacation_df[vacation_df["Ecode"].astype(str) == selected_ecode])
