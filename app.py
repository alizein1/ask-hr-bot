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
        "1. Purpose and Scope": [
            "who does the code apply", "scope", "purpose"
        ],
        "2. Our Values and Leadership Commitments": [
            "values", "ethics", "integrity", "leadership"
        ],
        "3. Making Ethical Decisions and Speaking Up": [
            "ethical", "report", "speak up", "misconduct", "report violation",
            "raise a concern", "whistleblower", "see someone break the rules", "how do i report a violation",
            "how do i raise a concern", "can i report unethical", "how do i speak up"
        ],
        "4. Zero Tolerance for Corruption, Bribery & Gifts": [
            "bribe", "gift", "kickback", "vendor", "entertainment", "can i accept a gift", "is bribery", "take a commission"
        ],
        "5. Conflicts of Interest": [
            "conflict of interest", "family", "second job", "related party", "hire my relative", "work another job"
        ],
        "6. Harassment, Discrimination & Workplace Culture": [
            "harassment", "bully", "abuse", "discrimination", "bullied", "cursed", "insulted", "report harassment",
            "process for workplace abuse", "someone bullied me", "manager abused me", "coworker insulted", "someone curses at me"
        ],
        "7. Data Protection and Confidentiality": [
            "confidential", "data", "privacy", "can i share company data", "what is confidential"
        ],
        "8. Whistleblower Protection and Escalation Channels": [
            "whistleblower", "retaliation", "anonymous", "hotline", "protected if i report", "is it safe to report"
        ],
        "9. Vendor and Supplier Integrity Standards": [
            "vendor", "supplier", "third-party", "vendor rules"
        ],
        "10. Environment and Social Responsibility": [
            "environment", "sustainability", "community", "environmental policies", "sustainability at cpg"
        ],
        "11. Political Neutrality and Government Relations": [
            "politics", "elections", "public official", "political activity at work"
        ],
        "12. Compliance, Enforcement, and Disciplinary Measures": [
            "violation", "discipline", "termination", "what if i steal", "break company rules", "consequences", "penalties",
            "misconduct", "get fired for discrimination", "disciplinary action", "penalties for theft", "fraud"
        ],
        "13. Annual Review and Acknowledgment": [
            "review", "acknowledgment"
        ],
        "14. Conclusion": [
            "conclusion", "summary"
        ],
        "15. Employee Receipt & Acceptance": [
            "receipt", "signature", "accept"
        ]
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

def match_employee_question(question, emp_data):
    q = question.lower()
    # English + Arabic triggers for full details/profile
    if any(x in q for x in [
        "my details", "all my data", "my info", "full profile", "my record", "show my details", "show my profile",
        "كل تفاصيل ملفي", "ملفي بالكامل", "جميع معلوماتي", "بياناتي الكاملة", "أريد كل تفاصيل ملفي", "تفاصيل ملفي"
    ]):
        return "📋 Full Employee Info", emp_data
    elif any(x in q for x in ["salary", "payment", "pay", "bonus", "nssf", "income tax"]):
        cols = ["Payment Method", "TRANSPORT", "BONUS", "COMM", "OVERTIME", "ABSENCE", "Loan", "TRN-DD", "InSurance", "FAM ALL", "NSSF 3%", "INCOMETAX", "Total Ded", "Total USD", "Total"]
        return "💰 Salary Breakdown", emp_data[[col for col in cols if col in emp_data.columns]]
    elif any(x in q for x in ["joining date", "start date", "hire date", "joined"]):
        return "📅 Joining Date", emp_data[["JOINING DATE"]]
    elif any(x in q for x in ["leave", "annual leave", "vacation", "leave balance"]):
        return "🌴 Annual Leaves", emp_data[["ANNUAL LEAVES"]]
    elif any(x in q for x in ["social security", "nssf number", "social number"]):
        return "🧾 Social Security Number", emp_data[["SOCIAL SECURITY NUMBER"]]
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

    st.subheader("💬 Ask Something")
    query = st.text_input("Ask a policy, HR, or team question...")

    if query:
        # HR Team Gallery (EN/AR)
        hr_keywords = [
            "who is hr", "hr team", "human resources team", 
            "من فريق الموارد", "موظفي الموارد البشرية", "فريق الموارد", "فريق اتش ار"
        ]
        if any(kw in query.lower() for kw in hr_keywords):
            st.subheader('👥 Meet Your HR Team')
            cols = st.columns(3)
            cols[0].image('hr_team_photos/thumbnail_IMG_0396.jpg', use_column_width=True)
            cols[1].image('hr_team_photos/thumbnail_IMG_3345.jpg', use_column_width=True)
            cols[2].image('hr_team_photos/thumbnail_IMG_3347.jpg', use_column_width=True)
            cols[0].image('hr_team_photos/thumbnail_IMG_3522.jpg', use_column_width=True)
            cols[1].image('hr_team_photos/thumbnail_IMG_3529.jpg', use_column_width=True)
            cols[2].image('hr_team_photos/thumbnail_IMG_3767.jpg', use_column_width=True)
            cols[0].image('hr_team_photos/thumbnail_IMG_3958.jpg', use_column_width=True)
            st.stop()

        # Special historical Q&A
        if "من اغتال ولي عهد النمسا" in query:
            st.success("فرانس فرديناند")
            st.stop()

        section, section_text = match_policy_section(query, sections)
        if section and section_text and "not found" not in section_text.lower():
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
                    # Show PDF download only if employee asks for full details/profile (English or Arabic)
                    if "full" in response.lower() or "profile" in response.lower() or "details" in response.lower() or "ملفي" in query or "تفاصيل" in query or "بياناتي" in query:
                        pdf_name = f"employee_data_{ecode}.pdf"
                        generate_employee_pdf(emp_data, pdf_name)
                        with open(pdf_name, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_name}">📥 Download My HR Data (PDF)</a>', unsafe_allow_html=True)
            else:
                st.warning("Sorry, I couldn't match your question. Try rephrasing.")
