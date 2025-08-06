import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
from io import BytesIO
import base64

def show_hr_dashboard():
    st.markdown("## 📊 HR Insights Dashboard")
    
    try:
        df = pd.read_excel("Mass file - To be used for Dashboard.xlsx", sheet_name=0)
        df.columns = df.columns.str.strip()

        st.markdown("### Select a question to explore:")
        question = st.selectbox("Choose insight", [
            "Employee count by age group",
            "Employee count by grade",
            "Employee count by band",
            "Employee count by company",
            "Employee count by nationality",
            "Employee count by gender",
            "Employee count by job title"
        ])

        if question == "Employee count by age group":
            bins = [18, 25, 35, 45, 55, 65]
            labels = ['18–25', '26–35', '36–45', '46–55', '56–65']
            df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
            plot_column(df, "Age Group", "Employee Count by Age Group")

        elif question == "Employee count by grade":
            plot_column(df, "Grade", "Employee Count by Grade")

        elif question == "Employee count by band":
            plot_column(df, "Band", "Employee Count by Band")

        elif question == "Employee count by company":
            plot_column(df, "Company", "Employee Count by Company")

        elif question == "Employee count by nationality":
            plot_column(df, "Nationality", "Employee Count by Nationality")

        elif question == "Employee count by gender":
            plot_column(df, "Gender", "Employee Count by Gender")

        elif question == "Employee count by job title":
            plot_column(df, "Job Title", "Employee Count by Job Title")

    except Exception as e:
        st.error(f"Failed to load dashboard: {e}")

def plot_column(df, column_name, title):
    df = df[df[column_name].notna()]
    counts = df[column_name].value_counts().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=counts.index, y=counts.values, ax=ax)
    ax.set_title(title)
    ax.set_ylabel("Number of Employees")
    ax.set_xlabel(column_name)
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
