# Ask HR - Capital Partners Group

Smart HR bot using Streamlit + OpenAI + Excel dashboards.

## Features
- Smart Q&A from Excel HR data
- Policy summaries from company code of conduct
- Auto dashboard generation (nationalities, gender, job titles, etc.)
- Supports OpenAI GPT-4o
- Streamlit Cloud ready

## How to Run

1. Add your Excel and policy files inside `/data/`
2. Add your company logo as `logo.png` inside `/assets/`
3. Create `.streamlit/secrets.toml` with your OpenAI key:

```
OPENAI_API_KEY = "your-api-key-here"
```

4. Run:
```
streamlit run app.py
```

## Deploy to Streamlit Cloud

- Upload all files or push to GitHub
- Add OpenAI key in `Secrets`
