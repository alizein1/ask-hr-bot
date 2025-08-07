# utils/dashboard_utils.py
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

    if "nationalit" in prompt:
        data = df.groupby(['Entity', 'Nationality']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "gender" in prompt:
        data = df.groupby(['Entity', 'Gender']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "band" in prompt:
        data = df.groupby(['Entity', 'Band']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "grade" in prompt:
        data = df.groupby(['Entity', 'Grade']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "job title" in prompt:
        data = df.groupby(['Entity', 'Job Title']).size().unstack(fill_value=0)
        st.bar_chart(data.T)

    elif "age" in prompt:
        bins = [18, 25, 35, 45, 55, 70]
        labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
        df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
        data = df.groupby(['Entity', 'Age Group']).size().unstack(fill_value=0)
        st.bar_chart(data.T)
