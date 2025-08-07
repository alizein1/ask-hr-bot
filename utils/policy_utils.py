
from docx import Document

try:
    from utils.openai_utils import ask_openai
except ImportError:
    def ask_openai(prompt): return "[GPT not available]"

def load_policy_sections(docx_path):
    try:
        doc = Document(docx_path)
        sections = []
        current_title = ""
        current_body = ""
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if para.style.name.startswith("Heading") or text.isupper():
                if current_title and current_body:
                    sections.append(f"{current_title}: {current_body.strip()}")
                    current_body = ""
                current_title = text
            else:
                current_body += " " + text
        if current_title and current_body:
            sections.append(f"{current_title}: {current_body.strip()}")
        return sections
    except Exception as e:
        return [f"Error loading policy file: {e}"]

def answer_policy_question(question, policy_sections):
    policy_text = "\n\n".join(policy_sections[:20])  # limit for context
    prompt = f"""You are an HR assistant. Based on the company's policy sections below, answer the user's question in a concise and structured way.

Policy Sections:
{policy_text}

User's Question:
{question}

Answer clearly and professionally:
"""
    return ask_openai(prompt)
