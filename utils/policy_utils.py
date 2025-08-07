from docx import Document
from utils.openai_utils import ask_openai

def load_policy_sections(docx_path):
    doc = Document(docx_path)
    sections = []
    current_heading = ""
    current_content = []

    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            if current_heading:
                sections.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content).strip()
                })
            current_heading = para.text.strip()
            current_content = []
        elif para.text.strip():
            current_content.append(para.text.strip())

    if current_heading:
        sections.append({
            "heading": current_heading,
            "content": "\n".join(current_content).strip()
        })

    return sections

def answer_policy_question(user_question, policy_sections):
    context = ""
    for section in policy_sections:
        context += f"\n\n## {section['heading']}\n{section['content']}"

    prompt = f"""
You are a professional HR policy assistant. Below is the Capital Partners Group Code of Conduct and Business Ethics Policy:

{context}

Based on this document, provide a clear, concise, and structured answer to this question:

\"{user_question}\"

If the policy does not contain relevant information, respond politely that no relevant policy content was found.
"""
    return ask_openai(prompt)
