import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from collections import OrderedDict
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import re

# Register Unicode font for Arabic support
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# === Load & Cache Files ===
@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

@st.cache_data
def load_policy_text():
    with open("capital_partners_policy.txt", "r", encoding="utf-8") as file:
        return file.read()

# === Parse Policy Sections ===
def parse_policy_sections(policy_text):
    section_titles = [
        "CEO Message",
        "Copyright and Confidentiality Notice",
        "Change of Record Table",
        "Approval to Issue",
        "1. Purpose and Scope",
        "2. Our Values and Leadership Commitments",
        "3. Making Ethical Decisions and Speaking Up",
        "4. Zero Tolerance for Corruption, Bribery & Gifts",
        "5. Conflicts of Interest",
        "6. Harassment, Discrimination & Workplace Culture",
        "7. Data Protection and Confidentiality",
        "8. Whistleblower Protection and Escalation Channels",
        "9. Vendor and Supplier Integrity Standards",
        "10. Environment and Social Responsibility",
        "11. Political Neutrality and Government Relations",
        "12. Compliance, Enforcement, and Disciplinary Measures",
        "13. Annual Review and Acknowledgment",
        "14. Conclusion",
        "15. Employee Receipt & Acceptance"
    ]
    pattern = '|'.join(re.escape(title) for title in section_titles)
    splits = re.split(f'({pattern})', policy_text)
    sections = OrderedDict()
    i = 1
    while i < len(splits):
        title = splits[i].strip()
        content = splits[i+1].strip() if i+1 < len(splits) else ''
        sections[title] = content
        i += 2
    return sections

# === Match Policy Section ===
def match_policy_section(query, sections):
    q = query.lower()

    keywords_map = {
        "1. Purpose and Scope": ["who does the code apply", "policy applies to", "scope", "purpose of code", "who is included", "who must follow"],
        "2. Our Values and Leadership Commitments": ["values", "leadership", "integrity", "ethics culture", "core principles", "ethical leadership"],
        "3. Making Ethical Decisions and Speaking Up": ["ethical decision", "report issue", "raising concerns", "speak up", "misconduct", "how to decide"],
        "4. Zero Tolerance for Corruption, Bribery & Gifts": ["bribery", "gift", "kickback", "vendor present", "cash", "entertainment", "corruption", "zero tolerance"],
        "5. Conflicts of Interest": ["conflict of interest", "second job", "family business", "hiring relatives", "related party", "personal benefit"],
        "6. Harassment, Discrimination & Workplace Culture": ["harassment", "bullying", "abuse", "discrimination", "respect", "inappropriate", "hostile", "sexual harassment"],
        "7. Data Protection and Confidentiality": ["confidential", "data", "privacy", "sensitive information", "leak", "documents", "information protection"],
        "8. Whistleblower Protection and Escalation Channels": ["whistleblower", "anonymous", "hotline", "report wrongdoing", "speak safely", "retaliation", "escalate", "complaint"],
        "9. Vendor and Supplier Integrity Standards": ["supplier", "vendor", "third-party", "contractor", "ethics for suppliers", "partner conduct"],
        "10. Environment and Social Responsibility": ["environment", "recycling", "waste", "sustainability", "social responsibility", "community", "emissions", "green policy"],
        "11. Political Neutrality and Government Relations": ["politics", "government", "elections", "donation", "lobby", "campaign", "political activity", "public official"],
        "12. Compliance, Enforcement, and Disciplinary Measures": ["violation", "discipline", "enforcement", "termination", "audit", "compliance", "consequences"],
        "13. Annual Review and Acknowledgment": ["annual review", "acknowledgment", "yearly", "read policy", "confirm reading"],
        "14. Conclusion": ["conclusion", "final note", "summary", "ethics overall"],
        "15. Employee Receipt & Acceptance": ["receipt", "accept policy", "signature", "employee form", "consent"]
    }

    for section, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in q:
                return section, sections.get(section, "Section content not found.")
    return None, "❌ No relevant section found."

# === Auth ===
def authenticate(ecode, pin, pin_df):
    pin_df["PIN"] = pin_df["PIN"].astype(str)
    return not pin_df[(pin_df["ECODE"] == ecode) & (pin_df["PIN"] == pin)].empty

# === PDF Utilities ===
def generate_employee_pdf(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    data = [["Field", "Value"]]
    for col in df.columns:
        data.append([col, str(df.iloc[0][col])])
    table = Table(data, colWidths=[180, 340])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),12),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    story = [table]
    doc.build(story)
    return filename

def generate_policy_section_pdf(title, content, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12), Paragraph(content.replace("\n", "<br/>"), styles["BodyText"])]
    doc.build(story)
    return filename

# === HR Question Handler ===
def match_employee_question(question, emp_data):
    q = question.lower()

    if any(kw in q for kw in ["salary", "my salary", "how much do i get", "payment", "pay breakdown", "bonus", "nssf", "income tax"]):
        if emp_data.empty:
            return "❌ No employee data found.", None
        salary_cols = [
            "Payment Method", "TRANSPORT", "BONUS", "COMM", "OVERTIME", "ABSENCE",
            "Loan", "TRN-DD", "InSurance", "FAM ALL", "NSSF 3%", "INCOMETAX", "Total Ded", "Total USD", "Total"
        ]
        salary_data = emp_data[[col for col in salary_cols if col in emp_data.columns]]
        return "💰 Here is your salary breakdown:", salary_data

    elif any(kw in q for kw in ["joining date", "when did i join", "start date", "hired date", "employment start"]):
        if "JOINING DATE" in emp_data.columns:
            date = emp_data.iloc[0]["JOINING DATE"]
            return f"📅 You joined the company on: **{date}**", None

    elif any(kw in q for kw in ["leave balance", "annual leave", "how many leaves", "my leaves", "vacation days", "remaining leaves"]):
        if "ANNUAL LEAVES" in emp_data.columns:
            leaves = emp_data.iloc[0]["ANNUAL LEAVES"]
            return f"🌴 Your current annual leave balance is: **{leaves} days**", None

    elif any(kw in q for kw in ["my details", "show my info", "full profile", "employee file", "personal record"]):
        return "📋 Here are all your registered HR details:", emp_data

    return None, None

# === Main App ===
df, pin_df = load_data()
policy_text = load_policy_text()
sections = parse_policy_sections(policy_text)

st.set_page_config("Ask HR - Capital Partners Group", layout="wide")
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
            st.error("Invalid credentials.")
else:
    ecode = st.session_state.ecode
    emp_data = df[df["ECODE"] == ecode]

    st.subheader("🧾 Your HR Details")
    st.dataframe(emp_data)

    pdf_name = f"employee_data_{ecode}.pdf"
    generate_employee_pdf(emp_data, pdf_name)
    with open(pdf_name, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_name}">📥 Download My HR Data (PDF)</a>', unsafe_allow_html=True)

    st.subheader("💬 Ask Something")
    query = st.text_input("Ask a policy or HR question...")

    if query:
        matched_title, content = match_policy_section(query, sections)

        if matched_title:
            st.success(f"🔎 Matched Section: {matched_title}")
            st.markdown(f"**{matched_title}**\n\n{content}")
            pdf_section = f"section_{matched_title.replace(' ', '_')}.pdf"
            generate_policy_section_pdf(matched_title, content, pdf_section)
            with open(pdf_section, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_section}">📥 Download This Policy Section (PDF)</a>', unsafe_allow_html=True)
        else:
            answer, table = match_employee_question(query, emp_data)
           
