import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import re

def load_dashboard_data():
    return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")

def show_dashboard(df, prompt):
    df.columns = df.columns.str.strip()
    prompt_lower = prompt.lower()

    # Optional entity filtering
    entity_match = re.search(r"in\s+(capital partners|tawfeer|prologistics|[a-zA-Z ]+)", prompt_lower)
    if entity_match:
        entity = entity_match.group(1).strip().title()
        df = df[df['Entity'].str.lower() == entity.lower()]
        st.markdown(f"### Dashboard for {entity}")

    if "gender" in prompt_lower:
        show_bar_chart(df, 'Gender', 'Gender Distribution')

    elif "nationalit" in prompt_lower:
        show_pie_chart(df, 'Nationality', 'Nationality Breakdown')

    elif "job title" in prompt_lower:
        show_bar_chart(df, 'Job Title', 'Job Title Distribution')

    elif "grade" in prompt_lower:
        show_bar_chart(df, 'Grade', 'Grade Distribution')

    elif "band" in prompt_lower:
        show_bar_chart(df, 'Band', 'Band Distribution')

    elif "age" in prompt_lower:
        df['Age Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 55, 70], labels=["18-25", "26-35", "36-45", "46-55", "56+"])
        show_bar_chart(df, 'Age Group', 'Age Group Distribution')

def show_bar_chart(df, column, title):
    try:
        counts = df[column].value_counts().sort_values(ascending=False)
        fig, ax = plt.subplots()
        counts.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel(column)
        ax.set_ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting bar chart: {e}")

def show_pie_chart(df, column, title):
    try:
        counts = df[column].value_counts()
        fig, ax = plt.subplots()
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        ax.set_title(title)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting pie chart: {e}")

def show_employee_details(df, name):
    name_lower = name.lower()
    results = df[df['Full Name'].str.lower().str.contains(name_lower, na=False)]
    if results.empty:
        st.warning("No employee found matching that name.")
    else:
        st.dataframe(results.reset_index(drop=True))
