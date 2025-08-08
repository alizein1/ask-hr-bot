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
    q = query.lower().strip()

    # Flexible triggers for all policy sections and scenarios
    keywords_map = {
        "1. Purpose and Scope": [
            "who does the code apply", "policy applies", "policy coverage", "مين لازم يلتزم", "لمن يطبق", "scope", "purpose"
        ],
        "2. Our Values and Leadership Commitments": [
            "values", "core values", "leadership", "integrity", "ethics culture", "vision", "principles", "guiding values",
            "سلوك القيادة", "قيم الشركة", "قيمنا", "قيم القيادة"
        ],
        "3. Making Ethical Decisions and Speaking Up": [
            "ethical", "ethics", "decision making", "report", "how do i report", "report issue", "reporting violation",
            "complaint", "how do i file a complaint", "raise a concern", "misconduct", "how do i speak up", "speak up",
            "ابلاغ", "اشتكيت", "كيف أبلغ", "كيف أقدم شكوى", "الإبلاغ"
        ],
        "4. Zero Tolerance for Corruption, Bribery & Gifts": [
            "bribe", "bribery", "gift", "kickback", "vendor", "accepting a gift", "corruption", "entertainment", "commission",
            "is bribery allowed", "هدية", "رشوة", "مكافأة", "فساد", "فساد مالي"
        ],
        "5. Conflicts of Interest": [
            "conflict of interest", "family", "second job", "related party", "hire my relative", "outside job", "personal gain",
            "outside work", "can i work another job", "hiring relatives", "مصالح متضاربة", "عمل إضافي", "أقارب"
        ],
        "6. Harassment, Discrimination & Workplace Culture": [
            "harassment", "bully", "bullying", "abuse", "discrimination", "offensive language", "cursed", "insulted",
            "report harassment", "workplace violence", "abusive", "hostile", "verbal abuse", "sexism", "sexual harassment",
            "someone bullied me", "manager abused me", "coworker insulted", "curse words", "swearing", "offensive jokes",
            "feel unsafe", "my boss yelled", "humiliating staff", "mistreatment", "unfair treatment",
            "كيف أبلغ عن التنمر", "تحرش", "شتمي", "تعرضت للتنمر", "إهانة", "إساءة", "شتمني", "سلوك مسيء",
            "someone curses me", "coworker shouted", "manager yelled", "if someone bullies me", "if i am cursed"
        ],
        "7. Data Protection and Confidentiality": [
            "confidential", "data", "privacy", "data privacy", "personal data", "data breach", "share company data",
            "what is confidential", "who can access data", "معلومات سرية", "خصوصية", "بيانات حساسة"
        ],
        "8. Whistleblower Protection and Escalation Channels": [
            "whistleblower", "protected", "retaliation", "anonymous", "hotline", "can i report", "how to report safely",
            "protected if i report", "safe to report", "protection", "is it safe", "بلغت عن مخالفة", "حماية المبلغين", "الابلاغ بسرية"
        ],
        "9. Vendor and Supplier Integrity Standards": [
            "vendor", "supplier", "third-party", "partner conduct", "supplier policy", "contractor", "vendor rules",
            "شركات متعاقدة", "موردين", "مقاولين"
        ],
        "10. Environment and Social Responsibility": [
            "environment", "sustainability", "waste", "green policy", "community", "emissions", "environmental policies",
            "supporting local", "recycling", "community support", "البيئة", "المسؤولية الاجتماعية", "إعادة التدوير", "مجتمع"
        ],
        "11. Political Neutrality and Government Relations": [
            "politics", "elections", "public official", "political activity", "political donation", "lobbying",
            "government", "can i campaign", "campaign", "neutrality", "نشاط سياسي", "سياسة", "تبرعات سياسية"
        ],
        "12. Compliance, Enforcement, and Disciplinary Measures": [
            "violation", "discipline", "termination", "steal", "stole", "breaking the rules", "consequences",
            "penalties", "misconduct", "get fired", "disciplinary action", "punishment", "legal action", "audit",
            "fraud", "fraudulent", "can i get fired", "سرقة", "عقوبة", "عقوبات", "طرد", "جزاءات", "فصل", "عقوبات قانونية", "تدابير تأديبية",
            "what happens if i steal", "what if i break the rules", "what happens if someone steals"
        ],
        "13. Annual Review and Acknowledgment": [
            "review", "acknowledgment", "annual review", "read policy", "policy review", "تحديث سنوي", "مراجعة سنوية"
        ],
        "14. Conclusion": [
            "conclusion", "final note", "summary", "ethics overall", "خلاصة", "ملخص"
        ],
        "15. Employee Receipt & Acceptance": [
            "receipt", "signature", "accept", "employee consent", "acknowledge", "توقيع", "استلام", "موافقة"
        ]
    }

    # Special cases for natural questions
    # "what happens if someone bullies me at work"
    if "bully" in q or "bullying" in q or "someone bullies me" in q or "تعرضت للتنمر" in q or "شتمني" in q or "curse" in q or "cursed" in q:
        return "6. Harassment, Discrimination & Workplace Culture", sections.get("6. Harassment, Discrimination & Workplace Culture", "")
    if "bribery" in q or "is bribery allowed" in q or "can i accept a gift" in q or "رشوة" in q or "هدية" in q:
        return "4. Zero Tolerance for Corruption, Bribery & Gifts", sections.get("4. Zero Tolerance for Corruption, Bribery & Gifts", "")
    if "report" in q and ("misconduct" in q or "violation" in q or "problem" in q or "كيف أبلغ" in q):
        return "3. Making Ethical Decisions and Speaking Up", sections.get("3. Making Ethical Decisions and Speaking Up", "")
    if "policy" in q or "rule" in q or "code" in q or "ethic" in q or "سياسة" in q or "قانون" in q:
        return "ALL_POLICY", ""
    # All mapped keywords
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
    q = question.lower().strip()
    # Ultra-flexible triggers for full profile/details
    profile_triggers = [
        "my details", "all my data", "my info", "full profile", "my record", "show my details", "show my profile", "download my profile", "download my details",
        "كل تفاصيل ملفي", "ملفي بالكامل", "جميع معلوماتي", "بياناتي الكاملة", "أريد كل تفاصيل ملفي", "تفاصيل ملفي", "pdf ملفي", "تحميل ملفي"
    ]
    salary_triggers = [
        "salary", "salary slip", "payment", "pay", "bonus", "nssf", "income tax", "راتبي", "تفاصيل الراتب", "سلم الرواتب", "الراتب", "كم راتبي", "show me my salary breakdown"
    ]
    leave_triggers = [
        "leave", "annual leave", "vacation", "leave balance", "رصيد الإجازات", "عدد الإجازات", "اجازة", "إجازاتي", "رصيدي من الاجازات", "كم اجازتي"
    ]
    nssf_triggers = [
        "social security", "nssf number", "social number", "رقم الضمان", "رقم الضمان الاجتماعي", "ضمان", "الضمان"
    ]
    joining_triggers = [
        "joining date", "start date", "hire date", "joined", "تاريخ الانضمام", "متى التحاقي", "متى انضممت"
    ]

    if any(x in q for x in profile_triggers):
        return "📋 Full Employee Info", emp_data
    elif any(x in q for x in salary_triggers):
        cols = ["Payment Method", "TRANSPORT", "BONUS", "COMM", "OVERTIME", "ABSENCE", "Loan", "TRN-DD", "InSurance", "FAM ALL", "NSSF 3%", "INCOMETAX", "Total Ded", "Total USD", "Total"]
        return "💰 Salary Breakdown", emp_data[[col for col in cols if col in emp_data.columns]]
    elif any(x in q for x in joining_triggers):
        return "📅 Joining Date", emp_data[["JOINING DATE"]]
    elif any(x in q for x in leave_triggers):
        return "🌴 Annual Leaves", emp_data[["ANNUAL LEAVES"]]
    elif any(x in q for x in nssf_triggers):
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
            cols[2].image('hr_team_photos/thumbnail_IMG_3989.jpg', use_column_width=True)  # NEW PHOTO ADDED!
            st.stop()

        # Special historical Q&A
        if "من اغتال ولي عهد النمسا" in query:
            st.success("فرانس فرديناند")
            st.stop()

        section, section_text = match_policy_section(query, sections)
        if section == "ALL_POLICY":
            st.info("🔎 Please select a policy section to learn more or download:")
            for sec, txt in sections.items():
                if sec[0].isdigit():
                    st.markdown(f"**{sec}** — {txt.split('.')[0][:70]}...")
                    pdf_section = f"section_{sec.replace(' ', '_')}.pdf"
                    generate_policy_section_pdf(sec, txt, pdf_section)
                    with open(pdf_section, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                        st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{pdf_section}">📥 Download ({sec})</a>', unsafe_allow_html
