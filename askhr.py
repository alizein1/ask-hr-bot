
import streamlit as st
import openai
import pandas as pd

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

salary_df = load_salary_data()
vacation_df = load_vacation_data()
policy_text = load_policy()

st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.markdown("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if not api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

openai.api_key = api_key

employee_name = st.selectbox("Select your name", salary_df["Name"].unique())

user_question = st.text_input("What do you want to ask?")

if user_question:
    with st.spinner("Thinking..."):
        context = f"""
You are an HR assistant bot. Below is the HR policy and employee data. Use it to answer user questions in a clear and helpful way.

Company HR Policy:
{policy_text}

Employee Salary Info:
{salary_df[salary_df["Name"] == employee_name].to_string(index=False)}

Employee Vacation Info:
{vacation_df[vacation_df["Name"] == employee_name].to_string(index=False)}

Question: {user_question}
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": context}],
                max_tokens=500
            )
            st.success(response.choices[0].message.content.strip())
        except Exception as e:
            st.error(f"Error: {e}")
