import streamlit as st
import pandas as pd
import openai

# Load policy text from file
@st.cache_data
def load_policy():
    with open("Capital_Partners_Code_of_Conduct.txt", "r", encoding="utf-8") as f:
        return f.read()

# Load salary data
@st.cache_data
def load_salary_data():
    return pd.read_excel("salaries.xlsx")

# Load vacation data
@st.cache_data
def load_vacation_data():
    return pd.read_excel("vacation.xlsx")

# Initialize page
st.set_page_config(page_title="ASK HR", page_icon="💼")
st.title("ASK HR")
st.subheader("HR Department - Tawfeer")
st.write("Hello 👋 I’m AskHR, your smart assistant for quick HR help. Ask me anything!")

# Get OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
if not openai_api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

openai.api_key = openai_api_key

# Load data
policy_text = load_policy()
salary_df = load_salary_data()
vacation_df = load_vacation_data()

# Select employee
employee_name = st.selectbox("Select your name", salary_df["Name"].unique())

# Ask question
user_question = st.text_input("What do you want to ask?")

if user_question and employee_name:
    # Extract employee data
    selected_salary = salary_df[salary_df["Name"] == employee_name]
    selected_vacation = vacation_df[vacation_df["Name"] == employee_name]

    salary_info = selected_salary.to_string(index=False)
    vacation_info = selected_vacation.to_string(index=False)

    context = f"""
You are an HR assistant. Answer the employee's question using the policy and their personal data below.

Company HR Policy:
{policy_text}

Employee Salary Details:
{salary_info}

Employee Vacation Details:
{vacation_info}

Now answer the following question clearly and professionally in English or Arabic, depending on how the question was asked:
"""

    with st.spinner("Thinking..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_question},
            ]
        )
        st.markdown("**Response:**")
        st.success(response.choices[0].message["content"])