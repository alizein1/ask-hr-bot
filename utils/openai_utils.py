import openai
import os
import pandas as pd
import re
from 
docx import Document
from difflib import get_close_matches

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI error: {e}"

def summarize_policies():
    try:
        doc = Document("data/02 Capital Partners Group Code of Conducts and Business Ethics Policy (1).docx")
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        summary_prompt = f"Summarize the main policy sections into bullet points from this document:\n\n{text[:3000]}"
        return ask_openai(summary_prompt)
    except Exception as e:
        return f"Error reading policy document: {e}"

def ask_hr_excel_bot(df, prompt):
    prompt_lower = prompt.lower()

    # Clean column names
    df.columns = df.columns.str.strip()

    # Filter by entity if present
    entity_match = re.search(r"in\s+(capital partners|tawfeer|prologistics|[a-zA-Z ]+)", prompt_lower)
    if entity_match:
        entity = entity_match.group(1).strip().title()
        filtered_df = df[df['Entity'].str.lower() == entity.lower()]
    else:
        filtered_df = df

    result = ""

    # Try matching a name
    try:
        full_names = df['Full Name'].dropna().astype(str).str.lower().tolist()
        name_matches = get_close_matches(prompt_lower, full_names, n=3, cutoff=0.6)
        if name_matches:
            match = name_matches[0]
            person_df = df[df['Full Name'].str.lower() == match]
            if not person_df.empty:
                if "band" in prompt_lower:
                    band = person_df.iloc[0]['Band']
                    return f"{person_df.iloc[0]['Full Name']} is in band: {band}"
                elif "job title" in prompt_lower:
                    job = person_df.iloc[0]['Job Title']
                    return f"{person_df.iloc[0]['Full Name']} has the job title: {job}"
                else:
                    return person_df.to_string(index=False)
    except:
        pass

    try:
        if "nationalit" in prompt_lower:
            counts = filtered_df['Nationality'].value_counts()
            result += f"Total nationalities: {counts.count()}\n\n" + counts.to_string()

        elif "gender" in prompt_lower:
            counts = filtered_df['Gender'].value_counts()
            result += counts.to_string()

        elif "band" in prompt_lower:
            counts = filtered_df['Band'].value_counts()
            result += counts.to_string()

        elif "grade" in prompt_lower:
            counts = filtered_df['Grade'].value_counts()
            result += counts.to_string()

        elif "job title" in prompt_lower:
            counts = filtered_df['Job Title'].value_counts()
            result += counts.to_string()

        elif "age" in prompt_lower:
            bins = [18, 25, 35, 45, 55, 70]
            labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
            filtered_df['Age Group'] = pd.cut(filtered_df['Age'], bins=bins, labels=labels)
            counts = filtered_df['Age Group'].value_counts().sort_index()
            result += counts.to_string()

        elif "how many" in prompt_lower or "count" in prompt_lower:
            result += f"Total employees: {len(filtered_df)}"

        elif "policy" in prompt_lower or "policies" in prompt_lower:
            result += summarize_policies()

        else:
            result += "No exact match for dashboard keyword, but you can still try visual insights."

    except Exception as e:
        result += f"Excel processing error: {e}"

    return result
