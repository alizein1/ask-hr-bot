import pandas as pd
import plotly.express as px
from utils.openai_utils import ask_openai

def load_dashboard_data():
    return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")

def dynamic_data_response(df: pd.DataFrame, question: str) -> dict:
    """
    Analyze user question, detect columns and filters,
    return a dict with:
    - found: bool
    - chart: plotly figure or None
    - table: pd.DataFrame or None
    - explanation: str or None
    """
    import json

    # Step 1: Use GPT to parse user question for columns and filters
    parse_prompt = f"""
You are a data analyst. The available columns are: {list(df.columns)}.
A user asked: \"{question}\".

Return a JSON with keys:
- columns: list of columns to group or filter by,
- filters: dictionary of filters as {{"ColumnName": "value"}},
- aggregate: what to count or summarize (e.g. count, average of Salary),
- response_type: either 'chart' or 'table'.

Return only valid columns from the data.
If no meaningful columns found, return empty lists/dicts.
Example:
{{
  "columns": ["Nationality"],
  "filters": {{"Entity": "Tawfeer"}},
  "aggregate": "count",
  "response_type": "chart"
}}
"""

    parse_response = ask_openai(parse_prompt)

    try:
        parsed = json.loads(parse_response)
    except:
        return {"found": False, "chart": None, "table": None, "explanation": None}

    if not parsed.get("columns") and not parsed.get("filters"):
        return {"found": False, "chart": None, "table": None, "explanation": None}

    # Step 2: Filter DataFrame by filters
    df_filtered = df.copy()
    for col, val in parsed.get("filters", {}).items():
        if col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(val, case=False, na=False)]

    # Step 3: Aggregate data
    group_cols = parsed.get("columns", [])
    aggregate = parsed.get("aggregate", "count")
    response_type = parsed.get("response_type", "chart")

    if not group_cols:
        # Show filtered table only
        explanation = ask_openai(f"Analyze this data sample:\n{df_filtered.head(10).to_markdown()}\nQuestion: {question}\nProvide a concise insight summary.")
        return {"found": True, "chart": None, "table": df_filtered, "explanation": explanation}

    if aggregate == "count":
        agg_df = df_filtered.groupby(group_cols).size().reset_index(name="Count")
    elif aggregate.startswith("average"):
        colname = aggregate.split("of")[-1].strip()
        if colname in df_filtered.columns:
            agg_df = df_filtered.groupby(group_cols)[colname].mean().reset_index()
            agg_df.rename(columns={colname: f"Average {colname}"}, inplace=True)
        else:
            agg_df = df_filtered.groupby(group_cols).size().reset_index(name="Count")
    else:
        agg_df = df_filtered.groupby(group_cols).size().reset_index(name="Count")

    # Step 4: Build chart if requested
    fig = None
    if response_type == "chart":
        if len(group_cols) == 1:
            fig = px.bar(agg_df, x=group_cols[0], y=agg_df.columns[-1], title=f"Dashboard: {group_cols[0]} vs {agg_df.columns[-1]}")
        elif len(group_cols) == 2:
            fig = px.bar(agg_df, x=group_cols[0], y=agg_df.columns[-1], color=group_cols[1], barmode="group",
                         title=f"Dashboard: {group_cols[0]} & {group_cols[1]} vs {agg_df.columns[-1]}")
        else:
            fig = px.bar(agg_df, x=group_cols[0], y=agg_df.columns[-1], title=f"Dashboard: {group_cols[0]} vs {agg_df.columns[-1]}")

    # Step 5: GPT explanation of aggregated data
    explanation_prompt = f"Here is aggregated data:\n{agg_df.head(10).to_markdown()}\nQuestion: {question}\nProvide a concise insightful summary."
    explanation = ask_openai(explanation_prompt)

    return {
        "found": True,
        "chart": fig,
        "table": agg_df,
        "explanation": explanation
    }

def generate_excel_download_link(df):
    from io import BytesIO
    import base64
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="export.xlsx">📥 Download Excel file</a>'
    return href

def generate_pdf_download_link(df):
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Dashboard Export", styles["Title"])]

    for col in df.columns:
        text = f"<b>{col}</b>: {', '.join(map(str, df[col].unique()))}"
        elements.append(Paragraph(text, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    import base64
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="export.pdf">📄 Download PDF file</a>'
    return href
