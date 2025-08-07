import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import docx
import re
from collections import OrderedDict

# Arabic font support
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# Load files
@st.cache_data
def load_data():
    df = pd.read_excel("PROLOGISTICS.xlsx")
    pin_df = pd.read_csv("Employee_PIN_List.csv")
    return df, pin_df

@st.cache_data
def load_policy_text():
    with open("capital_partners_policy.txt", "r", encoding="utf-8") as f:
        return f.read()

# Parse policy sections
def parse_policy_sections(policy_text):
    titles = [
        "CEO Message", "Copyright and Confidentiality Notice", "Change of Record Table", "Approval to Issue",
        "1. Purpose and Scope", "2. Our Values and Leadership Commitments", "3. Making Ethical Decisions and Speaking Up",
        "4. Zero Tolerance for Corruption, Bribery & Gifts", "5. Conflicts of Interest",
        "6. Harassment, Discrimination & Workplace Culture", "7. Data Protection and Confidentiality",
        "8. Whistleblower Protection and Escalation Channels", "9. Vendor and Supplier Integrity Standards",
        "10. Environment and Social Responsibility", "11. Political Neutrality and Government Relations",
        "12. Compliance, Enforcement, and Disciplinary Measures", "13. Annual Review and Acknowledgment",
        "14. Conclusion", "15. Employee Receipt & Acceptance"
    ]
    pattern = '|'.join(re.escape(t) for t in titles)
    chunks = re.split(f'({pattern})', policy_text)
    sections = OrderedDict()
    i = 1
    while i < len(chunks):
        title = chunks[i].strip()
        content = chunks[i+1].strip() if i+1 < len(chunks) else ''
        sections[title] = content
        i += 2
    return sections

# Match query to section
def match_policy_section(query, sections):
    q = query.lower()
    keywords = {
        "purpose": "1. Purpose and Scope",
        "value": "2. Our Values and Leadership Commitments",
        "ethical": "3. Making Ethical Decisions and Speaking Up",
        "bribery": "4. Zero Tolerance for Corruption, Bribery & Gifts",
        "gift": "4. Zero Tolerance for Corruption, Bribery & Gifts",
        "corruption": "4. Zero Tolerance for Corruption, Bribery & Gifts",
        "conflict": "5. Conflicts of Interest",
        "harassment": "6. Harassment, Discrimination & Workplace Culture",
        "discrimination": "6. Harassment, Discrimination & Workplace Culture",
        "data": "7. Data Protection and Confidentiality",
        "confidential": "7. Data Protection and Confidentiality",
        "whistle": "8. Whistleblower Protection and Escalation Channels",
        "supplier": "9. Vendor and Supplier Integrity Standards",
        "vendor": "9. Vendor and Supplier Integrity Standards",
        "environment": "10. Environment and Social Responsibility",
        "politic": "11. Political Neutrality and Government Relations",
        "disciplinary": "12. Compliance, Enforcement, and Disciplinary Measures",
        "acknowledge": "13. Annual Review and Acknowledgment",
        "conclusion": "14. Conclusion",
        "receipt": "15. Employee Receipt & Acceptance",
        "ceo": "CEO Message"
    }
    for kw, title in keywords.items():
        if kw in q:
            return title, sections.get(title, "Section content not found.")
    return None, "❌ No relevant section found."

# Generate section PDF
def generate_policy_section_pdf(title, content, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12), Paragraph(content.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)
    return filename

# Generate employee PDF (tabular with Arabic support)
def generate_employee_pdf_arabic(df, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    data = [["Field", "Value"]]
    for col in df.columns:
        val = str(df.iloc[0][col])
        data.append([col, val])
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

# Authenticate login
def authenticate(ecode, pin, pin_df):
    pin_df["PIN"] = pin_df["PIN"].astype(str)
    match = pin_df[(pin_df["ECODE"] == ecode) & (pin_df["PIN"] == pin)]
    return not match.empty

# Main app
def main():
    st.set_page_config(page_title="Ask HR", layout="wide")
    st.image("logo.png", width=150)
    st.image("middle_banner_image.png", use_container_width=True)
    st.title("🤖 Ask HR - Capital Partners Group")

    df, pin_df = load_data()
    policy_text = load_policy_text()
    sections = parse_policy_sections(policy_text)

    ecode = st.text_input("Enter your ECODE")
    pin = st.text_input("Enter your 3-digit PIN", type="password")

    if st.button("Login"):
        if authenticate(ecode, pin, pin_df):
            st.success("Logged in successfully ✅")
            emp_data = df[df["ECODE"] == ecode]

            st.subheader("🧾 Your HR Details")
            st.dataframe(emp_data)

            if not emp_data.empty:
                pdf_path = f"employee_data_{ecode}.pdf"
                generate_employee_pdf_arabic(emp_data, pdf_path)
                with open(pdf_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_path}">📥 Download HR Details as PDF</a>', unsafe_allow_html=True)

            st.subheader("💬 Ask a Question")
            user_q = st.text_input("What would you like to ask?")
            if user_q:
                title, answer = match_policy_section(user_q, sections)
                st.markdown(f"**{title}**\n\n{answer}")
                if title and answer:
                    pdf_section = f"{title.replace(' ', '_')}.pdf"
                    generate_policy_section_pdf(title, answer, pdf_section)
                    with open(pdf_section, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_section}">📥 Download This Policy Section as PDF</a>', unsafe_allow_html=True)
        else:
            st.error("Invalid credentials. Please try again.")

if __name__ == "__main__":
    main()
