from docx import Document

try:
    from openai_utils import ask_openai
except ImportError:
    def ask_openai(prompt):
        return "[OpenAI not available] GPT-based policy answer would appear here."

def load_policy_text(docx_path):
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
        return text
    except Exception as e:
        return f"Error loading policy file: {e}"

def answer_policy_question(question, policy_text):
    prompt = f"""
You are an HR assistant at Capital Partners Group. Based on the official Code of Conduct and Business Ethics Policy below, answer the user's question clearly, professionally, and concisely.

Policy Document:
{policy_text}

User's Question:
{question}

Answer:
"""
    return ask_openai(prompt)