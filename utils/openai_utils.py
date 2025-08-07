# utils/openai_utils.py
import openai
import os
import pandas as pd
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def ask_hr_excel_bot(df, prompt):
    prompt_lower = prompt.lower()
    df.columns = df.columns.str.strip()

    entity_match = re.search(r"in\s+(capital partners|tawfeer|prologistics|[a-zA-Z ]+)", prompt_lower)
    if entity_match:
        entity = entity_match.group(1).strip().title()
        filtered_df = df[df['Entity'].str.lower() == entity.lower()]
    else:
        filtered_df = df

    result = ""

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

    else:
        result += "No exact match for dashboard keyword, but you can still try visual insights."

    return result
