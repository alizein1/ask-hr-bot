import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_dashboard_data():
    return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")

def show_employee_details(df, prompt):
    filtered = df[df['Full Name'].str.lower().str.contains(prompt.lower())]
    if not filtered.empty:
        st.dataframe(filtered)
    else:
        st.warning("No matching employee found.")

def show_dashboard(df, prompt):
    prompt = prompt.lower()
    matched_column = None
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in prompt or col_lower.rstrip("s") in prompt or col_lower + "s" in prompt:
            matched_column = col
            break

    if matched_column:
        try:
            data = df.groupby(['Entity', matched_column]).size().unstack(fill_value=0)
            st.bar_chart(data.T)
        except Exception as e:
            st.error(f"Couldn't generate dashboard for: {matched_column}")
            st.exception(e)
    elif "age" in prompt:
        bins = [18, 25, 35, 45, 55, 70]
        labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
        df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
        data = df.groupby(['Entity', 'Age Group']).size().unstack(fill_value=0)
        st.bar_chart(data.T)
    else:
        st.warning("No matching dashboard available for this prompt.")

def export_dashboard_data(df, prompt):
    prompt = prompt.lower()
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in prompt or col_lower.rstrip("s") in prompt or col_lower + "s" in prompt:
            return df[['Entity', col]]
    if "age" in prompt:
        return df[['Entity', 'Age']]
    return pd.DataFrame()
