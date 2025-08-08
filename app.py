
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

@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

@st.cache_data
def load_policy_text():
    with open("capital_partners_policy.txt", "r", encoding="utf-8") as file:
        return file.read()

def parse_policy_sections(policy_text):
    section_titles = [
        "CEO Message", "Copyright and Confidentiality Notice", "Change of Record Table", "Approval to Issue",
        "1. Purpose and Scope", "2. Our Values and Leadership Commitments",
        "3. Making Ethical Decisions and Speaking Up", "4. Zero Tolerance for Corruption, Bribery & Gifts",
        "5. Conflicts of Interest", "6. Harassment, Discrimination & Workplace Culture",
        "7. Data Protection and Confidentiality", "8. Whistleblower Protection and Escalation Channels",
        "9. Vendor and Supplier Integrity Standards", "10. Environment and Social Responsibility",
        "11. Political Neutrality and Government Relations", "12. Compliance, Enforcement, and Disciplinary Measures",
        "13. Annual Review and Acknowledgment", "14. Conclusion", "15. Employee Receipt & Acceptance"
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

def match_policy_section(query, sections):
    q = query.lower()
    keywords_map = {
        "1. Purpose and Scope": ["who does the code apply", "scope", "purpose"],
        "2. Our Values and Leadership Commitments": ["values", "ethics", "integrity", "leadership"],
        "3. Making Ethical Decisions and Speaking Up": ["ethical", "report", "speak up", "misconduct"],
        "4. Zero Tolerance for Corruption, Bribery & Gifts": ["bribe", "gift", "kickback", "vendor", "entertainment"],
        "5. Conflicts of Interest": ["conflict of interest", "family", "second job", "related party"],
        "6. Harassment, Discrimination & Workplace Culture": ["harassment", "bully", "abuse", "discrimination"],
        "7. Data Protection and Confidentiality": ["confidential", "data", "privacy"],
        "8. Whistleblower Protection and Escalation Channels": ["whistleblower", "retaliation", "anonymous", "hotline"],
        "9. Vendor and Supplier Integrity Standards": ["vendor", "supplier", "third-party"],
        "10. Environment and Social Responsibility": ["environment", "sustainability", "community"],
        "11. Political Neutrality and Government Relations": ["politics", "elections", "public official"],
        "12. Compliance, Enforcement, and Disciplinary Measures": ["violation", "discipline", "termination"],
        "13. Annual Review and Acknowledgment": ["review", "acknowledgment"],
        "14. Conclusion": ["conclusion", "summary"],
        "15. Employee Receipt & Acceptance": ["receipt", "signature", "accept"]
    }
    for section, keywords in keywords_map.items():
        for kw in keywords:
            if kw in q:
                return section, sections.get(section, "Section content not found.")
    return None, "❌ No relevant section found."

def authenticate(ecode, pin, pin_df):
    pin_df["PIN"] = pin_df["PIN"].astype(str)
    return not pin_df[(pin_df["ECODE"] == ecode) & (pin_df["PIN"] == pin)].empty

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

# === Smart HR Answers ===
def match_employee_question(question, emp_data):
    q = question.lower()
    if any(x in q for x in ["salary", "payment", "pay", "bonus", "nssf", "income tax"]):
        cols = ["Payment Method", "TRANSPORT", "BONUS", "COMM", "OVERTIME", "ABSENCE", "Loan", "TRN-DD", "InSurance", "FAM ALL", "NSSF 3%", "INCOMETAX", "Total Ded", "Total USD", "Total"]
        return "💰 Salary Breakdown", emp_data[[col for col in cols if col in emp_data.columns]]
    elif any(x in q for x in ["joining date", "start date", "hire date", "joined"]):
        return "📅 Joining Date", emp_data[["JOINING DATE"]]
    elif any(x in q for x in ["leave", "annual leave", "vacation", "leave balance"]):
        return "🌴 Annual Leaves", emp_data[["ANNUAL LEAVES"]]
    elif any(x in q for x in ["social security", "nssf number", "social number"]):
        return "🧾 Social Security Number", emp_data[["SOCIAL SECURITY NUMBER"]]
    elif any(x in q for x in ["my info", "all my data", "my profile", "my record"]):
        return "📋 Full Employee Info", emp_data
    return None, None

# === Streamlit UI ===
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
        section, section_text = match_policy_section(query, sections)
        if section:
            st.success(f"🔎 Matched Section: {section}")
            st.markdown(f"**{section}**\n\n{section_text}")
            pdf_section = f"section_{section.replace(' ', '_')}.pdf"
            generate_policy_section_pdf(section, section_text, pdf_section)
            with open(pdf_section, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_section}">📥 Download This Policy Section (PDF)</a>', unsafe_allow_html=True)
        else:
            response, table = match_employee_question(query, emp_data)
            if response:
                st.info(response)
                if table is not None:
                    st.dataframe(table)
            else:
                st.warning("Sorry, I couldn't match your question. Try rephrasing.")

