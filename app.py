# Ask HR - Streamlit App for Capital Partners Group
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ================== SMART POLICY CHATBOT ==================
def smart_policy_answer(query):
    q = query.lower().strip()
    topics = [
        {
            "keywords": ["who does the code apply", "scope", "copy of the policy", "how often reviewed", "what is the code"],
            "answer": "The Code applies to all employees, executives, partners, and suppliers of Capital Partners Group. It provides a clear ethical foundation for decision-making and outlines expectations for professional, legal, and values-based conduct."
        },
        {
            "keywords": ["company values", "values guide", "expected from leaders"],
            "answer": "CPG's core values are: Quality, Credibility, Growth, Commitment, Accountability, Professionalism, and Integrity. Leaders must model ethical behavior and integrate the Code into team discussions and decisions."
        },
        {
            "keywords": ["ethical decisions", "witness unethical", "report misconduct", "consequences of violating"],
            "answer": "Employees are expected to act legally, align with values, and report concerns to managers, HR, or anonymously. There will be no retaliation. Violations may lead to disciplinary action."
        },
        {
            "keywords": ["bribery", "gifts", "corruption", "kickbacks"],
            "answer": "Bribery, gifts, and personal benefits are forbidden. Anything offered to public officials requires prior HR approval. Violations may result in termination."
        },
        {
            "keywords": ["conflict of interest", "another job", "hire relative"],
            "answer": "Conflicts must be disclosed if they involve outside work, relatives, or financial interest in vendors/competitors. All disclosures go through HR or management."
        },
        {
            "keywords": ["harassment", "discrimination", "bullying", "offensive comments"],
            "answer": "All harassment or discrimination is prohibited. Reports can go to HR or Ethics Hotline. No retaliation is tolerated. Disciplinary action will follow confirmed cases."
        },
        {
            "keywords": ["confidential information", "company data", "data protection"],
            "answer": "Company data must be handled securely, accessed only as needed, and never used for personal purposes. Breaches must be reported immediately."
        },
        {
            "keywords": ["whistleblower", "retaliation", "wrongdoing", "hotline"],
            "answer": "CPG ensures anonymous reporting and zero retaliation. Reports are investigated seriously and confidentially."
        },
        {
            "keywords": ["suppliers", "vendors", "third party"],
            "answer": "All vendors must follow CPG's Code. Violations like unsafe labor, bribery, or unauthorized subcontracting result in contract termination."
        },
        {
            "keywords": ["sustainability", "environment", "social responsibility", "communities"],
            "answer": "CPG supports sustainability, compliance with environmental laws, and invests in community education, health, and development."
        },
        {
            "keywords": ["political", "politics", "donations"],
            "answer": "No company resources can be used for political activities. Employees may not use their position for political gain and must disclose public roles."
        },
        {
            "keywords": ["violations", "disciplinary actions", "compliance", "enforcement"],
            "answer": "Violations may lead to warnings, suspension, termination, or legal action. CPG may audit and expects full cooperation."
        }
    ]
    for topic in topics:
        for keyword in topic["keywords"]:
            if keyword in q:
                return topic["answer"]
    return "❌ Sorry, I couldn't find a specific answer. Please contact HR for more information."

# ================ APP UTILITY FUNCTIONS ===================
@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

def authenticate(ecode, pin, pin_df):
    pin_df["PIN"] = pin_df["PIN"].astype(str)
    return not pin_df[(pin_df["ECODE"] == ecode) & (pin_df["PIN"] == pin)].empty

def generate_pdf(data, filename="employee_data.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = [Paragraph("Employee HR Details", styles["Title"]), Spacer(1, 12)]
    for col in data.columns:
        value = data.iloc[0][col]
        story.append(Paragraph(f"<b>{col}:</b> {value}", styles["Normal"]))
        story.append(Spacer(1, 6))
    doc.build(story)
    return filename

def get_pdf_download_button(emp_data, ecode):
    filename = f"employee_data_{ecode}.pdf"
    generate_pdf(emp_data, filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download My HR Data (PDF)</a>'

def show_dashboard(df, query):
    query = query.lower()
    with st.expander("📊 HR Data Insights"):
        if "nationalities" in query and "Nationality" in df.columns:
            fig = px.histogram(df, x="Nationality", title="Employee Nationalities")
            st.plotly_chart(fig)
        if "declared" in query or "nssf" in query:
            if "SOCIAL SECURITY NUMBER" in df.columns:
                declared = df["SOCIAL SECURITY NUMBER"].notna().sum()
                st.metric("Declared Employees", declared)
        if "overtime" in query and "OVERTIME" in df.columns:
            fig = px.histogram(df, x="OVERTIME", title="Overtime Distribution")
            st.plotly_chart(fig)
        if "join" in query and "JOINING DATE" in df.columns:
            df["JOINING DATE"] = pd.to_datetime(df["JOINING DATE"], errors='coerce')
            join_counts = df["JOINING DATE"].dt.year.value_counts().sort_index()
            st.bar_chart(join_counts)
        if "area" in query and "Area Mng" in df.columns:
            st.bar_chart(df["Area Mng"].value_counts())

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

# ====================== MAIN APP ==========================
df, pin_df = load_data()

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
        st.markdown(get_pdf_download_button(emp_data, ecode), unsafe_allow_html=True)

        st.subheader("💬 Ask a Question")
        question = st.text_input("What would you like to ask?")
        if question:
            q_lower = question.lower()
            if any(word in q_lower for word in [
                "policy", "ethics", "conduct", "harassment", "corruption", "bribery",
                "conflict", "values", "zero tolerance", "disciplinary", "code of ethics",
                "data protection", "confidential", "political", "whistleblower", "vendors", "suppliers"
            ]):
                st.info("Answering your policy question...")
                answer = smart_policy_answer(q_lower)
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
