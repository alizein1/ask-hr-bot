# Ask HR - Streamlit App for Capital Partners Group
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

@st.cache_data
def load_policy_txt():
    with open("capital_partners_policy.txt", "r", encoding="utf-8") as f:
        return f.read()

def authenticate(ecode, pin, pin_df):
    pin_df["PIN"] = pin_df["PIN"].astype(str)
    return not pin_df[(pin_df["ECODE"] == ecode) & (pin_df["PIN"] == pin)].empty

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

        if "join" in query:
            if "JOINING DATE" in df.columns:
                df["JOINING DATE"] = pd.to_datetime(df["JOINING DATE"], errors='coerce')
                join_counts = df["JOINING DATE"].dt.year.value_counts().sort_index()
                st.bar_chart(join_counts)

        if "area" in query and "Area Mng" in df.columns:
            st.bar_chart(df["Area Mng"].value_counts())

# Smart search in plain text policy
def search_policy(policy_text, query):
    query = query.lower()
    lines = policy_text.split("\n")
    matched = [line for line in lines if query in line.lower()]
    if matched:
        return "\n\n".join(matched[:5])

    # Try keyword approximation
    keywords = [
        "harassment", "bribery", "termination", "conflict of interest",
        "whistleblower", "ethics", "integrity", "disciplinary", "discrimination",
        "data protection", "fraud", "gifts", "employee behavior", "compliance"
    ]
    for word in keywords:
        if word in query:
            for line in lines:
                if word in line.lower():
                    return f"📌 Found something about '{word}':\n\n{line.strip()}"
    return "❌ No relevant policy section found."

# General HR responses
def general_answers(q):
    q = q.lower()
    faqs = {
        "leave": "To apply for leave, send your request to your manager and CC HR.",
        "salary": "Your salary and related components are listed in the HR table above.",
        "loan": "Loans are deducted monthly. Contact Finance for breakdowns.",
        "insurance": "Medical insurance covers hospitalization. Contact HR for card or info.",
        "attendance": "Make sure your punch is synced. Inform HR if there's an issue."
    }
    for k, v in faqs.items():
        if k in q:
            return v
    return "I’ll pass this question to the HR team for a detailed answer."

# Load everything
df, pin_df = load_data()
policy_text = load_policy_txt()

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
        st.markdown(download_dataframe(emp_data, "excel"), unsafe_allow_html=True)
        st.markdown(download_dataframe(emp_data, "csv"), unsafe_allow_html=True)

        st.subheader("💬 Ask a Question")
        question = st.text_input("What would you like to ask?")

        if question:
            q_lower = question.lower()
            if any(kw in q_lower for kw in ["policy", "ethics", "conduct", "harassment", "termination", "compliance", "behavior", "gifts", "fraud"]):
                st.info("Searching the policy file...")
                answer = search_policy(policy_text, q_lower)
            elif any(col.lower() in q_lower for col in df.columns):
                answer = emp_data.to_markdown()
            elif any(word in q_lower for word in ["insights", "nationalities", "declared", "area", "overtime", "joining"]):
                st.markdown("📊 Showing HR insights based on your question:")
                show_dashboard(df, q_lower)
                return
            else:
                answer = general_answers(q_lower)
            st.markdown(answer)

if __name__ == "__main__":
    main()
