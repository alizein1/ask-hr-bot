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
import random

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
            "who does the code apply", "scope", "purpose", "policy applies", "policy applies to", "policy coverage",
            "مين لازم يلتزم", "لمن يطبق"
        ],
        "2. Our Values and Leadership Commitments": [
            "values", "core values", "leadership", "integrity", "ethics culture", "vision", "principles", "guiding values",
            "سلوك القيادة", "قيم الشركة", "قيمنا", "قيم القيادة"
        ],
        "3. Making Ethical Decisions and Speaking Up": [
            "ethical", "ethics", "report", "speak up", "misconduct", "raise concern", "how to report", "reporting violation",
            "report problem", "whistleblower", "see someone break the rules", "if i see", "complaint",
            "how do i file a complaint", "anonymous reporting", "ابلاغ", "اشتكيت", "كيف أبلغ", "كيف أقدم شكوى", "الإبلاغ"
        ],
        "4. Zero Tolerance for Corruption, Bribery & Gifts": [
            "bribe", "gift", "kickback", "vendor", "accepting a gift", "corruption", "entertainment", "can i accept a gift",
            "is bribery allowed", "commission", "هدية", "رشوة", "مكافأة", "فساد", "فساد مالي"
        ],
        "5. Conflicts of Interest": [
            "conflict of interest", "family", "second job", "related party", "hire my relative", "outside job", "personal gain",
            "outside work", "can i work another job", "hiring relatives", "مصالح متضاربة", "عمل إضافي", "أقارب"
        ],
        "6. Harassment, Discrimination & Workplace Culture": [
            "harassment", "bully", "bullying", "abuse", "discrimination", "offensive language", "cursed", "insulted",
            "report harassment", "workplace violence", "abusive", "hostile", "verbal abuse", "sexism", "sexual harassment",
            "someone bullied me", "manager abused me", "coworker insulted", "curse words", "swearing", "offensive jokes",
            "feel unsafe", "my boss yelled", "humiliating staff", "mistreatment", "unfair treatment", "كيف أبلغ عن التنمر", "تحرش", "شتمي", "تعرضت للتنمر", "إهانة", "إساءة", "شتمني", "سلوك مسيء"
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
            "fraud", "fraudulent", "can i get fired", "سرقة", "عقوبة", "عقوبات", "طرد", "جزاءات", "فصل", "عقوبات قانونية", "تدابير تأديبية"
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

    for section, keywords in keywords_map.items():
        for kw in keywords:
            if kw in q:
                return section, sections.get(section, "Section content not found.")

    fallback_policy_words = [
        "policy", "rule", "قانون", "سياسة", "code", "procedure", "ethic", "compliance", "behavior", "conduct", "system", "what is the policy", "what does the code say", "شرح السياسة"
    ]
    if any(w in q for w in fallback_policy_words):
        return "ALL_POLICY", ""  # signal for showing all

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

# Mental health smart detection
def mental_health_responses(q):
    mh_keywords = [
        "lonely", "alone", "depressed", "stressed", "burnt out", "overwhelmed",
        "anxious", "panic", "anxiety", "mental health", "no one listens", "need someone to talk",
        "worried", "can't sleep", "tired", "sad", "hopeless", "don't feel well",
        "what to do when I feel lonely", "i feel down", "i feel lost", "unhappy",
        "how to cope", "how to deal with stress", "i need help", "mental support",
        "أشعر بالوحدة", "ضغوطات", "قلق", "تعبت", "حدا يسمعني", "أشعر بالإرهاق", "مزاجي سيء", "اكتئاب", "قلقان", "تعبان", "مهموم",
        "حزين", "أشعر بالحزن", "إرهاق نفسي", "دعم نفسي", "أشعر بالاكتئاب", "أحتاج للمساعدة", "مساعدة نفسية", "ضغوط نفسية"
    ]
    responses = [
        "You are not alone. Your feelings are valid. If you need someone to talk to, our HR team is here to support you.",
        "We care about your well-being. Taking a small break or talking to a colleague may help. Reach out if you’d like to chat privately.",
        "If you ever feel overwhelmed, remember it’s okay to ask for help. HR and management support mental health.",
        "Feeling stressed is a sign to slow down. Consider talking with your manager or a friend, and take care of yourself.",
        "Mental health matters as much as physical health. Please let HR know if you need support or resources.",
        "You can always ask for a short break or a mental wellness day if things feel heavy.",
        "Small steps count. You’re doing better than you think. Don’t hesitate to reach out.",
        "Our company values your well-being. If you’re feeling down, we can connect you with professional support.",
        "Taking care of yourself is important. HR is always here to listen.",
        "Sometimes talking about it makes a big difference. If you want, HR can suggest wellness programs.",
        "It’s normal to have tough days. You matter and your feelings count.",
        "If you’d like to explore mental health resources, we’re happy to provide them.",
        "You're an important part of the team. Your mental wellness is a priority for us.",
        "Caring for your mental health helps you and your colleagues thrive. We’re here if you need us.",
        "Don’t hesitate to talk to someone—friends, family, or HR. You deserve support.",
        "أنت لست وحدك. صحتك النفسية مهمة بالنسبة لنا.",
        "من الطبيعي أن تمر بأيام صعبة، لا تتردد بطلب الدعم متى احتجت.",
        "إذا كنت بحاجة لمن يستمع إليك، فريق الموارد البشرية موجود دائمًا.",
        "كلنا معرضون للضغوط. لا تخجل من مشاركة مشاعرك مع شخص تثق به.",
        "الصحة النفسية أولويتنا جميعاً. لا تتردد بالطلب المساعدة.",
        "تحدث مع زميل أو صديق، أحياناً الحديث فقط يخفف عنك.",
        "أنت جزء مهم من الفريق وراحتك النفسية ضرورية لنجاحك.",
        # Add up to 100 unique statements as desired...
    ]
    for kw in mh_keywords:
        if kw in q:
            return random.choice(responses)
    return None

def match_employee_question(question, emp_data):
    q = question.lower()
    # Super expanded triggers for full details/profile
    full_triggers = [
        # English
        "my details", "all my data", "my info", "full profile", "my record", "show my details", "show my profile",
        "my complete file", "show everything about me", "all my info", "see my full info", "display my file", "all about me", "all fields", "show my personal data", "all my records", "complete employee details", "full details", "all of my information", "see my data", "give me everything",
        # Arabic
        "كل تفاصيل ملفي", "ملفي بالكامل", "جميع معلوماتي", "بياناتي الكاملة", "أريد كل تفاصيل ملفي", "تفاصيل ملفي", "ملفي", "بياناتي", "أظهر لي كل شيء", "كل عني", "جميع الحقول", "ملف الموظف بالكامل", "معلوماتي كاملة", "كامل بياناتي", "كل شيء عني", "ملفي الشخصي الكامل"
    ]
    if any(x in q for x in full_triggers):
        return "📋 Full Employee Info", emp_data
    elif any(x in q for x in ["salary", "payment", "pay", "bonus", "nssf", "income tax", "راتبي", "تفاصيل الراتب", "قيمة راتبي", "أريد تفاصيل راتبي"]):
        cols = ["Payment Method", "TRANSPORT", "BONUS", "COMM", "OVERTIME", "ABSENCE", "Loan", "TRN-DD", "InSurance", "FAM ALL", "NSSF 3%", "INCOMETAX", "Total Ded", "Total USD", "Total"]
        return "💰 Salary Breakdown", emp_data[[col for col in cols if col in emp_data.columns]]
    elif any(x in q for x in ["joining date", "start date", "hire date", "joined", "تاريخ الانضمام", "متى التحاقي", "متى بدأت العمل", "تاريخ بداية عملي"]):
        return "📅 Joining Date", emp_data[["JOINING DATE"]]
    elif any(x in q for x in ["leave", "annual leave", "vacation", "leave balance", "رصيد الإجازات", "عدد الإجازات", "كم اجازاتي", "اجازاتي", "رصيدي"]):
        return "🌴 Annual Leaves", emp_data[["ANNUAL LEAVES"]]
    elif any(x in q for x in ["social security", "nssf number", "social number", "رقم الضمان", "رقم الضمان الاجتماعي"]):
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
            cols = st
