
import openai
import pandas as pd

def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert HR assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def ask_hr_excel_bot(df, user_prompt):
    preview = df.head(20).to_markdown()
    prompt = f"""You are a professional HR analyst bot. Here's a sample of employee data:

{preview}

Based on this data, answer this user query:
{user_prompt}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an HR data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()
