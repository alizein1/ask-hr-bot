import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an HR assistant for Capital Partners Group."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def ask_hr_excel_bot(df, question):
    prompt = f"""You are an HR data analyst bot. You have the following employee dataset in a Pandas DataFrame:
{df.head(5).to_markdown()}
The columns are: {', '.join(df.columns)}

Based on this data, answer the following question using only the file:
'{question}'

If possible, describe or suggest a chart to show the answer visually. Do not make up data or give general advice. Only use the file content.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert HR data bot that analyzes Excel data using Pandas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
