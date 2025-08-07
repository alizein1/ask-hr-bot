import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from collections import OrderedDict
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import re

# === Load & Cache Files ===
@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

@st.cache_data
def load_policy_text():
    with open("capital_partners_policy.txt", "r") as file:
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

    st.subheader("💬 Ask About Policy")
    query = st.text_input("Ask something about the policy...")
    if query:
        matched_title = next((title for title in sections if any(word in query.lower() for word in title.lower().split())), None)
        if matched_title:
            content = sections[matched_title]
            st.success(f"🔎 Matched Section: {matched_title}")
            st.markdown(f"**{matched_title}**\n\n{content}")
            pdf_section = f"section_{matched_title.replace(' ', '_')}.pdf"
            generate_policy_section_pdf(matched_title, content, pdf_section)
            with open(pdf_section, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_section}">📥 Download This Policy Section (PDF)</a>', unsafe_allow_html=True)
        else:
            st.warning("No matching section found. Please rephrase your question.")
