import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def ask_openai(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def ask_hr_excel_bot(df, prompt):
    preview = df.head(5).to_markdown(index=False)
    message = f"""You are an HR assistant. Based on the following employee data table:

{preview}

Answer this question: {prompt}

Be specific and concise."""
    return ask_openai(message)
