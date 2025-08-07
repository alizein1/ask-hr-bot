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

@st.cache_data
def load_policy():
    doc = docx.Document("02 Capital Partners Group Code of Conducts and Business Ethics Policy.docx")
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])

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

# Analysis dashboard (only triggered on request)
def show_dashboard(df, query):
    query = query.lower()
    with st.expander("📊 HR Data Insights"):
        if "nationalities" in query:
            if "Nationality" in df.columns:
                fig = px.histogram(df, x="Nationality", title="Employee Nationalities")
                st.plotly_chart(fig)

        if "declared" in query or "nssf" in query:
            if "SOCIAL SECURITY NUMBER" in df.columns:
                declared = df["SOCIAL SECURITY NUMBER"].notna().sum()
                st.metric("Declared Employees", declared)

        if "overtime" in query:
            if "OVERTIME" in df.columns:
                fig = px.histogram(df, x="OVERTIME", title="Overtime Distribution")
                st.plotly_chart(fig)

        if "join" in query or "joining" in query:
            if "JOINING DATE" in df.columns:
                df["JOINING DATE"] = pd.to_datetime(df["JOINING DATE"], errors='coerce')
                join_counts = df["JOINING DATE"].dt.year.value_counts().sort_index()
                st.bar_chart(join_counts)

        if "area" in query and "Area Mng" in df.columns:
            area_counts = df["Area Mng"].value_counts()
            st.bar_chart(area_counts)

# Policy Q&A
def search_policy(policy_text, query):
    query = query.lower()
    matches = [p for p in policy_text.split("\n") if query in p.lower()]
    if matches:
        return "\n\n".join(matches[:5])

    keywords = {
        "harassment": "Harassment, Discrimination & Workplace Culture",
        "termination": "Compliance, Enforcement, and Disciplinary Measures",
        "conflict of interest": "Conflicts of Interest",
        "bribery": "Zero Tolerance for Corruption, Bribery & Gifts",
        "ethics": "Code of Ethics and Business Conduct",
        "data": "Data Protection and Confidentiality",
        "whistleblower": "Whistleblower Protection and Escalation Channels"
    }
    for key, section in keywords.items():
        if key in query:
            return f"📌 Refer to the section: **{section}** in the Code of Conduct."
    return "No relevant section found in the policy document."

# General HR Q&A
def general_answers(question):
    hr_faq = {
        "leave": "To apply for leave, send your request to your line manager and CC HR.",
        "salary slip": "Your salary slip is issued monthly. Contact HR if not received.",
        "insurance": "Medical insurance covers hospitalization & emergency. For details, email HR.",
        "attendance": "For attendance issues, please ensure your punch records are synced and notify HR.",
        "loan": "Loan deductions are shown in your payslip. Contact finance for breakdown."
    }
    for keyword, answer in hr_faq.items():
        if keyword in question.lower():
            return answer
    return "I'm forwarding this to the HR team for a detailed response."

# Global policy & data
df, pin_df = load_data()
policy_text = load_policy()

# Main app
def main():
    st.set_page_config(page_title="Ask HR", layout="wide")
    st.image("logo.png", width=150)
    st.image("middle_banner_image.png", width=600)
    st.title("🤖 Ask HR - Capital Partners Group")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        ecode = st.text_input("Enter your ECODE")
        pin = st.text_input("Enter your 3-digit PIN", type="password")
        if st.button("Login"):
            if authenticate(ecode, pin, pin_df):
                st.session_state.authenticated = True
                st.session_state.ecode = ecode
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    else:
        ecode = st.session_state.ecode
        emp_data = df[df["ECODE"] == ecode]

        st.subheader("🧾 Your HR Details")
        st.dataframe(emp_data)
        st.markdown(download_dataframe(emp_data, filetype="excel"), unsafe_allow_html=True)
        st.markdown(download_dataframe(emp_data, filetype="csv"), unsafe_allow_html=True)

        st.subheader("💬 Ask a Question")
        user_q = st.text_input("What would you like to ask?")

        if user_q:
            query = user_q.lower()

            if any(word in query for word in ["policy", "ethics", "rule", "harassment", "bribery", "termination", "conflict", "zero tolerance", "data"]):
                st.info("🔍 Searching the policy file...")
                answer = search_policy(policy_text, query)

            elif any(col.lower() in query for col in df.columns):
                st.info("📊 Showing your HR data...")
                answer = emp_data.to_markdown()

            elif any(kw in query for kw in ["analysis", "insights", "show dashboard", "how many", "nationalities", "declared", "overtime", "joining", "area"]):
                answer = "📊 Here's what I found in the HR analytics:"
                st.markdown(answer)
                show_dashboard(df, query)
                return

            else:
                answer = general_answers(user_q)

            st.markdown(answer)

if __name__ == "__main__":
    main()
