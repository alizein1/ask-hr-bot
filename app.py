# Ask HR - Streamlit App for Capital Partners Group
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
import docx
import plotly.express as px

# Load files
@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

def load_policy():
    doc = docx.Document("02 Capital Partners Group Code of Conducts and Business Ethics Policy.docx")
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
    return full_text

# Authenticate login
def authenticate(ecode, pin, pin_df):
    pin_df["PIN"] = pin_df["PIN"].astype(str)
    match = pin_df[(pin_df["ECODE"] == ecode) & (pin_df["PIN"] == pin)]
    return not match.empty

# Download utility
def download_dataframe(df, filetype="excel"):
    output = BytesIO()
    if filetype == "excel":
        df.to_excel(output, index=False)
        ext = "xlsx"
    else:
        df.to_csv(output, index=False)
        ext = "csv"
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:file/{ext};base64,{b64}" download="employee_data.{ext}">📥 Download {ext.upper()}</a>'
    return href

# Analysis dashboard
def show_dashboard(df):
    st.subheader("🔍 HR Data Insights")
    tabs = st.tabs(["Nationalities", "Declared", "Overtime", "Join Dates"])

    with tabs[0]:
        if "Nationality" in df.columns:
            fig = px.histogram(df, x="Nationality", title="Employee Nationalities")
            st.plotly_chart(fig)

    with tabs[1]:
        if "SOCIAL SECURITY NUMBER" in df.columns:
            declared = df["SOCIAL SECURITY NUMBER"].notna().sum()
            st.metric("Declared Employees", declared)

    with tabs[2]:
        if "OVERTIME" in df.columns:
            fig = px.histogram(df, x="OVERTIME", title="Overtime Distribution")
            st.plotly_chart(fig)

    with tabs[3]:
        if "JOINING DATE" in df.columns:
            df["JOINING DATE"] = pd.to_datetime(df["JOINING DATE"], errors='coerce')
            join_counts = df["JOINING DATE"].dt.year.value_counts().sort_index()
            st.bar_chart(join_counts)

# Policy Q&A
def search_policy(policy_text, query):
    results = [line for line in policy_text.split("\n") if query.lower() in line.lower()]
    return "\n".join(results) if results else "No relevant section found."

# General HR Q&A
def general_answers(question):
    hr_faq = {
        "leave": "To apply for leave, send your request to your line manager and CC HR.",
        "salary slip": "Your salary slip is issued monthly. Contact HR if not received.",
        "insurance": "Medical insurance covers hospitalization & emergency. For details, email HR."
    }
    for keyword, answer in hr_faq.items():
        if keyword in question.lower():
            return answer
    return "I'll forward this to the HR team."

# Main app
def main():
    st.set_page_config(page_title="Ask HR", layout="wide")
    st.image("logo.png", width=150)
st.image("middle_banner_image.png", width=600)
    st.title("🤖 Ask HR - Capital Partners Group")

    df, pin_df = load_data()
    policy_text = load_policy()

    ecode = st.text_input("Enter your ECODE")
    pin = st.text_input("Enter your 3-digit PIN", type="password")

    if st.button("Login"):
        if authenticate(ecode, pin, pin_df):
            st.success("Logged in successfully ✅")

            emp_data = df[df["ECODE"] == ecode]

            st.subheader("🧾 Your HR Details")
            st.dataframe(emp_data)
            st.markdown(download_dataframe(emp_data, filetype="excel"), unsafe_allow_html=True)
            st.markdown(download_dataframe(emp_data, filetype="csv"), unsafe_allow_html=True)

            st.subheader("💬 Ask a Question")
            user_q = st.text_input("What would you like to ask?")
            if user_q:
                if any(word in user_q.lower() for word in ["policy", "ethics", "rule", "harassment", "bribery", "termination"]):
                    st.info("🔍 Searching the policy file...")
                    answer = search_policy(policy_text, user_q)
                elif any(word in user_q.lower() for word in df.columns.str.lower()):
                    st.info("📊 Analyzing data...")
                    answer = emp_data.to_markdown()
                else:
                    answer = general_answers(user_q)
                st.markdown(answer)

            show_dashboard(df)
        else:
            st.error("Invalid credentials. Please try again.")

if __name__ == "__main__":
    main()
